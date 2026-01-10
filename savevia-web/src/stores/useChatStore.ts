import { create } from 'zustand'

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  isStreaming?: boolean
  createdAt?: string
}

export interface Conversation {
  id: number
  title: string
  createdAt: string
  updatedAt: string
}

interface ChatState {
  // UI state
  isOpen: boolean
  isLoading: boolean
  error: string | null

  // Flags to handle edge cases
  shouldReopenOnBack: boolean  // Reopen chat when user swipes back from card detail
  skipLoadHistory: boolean   // Skip loading history after deleting conversation
  pendingDeleteConversationId: number | null  // Delayed deletion until new message sent

  // Conversation data
  currentConversationId: number | null
  messages: ChatMessage[]
  conversations: Conversation[]
  suggestions: string[]

  // Actions
  setOpen: (open: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // Message actions
  addMessage: (message: ChatMessage) => void
  setMessages: (messages: ChatMessage[]) => void
  updateLastMessage: (content: string) => void
  appendToLastMessage: (chunk: string) => void
  setMessageStreaming: (isStreaming: boolean) => void
  clearMessages: () => void

  // Conversation actions
  setCurrentConversationId: (id: number | null) => void
  setConversations: (conversations: Conversation[]) => void
  setSuggestions: (suggestions: string[]) => void
  setPendingDeleteConversationId: (id: number | null) => void

  // Flag actions
  setShouldReopenOnBack: (value: boolean) => void
  setSkipLoadHistory: (value: boolean) => void

  // Reset
  reset: () => void
}

const initialState = {
  isOpen: false,
  isLoading: false,
  error: null,
  shouldReopenOnBack: false,
  skipLoadHistory: false,
  pendingDeleteConversationId: null,
  currentConversationId: null,
  messages: [],
  conversations: [],
  suggestions: [],
}

export const useChatStore = create<ChatState>((set, _get) => ({
  ...initialState,

  setOpen: (open) => {
    console.log('[ChatStore] setOpen called:', open, 'stack:', new Error().stack)
    set({ isOpen: open })
  },
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setMessages: (messages) => set({ messages }),

  updateLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages]
      if (messages.length > 0) {
        messages[messages.length - 1] = {
          ...messages[messages.length - 1],
          content,
        }
      }
      return { messages }
    }),

  appendToLastMessage: (chunk) =>
    set((state) => {
      const messages = [...state.messages]
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1]
        messages[messages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + chunk,
        }
      }
      return { messages }
    }),

  setMessageStreaming: (isStreaming) =>
    set((state) => {
      const messages = [...state.messages]
      if (messages.length > 0) {
        messages[messages.length - 1] = {
          ...messages[messages.length - 1],
          isStreaming,
        }
      }
      return { messages }
    }),

  clearMessages: () =>
    set({
      messages: [],
      currentConversationId: null,
    }),

  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  setConversations: (conversations) => set({ conversations }),
  setSuggestions: (suggestions) => set({ suggestions }),
  setPendingDeleteConversationId: (id) => set({ pendingDeleteConversationId: id }),

  setShouldReopenOnBack: (value) => set({ shouldReopenOnBack: value }),
  setSkipLoadHistory: (value) => set({ skipLoadHistory: value }),

  reset: () => set(initialState),
}))
