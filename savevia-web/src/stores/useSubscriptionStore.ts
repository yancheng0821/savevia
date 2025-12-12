import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { checkSubscriptionStatus } from '../services/iap'

interface SubscriptionState {
  // Subscription status (simple boolean - RevenueCat manages details)
  isSubscribed: boolean

  // Loading state
  isLoading: boolean
  isChecked: boolean // Has checked subscription status at least once

  // Actions
  setSubscribed: (subscribed: boolean) => void
  checkSubscription: () => Promise<void>
  clearSubscription: () => void
}

export const useSubscriptionStore = create<SubscriptionState>()(
  persist(
    (set) => ({
      isSubscribed: false,
      isLoading: false,
      isChecked: false,

      setSubscribed: (subscribed) => {
        set({
          isSubscribed: subscribed,
          isChecked: true,
        })
      },

      checkSubscription: async () => {
        set({ isLoading: true })
        try {
          const isSubscribed = await checkSubscriptionStatus()
          set({
            isSubscribed,
            isChecked: true,
          })
        } catch (error) {
          console.error('Failed to check subscription:', error)
          set({ isChecked: true })
        } finally {
          set({ isLoading: false })
        }
      },

      clearSubscription: () => {
        set({
          isSubscribed: false,
          isChecked: false,
        })
      },
    }),
    {
      name: 'savevia-subscription',
      partialize: (state) => ({
        isSubscribed: state.isSubscribed,
        isChecked: state.isChecked,
      }),
    }
  )
)
