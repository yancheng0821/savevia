import { useState, useRef, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { CloseOutlined, SendOutlined, DeleteOutlined, LoadingOutlined, RightOutlined, AudioOutlined, BorderOutlined } from '@ant-design/icons'
import { message } from 'antd'
import { Keyboard } from '@capacitor/keyboard'
import { Capacitor } from '@capacitor/core'
import { SpeechRecognition } from '@capacitor-community/speech-recognition'
import { useChatStore, ChatMessage } from '../stores/useChatStore'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import { chatApi, userApi, cardApi } from '../services/api'
import { CreditCard } from '../types'
import i18next from 'i18next'

// Find card by name (fuzzy match)
function findCardByName(name: string, cards: CreditCard[]): CreditCard | undefined {
  const normalizedName = name.toLowerCase().replace(/[（）()]/g, '').trim()
  return cards.find(card => {
    const cardName = card.name.toLowerCase().replace(/[（）()]/g, '').trim()
    // Check if names match (allowing for slight variations)
    return cardName.includes(normalizedName) || normalizedName.includes(cardName) ||
      // Also try without bank suffix
      normalizedName.replace(/\s*[\(（].*$/, '').includes(cardName) ||
      cardName.includes(normalizedName.replace(/\s*[\(（].*$/, ''))
  })
}

// Desktop chat-window width bounds (the resize "临界点" / hard stops)
const MIN_CHAT_WIDTH = 360
const MAX_CHAT_WIDTH = 720
const DEFAULT_CHAT_WIDTH = 400

// "Deep thinking" indicator — reveals friendly, non-technical activity steps
// while the assistant works (before the first answer token streams in).
function ChatThinking() {
  const { t } = useTranslation()
  const raw = t('chat.thinkingSteps', { returnObjects: true })
  const steps = Array.isArray(raw) ? (raw as string[]) : []
  const [idx, setIdx] = useState(0)

  useEffect(() => {
    if (steps.length <= 1) return
    const timer = setInterval(() => {
      setIdx((i) => (i < steps.length - 1 ? i + 1 : i))
    }, 1600)
    return () => clearInterval(timer)
  }, [steps.length])

  return (
    <div className="chat-thinking">
      <div className="chat-thinking-title">
        {t('chat.thinking')}
        <span className="chat-thinking-dots"><span /><span /><span /></span>
      </div>
      {steps.length > 0 && (
        <div className="chat-thinking-steps">
          {steps.slice(0, idx + 1).map((step, i) => (
            <div key={i} className={`chat-thinking-step ${i === idx ? 'active' : 'done'}`}>
              <span className="chat-thinking-step-icon">
                {i === idx ? <LoadingOutlined /> : '✓'}
              </span>
              <span className="chat-thinking-step-text">{step}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ChatWindow() {
  const { t } = useTranslation()
  const {
    isOpen,
    setOpen,
    isLoading,
    setLoading,
    setError,
    messages,
    addMessage,
    setMessages,
    appendToLastMessage,
    setMessageStreaming,
    clearMessages,
    currentConversationId,
    setCurrentConversationId,
    suggestions,
    setSuggestions,
    skipLoadHistory,
    setSkipLoadHistory,
  } = useChatStore()

  const { selectedCards } = useOptimizerStore()
  const { user } = useAuthStore()
  const userInitial = (user?.name?.trim()?.[0] || user?.email?.trim()?.[0] || 'U').toUpperCase()
  const navigate = useNavigate()

  // Get all cards for card link matching
  const { data: allCards = [] } = useQuery({
    queryKey: ['cards'],
    queryFn: cardApi.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
  const [inputValue, setInputValue] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [chatRemaining, setChatRemaining] = useState<number | null>(null)
  const [hasAnimated, setHasAnimated] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  const [toastMessage, setToastMessage] = useState<string | null>(null)
  const isRecordingRef = useRef(false)  // Ref to track recording state in callbacks
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null)  // Timer for 30s limit
  const toastTimerRef = useRef<NodeJS.Timeout | null>(null)  // Timer for toast auto-hide
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const abortRef = useRef<(() => void) | null>(null)
  const chatWindowRef = useRef<HTMLDivElement>(null)
  const webRecognitionRef = useRef<any>(null)
  // Typewriter buffer for smooth SSE streaming (decouples render cadence from network bursts)
  const typeBufferRef = useRef('')
  const streamEndedRef = useRef(false)
  const typeRafRef = useRef<number | null>(null)

  // --- Desktop resize: drag the left edge to widen/narrow, clamped to bounds ---
  const [chatWidth, setChatWidth] = useState<number>(() => {
    const saved = Number(localStorage.getItem('sv-chat-width'))
    return saved >= MIN_CHAT_WIDTH && saved <= MAX_CHAT_WIDTH ? saved : DEFAULT_CHAT_WIDTH
  })
  const widthRef = useRef(chatWidth)
  const resizeRef = useRef<{ startX: number; startWidth: number } | null>(null)

  const onResizeMove = useCallback((e: PointerEvent) => {
    const s = resizeRef.current
    if (!s) return
    // Window is anchored bottom-right, so dragging the left edge LEFT widens it.
    const maxW = Math.min(MAX_CHAT_WIDTH, window.innerWidth - 40)
    const next = Math.min(Math.max(s.startWidth + (s.startX - e.clientX), MIN_CHAT_WIDTH), maxW)
    widthRef.current = next
    setChatWidth(next)
  }, [])

  const onResizeEnd = useCallback(() => {
    resizeRef.current = null
    window.removeEventListener('pointermove', onResizeMove)
    window.removeEventListener('pointerup', onResizeEnd)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
    try { localStorage.setItem('sv-chat-width', String(Math.round(widthRef.current))) } catch { /* ignore */ }
  }, [onResizeMove])

  const onResizeStart = useCallback((e: React.PointerEvent) => {
    // Mobile is a full-screen bottom sheet — no resizing there.
    if (window.innerWidth <= 640) return
    e.preventDefault()
    resizeRef.current = { startX: e.clientX, startWidth: widthRef.current }
    window.addEventListener('pointermove', onResizeMove)
    window.addEventListener('pointerup', onResizeEnd)
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'ew-resize'
  }, [onResizeMove, onResizeEnd])

  // Cancel the typewriter loop on unmount
  useEffect(() => {
    return () => {
      if (typeRafRef.current != null) cancelAnimationFrame(typeRafRef.current)
    }
  }, [])

  // Track animation state to prevent re-animation on iOS swipe back
  useEffect(() => {
    if (isOpen && !hasAnimated) {
      setHasAnimated(true)
    } else if (!isOpen) {
      setHasAnimated(false)
    }
  }, [isOpen, hasAnimated])

  // Check speech recognition support
  useEffect(() => {
    const checkSpeechSupport = async () => {
      if (Capacitor.isNativePlatform()) {
        // Check native speech recognition
        try {
          const { available } = await SpeechRecognition.available()
          setSpeechSupported(available)
        } catch {
          setSpeechSupported(false)
        }
      } else {
        // Check Web Speech API
        const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
        setSpeechSupported(!!SpeechRecognitionAPI)
      }
    }
    checkSpeechSupport()
  }, [])

  // Get speech recognition language code
  const getSpeechLanguage = () => {
    // Use resolvedLanguage which gives the actual loaded language (e.g., 'zh' not 'zh-CN')
    // Fallback to language and extract base code if needed
    const lang = i18next.resolvedLanguage || i18next.language?.split('-')[0] || 'en'
    const languageMap: Record<string, string> = {
      'zh': 'zh-CN',
      'en': 'en-US',
      'ja': 'ja-JP',
      'ko': 'ko-KR',
      'es': 'es-ES',
      'fr': 'fr-FR',
    }
    return languageMap[lang] || 'en-US'
  }

  // Helper to update input value and scroll to end
  const updateInputWithScroll = (text: string) => {
    setInputValue(text)
    // Scroll input to show latest text
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.scrollLeft = inputRef.current.scrollWidth
      }
    }, 0)
  }

  // Start 30-second recording timer
  const startRecordingTimer = () => {
    // Clear any existing timer
    if (recordingTimerRef.current) {
      clearTimeout(recordingTimerRef.current)
    }
    // Get the timeout message now to avoid closure issues
    const timeoutMsg = t('chat.voiceTimeout')
    // Set new 30-second timer
    recordingTimerRef.current = setTimeout(async () => {
      if (isRecordingRef.current) {
        await stopRecording()
        showToast(timeoutMsg)
      }
    }, 30000)
  }

  // Clear recording timer
  const clearRecordingTimer = () => {
    if (recordingTimerRef.current) {
      clearTimeout(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
  }

  // Show toast message
  const showToast = (msg: string, duration = 2500) => {
    // Clear any existing timer
    if (toastTimerRef.current) {
      clearTimeout(toastTimerRef.current)
    }
    setToastMessage(msg)
    toastTimerRef.current = setTimeout(() => {
      setToastMessage(null)
      toastTimerRef.current = null
    }, duration)
  }

  // Handle voice input
  const handleVoiceInput = async () => {
    if (isLoading) return

    if (isRecording) {
      // Stop recording
      await stopRecording()
      return
    }

    // Start recording
    if (Capacitor.isNativePlatform()) {
      // Use native speech recognition
      try {
        // Check if permission is already granted before requesting
        const checkStatus = await SpeechRecognition.checkPermissions()
        if (checkStatus.speechRecognition !== 'granted') {
          // Only request if not already granted
          const permStatus = await SpeechRecognition.requestPermissions()
          if (permStatus.speechRecognition !== 'granted') {
            message.warning(t('chat.voicePermissionDenied'))
            return
          }
        }

        setIsRecording(true)
        isRecordingRef.current = true
        startRecordingTimer()

        // Listen for partial results (real-time transcription)
        SpeechRecognition.addListener('partialResults', (data: { matches: string[] }) => {
          if (data.matches && data.matches.length > 0) {
            updateInputWithScroll(data.matches[0])
          }
        })

        // Listen for state changes - restart if stopped unexpectedly
        SpeechRecognition.addListener('listeningState', async (data: { status: 'started' | 'stopped' }) => {
          if (data.status === 'stopped' && isRecordingRef.current) {
            // Restart recognition to continue listening
            try {
              await SpeechRecognition.start({
                language: getSpeechLanguage(),
                maxResults: 1,
                popup: false,
                partialResults: true,
              })
            } catch {
              // If restart fails, stop recording
              clearRecordingTimer()
              setIsRecording(false)
              isRecordingRef.current = false
            }
          }
        })

        // Start with partialResults to get real-time transcription
        await SpeechRecognition.start({
          language: getSpeechLanguage(),
          maxResults: 1,
          popup: false,
          partialResults: true,
        })
      } catch (err) {
        console.error('Speech recognition error:', err)
        clearRecordingTimer()
        setIsRecording(false)
        message.error(t('chat.voiceError'))
      }
    } else {
      // Use Web Speech API
      const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      if (!SpeechRecognitionAPI) {
        message.warning(t('chat.voiceNotSupported'))
        return
      }

      try {
        const recognition = new SpeechRecognitionAPI()
        recognition.lang = getSpeechLanguage()
        recognition.continuous = true  // Keep listening until manually stopped
        recognition.interimResults = true

        recognition.onresult = (event: any) => {
          // Get all transcripts from all results
          let finalTranscript = ''
          let interimTranscript = ''

          for (let i = 0; i < event.results.length; i++) {
            const result = event.results[i]
            if (result.isFinal) {
              finalTranscript += result[0].transcript
            } else {
              interimTranscript += result[0].transcript
            }
          }

          updateInputWithScroll(finalTranscript + interimTranscript)
        }

        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
          // Don't stop for no-speech error in continuous mode
          if (event.error !== 'aborted' && event.error !== 'no-speech') {
            clearRecordingTimer()
            setIsRecording(false)
            isRecordingRef.current = false
            message.error(t('chat.voiceError'))
          }
        }

        recognition.onend = () => {
          // In continuous mode, restart if still recording
          if (webRecognitionRef.current && isRecordingRef.current) {
            try {
              recognition.start()
            } catch {
              clearRecordingTimer()
              setIsRecording(false)
              isRecordingRef.current = false
              webRecognitionRef.current = null
            }
          } else {
            clearRecordingTimer()
            setIsRecording(false)
            isRecordingRef.current = false
            webRecognitionRef.current = null
          }
        }

        webRecognitionRef.current = recognition
        setIsRecording(true)
        isRecordingRef.current = true
        startRecordingTimer()
        recognition.start()
      } catch (err) {
        console.error('Web Speech error:', err)
        message.error(t('chat.voiceError'))
      }
    }
  }

  const stopRecording = async () => {
    // Set ref first to prevent auto-restart in callbacks
    isRecordingRef.current = false
    clearRecordingTimer()

    if (Capacitor.isNativePlatform()) {
      try {
        await SpeechRecognition.stop()
        await SpeechRecognition.removeAllListeners()
      } catch (err) {
        console.error('Stop recording error:', err)
      }
    } else {
      if (webRecognitionRef.current) {
        webRecognitionRef.current.stop()
        webRecognitionRef.current = null
      }
    }
    setIsRecording(false)
    // Focus input after recording stops so cursor is visible
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
  }

  // Cleanup on close
  useEffect(() => {
    if (!isOpen && isRecording) {
      stopRecording()
    }
  }, [isOpen])

  // Handle card click - navigate to card detail
  const handleCardClick = (cardId: number) => {
    console.log('[ChatWindow] handleCardClick, cardId:', cardId)
    // Use sessionStorage to persist flag across bfcache restoration
    sessionStorage.setItem('shouldReopenChat', 'true')
    console.log('[ChatWindow] Set shouldReopenChat to true, calling setOpen(false)')
    setOpen(false)
    navigate(`/cards/${cardId}`)
  }


  // Render markdown with clickable card names
  const renderMarkdown = useCallback((text: string): React.ReactNode => {
    if (!text) return null

    // Split by **bold** pattern
    const parts = text.split(/(\*\*[^*]+\*\*)/g)

    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2)
        // Try to find matching card from all cards in system
        const matchedCard = findCardByName(boldText, allCards)

        if (matchedCard) {
          // Render as clickable card link
          return (
            <span
              key={index}
              className="chat-card-link"
              onClick={() => handleCardClick(matchedCard.id)}
            >
              {boldText}
              <RightOutlined className="chat-card-link-icon" />
            </span>
          )
        }
        // Just bold text
        return <strong key={index}>{boldText}</strong>
      }
      // Handle newlines
      if (part.includes('\n')) {
        return part.split('\n').map((line, lineIndex, arr) => (
          <span key={`${index}-${lineIndex}`}>
            {line}
            {lineIndex < arr.length - 1 && <br />}
          </span>
        ))
      }
      return part
    })
  }, [allCards, handleCardClick])

  // Scroll to bottom when messages change
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const scrollRAFRef = useRef<number | null>(null)

  useEffect(() => {
    if (scrollRAFRef.current) {
      cancelAnimationFrame(scrollRAFRef.current)
    }

    scrollRAFRef.current = requestAnimationFrame(() => {
      const container = messagesContainerRef.current
      if (!container) return

      const lastMessage = messages[messages.length - 1]
      const isStreaming = lastMessage?.isStreaming

      if (isStreaming) {
        // During streaming: directly set scrollTop for stable, smooth following
        container.scrollTop = container.scrollHeight
      } else {
        // After streaming: use smooth scrollIntoView
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }
    })

    return () => {
      if (scrollRAFRef.current) {
        cancelAnimationFrame(scrollRAFRef.current)
      }
    }
  }, [messages])

  // Track current language for suggestions reload
  const [currentLang, setCurrentLang] = useState(i18next.language)

  // Load suggestions, recent conversation, and usage on open
  useEffect(() => {
    if (isOpen) {
      // Reload suggestions if language changed or not loaded yet
      const lang = i18next.language
      if (suggestions.length === 0 || lang !== currentLang) {
        setCurrentLang(lang)
        loadSuggestions()
      }
      // Load chat usage info
      loadChatUsage()

      if (messages.length === 0) {
        if (currentConversationId) {
          // Has conversation ID but no messages - load messages for this conversation
          loadConversationMessages(currentConversationId)
        } else if (!skipLoadHistory) {
          // No conversation ID and no messages - load most recent conversation
          loadRecentConversation()
        }
      } else {
        // Already have messages, scroll to bottom instantly
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'instant' })
        }, 50)
      }
    }
  }, [isOpen, skipLoadHistory, currentConversationId])

  const loadConversationMessages = async (conversationId: number) => {
    setIsLoadingHistory(true)
    try {
      const msgResult = await chatApi.getMessages(conversationId)
      if (msgResult.data && msgResult.data.length > 0) {
        const loadedMessages: ChatMessage[] = msgResult.data.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          createdAt: msg.createdAt,
        }))
        setMessages(loadedMessages)
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'instant' })
        }, 50)
      }
    } catch (err) {
      console.error('Failed to load conversation messages:', err)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const loadRecentConversation = async () => {
    setIsLoadingHistory(true)
    try {
      // Get user's conversations
      const convResult = await chatApi.getConversations(1)
      if (convResult.data && convResult.data.length > 0) {
        const recentConv = convResult.data[0]
        // Load messages from the most recent conversation
        const msgResult = await chatApi.getMessages(recentConv.id)
        if (msgResult.data && msgResult.data.length > 0) {
          setCurrentConversationId(recentConv.id)
          // Set all messages at once
          const loadedMessages: ChatMessage[] = msgResult.data.map((msg: any) => ({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            createdAt: msg.createdAt,
          }))
          setMessages(loadedMessages)
          // Scroll to bottom instantly after loading
          setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'instant' })
          }, 50)
        }
      }
    } catch (err) {
      console.error('Failed to load recent conversation:', err)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  // Focus input on open - disabled on mobile to prevent keyboard issues
  useEffect(() => {
    if (isOpen) {
      const isMobile = window.innerWidth <= 640
      if (!isMobile) {
        // Only auto-focus on desktop
        setTimeout(() => inputRef.current?.focus(), 300)
      }
    }
  }, [isOpen])

  // Prevent body scroll when chat is open
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.documentElement.style.setProperty('--scroll-y', `${scrollY}px`)
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'

      return () => {
        document.body.style.overflow = ''
        document.body.style.position = ''
        document.body.style.top = ''
        document.body.style.width = ''
        window.scrollTo(0, scrollY)
      }
    }
  }, [isOpen])

  // Handle keyboard using Capacitor Keyboard plugin (iOS/Android)
  useEffect(() => {
    if (!isOpen) return

    // Only use Capacitor Keyboard on native platforms
    if (!Capacitor.isNativePlatform()) return

    // Check if mobile
    const isMobile = window.innerWidth <= 640
    if (!isMobile) return

    // Get safe area inset from CSS
    const getSafeAreaTop = () => {
      const temp = document.createElement('div')
      temp.style.paddingTop = 'env(safe-area-inset-top, 0px)'
      document.body.appendChild(temp)
      const safeArea = parseInt(getComputedStyle(temp).paddingTop) || 0
      document.body.removeChild(temp)
      return safeArea
    }

    const safeAreaTop = getSafeAreaTop()
    const topMargin = 20
    const totalTopOffset = safeAreaTop + topMargin
    const fullScreenHeight = window.innerHeight

    console.log('[ChatWindow] Keyboard plugin init:', { fullScreenHeight, safeAreaTop, totalTopOffset })

    const updateChatSize = (keyboardHeight: number) => {
      const chatWindow = chatWindowRef.current
      if (!chatWindow) return

      if (keyboardHeight > 0) {
        // Keyboard is open
        // Chat extends to bottom, input container has padding to stay above keyboard
        chatWindow.style.top = `${totalTopOffset}px`
        chatWindow.style.height = ''
        chatWindow.style.bottom = '0'
        chatWindow.classList.add('keyboard-open')
        // Set keyboard height as CSS variable for input positioning
        chatWindow.style.setProperty('--keyboard-height', `${keyboardHeight}px`)

        console.log('[ChatWindow] keyboard show:', { keyboardHeight })

        // Scroll messages to bottom
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'instant' })
        }, 50)
      } else {
        // Keyboard is closed - fill screen
        chatWindow.style.top = `${totalTopOffset}px`
        chatWindow.style.height = ''
        chatWindow.style.bottom = '0'
        chatWindow.classList.remove('keyboard-open')
        chatWindow.style.removeProperty('--keyboard-height')
      }
    }

    // Listen to Capacitor Keyboard events
    const showListener = Keyboard.addListener('keyboardWillShow', (info) => {
      console.log('[ChatWindow] keyboardWillShow:', info.keyboardHeight)
      updateChatSize(info.keyboardHeight)
    })

    const hideListener = Keyboard.addListener('keyboardWillHide', () => {
      console.log('[ChatWindow] keyboardWillHide')
      updateChatSize(0)
    })

    return () => {
      showListener.then(handle => handle.remove())
      hideListener.then(handle => handle.remove())
      // Reset styles
      const chatWindow = chatWindowRef.current
      if (chatWindow) {
        chatWindow.style.top = ''
        chatWindow.style.height = ''
        chatWindow.style.bottom = ''
        chatWindow.classList.remove('keyboard-open')
      }
    }
  }, [isOpen])

  const loadSuggestions = async () => {
    try {
      const result = await chatApi.getSuggestions(i18next.language)
      if (result.data) {
        setSuggestions(result.data)
      }
    } catch (err) {
      console.error('Failed to load suggestions:', err)
    }
  }

  const loadChatUsage = async () => {
    try {
      const result = await userApi.getAiUsage()
      if (result.data) {
        setChatRemaining(result.data.chatRemaining)
      }
    } catch (err) {
      console.error('Failed to load chat usage:', err)
    }
  }

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: text.trim(),
    }

    // Add user message
    addMessage(userMessage)
    setInputValue('')
    setLoading(true)
    setError(null)

    // Add placeholder for assistant response
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: '',
      isStreaming: true,
    }
    addMessage(assistantMessage)

    // Smooth "typewriter": SSE chunks fill a buffer; a rAF loop reveals them at
    // a steady cadence so bursty network delivery still renders fluidly.
    typeBufferRef.current = ''
    streamEndedRef.current = false
    if (typeRafRef.current != null) {
      cancelAnimationFrame(typeRafRef.current)
      typeRafRef.current = null
    }

    const finalize = () => {
      setMessageStreaming(false)
      setLoading(false)
      loadChatUsage()
    }

    const pump = () => {
      const buf = typeBufferRef.current
      if (buf.length > 0) {
        // Drain faster when a backlog builds up, so we never visibly lag behind.
        const take = Math.max(1, Math.ceil(buf.length / 8))
        typeBufferRef.current = buf.slice(take)
        appendToLastMessage(buf.slice(0, take))
      }
      if (typeBufferRef.current.length > 0 || !streamEndedRef.current) {
        typeRafRef.current = requestAnimationFrame(pump)
      } else {
        typeRafRef.current = null
        finalize()
      }
    }
    typeRafRef.current = requestAnimationFrame(pump)

    // Start streaming
    abortRef.current = chatApi.streamMessage(
      text.trim(),
      currentConversationId,
      i18next.language,
      {
        onConversationId: (id) => {
          setCurrentConversationId(id)
        },
        onChunk: (chunk) => {
          // Feed the typewriter buffer instead of rendering immediately.
          typeBufferRef.current += chunk
        },
        onDone: () => {
          // Let the typewriter drain the remaining buffer, then finalize().
          streamEndedRef.current = true
        },
        onError: (err) => {
          streamEndedRef.current = true
          if (typeRafRef.current != null) {
            cancelAnimationFrame(typeRafRef.current)
            typeRafRef.current = null
          }
          setError(err)
          setLoading(false)
          setMessageStreaming(false)
          message.error(err)
        },
      }
    )
  }, [isLoading, currentConversationId])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  const handleClose = () => {
    console.log('[ChatWindow] handleClose called')
    // Abort any ongoing stream
    if (abortRef.current) {
      abortRef.current()
      abortRef.current = null
    }
    // Stop the typewriter loop
    if (typeRafRef.current != null) {
      cancelAnimationFrame(typeRafRef.current)
      typeRafRef.current = null
    }
    // Reset skipLoadHistory so next open will load recent conversation
    setSkipLoadHistory(false)
    setOpen(false)
  }

  const handleNewChat = () => {
    if (abortRef.current) {
      abortRef.current()
      abortRef.current = null
    }
    if (typeRafRef.current != null) {
      cancelAnimationFrame(typeRafRef.current)
      typeRafRef.current = null
    }
    // Just clear local state - don't delete from database
    // Next message will create a new conversation
    // Set flag to prevent immediately reloading the old conversation
    setSkipLoadHistory(true)
    clearMessages()
    setLoading(false)
    setShowDeleteConfirm(false)
  }

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true)
  }

  if (!isOpen) return null

  return (
    <div className={`chat-window-overlay ${hasAnimated ? 'chat-no-animate' : ''}`}>
      <div
        ref={chatWindowRef}
        className={`chat-window ${hasAnimated ? 'chat-no-animate' : ''}`}
        style={{ '--chat-width': `${chatWidth}px` } as React.CSSProperties}
      >
        {/* Resize handle (desktop only) — drag the left edge to widen/narrow */}
        <div
          className="chat-resize-handle"
          onPointerDown={onResizeStart}
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize chat width"
        />

        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-info">
            <img src="/logo-full.svg" alt="SaveVia" className="chat-header-logo" />
            <span className="chat-header-subtitle">
              {selectedCards.length > 0
                ? t('chat.cardsSelected', { count: selectedCards.length })
                : t('chat.noCards')}
              {chatRemaining !== null && (
                <> · {t('chat.chatRemaining', { count: chatRemaining })}</>
              )}
            </span>
          </div>
          <div className="chat-header-actions">
            {messages.length > 0 && (
              <button className="chat-header-btn" onClick={handleDeleteClick} aria-label={t('chat.newChat')}>
                <DeleteOutlined />
              </button>
            )}
            <button className="chat-header-btn" onClick={handleClose} aria-label={t('common.close')}>
              <CloseOutlined />
            </button>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="chat-confirm-overlay" onClick={() => setShowDeleteConfirm(false)}>
            <div className="chat-confirm-modal" onClick={e => e.stopPropagation()}>
              <div className="chat-confirm-title">{t('chat.newChatConfirm')}</div>
              <div className="chat-confirm-actions">
                <button className="chat-confirm-btn chat-confirm-cancel" onClick={() => setShowDeleteConfirm(false)}>
                  {t('common.cancel')}
                </button>
                <button className="chat-confirm-btn chat-confirm-ok" onClick={handleNewChat}>
                  {t('common.confirm')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Toast Notification */}
        {toastMessage && (
          <div className="chat-toast">
            {toastMessage}
          </div>
        )}

        {/* Messages */}
        <div className="chat-messages" ref={messagesContainerRef}>
          {isLoadingHistory ? (
            <div className="chat-empty">
              <LoadingOutlined style={{ fontSize: 24, color: '#6b7280' }} />
            </div>
          ) : messages.length === 0 ? (
            <div className="chat-empty">
              <div className="chat-empty-title">{t('chat.emptyTitle')}</div>
              <div className="chat-empty-subtitle">{t('chat.emptySubtitle')}</div>
              <div className="chat-suggestions">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="chat-suggestion-btn"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => {
                const isUser = msg.role === 'user'
                return (
                  <div
                    key={index}
                    className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}
                  >
                    <div className="chat-avatar" aria-hidden="true">
                      {isUser ? (
                        user?.avatarUrl ? (
                          <img src={user.avatarUrl} alt="" className="chat-avatar-img" />
                        ) : (
                          <span className="chat-avatar-initial">{userInitial}</span>
                        )
                      ) : (
                        <img src="/logo.svg" alt="SaveVia" className="chat-avatar-logo" />
                      )}
                    </div>
                    <div className="chat-message-content">
                      {msg.content ? renderMarkdown(msg.content) : (msg.isStreaming ? <ChatThinking /> : null)}
                    </div>
                  </div>
                )
              })}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <form className="chat-input-container" onSubmit={handleSubmit}>
          <div className="chat-input-box">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              placeholder={isRecording ? t('chat.voiceListening') : t('chat.inputPlaceholder')}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading || isRecording}
            />
            {speechSupported && (
              <button
                type="button"
                className={`chat-voice-btn ${isRecording ? 'recording' : ''}`}
                onClick={handleVoiceInput}
                disabled={isLoading}
                aria-label={isRecording ? t('chat.voiceStop') : t('chat.voiceStart')}
              >
                {isRecording ? <BorderOutlined /> : <AudioOutlined />}
              </button>
            )}
            <button
              type="submit"
              className="chat-send-btn"
              disabled={!inputValue.trim() || isLoading || isRecording}
            >
              {isLoading ? <LoadingOutlined /> : <SendOutlined />}
            </button>
          </div>
        </form>
      </div>

      <style>{`
        .chat-window-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.4);
          z-index: 10000;
          display: flex;
          align-items: flex-end;
          justify-content: flex-end;
          padding: 20px;
          padding-bottom: calc(20px + env(safe-area-inset-bottom, 0px));
          animation: overlayFadeIn 0.2s ease;
          /* GPU acceleration for iOS stability */
          -webkit-transform: translateZ(0);
          transform: translateZ(0);
          -webkit-backface-visibility: hidden;
          backface-visibility: hidden;
        }

        @keyframes overlayFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        /* Disable animation after first render (prevents flicker on iOS swipe back) */
        .chat-window-overlay.chat-no-animate {
          animation: none;
        }

        .chat-window.chat-no-animate {
          animation: none;
        }

        .chat-window {
          width: var(--chat-width, 400px);
          max-width: 100%;
          height: 600px;
          position: relative;
          max-height: calc(100vh - 100px);
          background: #fffcf5;
          border-radius: 20px;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
          animation: windowSlideUp 0.3s cubic-bezier(0.32, 0.72, 0, 1);
          /* GPU acceleration for iOS stability */
          -webkit-transform: translateZ(0);
          transform: translateZ(0);
          -webkit-backface-visibility: hidden;
          backface-visibility: hidden;
          /* Allow touch scrolling on iOS */
          touch-action: pan-y;
        }

        /* Resize handle — left edge, desktop only */
        .chat-resize-handle {
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 10px;
          cursor: ew-resize;
          z-index: 20;
          touch-action: none;
        }

        .chat-resize-handle::after {
          content: '';
          position: absolute;
          left: 3px;
          top: 50%;
          transform: translateY(-50%);
          width: 4px;
          height: 44px;
          border-radius: 4px;
          background: rgba(0, 0, 0, 0.12);
          opacity: 0;
          transition: opacity 0.2s ease;
        }

        .chat-resize-handle:hover::after,
        .chat-resize-handle:active::after {
          opacity: 1;
        }

        html.dark-mode .chat-resize-handle::after {
          background: rgba(255, 255, 255, 0.2);
        }

        @keyframes windowSlideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        /* Mobile: full screen bottom sheet */
        @media (max-width: 640px) {
          .chat-window-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 0;
            background: rgba(0, 0, 0, 0.3);
            /* Height set by JS for keyboard handling, fallback to 100% */
            height: 100%;
            /* Prevent iOS scroll bounce */
            overscroll-behavior: none;
          }

          /* No edge-resize on the mobile full-screen sheet */
          .chat-resize-handle {
            display: none;
          }

          .chat-window {
            position: fixed;
            top: calc(env(safe-area-inset-top, 0px) + 20px);
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: auto;
            max-height: none;
            border-radius: 20px 20px 0 0;
            box-shadow: none;
            animation: mobileSlideUp 0.35s cubic-bezier(0.32, 0.72, 0, 1);
            /* Ensure proper stacking and rendering */
            -webkit-transform: translate3d(0, 0, 0);
            transform: translate3d(0, 0, 0);
          }

          @keyframes mobileSlideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
          }

        }

        .chat-header {
          background: #fffcf5;
          border-bottom: 1px solid rgba(0, 0, 0, 0.06);
          padding: 16px 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        /* Mobile header with drag handle */
        @media (max-width: 640px) {
          .chat-header {
            padding-top: 24px;
            position: relative;
          }

          .chat-header::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            width: 36px;
            height: 4px;
            background: rgba(0, 0, 0, 0.15);
            border-radius: 2px;
          }
        }

        .chat-header-info {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 2px;
          flex: 1;
        }

        .chat-header-logo {
          height: 32px;
          width: auto;
        }

        /* Delete Confirmation Modal */
        .chat-confirm-overlay {
          position: absolute;
          inset: 0;
          background: rgba(0, 0, 0, 0.4);
          z-index: 100;
          display: flex;
          align-items: center;
          justify-content: center;
          animation: overlayFadeIn 0.15s ease;
          border-radius: 20px;
          touch-action: auto;
        }

        .chat-confirm-modal {
          background: #fffcf5;
          border-radius: 14px;
          touch-action: auto;
          padding: 20px;
          width: 280px;
          text-align: center;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
          animation: modalScaleIn 0.2s cubic-bezier(0.32, 0.72, 0, 1);
        }

        @keyframes modalScaleIn {
          from { transform: scale(0.9); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }

        .chat-confirm-title {
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 20px;
        }

        .chat-confirm-actions {
          display: flex;
          gap: 12px;
        }

        .chat-confirm-btn {
          flex: 1;
          padding: 12px 16px;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          touch-action: manipulation;
          -webkit-tap-highlight-color: transparent;
        }

        .chat-confirm-cancel {
          background: rgba(0, 0, 0, 0.06);
          border: none;
          color: #374151;
        }

        .chat-confirm-cancel:active {
          background: rgba(0, 0, 0, 0.1);
        }

        .chat-confirm-ok {
          background: #111827;
          border: none;
          color: white;
        }

        .chat-confirm-ok:active {
          background: #1f2937;
        }

        .chat-header-subtitle {
          font-size: 11px;
          color: #6b7280;
          text-align: left;
        }

        .chat-header-actions {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .chat-header-btn {
          padding: 8px;
          border: none;
          background: transparent;
          color: #9ca3af;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          transition: all 0.15s;
          touch-action: manipulation;
          -webkit-tap-highlight-color: transparent;
        }

        .chat-header-btn:hover {
          color: #6b7280;
        }

        .chat-header-btn:active {
          transform: scale(0.9);
          color: #374151;
        }

        .chat-messages {
          flex: 1;
          min-height: 0;
          overflow-y: auto;
          -webkit-overflow-scrolling: touch;
          overscroll-behavior: contain;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          /* GPU acceleration for smooth scrolling */
          will-change: scroll-position;
          transform: translateZ(0);
          -webkit-transform: translateZ(0);
        }

        .chat-empty {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 20px;
        }

        .chat-empty-title {
          font-size: 18px;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 8px;
        }

        .chat-empty-subtitle {
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 24px;
        }

        .chat-suggestions {
          display: flex;
          flex-direction: column;
          gap: 10px;
          width: 100%;
          max-width: 300px;
        }

        .chat-suggestion-btn {
          padding: 12px 16px;
          border-radius: 12px;
          border: 1px solid rgba(0, 0, 0, 0.08);
          background: rgba(0, 0, 0, 0.02);
          color: #374151;
          font-size: 14px;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s;
        }

        .chat-suggestion-btn:hover {
          background: rgba(0, 0, 0, 0.04);
          border-color: rgba(0, 0, 0, 0.12);
          color: #111827;
        }

        .chat-message {
          max-width: 88%;
          display: flex;
          align-items: flex-end;
          gap: 8px;
          animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .chat-message-user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .chat-message-assistant {
          align-self: flex-start;
        }

        /* Per-message avatars (chat-log feel) */
        .chat-avatar {
          width: 30px;
          height: 30px;
          border-radius: 50%;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          margin-bottom: 2px;
        }

        .chat-avatar-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .chat-avatar-logo {
          width: 24px;
          height: 24px;
          object-fit: contain;
        }

        .chat-message-user .chat-avatar {
          background: linear-gradient(135deg, #3b82f6 0%, #14b8a6 100%);
          color: #fff;
          font-size: 13px;
          font-weight: 600;
          line-height: 1;
        }

        .chat-message-assistant .chat-avatar {
          background: #ffffff;
          border: 1px solid rgba(0, 0, 0, 0.06);
        }

        .chat-message-content {
          padding: 12px 16px;
          border-radius: 16px;
          font-size: 14px;
          line-height: 1.5;
          white-space: pre-wrap;
          word-break: break-word;
          min-width: 0;
        }

        .chat-message-user .chat-message-content {
          background: linear-gradient(135deg, #3b82f6 0%, #14b8a6 100%);
          color: white;
          border-bottom-right-radius: 4px;
        }

        .chat-message-assistant .chat-message-content {
          background: rgba(0, 0, 0, 0.04);
          color: #1f2937;
          border-bottom-left-radius: 4px;
        }

        /* Deep-thinking indicator (shown while waiting for the first token) */
        .chat-thinking {
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-width: 180px;
        }

        .chat-thinking-title {
          display: inline-flex;
          align-items: center;
          font-size: 13px;
          font-weight: 600;
          color: #6b7280;
        }

        .chat-thinking-dots {
          display: inline-flex;
          gap: 3px;
          margin-left: 6px;
        }

        .chat-thinking-dots span {
          width: 4px;
          height: 4px;
          border-radius: 50%;
          background: #9ca3af;
          animation: thinkingDot 1.2s infinite ease-in-out;
        }

        .chat-thinking-dots span:nth-child(2) { animation-delay: 0.15s; }
        .chat-thinking-dots span:nth-child(3) { animation-delay: 0.3s; }

        @keyframes thinkingDot {
          0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
          40% { opacity: 1; transform: translateY(-2px); }
        }

        .chat-thinking-steps {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .chat-thinking-step {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #9ca3af;
          animation: fadeIn 0.3s ease;
          transition: color 0.2s ease;
        }

        .chat-thinking-step.active {
          color: #374151;
        }

        .chat-thinking-step-icon {
          width: 14px;
          font-size: 11px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          color: #14b8a6;
          flex-shrink: 0;
        }

        .chat-thinking-step.active .chat-thinking-step-icon {
          color: #2563eb;
        }

        html.dark-mode .chat-thinking-title { color: #9ca3af; }
        html.dark-mode .chat-thinking-step { color: #6b7280; }
        html.dark-mode .chat-thinking-step.active { color: #e5e7eb; }

        /* Clickable card link in chat */
        .chat-card-link {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          font-weight: 600;
          color: inherit;
          cursor: pointer;
          transition: all 0.15s ease;
          border-radius: 4px;
          padding: 2px 6px;
          margin: 0 -2px;
          background: rgba(0, 0, 0, 0.06);
        }

        .chat-card-link:hover {
          background: rgba(0, 0, 0, 0.1);
        }

        .chat-card-link:active {
          transform: scale(0.98);
        }

        .chat-card-link-icon {
          font-size: 10px;
          opacity: 0.5;
        }

        .chat-input-container {
          padding: 12px 16px;
          padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
          display: flex;
          gap: 10px;
          background: #fffcf5;
          flex-shrink: 0;
        }

        /* Mobile: more bottom padding */
        @media (max-width: 640px) {
          .chat-input-container {
            padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
          }
        }

        /* When keyboard is open: no bottom radius, input has padding for keyboard */
        .chat-window.keyboard-open {
          border-radius: 20px 20px 0 0;
        }

        .chat-window.keyboard-open .chat-input-container {
          padding-bottom: calc(var(--keyboard-height, 0px) + 8px);
        }

        .chat-window.keyboard-open .chat-messages {
          padding-bottom: 0;
        }

        .chat-input-box {
          flex: 1;
          display: flex;
          align-items: center;
          background: #f5f3f0;
          border: none;
          border-radius: 10px;
          padding: 10px 14px;
          gap: 10px;
          transition: all 0.2s ease;
        }

        .chat-input-box:focus-within {
          background: #fff;
          box-shadow: 0 0 0 1px #d1d5db;
        }

        .chat-input {
          flex: 1;
          border: none;
          background: transparent;
          font-size: 15px;
          color: #111827;
          outline: none;
          caret-color: #111827;
        }

        .chat-input::placeholder {
          color: #9ca3af;
        }

        .chat-input:disabled {
          opacity: 0.6;
        }

        .chat-send-btn {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: none;
          background: #111827;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          transition: all 0.2s;
        }

        .chat-send-btn:hover:not(:disabled) {
          background: #1f2937;
        }

        .chat-send-btn:active:not(:disabled) {
          transform: scale(0.95);
        }

        .chat-send-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .chat-voice-btn {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: none;
          background: transparent;
          color: #6b7280;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          transition: all 0.2s;
          font-size: 16px;
        }

        .chat-voice-btn:hover:not(:disabled) {
          color: #111827;
          background: rgba(0, 0, 0, 0.05);
        }

        .chat-voice-btn:active:not(:disabled) {
          transform: scale(0.95);
        }

        .chat-voice-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .chat-voice-btn.recording {
          color: #111827;
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.05); }
        }

        /* Dark mode */
        html.dark-mode .chat-window {
          background: #0f0f0f;
        }

        html.dark-mode .chat-header {
          background: #0f0f0f;
          border-bottom-color: rgba(255, 255, 255, 0.08);
        }

        html.dark-mode .chat-header::before {
          background: rgba(255, 255, 255, 0.2);
        }

        html.dark-mode .chat-header-subtitle {
          color: #9ca3af;
        }

        html.dark-mode .chat-header-btn {
          color: #6b7280;
        }

        html.dark-mode .chat-header-btn:hover {
          color: #9ca3af;
        }

        html.dark-mode .chat-header-btn:active {
          color: #d1d5db;
        }

        html.dark-mode .chat-confirm-modal {
          background: #1f2937;
        }

        html.dark-mode .chat-confirm-title {
          color: #f3f4f6;
        }

        html.dark-mode .chat-confirm-cancel {
          background: rgba(255, 255, 255, 0.1);
          color: #e5e7eb;
        }

        html.dark-mode .chat-confirm-cancel:active {
          background: rgba(255, 255, 255, 0.15);
        }

        html.dark-mode .chat-confirm-ok {
          background: #f3f4f6;
          color: #111827;
        }

        html.dark-mode .chat-confirm-ok:active {
          background: #e5e7eb;
        }

        /* Toast Notification */
        .chat-toast {
          position: absolute;
          top: 80px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.75);
          color: white;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          z-index: 101;
          animation: toastFadeIn 0.2s ease;
          white-space: nowrap;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        @keyframes toastFadeIn {
          from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
          to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }

        html.dark-mode .chat-toast {
          background: rgba(255, 255, 255, 0.9);
          color: #111827;
        }

        html.dark-mode .chat-empty-title {
          color: #f3f4f6;
        }

        html.dark-mode .chat-empty-subtitle {
          color: #9ca3af;
        }

        html.dark-mode .chat-suggestion-btn {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(255, 255, 255, 0.1);
          color: #e5e7eb;
        }

        html.dark-mode .chat-suggestion-btn:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: rgba(255, 255, 255, 0.15);
        }

        html.dark-mode .chat-message-user .chat-message-content {
          background: #2563eb;
        }

        html.dark-mode .chat-message-assistant .chat-message-content {
          background: rgba(255, 255, 255, 0.06);
          color: #e5e7eb;
        }

        /* Keep the SaveVia logo legible on dark background */
        html.dark-mode .chat-message-assistant .chat-avatar {
          background: #f3f4f6;
          border-color: rgba(255, 255, 255, 0.1);
        }

        html.dark-mode .chat-card-link {
          color: inherit;
          background: rgba(255, 255, 255, 0.1);
        }

        html.dark-mode .chat-card-link:hover {
          background: rgba(255, 255, 255, 0.15);
        }

        html.dark-mode .chat-input-container {
          background: #0f0f0f;
        }

        html.dark-mode .chat-input-box {
          background: rgba(255, 255, 255, 0.08);
        }

        html.dark-mode .chat-input-box:focus-within {
          background: rgba(255, 255, 255, 0.12);
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
        }

        html.dark-mode .chat-input {
          color: #f3f4f6;
          caret-color: #f3f4f6;
        }

        html.dark-mode .chat-input::placeholder {
          color: #6b7280;
        }

        html.dark-mode .chat-send-btn {
          background: #2563eb;
        }

        html.dark-mode .chat-send-btn:hover:not(:disabled) {
          background: #3b82f6;
        }

        html.dark-mode .chat-voice-btn {
          color: #9ca3af;
        }

        html.dark-mode .chat-voice-btn:hover:not(:disabled) {
          color: #f3f4f6;
          background: rgba(255, 255, 255, 0.1);
        }

        html.dark-mode .chat-voice-btn.recording {
          color: #f3f4f6;
        }
      `}</style>
    </div>
  )
}
