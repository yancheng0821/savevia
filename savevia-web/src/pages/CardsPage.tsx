import { useState, useEffect, useLayoutEffect, useRef, useCallback, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import Loading from '../components/Loading'
import { useTranslation } from 'react-i18next'
import { CheckOutlined, ArrowRightOutlined, DownOutlined, RightOutlined, VerticalAlignTopOutlined, VerticalAlignBottomOutlined, BarsOutlined, SearchOutlined, CloseCircleFilled, AppstoreOutlined, PicLeftOutlined } from '@ant-design/icons'
import { cardApi, userApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import { useCardsPageStore } from '../stores/useCardsPageStore'
import type { CreditCard } from '../types'
import { getCardImageUrl, failedImages, loadedImages } from '../utils/cardImages'

// Default card style fallback
const DEFAULT_CARD_STYLE = { gradient: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)', textColor: 'white' }

// Bank fallback colors (used when imageUrl is not set)
const BANK_FALLBACK_COLORS: Record<string, { gradient: string; textColor: string }> = {
  'AMEX': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'American Express': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'TD': { gradient: 'linear-gradient(135deg, #34a853 0%, #1e7e34 100%)', textColor: 'white' },
  'RBC': { gradient: 'linear-gradient(135deg, #003168 0%, #001a3a 100%)', textColor: 'white' },
  'Scotiabank': { gradient: 'linear-gradient(135deg, #ec111a 0%, #b30d14 100%)', textColor: 'white' },
  'CIBC': { gradient: 'linear-gradient(135deg, #8b1538 0%, #6b1029 100%)', textColor: 'white' },
  'BMO': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },
  'Rogers': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Tangerine': { gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)', textColor: 'white' },
  'Neo': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', textColor: 'white' },
  'PC Financial': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Simplii': { gradient: 'linear-gradient(135deg, #ff6600 0%, #e65c00 100%)', textColor: 'white' },
  'MBNA': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
  'National Bank': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Home Trust': { gradient: 'linear-gradient(135deg, #1e3a5f 0%, #152a45 100%)', textColor: 'white' },
}

// Bank logos/abbreviations
const BANK_ABBR: Record<string, string> = {
  'TD': 'TD',
  'RBC': 'RBC',
  'Scotiabank': 'Scotia',
  'CIBC': 'CIBC',
  'BMO': 'BMO',
  'American Express': 'AMEX',
  'AMEX': 'AMEX',
  'Rogers': 'Rogers',
  'Tangerine': 'Tang',
  'Neo': 'Neo',
  'PC Financial': 'PC',
  'Simplii': 'Simplii',
  'MBNA': 'MBNA',
  'National Bank': 'NBC',
  'Home Trust': 'HT',
  'Brim': 'Brim',
  'Wealthsimple': 'WS',
  'Desjardins': 'Desj',
  'Canadian Tire': 'CT',
  'Vancity': 'Vancity',
  'Meridian': 'Merid',
  'Coast Capital': 'Coast',
  'Walmart': 'Walmart',
}

// Bank logo paths (local files)
const BANK_LOGOS: Record<string, string> = {
  'TD': '/logos/td.png',
  'RBC': '/logos/rbc.png',
  'Scotiabank': '/logos/scotiabank.png',
  'CIBC': '/logos/cibc.png',
  'BMO': '/logos/bmo.png',
  'American Express': '/logos/amex.png',
  'AMEX': '/logos/amex.png',
  'Rogers': '/logos/rogers.png',
  'Tangerine': '/logos/tangerine.png',
  'Neo': '/logos/neo.png',
  'PC Financial': '/logos/pc.png',
  'Simplii': '/logos/simplii.png',
  'MBNA': '/logos/mbna.png',
  'National Bank': '/logos/nationalbank.png',
  'Home Trust': '/logos/hometrust.png',
  'Brim': '/logos/brim.png',
  'Wealthsimple': '/logos/wealthsimple.png',
  'Desjardins': '/logos/desjardins.png',
  'Canadian Tire': '/logos/canadiantire.png',
  'Vancity': '/logos/vancity.png',
  'Meridian': '/logos/meridian.png',
  'Coast Capital': '/logos/coastcapital.png',
  'Walmart': '/logos/walmart.png',
}

// Parse card style from imageUrl JSON or use fallback
function getCardStyle(card: CreditCard) {
  // Try to parse imageUrl as JSON with gradient/textColor
  if (card.imageUrl) {
    try {
      const parsed = JSON.parse(card.imageUrl)
      if (parsed.gradient && parsed.textColor) {
        return { gradient: parsed.gradient, textColor: parsed.textColor }
      }
    } catch {
      // Not JSON, ignore
    }
  }
  // Fallback to bank colors
  return BANK_FALLBACK_COLORS[card.bank] || DEFAULT_CARD_STYLE
}

// Get card number prefix based on card network
function getCardNumberPrefix(cardName: string): string {
  const name = cardName.toLowerCase()
  if (name.includes('visa')) {
    return '4XXX'
  } else if (name.includes('mastercard')) {
    return '52XX'
  } else if (name.includes('amex') || name.includes('cobalt') || name.includes('gold rewards') || name.includes('platinum') || name.includes('simplycash')) {
    return '37XX'
  }
  // Default to Visa for unknown
  return '4XXX'
}

// Sync read from localStorage to get scroll position before hydration
const getStoredScrollPosition = (): number => {
  try {
    const stored = localStorage.getItem('sv-cards-page-storage')
    if (stored) {
      const parsed = JSON.parse(stored)
      return parsed.state?.scrollPosition || 0
    }
  } catch {
    // Ignore errors
  }
  return 0
}

function CardsPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { selectedCards, addCard, removeCard, setSelectedCards } = useOptimizerStore()
  const { isAuthenticated } = useAuthStore()
  const { activeBank, setActiveBank, scrollPosition, setScrollPosition } = useCardsPageStore()
  const [collapsedBanks, setCollapsedBanks] = useState<Record<string, boolean>>({})
  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  // View mode: 'grid' (small cards) or 'list' (large cards, one per row)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => {
    const saved = localStorage.getItem('sv_cardViewMode')
    return (saved === 'list' || saved === 'grid') ? saved : 'grid'
  })
  // Keyboard visibility detection for mobile
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false)
  // Real card images setting
  const [realCardImages, setRealCardImages] = useState(() => {
    const saved = localStorage.getItem('sv_realCardImages')
    return saved !== null ? saved === 'true' : true
  })
  const [customBankOrder, setCustomBankOrder] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('sv-bank-order')
      return saved ? JSON.parse(saved) : []
    } catch { return [] }
  })
  const [isEditMode, setIsEditMode] = useState(false)
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [targetIndex, setTargetIndex] = useState<number | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState(0)
  const [isDropping, setIsDropping] = useState(false)
  const [disableTransition, setDisableTransition] = useState(false)
  const tabsRef = useRef<HTMLDivElement>(null)
  const reorderListRef = useRef<HTMLDivElement>(null)
  const dragStartYRef = useRef<number>(0)
  const itemHeightRef = useRef<number>(0)
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isInitialLoadRef = useRef(true)
  // Get initial scroll position from localStorage synchronously to prevent flicker
  const initialScrollPosition = useRef(getStoredScrollPosition())
  // Initialize to true if we need to restore scroll - prevents early scroll events from resetting position
  const isRestoringScrollRef = useRef(initialScrollPosition.current > 0)

  const toggleBank = (bank: string) => {
    setCollapsedBanks(prev => ({ ...prev, [bank]: !prev[bank] }))
  }

  // Listen for storage changes (when setting is updated in MePage)
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('sv_realCardImages')
      setRealCardImages(saved !== null ? saved === 'true' : true)
    }
    window.addEventListener('storage', handleStorageChange)
    const handleFocus = () => {
      const saved = localStorage.getItem('sv_realCardImages')
      setRealCardImages(saved !== null ? saved === 'true' : true)
    }
    window.addEventListener('focus', handleFocus)
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleFocus)
    }
  }, [])

  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: cardApi.getAll,
  })

  // Auto-save with debounce
  const debouncedSave = useCallback((cardIds: number[]) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        await userApi.saveUserCards(cardIds)
      } catch (error) {
        console.error('Auto-save failed:', error)
      }
    }, 1000)
  }, [])

  // Load user's saved cards when authenticated
  useEffect(() => {
    const loadUserCards = async () => {
      if (isAuthenticated && cards && cards.length > 0) {
        try {
          const response = await userApi.getUserCards()
          if (response.code === 200 && response.data && response.data.length > 0) {
            const savedCardIds = response.data
            const savedCards = cards.filter(c => savedCardIds.includes(c.id))
            if (savedCards.length > 0) {
              setSelectedCards(savedCards)
            }
          }
        } catch (error) {
          console.error('Failed to load user cards:', error)
        }
      }
      isInitialLoadRef.current = false
    }
    loadUserCards()
  }, [isAuthenticated, cards, setSelectedCards])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])


  const isSelected = (cardId: number) => selectedCards.some((c) => c.id === cardId)

  const handleCardToggle = (card: CreditCard) => {
    let newCardIds: number[]
    if (isSelected(card.id)) {
      removeCard(card.id)
      newCardIds = selectedCards.filter(c => c.id !== card.id).map(c => c.id)
    } else {
      addCard(card)
      newCardIds = [...selectedCards.map(c => c.id), card.id]
    }
    // Auto-save if authenticated
    if (isAuthenticated && !isInitialLoadRef.current) {
      debouncedSave(newCardIds)
    }
  }

  const handleContinue = () => {
    if (selectedCards.length > 0) {
      navigate('/optimizer')
    }
  }

  // Restore scroll position on mount using the synchronously read value
  // Use useLayoutEffect to restore before browser paint, avoiding flash
  useLayoutEffect(() => {
    const storedPosition = initialScrollPosition.current
    if (storedPosition > 0) {
      // Restore scroll position immediately before paint
      window.scrollTo(0, storedPosition)
      // Mark restoration complete after scroll settles
      setTimeout(() => {
        isRestoringScrollRef.current = false
      }, 100)
    } else {
      isRestoringScrollRef.current = false
    }
  }, []) // Only run on mount

  // Monitor scroll position and save in real-time
  useEffect(() => {
    const handleScroll = () => {
      // Skip updating during scroll restoration
      if (isRestoringScrollRef.current) return
      const newScrollY = window.scrollY
      // Don't save near-zero positions - prevents losing scroll position when
      // App.tsx ScrollToTop scrolls to 0 during navigation to detail page
      if (newScrollY > 50) {
        setScrollPosition(newScrollY)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [setScrollPosition])

  // Detect keyboard visibility on mobile (using visualViewport API)
  useEffect(() => {
    const viewport = window.visualViewport
    if (!viewport) return

    const handleResize = () => {
      // If visual viewport height is significantly less than window height, keyboard is likely open
      const heightDiff = window.innerHeight - viewport.height
      setIsKeyboardVisible(heightDiff > 150)
    }

    viewport.addEventListener('resize', handleResize)
    return () => viewport.removeEventListener('resize', handleResize)
  }, [])

  // Scroll to top
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Scroll to bottom
  const scrollToBottom = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    })
  }

  // Group cards by bank
  const groupedCards = useMemo(() => {
    if (!cards) return null
    return cards.reduce(
      (acc, card) => {
        if (!acc[card.bank]) {
          acc[card.bank] = []
        }
        acc[card.bank].push(card)
        return acc
      },
      {} as Record<string, CreditCard[]>
    )
  }, [cards])

  // Get list of banks - use custom order if available, otherwise default order
  const banks = useMemo(() => {
    if (!groupedCards) return []
    const allBanks = Object.keys(groupedCards)

    if (customBankOrder.length > 0) {
      // Put custom ordered banks first, then remaining banks
      const orderedBanks = customBankOrder.filter(b => allBanks.includes(b))
      const remainingBanks = allBanks.filter(b => !customBankOrder.includes(b))
      return [...orderedBanks, ...remainingBanks]
    }
    return allBanks
  }, [groupedCards, customBankOrder])

  // Filter cards based on search query
  const filteredGroupedCards = useMemo(() => {
    if (!groupedCards || !searchQuery.trim()) return groupedCards
    const query = searchQuery.toLowerCase().trim()
    const result: Record<string, CreditCard[]> = {}
    for (const bank of Object.keys(groupedCards)) {
      const filtered = groupedCards[bank].filter(card =>
        card.name.toLowerCase().includes(query) ||
        card.bank.toLowerCase().includes(query)
      )
      if (filtered.length > 0) {
        result[bank] = filtered
      }
    }
    return result
  }, [groupedCards, searchQuery])

  // Get filtered banks (only banks that have matching cards)
  const filteredBanks = useMemo(() => {
    if (!searchQuery.trim()) return banks
    return banks.filter(bank => (filteredGroupedCards?.[bank]?.length ?? 0) > 0)
  }, [banks, filteredGroupedCards, searchQuery])

  // Save custom order to localStorage
  const saveBankOrder = useCallback((newOrder: string[]) => {
    setCustomBankOrder(newOrder)
    localStorage.setItem('sv-bank-order', JSON.stringify(newOrder))
  }, [])

  // Move bank from one position to another (only called on drop)
  const moveBank = useCallback((fromIndex: number, toIndex: number) => {
    if (fromIndex === toIndex) return
    const newOrder = [...banks]
    const [movedBank] = newOrder.splice(fromIndex, 1)
    newOrder.splice(toIndex, 0, movedBank)
    saveBankOrder(newOrder)
  }, [banks, saveBankOrder])

  const AUTO_SCROLL_THRESHOLD = 80
  const AUTO_SCROLL_SPEED = 8

  // Touch drag handlers
  const handleTouchStart = useCallback((index: number, e: React.TouchEvent) => {
    e.stopPropagation()
    const touch = e.touches[0]
    const listEl = reorderListRef.current
    if (!listEl) return

    // Get item height for calculations
    const items = listEl.querySelectorAll('.sv-bank-reorder-item')
    if (items[index]) {
      itemHeightRef.current = items[index].getBoundingClientRect().height
    }

    dragStartYRef.current = touch.clientY
    setDisableTransition(false)
    setDraggedIndex(index)
    setTargetIndex(index)
    setIsDragging(true)
    setDragOffset(0)

    if (navigator.vibrate) {
      navigator.vibrate(30)
    }
  }, [])

  const handleTouchEnd = useCallback(() => {
    if (draggedIndex === null || targetIndex === null) {
      setDraggedIndex(null)
      setTargetIndex(null)
      setIsDragging(false)
      setDragOffset(0)
      return
    }

    const shouldMove = draggedIndex !== targetIndex
    const itemHeight = itemHeightRef.current
    const finalOffset = (targetIndex - draggedIndex) * itemHeight

    // Start drop animation
    setIsDropping(true)
    setDragOffset(finalOffset)

    // After animation completes, update the array and reset
    const DROP_DURATION = 120
    setTimeout(() => {
      // Disable transitions before DOM reorder
      setDisableTransition(true)

      // Reset drag state
      setDraggedIndex(null)
      setTargetIndex(null)
      setIsDragging(false)
      setIsDropping(false)
      setDragOffset(0)

      // Update array (this triggers re-render with new order)
      if (shouldMove) {
        moveBank(draggedIndex, targetIndex)
      }

      // Re-enable transitions after DOM settles
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setDisableTransition(false)
        })
      })
    }, DROP_DURATION)
  }, [draggedIndex, targetIndex, moveBank])

  // Native touch handlers
  useEffect(() => {
    if (!isDragging || draggedIndex === null) return

    const handleNativeTouchMove = (e: TouchEvent) => {
      const touch = e.touches[0]
      e.preventDefault()

      // Calculate drag offset from start position
      const offset = touch.clientY - dragStartYRef.current
      setDragOffset(offset)

      // Auto-scroll when near edges
      const viewportHeight = window.innerHeight
      if (touch.clientY < AUTO_SCROLL_THRESHOLD) {
        window.scrollBy(0, -AUTO_SCROLL_SPEED)
      } else if (touch.clientY > viewportHeight - AUTO_SCROLL_THRESHOLD) {
        window.scrollBy(0, AUTO_SCROLL_SPEED)
      }

      // Calculate target index based on offset
      const itemHeight = itemHeightRef.current
      if (itemHeight > 0) {
        const indexOffset = Math.round(offset / itemHeight)
        const newTargetIndex = Math.max(0, Math.min(banks.length - 1, draggedIndex + indexOffset))
        if (newTargetIndex !== targetIndex) {
          setTargetIndex(newTargetIndex)
          if (navigator.vibrate) {
            navigator.vibrate(10)
          }
        }
      }
    }

    const handleNativeTouchEnd = () => {
      handleTouchEnd()
    }

    document.addEventListener('touchmove', handleNativeTouchMove, { passive: false })
    document.addEventListener('touchend', handleNativeTouchEnd)
    return () => {
      document.removeEventListener('touchmove', handleNativeTouchMove)
      document.removeEventListener('touchend', handleNativeTouchEnd)
    }
  }, [isDragging, draggedIndex, targetIndex, banks.length, handleTouchEnd])

  // Calculate transform for each item during drag
  const getItemTransform = useCallback((index: number): string => {
    // Keep transforms during both dragging and dropping animation
    if ((!isDragging && !isDropping) || draggedIndex === null || targetIndex === null) return ''

    const itemHeight = itemHeightRef.current
    if (itemHeight === 0) return ''

    if (index === draggedIndex) {
      // Dragged item follows the finger (no scale during drop)
      return isDropping ? `translateY(${dragOffset}px)` : `translateY(${dragOffset}px) scale(1.02)`
    }

    // Other items shift to make room
    if (draggedIndex < targetIndex) {
      // Dragging down: items between draggedIndex and targetIndex move up
      if (index > draggedIndex && index <= targetIndex) {
        return `translateY(${-itemHeight}px)`
      }
    } else if (draggedIndex > targetIndex) {
      // Dragging up: items between targetIndex and draggedIndex move down
      if (index >= targetIndex && index < draggedIndex) {
        return `translateY(${itemHeight}px)`
      }
    }

    return ''
  }, [isDragging, isDropping, draggedIndex, targetIndex, dragOffset])

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Loading size="large" />
      </div>
    )
  }

  // Toggle card image style
  const toggleCardImageStyle = () => {
    const newValue = !realCardImages
    setRealCardImages(newValue)
    localStorage.setItem('sv_realCardImages', String(newValue))
  }

  return (
    <div style={{ paddingBottom: '120px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h1 className="sv-cards-title" style={{ margin: 0 }}>
          {t('cards.title')}
        </h1>
        {/* Card style toggle button */}
        <button
          onClick={toggleCardImageStyle}
          className="sv-toggle-card-style-btn"
        >
          <span>{t('cards.toggleCardStyle')}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M8 3L4 7l4 4"/>
            <path d="M16 21l4-4-4-4"/>
            <path d="M4 7h16"/>
            <path d="M20 17H4"/>
          </svg>
        </button>
      </div>

      {/* Search Box */}
      <div className="sv-cards-search-wrapper">
        <div className="sv-cards-search-row">
          <div className="sv-cards-search-box">
            <SearchOutlined className="sv-cards-search-icon" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                if (e.target.value.trim()) {
                  setActiveBank(null)
                }
              }}
              placeholder={t('cards.searchPlaceholder') || 'Search cards...'}
              className="sv-cards-search-input"
            />
            {searchQuery && (
              <CloseCircleFilled
                className="sv-cards-search-clear"
                onClick={() => setSearchQuery('')}
              />
            )}
          </div>
          {/* View mode toggle */}
          <div className="sv-view-toggle">
            <button
              className={`sv-view-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => {
                setViewMode('grid')
                localStorage.setItem('sv_cardViewMode', 'grid')
              }}
              title={t('cards.gridView') || 'Grid view'}
            >
              <AppstoreOutlined />
            </button>
            <button
              className={`sv-view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => {
                setViewMode('list')
                localStorage.setItem('sv_cardViewMode', 'list')
              }}
              title={t('cards.listView') || 'List view'}
            >
              <PicLeftOutlined />
            </button>
          </div>
        </div>
        {searchQuery && filteredGroupedCards && (
          <div className="sv-cards-search-result">
            {Object.values(filteredGroupedCards).reduce((acc, cards) => acc + cards.length, 0)} {t('cards.resultsFound') || 'results found'}
          </div>
        )}
      </div>

      {/* Mobile Bank Tabs */}
      <div className="sv-bank-tabs-wrapper">
        <div className="sv-bank-tabs" ref={tabsRef}>
          <button
            className={`sv-bank-tab ${activeBank === null ? 'active' : ''}`}
            onClick={() => setActiveBank(null)}
          >
            <span className="sv-bank-tab-icon sv-bank-tab-icon-all">
              <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                <path d="M3 4h4v4H3V4zm5 0h4v4H8V4zm5 0h4v4h-4V4zM3 9h4v4H3V9zm5 0h4v4H8V9zm5 0h4v4h-4V9z"/>
              </svg>
            </span>
            <span className="sv-bank-tab-name">{t('cards.all')}</span>
          </button>
          {banks.map((bank) => {
            const logoUrl = BANK_LOGOS[bank]
            const selectedCount = groupedCards?.[bank]?.filter(c => isSelected(c.id)).length || 0
            return (
              <button
                key={bank}
                className={`sv-bank-tab ${activeBank === bank ? 'active' : ''}`}
                onClick={() => setActiveBank(activeBank === bank ? null : bank)}
              >
                <img className="sv-bank-tab-icon" src={logoUrl} alt={bank} />
                <span className="sv-bank-tab-name">{BANK_ABBR[bank] || bank}</span>
                {selectedCount > 0 && (
                  <span className="sv-bank-tab-badge">{selectedCount}</span>
                )}
              </button>
            )
          })}
        </div>

        {/* Edit order button */}
        <button
          className={`sv-bank-tabs-edit ${isEditMode ? 'active' : ''}`}
          onClick={() => setIsEditMode(!isEditMode)}
          title={t('cards.dragToReorder')}
        >
          {isEditMode ? <CheckOutlined /> : <BarsOutlined />}
        </button>
      </div>

      {/* Edit mode: show reorder list */}
      {isEditMode && (
        <div className="sv-bank-reorder-panel">
          <div
            className="sv-bank-reorder-list"
            ref={reorderListRef}
          >
            {banks.map((bank, index) => {
              const transform = getItemTransform(index)
              const isDraggedItem = draggedIndex === index
              // Transition: enabled for non-dragged items, or dragged item during drop
              // Disabled: for dragged item during drag, or all items during DOM reorder
              const shouldAnimate = !disableTransition && (!isDraggedItem || isDropping)
              return (
                <div
                  key={bank}
                  data-bank={bank}
                  className={`sv-bank-reorder-item ${isDraggedItem ? 'dragging' : ''}`}
                  style={{
                    transform: transform || undefined,
                    transition: shouldAnimate ? 'transform 120ms cubic-bezier(0.2, 0, 0, 1)' : 'none',
                    zIndex: isDraggedItem ? 10 : 1,
                  }}
                >
                  <img className="sv-bank-reorder-logo" src={BANK_LOGOS[bank]} alt={bank} />
                  <span className="sv-bank-reorder-name">{bank}</span>
                  <span
                    className="sv-bank-reorder-handle"
                    onTouchStart={(e) => handleTouchStart(index, e)}
                  >⋮⋮</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Cards Grid */}
      {filteredGroupedCards &&
        (activeBank ? [activeBank] : filteredBanks).map((bank) => {
          const bankCards = filteredGroupedCards[bank]
          if (!bankCards) return null
          const isCollapsed = collapsedBanks[bank]
          const selectedCount = bankCards.filter(c => isSelected(c.id)).length
          return (
          <div
            key={bank}
            style={{ marginBottom: '32px' }}
          >
            <div
              onClick={() => toggleBank(bank)}
              className="sv-cards-bank-header"
              style={{ marginBottom: isCollapsed ? '0' : '16px' }}
            >
              <div className="sv-cards-bank-left">
                {isCollapsed ? (
                  <RightOutlined className="sv-cards-bank-arrow" />
                ) : (
                  <DownOutlined className="sv-cards-bank-arrow" />
                )}
                {BANK_LOGOS[bank] && (
                  <img
                    src={BANK_LOGOS[bank]}
                    alt={bank}
                    className="sv-cards-bank-logo"
                    style={realCardImages ? { width: '24px', height: '24px' } : undefined}
                  />
                )}
                <span
                  className="sv-cards-bank-name"
                  style={realCardImages ? { fontSize: '14px' } : undefined}
                >
                  {bank}
                </span>
                <span
                  className="sv-cards-bank-count"
                  style={realCardImages ? { fontSize: '13px' } : undefined}
                >
                  {t('cards.cardCount', { count: bankCards.length })}
                </span>
              </div>
              {selectedCount > 0 && (
                <span
                  className="sv-cards-selected-badge"
                  style={realCardImages ? { fontSize: '13px' } : undefined}
                >
                  {t('cards.selectedCount', { count: selectedCount })}
                </span>
              )}
            </div>
            {!isCollapsed && (
            <div className={`sv-cards-grid ${viewMode === 'list' ? 'sv-cards-list' : ''}`}>
              {bankCards.map((card) => {
                const style = getCardStyle(card)
                const selected = isSelected(card.id)
                const imageKey = `${card.bank}|${card.name}`
                const cardImageUrl = realCardImages && !failedImages.has(imageKey) ? getCardImageUrl(card.bank, card.name) : null

                // List view - horizontal layout with thumbnail and info
                if (viewMode === 'list') {
                  return (
                    <div
                      key={card.id}
                      className={`sv-card-list-item ${selected ? 'selected' : ''}`}
                    >
                      {/* Card thumbnail - click to toggle selection */}
                      <div
                        className="sv-card-list-thumbnail"
                        style={{ background: style.gradient }}
                        onClick={() => handleCardToggle(card)}
                      >
                        {cardImageUrl && (
                          <img
                            src={cardImageUrl}
                            alt={card.name}
                            loading="lazy"
                            onLoad={(e) => {
                              loadedImages.add(imageKey)
                              ;(e.target as HTMLImageElement).style.opacity = '1'
                            }}
                            onError={(e) => {
                              failedImages.add(imageKey)
                              ;(e.target as HTMLImageElement).style.display = 'none'
                            }}
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              opacity: loadedImages.has(imageKey) ? 1 : 0,
                              transition: 'opacity 0.2s ease'
                            }}
                          />
                        )}
                        {selected && (
                          <div className="sv-card-list-check">
                            <CheckOutlined style={{ color: '#059669', fontSize: '10px' }} />
                          </div>
                        )}
                      </div>
                      {/* Card info + arrow - click to go to detail */}
                      <Link
                        to={`/cards/${card.id}`}
                        state={{ card }}
                        className="sv-card-list-link"
                      >
                        <div className="sv-card-list-info">
                          <div className="sv-card-list-name">{card.name}</div>
                          <div className="sv-card-list-meta">
                            <span className="sv-card-list-fee">
                              {card.annualFee === 0 ? t('cardDetail.noFee') : `$${card.annualFee}${t('common.perYear')}`}
                            </span>
                            <span className="sv-card-list-type">
                              {card.rewardType === 'POINTS' ? t('cards.points') : t('cards.cashback')}
                            </span>
                            {(() => {
                              const bestRule = card.rewardRules?.reduce((best, rule) =>
                                rule.rewardRate > (best?.rewardRate || 0) ? rule : best,
                                null as typeof card.rewardRules[0] | null
                              )
                              if (bestRule && bestRule.rewardRate > card.baseRewardRate) {
                                const rateDisplay = card.rewardType === 'POINTS'
                                  ? `${Math.round(bestRule.rewardRate / (card.pointValue || 0.01))}x`
                                  : `${(bestRule.rewardRate * 100).toFixed(0)}%`
                                return (
                                  <span className="sv-card-list-best">
                                    {t(`categories.${bestRule.category}`)} {rateDisplay}
                                  </span>
                                )
                              }
                              return null
                            })()}
                          </div>
                        </div>
                        <RightOutlined className="sv-card-list-arrow" />
                      </Link>
                    </div>
                  )
                }

                // Grid view - Real card image version
                if (cardImageUrl) {
                  return (
                    <div
                      key={card.id}
                      onClick={() => handleCardToggle(card)}
                      style={{
                        position: 'relative',
                        aspectRatio: '1.586',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        transform: selected ? 'translateY(-4px)' : 'scale(1)',
                        boxShadow: selected
                          ? '0 12px 40px rgba(0,0,0,0.25)'
                          : '0 2px 12px rgba(0,0,0,0.1)',
                        overflow: 'hidden',
                        // Show gradient as loading placeholder
                        background: style.gradient,
                      }}
                    >
                      <img
                        src={cardImageUrl}
                        alt={`${card.bank} ${card.name}`}
                        loading="lazy"
                        onLoad={(e) => {
                          loadedImages.add(imageKey)
                          ;(e.target as HTMLImageElement).style.opacity = '1'
                        }}
                        onError={(e) => {
                          // Mark as failed and hide image to show gradient fallback
                          failedImages.add(imageKey)
                          ;(e.target as HTMLImageElement).style.display = 'none'
                        }}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          display: 'block',
                          position: 'relative',
                          zIndex: 1,
                          opacity: loadedImages.has(imageKey) ? 1 : 0,
                          transition: 'opacity 0.2s ease'
                        }}
                      />
                      {/* Full overlay to soften the card image */}
                      <div style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.05) 80%, rgba(0,0,0,0.8) 100%)',
                        borderRadius: '12px',
                        zIndex: 2
                      }} />
                      {/* Selected checkmark - top left, frosted glass style */}
                      {selected && (
                        <div style={{
                          position: 'absolute',
                          top: '10px',
                          left: '10px',
                          width: '26px',
                          height: '26px',
                          background: 'rgba(255,255,255,0.85)',
                          backdropFilter: 'blur(8px)',
                          WebkitBackdropFilter: 'blur(8px)',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          zIndex: 10,
                          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                        }}>
                          <CheckOutlined style={{ color: '#059669', fontSize: '13px' }} />
                        </div>
                      )}
                      {/* Bottom info bar */}
                      <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '24px 12px 10px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        zIndex: 5
                      }}>
                        <span style={{
                          fontSize: '13px',
                          fontWeight: '600',
                          color: 'white',
                          textShadow: '0 2px 6px rgba(0,0,0,0.8)',
                          flex: 1,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          marginRight: '10px'
                        }}>
                          {card.name}
                        </span>
                        <Link
                          to={`/cards/${card.id}`}
                          state={{ card }}
                          onClick={(e) => e.stopPropagation()}
                          style={{
                            fontSize: '13px',
                            fontWeight: '600',
                            color: 'white',
                            textDecoration: 'none',
                            textShadow: '0 2px 6px rgba(0,0,0,0.8)',
                            flexShrink: 0
                          }}
                        >
                          {t('cards.details')} →
                        </Link>
                      </div>
                    </div>
                  )
                }

                // Grid view - Fallback: gradient card style (no image URL or image failed to load)
                return (
                  <div
                    key={card.id}
                    onClick={() => handleCardToggle(card)}
                    style={{
                      position: 'relative',
                      aspectRatio: '1.586',
                      background: style.gradient,
                      borderRadius: '12px',
                      padding: '16px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      transform: selected ? 'translateY(-4px)' : 'scale(1)',
                      boxShadow: selected
                        ? '0 12px 40px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.1)'
                        : '0 2px 12px rgba(0,0,0,0.1)',
                      overflow: 'hidden'
                    }}
                  >
                    {/* Selected checkmark - positioned at top left */}
                    {selected && (
                      <div style={{
                        position: 'absolute',
                        top: '12px',
                        left: '12px',
                        width: '24px',
                        height: '24px',
                        background: 'white',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 10,
                        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                      }}>
                        <CheckOutlined style={{ color: '#059669', fontSize: '12px' }} />
                      </div>
                    )}

                    {/* Top row: bank + annual fee */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start'
                    }}>
                      <div
                        className="sv-card-bank-abbr"
                        style={{
                          fontSize: '16px',
                          fontWeight: '800',
                          color: style.textColor,
                          letterSpacing: '0.5px',
                          marginLeft: selected ? '32px' : '0',
                          transition: 'margin-left 0.2s ease'
                        }}
                      >
                        {BANK_ABBR[bank] || bank.substring(0, 4).toUpperCase()}
                      </div>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: '600',
                        color: style.textColor,
                        opacity: 0.7
                      }}>
                        {card.annualFee === 0 ? t('cardDetail.noFee') : `$${card.annualFee}${t('common.perYear')}`}
                      </span>
                    </div>

                    {/* Card name - middle */}
                    <div
                      className="sv-card-name"
                      style={{
                        position: 'absolute',
                        top: '45%',
                        left: '16px',
                        right: '16px',
                        transform: 'translateY(-50%)',
                        fontSize: '13px',
                        fontWeight: '600',
                        color: style.textColor,
                        lineHeight: '1.3'
                      }}
                    >
                      {card.name}
                    </div>

                    {/* Bottom row: card number + details link */}
                    <div
                      className="sv-card-bottom-row"
                      style={{
                        position: 'absolute',
                        bottom: '14px',
                        left: '16px',
                        right: '16px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <span
                        className="sv-card-number-placeholder"
                        style={{
                          fontSize: '10px',
                          fontWeight: '500',
                          color: style.textColor,
                          opacity: 0.5,
                          letterSpacing: '1.5px'
                        }}
                      >
                        {getCardNumberPrefix(card.name)} •••• •••• ••••
                      </span>
                      <Link
                        to={`/cards/${card.id}`}
                        state={{ card }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          fontSize: '11px',
                          fontWeight: '600',
                          color: style.textColor,
                          opacity: 0.7,
                          textDecoration: 'none',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = '1'
                          e.currentTarget.style.transform = 'translateX(2px)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = '0.7'
                          e.currentTarget.style.transform = 'translateX(0)'
                        }}
                      >
                        {t('cards.details')} →
                      </Link>
                    </div>
                  </div>
                )
              })}
            </div>
            )}
          </div>
          );
        })}

      {/* Fixed Bottom - Continue button (hidden when keyboard is open) */}
      {selectedCards.length > 0 && !isKeyboardVisible && (
        <div className="sv-cards-continue-wrapper">
          <button onClick={handleContinue} className="sv-cards-continue-btn">
            <span className="sv-cards-continue-text">
              {t('cards.continueWith', { count: selectedCards.length })}
            </span>
            <ArrowRightOutlined className="sv-cards-continue-arrow" />
          </button>
        </div>
      )}

      {/* Scroll to Top/Bottom Buttons - Use sync-read value before hydration, store value after (hidden when keyboard is open) */}
      {!isKeyboardVisible && (scrollPosition > 300 || (scrollPosition === 0 && initialScrollPosition.current > 300)) && (
        <div
          className="sv-scroll-buttons"
          style={{
            position: 'fixed',
            right: '16px',
            bottom: selectedCards.length > 0 ? '110px' : '90px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            zIndex: 20
          }}
        >
        <button
          onClick={scrollToTop}
          className="sv-scroll-btn"
          title={t('common.scrollTop') || 'Scroll to top'}
        >
          <VerticalAlignTopOutlined />
        </button>
        <button
          onClick={scrollToBottom}
          className="sv-scroll-btn"
          title={t('common.scrollBottom') || 'Scroll to bottom'}
        >
          <VerticalAlignBottomOutlined />
        </button>
        </div>
      )}
    </div>
  )
}

export default CardsPage
