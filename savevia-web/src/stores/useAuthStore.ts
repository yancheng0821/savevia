import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Capacitor } from '@capacitor/core'
import { GoogleAuth } from '@southdevs/capacitor-google-auth'
import { authApi, tokenManager } from '../services/api'
import { useOptimizerStore } from './useOptimizerStore'
import { pushNotificationService } from '../services/pushNotificationService'

interface User {
  id: number
  email: string
  name: string
  avatarUrl?: string
  hasPassword?: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  isPanelOpen: boolean

  setUser: (user: User | null) => void
  setPanelOpen: (open: boolean) => void
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  loginWithGoogle: (credential: string) => Promise<void>
  loginWithApple: (identityToken: string, fullName?: string, email?: string) => Promise<void>
  logout: () => void
  updateUserAvatar: (avatarUrl: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      isPanelOpen: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      setPanelOpen: (open) => set({ isPanelOpen: open }),

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const response = await authApi.login({ email, password })
          if (response.code === 200 && response.data) {
            tokenManager.setToken(response.data.token)
            if (response.data.refreshToken) {
              tokenManager.setRefreshToken(response.data.refreshToken)
            }
            set({
              user: response.data.user,
              isAuthenticated: true,
              isPanelOpen: false,
            })
            // Sync local data to backend first (if user calculated while anonymous)
            await useOptimizerStore.getState().syncLocalDataToBackend()
            // Then load user's saved data
            await useOptimizerStore.getState().loadUserData()
          } else {
            throw new Error(response.message || 'Login failed')
          }
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (email, password, name) => {
        set({ isLoading: true })
        try {
          const response = await authApi.register({ email, password, name })
          if (response.code === 200 && response.data) {
            // After registration, automatically login
            const loginResponse = await authApi.login({ email, password })
            if (loginResponse.code === 200 && loginResponse.data) {
              tokenManager.setToken(loginResponse.data.token)
              if (loginResponse.data.refreshToken) {
                tokenManager.setRefreshToken(loginResponse.data.refreshToken)
              }
              set({
                user: loginResponse.data.user,
                isAuthenticated: true,
                isPanelOpen: false,
              })
              // Sync all local data to backend for new user
              await useOptimizerStore.getState().syncLocalDataToBackend()
            } else {
              throw new Error(loginResponse.message || 'Login failed')
            }
          } else {
            throw new Error(response.message || 'Registration failed')
          }
        } finally {
          set({ isLoading: false })
        }
      },

      loginWithGoogle: async (credential) => {
        set({ isLoading: true })
        try {
          const response = await authApi.googleLogin({ credential })
          if (response.code === 200 && response.data) {
            tokenManager.setToken(response.data.token)
            if (response.data.refreshToken) {
              tokenManager.setRefreshToken(response.data.refreshToken)
            }
            set({
              user: response.data.user,
              isAuthenticated: true,
              isPanelOpen: false,
            })
            // Sync local data to backend first (if user calculated while anonymous)
            await useOptimizerStore.getState().syncLocalDataToBackend()
            // Then load user's saved data
            await useOptimizerStore.getState().loadUserData()
          } else {
            console.error('Google login failed: code=', response.code, 'data=', response.data, 'message=', response.message)
            throw new Error(response.message || 'Google login failed')
          }
        } finally {
          set({ isLoading: false })
        }
      },

      loginWithApple: async (identityToken, fullName, email) => {
        set({ isLoading: true })
        try {
          const response = await authApi.appleLogin({ identityToken, fullName, email })
          if (response.code === 200 && response.data) {
            tokenManager.setToken(response.data.token)
            if (response.data.refreshToken) {
              tokenManager.setRefreshToken(response.data.refreshToken)
            }
            set({
              user: response.data.user,
              isAuthenticated: true,
              isPanelOpen: false,
            })
            // Sync local data to backend first (if user calculated while anonymous)
            await useOptimizerStore.getState().syncLocalDataToBackend()
            // Then load user's saved data
            await useOptimizerStore.getState().loadUserData()
          } else {
            throw new Error(response.message || 'Apple login failed')
          }
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        tokenManager.clearAll()
        set({ user: null, isAuthenticated: false })
        // Clear optimizer data on logout
        useOptimizerStore.getState().reset()
        // Sign out from Google and unregister push on native platforms
        if (Capacitor.isNativePlatform()) {
          GoogleAuth.signOut().catch(() => {
            // Ignore errors - user might not be signed in with Google
          })
          pushNotificationService.unregister().catch(() => {
            // Ignore errors - device might not be registered
          })
        }
      },

      updateUserAvatar: (avatarUrl) => {
        set((state) => ({
          user: state.user ? { ...state.user, avatarUrl } : null
        }))
      },
    }),
    {
      name: 'savevia-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
