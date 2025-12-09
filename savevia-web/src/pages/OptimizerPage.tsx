import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { message } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined } from '@ant-design/icons'
import { optimizerApi, userApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import type { SpendingCategory } from '../types'

// Category config with icons
const CATEGORY_CONFIG: { category: SpendingCategory; icon: string; color: string }[] = [
  { category: 'RENT', icon: '🏠', color: '#6366f1' },
  { category: 'GROCERY', icon: '🛒', color: '#22c55e' },
  { category: 'DINING', icon: '🍽️', color: '#f97316' },
  { category: 'GAS', icon: '⛽', color: '#ef4444' },
  { category: 'TRAVEL', icon: '✈️', color: '#0ea5e9' },
  { category: 'TRANSIT', icon: '🚇', color: '#8b5cf6' },
  { category: 'STREAMING', icon: '📺', color: '#ec4899' },
  { category: 'PHARMACY', icon: '💊', color: '#14b8a6' },
  { category: 'RECURRING', icon: '🔄', color: '#64748b' },
  { category: 'ONLINE_SHOPPING', icon: '📦', color: '#f59e0b' },
  { category: 'FOREIGN', icon: '🌍', color: '#06b6d4' },
  { category: 'OTHER', icon: '💳', color: '#71717a' },
]

function OptimizerPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { selectedCards, monthlySpending, setSpending, setResult } = useOptimizerStore()
  const { isAuthenticated } = useAuthStore()
  const [localSpending, setLocalSpending] = useState<Partial<Record<SpendingCategory, number>>>(
    monthlySpending
  )
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({})
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isInitialLoadRef = useRef(true)

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

  const handleCalculate = () => {
    const spending = CATEGORY_CONFIG.reduce(
      (acc, { category }) => {
        acc[category] = localSpending[category] || 0
        return acc
      },
      {} as Record<SpendingCategory, number>
    )

    mutation.mutate({
      cardIds: selectedCards.map((c) => c.id),
      monthlySpending: spending,
    })
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
        {CATEGORY_CONFIG.map(({ category, icon, color }) => {
          const value = localSpending[category] || 0
          const hasValue = value > 0
          return (
            <div
              key={category}
              className={`sv-optimizer-card ${hasValue ? 'has-value' : ''}`}
              onClick={() => inputRefs.current[category]?.focus()}
              style={{ '--card-color': color } as React.CSSProperties}
            >
              <div className="sv-optimizer-card-header">
                <span className="sv-optimizer-card-icon">{icon}</span>
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
          disabled={totalMonthlySpending === 0 || mutation.isPending}
        >
          {mutation.isPending ? t('optimizer.calculating') : t('optimizer.calculate')}
          <ArrowRightOutlined />
        </button>
      </div>
    </div>
  )
}

export default OptimizerPage
