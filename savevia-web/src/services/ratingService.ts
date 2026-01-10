import { Capacitor } from '@capacitor/core'
import { InAppReview } from '@capacitor-community/in-app-review'

const RATING_PROMPTED_KEY = 'sv_rating_prompted'
const FIRST_RESULT_TIME_KEY = 'sv_first_result_time'
const DELAY_BEFORE_PROMPT = 45000 // 45 seconds after first result

export const ratingService = {
  /**
   * Check if user has already been prompted for rating
   */
  hasBeenPrompted(): boolean {
    return localStorage.getItem(RATING_PROMPTED_KEY) === 'true'
  },

  /**
   * Mark that user has been prompted
   */
  markAsPrompted(): void {
    localStorage.setItem(RATING_PROMPTED_KEY, 'true')
  },

  /**
   * Record when user first got optimization result
   */
  recordFirstResult(): void {
    if (!localStorage.getItem(FIRST_RESULT_TIME_KEY)) {
      localStorage.setItem(FIRST_RESULT_TIME_KEY, Date.now().toString())
    }
  },

  /**
   * Check if this is user's first result (no previous record)
   */
  isFirstResult(): boolean {
    return !localStorage.getItem(FIRST_RESULT_TIME_KEY)
  },

  /**
   * Request app store review using native API
   * Only works on native platforms (iOS/Android)
   */
  async requestReview(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) {
      console.log('Rating: Not on native platform, skipping')
      return false
    }

    try {
      await InAppReview.requestReview()
      this.markAsPrompted()
      console.log('Rating: Review requested successfully')
      return true
    } catch (error) {
      console.error('Rating: Failed to request review', error)
      return false
    }
  },

  /**
   * Schedule rating prompt after user gets first optimization result
   * Call this when user views their first result
   */
  scheduleRatingPrompt(): void {
    // Skip if already prompted or not on native platform
    if (this.hasBeenPrompted() || !Capacitor.isNativePlatform()) {
      return
    }

    // Only prompt on first result
    if (!this.isFirstResult()) {
      return
    }

    // Record this as first result
    this.recordFirstResult()

    // Schedule the prompt after delay
    console.log(`Rating: Scheduling prompt in ${DELAY_BEFORE_PROMPT / 1000} seconds`)
    setTimeout(() => {
      this.requestReview()
    }, DELAY_BEFORE_PROMPT)
  },

  /**
   * Reset rating state (for testing)
   */
  reset(): void {
    localStorage.removeItem(RATING_PROMPTED_KEY)
    localStorage.removeItem(FIRST_RESULT_TIME_KEY)
  }
}
