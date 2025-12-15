import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { message } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined, LoadingOutlined } from '@ant-design/icons'
import { optimizerApi, userApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import { useSubscriptionStore } from '../stores/useSubscriptionStore'
import Paywall from '../components/Paywall'
import { isNativePlatform } from '../services/iap'
import type { SpendingCategory } from '../types'

// Category config with icons
const CATEGORY_CONFIG: Record<SpendingCategory, { icon: string; color: string }> = {
  // Daily Essentials
  DINING: { icon: '🍽️', color: '#f97316' },
  GROCERY: { icon: '🛒', color: '#22c55e' },
  PHARMACY: { icon: '💊', color: '#14b8a6' },
  // Transportation
  GAS: { icon: '⛽', color: '#ef4444' },
  TRANSIT: { icon: '🚇', color: '#8b5cf6' },
  EV_CHARGING: { icon: '⚡', color: '#16a34a' },
  // Shopping
  RETAIL: { icon: '🛍️', color: '#a855f7' },
  ONLINE_SHOPPING: { icon: '📦', color: '#f59e0b' },
  WHOLESALE: { icon: '🏪', color: '#0891b2' },
  HOME_IMPROVEMENT: { icon: '🔨', color: '#78716c' },
  // Bills & Services
  RENT: { icon: '🏠', color: '#6366f1' },
  RECURRING: { icon: '🔄', color: '#64748b' },
  TELECOM: { icon: '📱', color: '#2563eb' },
  INSURANCE: { icon: '📋', color: '#475569' },
  STREAMING: { icon: '📺', color: '#ec4899' },
  // Lifestyle
  TRAVEL: { icon: '✈️', color: '#0ea5e9' },
  ENTERTAINMENT: { icon: '🎬', color: '#f43f5e' },
  PERSONAL_SERVICES: { icon: '💇', color: '#d946ef' },
  FOREIGN: { icon: '🌍', color: '#06b6d4' },
  // Catch-all
  OTHER: { icon: '💳', color: '#71717a' },
}

// Grouped categories for organized display (no separators, just grouped order)
const CATEGORY_ORDER: SpendingCategory[] = [
  // Daily Essentials
  'DINING', 'GROCERY', 'PHARMACY',
  // Transportation
  'GAS', 'TRANSIT', 'EV_CHARGING',
  // Shopping
  'RETAIL', 'ONLINE_SHOPPING', 'WHOLESALE', 'HOME_IMPROVEMENT',
  // Bills & Services
  'RENT', 'RECURRING', 'TELECOM', 'INSURANCE', 'STREAMING',
  // Lifestyle
  'TRAVEL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'FOREIGN',
  // Other
  'OTHER',
]

function OptimizerPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { selectedCards, monthlySpending, setSpending, setResult } = useOptimizerStore()
  const { isAuthenticated, setPanelOpen } = useAuthStore()
  const { setSubscribed } = useSubscriptionStore()
  const [localSpending, setLocalSpending] = useState<Partial<Record<SpendingCategory, number>>>(
    monthlySpending
  )
  const [showPaywall, setShowPaywall] = useState(false)
  const [checkingUsage, setCheckingUsage] = useState(false)
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({})
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isInitialLoadRef = useRef(true)
  const isNative = isNativePlatform()

  // Auto-save with debounce
  const debouncedSave = useCallback((spending: Record<string, number>) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        await userApi.saveUserSpending(spending)
      } catch (error) {
        console.error('Auto-save spending failed:', error)
      }
    }, 1000)
  }, [])

  // Load user's saved spending when authenticated
  useEffect(() => {
    const loadUserSpending = async () => {
      if (isAuthenticated) {
        try {
          const response = await userApi.getUserSpending()
          if (response.code === 200 && response.data) {
            const savedSpending = response.data
            if (Object.keys(savedSpending).length > 0) {
              setLocalSpending(savedSpending as Partial<Record<SpendingCategory, number>>)
              Object.entries(savedSpending).forEach(([cat, val]) => {
                setSpending(cat as SpendingCategory, val as number)
              })
            }
          }
        } catch (error) {
          console.error('Failed to load user spending:', error)
        }
      }
      isInitialLoadRef.current = false
    }
    loadUserSpending()
  }, [isAuthenticated, setSpending])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])

  const mutation = useMutation({
    mutationFn: optimizerApi.calculate,
    onSuccess: (data) => {
      setResult(data)
      navigate('/result')
    },
    onError: () => {
      message.error(t('errors.unexpectedError'))
    },
  })

  const handleSpendingChange = (category: SpendingCategory, value: string) => {
    const numValue = value === '' ? 0 : parseInt(value.replace(/[^0-9]/g, ''), 10) || 0
    const newSpending = { ...localSpending, [category]: numValue }
    setLocalSpending(newSpending)
    setSpending(category, numValue)

    if (isAuthenticated && !isInitialLoadRef.current) {
      debouncedSave(newSpending as Record<string, number>)
    }
  }

  // Execute the optimization request
  const executeOptimization = (enableAi: boolean) => {
    const spending = CATEGORY_ORDER.reduce(
      (acc, category) => {
        acc[category] = localSpending[category] || 0
        return acc
      },
      {} as Record<SpendingCategory, number>
    )

    // Get current language from i18n
    const currentLocale = t('common.locale', { defaultValue: 'en' })

    // Get user ID from auth store
    const user = useAuthStore.getState().user

    mutation.mutate({
      userId: user?.id,
      cardIds: selectedCards.map((c) => c.id),
      monthlySpending: spending,
      locale: currentLocale,
      enableAiExplanation: enableAi,
    })
  }

  const handleCalculate = async () => {
    // For non-authenticated users, prompt to login
    if (!isAuthenticated) {
      message.info(t('optimizer.loginToOptimize'))
      setPanelOpen(true)
      return
    }

    // For all authenticated users, check AI usage limit
    setCheckingUsage(true)
    try {
      const response = await userApi.getAiUsage()
      if (response.code === 200 && response.data) {
        const { remaining, isProUser } = response.data
        if (remaining > 0) {
          // User has remaining AI usage
          executeOptimization(true)
        } else {
          // User has hit the limit
          console.log('AI usage limit reached:', { isProUser, isNative, remaining })
          if (isProUser) {
            // Pro user hit limit - just show message, no redirect
            message.warning(t('subscription.limitReachedPro'))
          } else {
            // Free user hit limit - show paywall directly (no message needed)
            // Native: can purchase in-app
            // Web: paywall shows "download app" message
            setShowPaywall(true)
          }
        }
      } else {
        // If we can't check usage, allow AI optimization
        executeOptimization(true)
      }
    } catch (error) {
      console.error('Failed to check AI usage:', error)
      // If check fails, allow AI optimization
      executeOptimization(true)
    } finally {
      setCheckingUsage(false)
    }
  }

  // Handle successful subscription from paywall
  const handleSubscribed = () => {
    setShowPaywall(false)
    setSubscribed(true)
    // After subscription, proceed with AI optimization
    executeOptimization(true)
  }

  const totalMonthlySpending = Object.values(localSpending).reduce((sum, val) => sum + (val || 0), 0)
  const filledCategories = Object.values(localSpending).filter(v => v && v > 0).length

  if (selectedCards.length === 0) {
    return (
      <div className="sv-optimizer-empty">
        <img src="/logo-full.svg" alt="SaveVia" className="sv-optimizer-empty-logo" />
        <p className="sv-optimizer-empty-text">{t('cards.noCardsSelected')}</p>
        <Link to="/cards" className="sv-optimizer-empty-btn">
          {t('cards.selectCards')} <ArrowRightOutlined />
        </Link>
      </div>
    )
  }

  return (
    <div className="sv-optimizer">
      {/* Header */}
      <div className="sv-optimizer-header">
        <h1 className="sv-optimizer-title">{t('optimizer.title')}</h1>
        <p className="sv-optimizer-subtitle">{t('optimizer.subtitle')}</p>
      </div>

      {/* Summary Cards */}
      <div className="sv-optimizer-summary">
        <div className="sv-optimizer-summary-item">
          <span className="sv-optimizer-summary-value">{selectedCards.length}</span>
          <span className="sv-optimizer-summary-label">{t('optimizer.cardsSelected')}</span>
        </div>
        <div className="sv-optimizer-summary-divider" />
        <div className="sv-optimizer-summary-item">
          <span className="sv-optimizer-summary-value">{filledCategories}</span>
          <span className="sv-optimizer-summary-label">{t('optimizer.categoriesFilled')}</span>
        </div>
      </div>

      {/* Category Grid */}
      <div className="sv-optimizer-grid">
        {CATEGORY_ORDER.map((category) => {
          const config = CATEGORY_CONFIG[category]
          const value = localSpending[category] || 0
          const hasValue = value > 0
          return (
            <div
              key={category}
              className={`sv-optimizer-card ${hasValue ? 'has-value' : ''}`}
              onClick={() => inputRefs.current[category]?.focus()}
              style={{ '--card-color': config.color } as React.CSSProperties}
            >
              <div className="sv-optimizer-card-header">
                <span className="sv-optimizer-card-icon">{config.icon}</span>
                <span className="sv-optimizer-card-label">{t(`categories.${category}`)}</span>
              </div>
              <div className="sv-optimizer-card-input">
                <span className="sv-optimizer-card-dollar">$</span>
                <input
                  ref={(el) => { inputRefs.current[category] = el }}
                  type="text"
                  inputMode="numeric"
                  value={value || ''}
                  onChange={(e) => handleSpendingChange(category, e.target.value)}
                  placeholder="0"
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Fixed Bottom Bar */}
      <div className="sv-optimizer-bottom">
        <div className="sv-optimizer-bottom-total">
          <span className="sv-optimizer-bottom-label">{t('optimizer.total')}</span>
          <span className="sv-optimizer-bottom-value">${totalMonthlySpending.toLocaleString()}</span>
          <span className="sv-optimizer-bottom-unit">{t('optimizer.perMonth')}</span>
        </div>
        <button
          className="sv-optimizer-bottom-btn"
          onClick={handleCalculate}
          disabled={totalMonthlySpending === 0 || mutation.isPending || checkingUsage}
        >
          {(mutation.isPending || checkingUsage) && !showPaywall ? (
            <>
              <LoadingOutlined spin />
              {t('optimizer.calculating')}
            </>
          ) : (
            <>
              {t('optimizer.calculate')}
              <ArrowRightOutlined />
            </>
          )}
        </button>
      </div>

      {/* Loading Overlay */}
      {mutation.isPending && (
        <div className="sv-ai-loading-overlay">
          <div className="sv-ai-loading-content">
            <div className="sv-ai-loading-logo">
              <img src="/logo-full.svg" alt="SaveVia" />
            </div>
            <div className="sv-ai-loading-text">
              {t('optimizer.calculating')}<span className="sv-ai-loading-dots"><span>.</span><span>.</span><span>.</span></span>
            </div>
          </div>
        </div>
      )}

      {/* Paywall Modal - shown when AI usage limit is hit */}
      {showPaywall && (
        <>
          {console.log('Rendering Paywall component, showPaywall:', showPaywall)}
          <Paywall
            onSubscribed={handleSubscribed}
            onClose={() => setShowPaywall(false)}
          />
        </>
      )}
    </div>
  )
}

export default OptimizerPage
