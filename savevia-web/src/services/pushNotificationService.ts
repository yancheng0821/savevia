import { Capacitor } from '@capacitor/core'
import { PushNotifications, Token, PushNotificationSchema, ActionPerformed } from '@capacitor/push-notifications'
import { Device } from '@capacitor/device'
import { App } from '@capacitor/app'
import { pushApi } from './api'
import i18n from '../i18n'

class PushNotificationService {
  private initialized = false
  private deviceToken: string | null = null
  private languageChangeHandler: (() => void) | null = null

  /**
   * Initialize push notifications
   * Should be called after user login
   */
  async initialize(): Promise<void> {
    if (this.initialized) return

    // Only works on native platforms
    if (!Capacitor.isNativePlatform()) {
      return
    }

    try {
      // Wait for i18n to be initialized
      await this.waitForI18n()

      // Check current permission status
      const permStatus = await PushNotifications.checkPermissions()

      if (permStatus.receive === 'prompt') {
        // Request permission
        const newStatus = await PushNotifications.requestPermissions()
        if (newStatus.receive !== 'granted') {
          return
        }
      } else if (permStatus.receive !== 'granted') {
        return
      }

      // Set up listeners BEFORE registering (to catch the registration event)
      this.setupListeners()

      // Set up language change listener to update device locale
      this.setupLanguageChangeListener()

      // Register with APNs/FCM
      await PushNotifications.register()

      // Clear badge when app starts
      this.clearBadge()

      // Clear badge when app comes to foreground
      App.addListener('appStateChange', ({ isActive }) => {
        if (isActive) {
          this.clearBadge()
        }
      })

      this.initialized = true
    } catch {
      // Ignore initialization errors
    }
  }

  /**
   * Wait for i18n to be initialized
   */
  private async waitForI18n(): Promise<void> {
    if (i18n.isInitialized) return

    return new Promise((resolve) => {
      i18n.on('initialized', () => resolve())
      // Timeout fallback after 3 seconds
      setTimeout(resolve, 3000)
    })
  }

  /**
   * Listen for language changes and update device locale
   */
  private setupLanguageChangeListener(): void {
    this.languageChangeHandler = () => {
      if (this.deviceToken) {
        this.updateDeviceLocale()
      }
    }
    i18n.on('languageChanged', this.languageChangeHandler)
  }

  /**
   * Update device locale when language changes
   */
  private async updateDeviceLocale(): Promise<void> {
    if (!this.deviceToken) return

    try {
      const currentLocale = this.getNormalizedLocale()
      await pushApi.registerDevice({
        deviceToken: this.deviceToken,
        platform: Capacitor.getPlatform() as 'ios' | 'android',
        deviceName: '',
        appVersion: '',
        osVersion: '',
        locale: currentLocale,
      })
    } catch {
      // Ignore errors
    }
  }

  /**
   * Get normalized locale code (e.g., 'zh' instead of 'zh-CN')
   */
  private getNormalizedLocale(): string {
    const lang = i18n.language || 'en'
    // Extract base language code (e.g., 'zh' from 'zh-CN')
    return lang.split('-')[0].toLowerCase()
  }

  /**
   * Set up push notification event listeners
   */
  private setupListeners(): void {
    // Registration success
    PushNotifications.addListener('registration', async (token: Token) => {
      this.deviceToken = token.value
      // Register device with backend
      await this.registerDeviceWithBackend(token.value)
    })

    // Registration error
    PushNotifications.addListener('registrationError', () => {
      // Ignore registration errors
    })

    // Notification received while app is in foreground
    PushNotifications.addListener('pushNotificationReceived', (notification: PushNotificationSchema) => {
      this.handleForegroundNotification(notification)
    })

    // Notification action performed (user tapped notification)
    PushNotifications.addListener('pushNotificationActionPerformed', (notification: ActionPerformed) => {
      this.handleNotificationTap(notification)
    })
  }

  /**
   * Register device token with backend
   */
  private async registerDeviceWithBackend(token: string): Promise<void> {
    try {
      const deviceInfo = await Device.getInfo()
      const appInfo = await App.getInfo()
      const currentLocale = this.getNormalizedLocale()

      await pushApi.registerDevice({
        deviceToken: token,
        platform: Capacitor.getPlatform() as 'ios' | 'android',
        deviceName: deviceInfo.model || deviceInfo.name,
        appVersion: appInfo.version,
        osVersion: deviceInfo.osVersion,
        locale: currentLocale,
      })
    } catch {
      // Ignore registration errors
    }
  }

  /**
   * Handle notification received while app is in foreground
   */
  private handleForegroundNotification(_notification: PushNotificationSchema): void {
    // Could show an in-app toast or banner here
  }

  /**
   * Handle notification tap (deep linking)
   */
  private handleNotificationTap(action: ActionPerformed): void {
    const data = action.notification.data as Record<string, any>

    // Handle different notification types
    if (data?.type === 'card_recommendation') {
      const cardId = data.cardId
      if (cardId) {
        window.location.href = `/cards/${cardId}`
      }
    } else if (data?.type === 'spending_reminder') {
      window.location.href = '/'
    } else if (data?.type === 'promo_expiry') {
      const cardId = data.cardId
      if (cardId) {
        window.location.href = `/cards/${cardId}`
      }
    }

    // Mark notification as read if we have an ID
    if (data?.notificationId) {
      pushApi.markAsRead(data.notificationId).catch(() => {})
    }
  }

  /**
   * Unregister device (e.g., on logout)
   */
  async unregister(): Promise<void> {
    if (!this.deviceToken) return

    try {
      await pushApi.unregisterDevice(this.deviceToken)
    } catch {
      // Ignore errors
    }

    // Clean up language change listener
    if (this.languageChangeHandler) {
      i18n.off('languageChanged', this.languageChangeHandler)
      this.languageChangeHandler = null
    }

    this.deviceToken = null
    this.initialized = false
  }

  /**
   * Check if push notifications are available and enabled
   */
  async isEnabled(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false

    try {
      const status = await PushNotifications.checkPermissions()
      return status.receive === 'granted'
    } catch {
      return false
    }
  }

  /**
   * Get current device token
   */
  getDeviceToken(): string | null {
    return this.deviceToken
  }

  /**
   * Clear app badge and delivered notifications
   */
  private clearBadge(): void {
    PushNotifications.removeAllDeliveredNotifications().catch(() => {})
  }
}

// Singleton instance
export const pushNotificationService = new PushNotificationService()
export default pushNotificationService
