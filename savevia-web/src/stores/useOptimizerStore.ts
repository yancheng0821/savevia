import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { CreditCard, SpendingCategory, OptimizationResult } from '../types'
import { userApi, cardApi, optimizerApi } from '../services/api'

interface OptimizerState {
  selectedCards: CreditCard[]
  monthlySpending: Partial<Record<SpendingCategory, number>>
  result: OptimizationResult | null
  isLoading: boolean

  setSelectedCards: (cards: CreditCard[]) => void
  addCard: (card: CreditCard) => void
  removeCard: (cardId: number) => void
  setSpending: (category: SpendingCategory, amount: number) => void
  setResult: (result: OptimizationResult | null) => void
  reset: () => void

  // Sync with backend for logged-in users
  loadUserData: () => Promise<void>
  syncCards: () => void
  syncSpending: () => void
  syncResult: () => void
  syncLocalDataToBackend: () => Promise<void>
}

const initialState = {
  selectedCards: [] as CreditCard[],
  monthlySpending: {} as Partial<Record<SpendingCategory, number>>,
  result: null as OptimizationResult | null,
  isLoading: false,
}

// Debounce timers
let spendingDebounceTimer: ReturnType<typeof setTimeout> | null = null
let cardsDebounceTimer: ReturnType<typeof setTimeout> | null = null
let resultDebounceTimer: ReturnType<typeof setTimeout> | null = null

const DEBOUNCE_DELAY = 1000 // 1 second

// Helper to check if user is logged in
const isLoggedIn = () => {
  return !!localStorage.getItem('token')
}

export const useOptimizerStore = create<OptimizerState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setSelectedCards: (cards) => {
        set({ selectedCards: cards })
        get().syncCards()
      },

      addCard: (card) => {
        set((state) => ({
          selectedCards: [...state.selectedCards, card],
        }))
        get().syncCards()
      },

      removeCard: (cardId) => {
        set((state) => ({
          selectedCards: state.selectedCards.filter((c) => c.id !== cardId),
        }))
        get().syncCards()
      },

      setSpending: (category, amount) => {
        set((state) => ({
          monthlySpending: { ...state.monthlySpending, [category]: amount },
        }))
        // Debounce sync to avoid too many requests
        get().syncSpending()
      },

      setResult: (result) => {
        set({ result })
        if (result) {
          get().syncResult()
        }
      },

      reset: () => set(initialState),

      // Load user data from backend after login
      loadUserData: async () => {
        set({ isLoading: true })
        try {
          // Load user's saved cards
          const cardsRes = await userApi.getUserCards()
          if (cardsRes.code === 200 && cardsRes.data && cardsRes.data.length > 0) {
            // Fetch full card details using batch API
            const savedCards = await cardApi.getByIds(cardsRes.data)
            if (savedCards && savedCards.length > 0) {
              set({ selectedCards: savedCards })
            }
          }

          // Load user's saved spending
          const spendingRes = await userApi.getUserSpending()
          if (spendingRes.code === 200 && spendingRes.data) {
            set({ monthlySpending: spendingRes.data as Partial<Record<SpendingCategory, number>> })
          }

          // Load user's saved result from optimizer service
          const resultRes = await optimizerApi.getUserResult()
          if (resultRes.code === 200 && resultRes.data) {
            set({ result: resultRes.data as OptimizationResult })
          }
        } catch (error) {
          console.error('Failed to load user data:', error)
        } finally {
          set({ isLoading: false })
        }
      },

      // Sync cards to backend (debounced, only for logged-in users)
      syncCards: () => {
        if (!isLoggedIn()) return
        if (cardsDebounceTimer) clearTimeout(cardsDebounceTimer)
        cardsDebounceTimer = setTimeout(async () => {
          if (!isLoggedIn()) return
          const { selectedCards } = get()
          try {
            await userApi.saveUserCards(selectedCards.map(c => c.id))
          } catch (error) {
            console.debug('Cards sync failed:', error)
          }
        }, DEBOUNCE_DELAY)
      },

      // Sync spending to backend (debounced, only for logged-in users)
      syncSpending: () => {
        if (!isLoggedIn()) return
        if (spendingDebounceTimer) clearTimeout(spendingDebounceTimer)
        spendingDebounceTimer = setTimeout(async () => {
          if (!isLoggedIn()) return
          const { monthlySpending } = get()
          try {
            await userApi.saveUserSpending(monthlySpending as Record<string, number>)
          } catch (error) {
            console.debug('Spending sync failed:', error)
          }
        }, DEBOUNCE_DELAY)
      },

      // Sync result to backend (debounced, only for logged-in users)
      syncResult: () => {
        if (!isLoggedIn()) return
        if (resultDebounceTimer) clearTimeout(resultDebounceTimer)
        resultDebounceTimer = setTimeout(async () => {
          if (!isLoggedIn()) return
          const { result } = get()
          if (!result) return
          try {
            await optimizerApi.saveUserResult(result)
          } catch (error) {
            console.debug('Result sync failed:', error)
          }
        }, DEBOUNCE_DELAY)
      },

      // Sync all local data to backend immediately (called after login/register)
      // Only syncs if backend doesn't already have data
      syncLocalDataToBackend: async () => {
        const { selectedCards, monthlySpending, result } = get()

        // Sync cards if local has data and backend doesn't
        if (selectedCards.length > 0) {
          try {
            const backendCards = await userApi.getUserCards()
            if (!backendCards.data || backendCards.data.length === 0) {
              await userApi.saveUserCards(selectedCards.map(c => c.id))
              console.debug('Cards synced to backend')
            }
          } catch (err) {
            // Backend check failed, try to sync anyway (new user case)
            try {
              await userApi.saveUserCards(selectedCards.map(c => c.id))
              console.debug('Cards synced to backend (fallback)')
            } catch (e) {
              console.debug('Cards sync failed:', e)
            }
          }
        }

        // Sync spending if local has data and backend doesn't
        if (Object.keys(monthlySpending).length > 0) {
          try {
            const backendSpending = await userApi.getUserSpending()
            if (!backendSpending.data || Object.keys(backendSpending.data).length === 0) {
              await userApi.saveUserSpending(monthlySpending as Record<string, number>)
              console.debug('Spending synced to backend')
            }
          } catch (err) {
            // Backend check failed, try to sync anyway
            try {
              await userApi.saveUserSpending(monthlySpending as Record<string, number>)
              console.debug('Spending synced to backend (fallback)')
            } catch (e) {
              console.debug('Spending sync failed:', e)
            }
          }
        }

        // Sync result if local has data and backend doesn't
        if (result) {
          try {
            const backendResult = await optimizerApi.getUserResult()
            if (!backendResult.data) {
              await optimizerApi.saveUserResult(result)
              console.debug('Result synced to backend')
            }
          } catch (err) {
            // Backend check failed, try to sync anyway
            try {
              await optimizerApi.saveUserResult(result)
              console.debug('Result synced to backend (fallback)')
            } catch (e) {
              console.debug('Result sync failed:', e)
            }
          }
        }
      },
    }),
    {
      name: 'sv-optimizer-storage',
      partialize: (state) => ({
        selectedCards: state.selectedCards,
        monthlySpending: state.monthlySpending,
        result: state.result,
      }),
    }
  )
)
