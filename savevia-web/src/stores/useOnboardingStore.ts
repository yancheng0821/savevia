import { create } from 'zustand'
import { SecureStoragePlugin } from 'capacitor-secure-storage-plugin'
import { Capacitor } from '@capacitor/core'

const ONBOARDING_KEY = 'savevia_has_seen_onboarding'

interface OnboardingState {
  hasSeenOnboarding: boolean
  isLoading: boolean
  setHasSeenOnboarding: (value: boolean) => void
  loadOnboardingState: () => Promise<void>
  resetOnboarding: () => void
}

export const useOnboardingStore = create<OnboardingState>()((set) => ({
  hasSeenOnboarding: false,
  isLoading: true,

  setHasSeenOnboarding: async (value: boolean) => {
    set({ hasSeenOnboarding: value })

    // Save to Keychain on native platforms (persists across app reinstalls)
    if (Capacitor.isNativePlatform()) {
      try {
        await SecureStoragePlugin.set({ key: ONBOARDING_KEY, value: String(value) })
      } catch (error) {
        console.error('Failed to save onboarding state to Keychain:', error)
        // Fallback to localStorage
        localStorage.setItem(ONBOARDING_KEY, String(value))
      }
    } else {
      localStorage.setItem(ONBOARDING_KEY, String(value))
    }
  },

  loadOnboardingState: async () => {
    let hasSeenOnboarding = false

    if (Capacitor.isNativePlatform()) {
      try {
        const result = await SecureStoragePlugin.get({ key: ONBOARDING_KEY })
        hasSeenOnboarding = result.value === 'true'
      } catch (error) {
        // Key doesn't exist or error - first time user
        console.log('Onboarding state not found in Keychain, first time user')
        hasSeenOnboarding = false
      }
    } else {
      hasSeenOnboarding = localStorage.getItem(ONBOARDING_KEY) === 'true'
    }

    set({ hasSeenOnboarding, isLoading: false })
  },

  resetOnboarding: async () => {
    set({ hasSeenOnboarding: false })

    if (Capacitor.isNativePlatform()) {
      try {
        await SecureStoragePlugin.remove({ key: ONBOARDING_KEY })
      } catch (error) {
        console.error('Failed to remove onboarding state from Keychain:', error)
      }
    }
    localStorage.removeItem(ONBOARDING_KEY)
  },
}))
