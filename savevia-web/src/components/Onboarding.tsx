import { useState, useMemo, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined } from '@ant-design/icons'

interface OnboardingProps {
  onComplete: () => void
}

// Card count options
const CARD_COUNT_OPTIONS = [
  { value: 1, label: '1-2' },
  { value: 3, label: '3-4' },
  { value: 5, label: '5-6' },
  { value: 7, label: '7+' },
]

// Annual spending options
const SPENDING_OPTIONS = [
  { value: 10000, label: '$0 - $20K' },
  { value: 35000, label: '$20K - $50K' },
  { value: 75000, label: '$50K - $100K' },
  { value: 150000, label: '$100K+' },
]

// Category config for display
const CATEGORY_CONFIG: Record<string, { icon: string; color: string }> = {
  // Daily Essentials
  DINING: { icon: '🍽️', color: '#f97316' },
  GROCERY: { icon: '🛒', color: '#22c55e' },
  PHARMACY: { icon: '💊', color: '#ec4899' },
  // Transportation
  GAS: { icon: '⛽', color: '#ef4444' },
  TRANSIT: { icon: '🚇', color: '#06b6d4' },
  EV_CHARGING: { icon: '⚡', color: '#16a34a' },
  // Shopping
  RETAIL: { icon: '🛍️', color: '#a855f7' },
  ONLINE_SHOPPING: { icon: '📦', color: '#f59e0b' },
  WHOLESALE: { icon: '🏪', color: '#0891b2' },
  HOME_IMPROVEMENT: { icon: '🔨', color: '#78716c' },
  // Bills & Services
  RENT: { icon: '🏠', color: '#6366f1' },
  RECURRING: { icon: '🔄', color: '#14b8a6' },
  TELECOM: { icon: '📱', color: '#2563eb' },
  INSURANCE: { icon: '📋', color: '#475569' },
  STREAMING: { icon: '📺', color: '#8b5cf6' },
  // Lifestyle
  TRAVEL: { icon: '✈️', color: '#3b82f6' },
  ENTERTAINMENT: { icon: '🎬', color: '#f43f5e' },
  PERSONAL_SERVICES: { icon: '💇', color: '#d946ef' },
  FOREIGN: { icon: '🌍', color: '#10b981' },
  // Catch-all
  OTHER: { icon: '💳', color: '#6b7280' },
}

// Category groups for organized display
const CATEGORY_GROUPS = [
  {
    key: 'daily',
    labelKey: 'categoryGroups.daily',
    categories: ['DINING', 'GROCERY', 'PHARMACY'],
  },
  {
    key: 'transport',
    labelKey: 'categoryGroups.transport',
    categories: ['GAS', 'TRANSIT', 'EV_CHARGING'],
  },
  {
    key: 'shopping',
    labelKey: 'categoryGroups.shopping',
    categories: ['RETAIL', 'ONLINE_SHOPPING', 'WHOLESALE', 'HOME_IMPROVEMENT'],
  },
  {
    key: 'bills',
    labelKey: 'categoryGroups.bills',
    categories: ['RENT', 'RECURRING', 'TELECOM', 'INSURANCE', 'STREAMING'],
  },
  {
    key: 'lifestyle',
    labelKey: 'categoryGroups.lifestyle',
    categories: ['TRAVEL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'FOREIGN'],
  },
  {
    key: 'other',
    labelKey: 'categoryGroups.other',
    categories: ['OTHER'],
  },
]

function Onboarding({ onComplete }: OnboardingProps) {
  const { t } = useTranslation()
  const [step, setStep] = useState(0)
  const [cardCount, setCardCount] = useState<number | null>(null)
  const [annualSpending, setAnnualSpending] = useState<number | null>(null)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])

  // Prevent iOS swipe-back gesture during onboarding
  useEffect(() => {
    // Prevent browser back gesture by blocking edge swipe
    const preventBackGesture = (e: TouchEvent) => {
      const touch = e.touches[0]
      // If touch starts near left edge (within 30px), prevent default
      if (touch && touch.clientX < 30) {
        e.preventDefault()
      }
    }

    // Add passive: false to allow preventDefault
    document.addEventListener('touchstart', preventBackGesture, { passive: false })
    document.addEventListener('touchmove', preventBackGesture, { passive: false })

    // Disable body scroll while onboarding is shown
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('touchstart', preventBackGesture)
      document.removeEventListener('touchmove', preventBackGesture)
      document.body.style.overflow = ''
    }
  }, [])

  // Calculate estimated savings based on user input
  // Before: 1.5-2.5%, After: 3-5%
  const savingsData = useMemo(() => {
    if (!annualSpending || selectedCategories.length === 0) {
      return { beforeCashback: 0, afterCashback: 0, extraSavings: 0, beforeRate: 0, afterRate: 0 }
    }

    // Before optimization: 1.5-2.5% based on card count
    // More cards = slightly better current cashback (users with more cards likely already optimizing a bit)
    const baseBeforeRate = 0.015 // 1.5% base
    const beforeCardBonus = cardCount ? Math.min(cardCount / 4, 1) * 0.01 : 0 // up to +1%
    const beforeRate = baseBeforeRate + beforeCardBonus // 1.5% - 2.5%
    const beforeCashback = annualSpending * beforeRate

    // After optimization: 3-4.5% cashback based on cards and categories
    const baseAfterRate = 0.03 // 3% base

    // More categories selected = better optimization potential (now 20 categories total)
    const categoryBonus = Math.min(selectedCategories.length / 20, 1) * 0.01 // up to +1%

    // More cards = more optimization options
    const cardBonus = cardCount ? Math.min(cardCount / 4, 1) * 0.005 : 0 // up to +0.5%

    const afterRate = baseAfterRate + categoryBonus + cardBonus // 3% - 4.5%
    const afterCashback = annualSpending * afterRate

    const roundedBefore = Math.round(beforeCashback / 10) * 10
    const roundedAfter = Math.round(afterCashback / 10) * 10

    return {
      beforeCashback: roundedBefore,
      afterCashback: roundedAfter,
      extraSavings: roundedAfter - roundedBefore, // Use rounded values for consistency
      beforeRate: Math.round(beforeRate * 100 * 10) / 10, // 1.5-2.5%
      afterRate: Math.round(afterRate * 100 * 10) / 10 // 3-4.5%
    }
  }, [annualSpending, selectedCategories, cardCount])

  const handleCategoryToggle = (categoryId: string) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      onComplete()
    }
  }

  const canProceed = () => {
    switch (step) {
      case 0: return cardCount !== null
      case 1: return annualSpending !== null
      case 2: return selectedCategories.length > 0
      case 3: return true
      default: return false
    }
  }

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="sv-onboarding-content">
            <h1 className="sv-onboarding-title">{t('onboarding.step1.title')}</h1>
            <p className="sv-onboarding-desc">{t('onboarding.step1.description')}</p>

            <div className="sv-onboarding-card-options">
              {CARD_COUNT_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`sv-onboarding-card-btn ${cardCount === option.value ? 'selected' : ''}`}
                  onClick={() => setCardCount(option.value)}
                >
                  <span className="sv-onboarding-card-num">{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        )

      case 1:
        return (
          <div className="sv-onboarding-content">
            <h1 className="sv-onboarding-title">{t('onboarding.step2.title')}</h1>
            <p className="sv-onboarding-desc">{t('onboarding.step2.description')}</p>

            <div className="sv-onboarding-spending-options">
              {SPENDING_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`sv-onboarding-spending-btn ${annualSpending === option.value ? 'selected' : ''}`}
                  onClick={() => setAnnualSpending(option.value)}
                >
                  <span>{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="sv-onboarding-content">
            <h1 className="sv-onboarding-title">{t('onboarding.step3.title')}</h1>
            <p className="sv-onboarding-desc">{t('onboarding.step3.description')}</p>

            <div className="sv-onboarding-category-groups">
              {CATEGORY_GROUPS.map(group => (
                <div key={group.key} className="sv-onboarding-category-group">
                  <div className="sv-onboarding-category-group-label">{t(group.labelKey)}</div>
                  <div className="sv-onboarding-categories">
                    {group.categories.map(categoryId => {
                      const category = CATEGORY_CONFIG[categoryId]
                      const isSelected = selectedCategories.includes(categoryId)
                      return (
                        <button
                          key={categoryId}
                          className={`sv-onboarding-category ${isSelected ? 'selected' : ''}`}
                          onClick={() => handleCategoryToggle(categoryId)}
                          style={{ '--category-color': category.color } as React.CSSProperties}
                        >
                          <span className="sv-onboarding-category-icon">{category.icon}</span>
                          <span className="sv-onboarding-category-label">{t(`categories.${categoryId}`)}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 3:
        return (
          <div className="sv-onboarding-content sv-onboarding-summary">
            <h1 className="sv-onboarding-title">{t('onboarding.summary.title')}</h1>

            <div className="sv-onboarding-comparison">
              <div className="sv-onboarding-compare-item sv-onboarding-compare-before">
                <span className="sv-onboarding-compare-label">{t('onboarding.summary.before')}</span>
                <span className="sv-onboarding-compare-value">${savingsData.beforeCashback.toLocaleString()}</span>
                <span className="sv-onboarding-compare-rate">~{savingsData.beforeRate}%</span>
              </div>
              <div className="sv-onboarding-compare-arrow">→</div>
              <div className="sv-onboarding-compare-item sv-onboarding-compare-after">
                <span className="sv-onboarding-compare-label">{t('onboarding.summary.after')}</span>
                <span className="sv-onboarding-compare-value">${savingsData.afterCashback.toLocaleString()}</span>
                <span className="sv-onboarding-compare-rate">~{savingsData.afterRate}%</span>
              </div>
            </div>

            <div className="sv-onboarding-extra">
              <span className="sv-onboarding-extra-label">{t('onboarding.summary.extraSavings')}</span>
              <span className="sv-onboarding-extra-amount">+${savingsData.extraSavings.toLocaleString()}</span>
              <span className="sv-onboarding-extra-period">/{t('onboarding.summary.perYear')}</span>
            </div>

            <p className="sv-onboarding-summary-text">
              {t('onboarding.summary.description', {
                cardCount: cardCount,
                categoryCount: selectedCategories.length
              })}
            </p>

            <p className="sv-onboarding-disclaimer">
              {t('onboarding.summary.disclaimer')}
            </p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="sv-onboarding">
      {/* Header with Logo */}
      <div className="sv-onboarding-header">
        <img src="/logo-full.svg" alt="SaveVia" className="sv-onboarding-logo" />
        <p className="sv-onboarding-welcome">{t('onboarding.welcome')}</p>
      </div>

      {/* Progress indicator */}
      <div className="sv-onboarding-progress">
        {[0, 1, 2, 3].map(i => (
          <div
            key={i}
            className={`sv-onboarding-progress-dot ${i === step ? 'active' : ''} ${i < step ? 'completed' : ''}`}
          />
        ))}
      </div>

      {/* Content */}
      <div className="sv-onboarding-main">
        {renderStep()}
      </div>

      {/* Bottom button */}
      <div className="sv-onboarding-footer">
        <button
          className={`sv-onboarding-btn ${!canProceed() ? 'disabled' : ''}`}
          onClick={handleNext}
          disabled={!canProceed()}
        >
          {step === 3 ? t('onboarding.summary.getStarted') : t('onboarding.continue')}
          <ArrowRightOutlined />
        </button>
      </div>

      <style>{`
        .sv-onboarding {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 10000;
          display: flex;
          flex-direction: column;
          background: #FFFCF5;
          padding-top: env(safe-area-inset-top, 0px);
          padding-bottom: env(safe-area-inset-bottom, 0px);
          /* Prevent iOS swipe-back gesture */
          touch-action: pan-y pinch-zoom;
          overscroll-behavior-x: none;
          -webkit-overflow-scrolling: touch;
        }

        .sv-onboarding-header {
          text-align: center;
          padding: 24px 24px 16px;
        }

        .sv-onboarding-logo {
          height: 44px;
          width: auto;
          margin-bottom: 8px;
        }

        .sv-onboarding-welcome {
          font-size: 15px;
          color: #6b7280;
          margin: 0;
        }

        .sv-onboarding-progress {
          display: flex;
          justify-content: center;
          gap: 8px;
          padding: 8px 24px 16px;
        }

        .sv-onboarding-progress-dot {
          width: 8px;
          height: 8px;
          border-radius: 4px;
          background: #e5e7eb;
          transition: all 0.3s ease;
        }

        .sv-onboarding-progress-dot.active {
          width: 24px;
          background: #111827;
        }

        .sv-onboarding-progress-dot.completed {
          background: #059669;
        }

        .sv-onboarding-main {
          flex: 1;
          display: flex;
          align-items: flex-start;
          justify-content: center;
          padding: 0 24px;
          overflow-y: auto;
        }

        .sv-onboarding-content {
          width: 100%;
          max-width: 400px;
          padding-top: 20px;
        }

        .sv-onboarding-title {
          font-size: 22px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 8px;
          line-height: 1.3;
        }

        .sv-onboarding-desc {
          font-size: 14px;
          color: #6b7280;
          line-height: 1.5;
          margin-bottom: 28px;
        }

        /* Card count options */
        .sv-onboarding-card-options {
          display: flex;
          gap: 12px;
          justify-content: center;
        }

        .sv-onboarding-card-btn {
          width: 72px;
          height: 72px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: #f3f4f6;
          border: none;
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .sv-onboarding-card-btn:active {
          transform: scale(0.95);
        }

        .sv-onboarding-card-btn.selected {
          background: #111827;
        }

        .sv-onboarding-card-num {
          font-size: 24px;
          font-weight: 700;
          color: #111827;
        }

        .sv-onboarding-card-btn.selected .sv-onboarding-card-num {
          color: white;
        }

        /* Spending options */
        .sv-onboarding-spending-options {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .sv-onboarding-spending-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px 20px;
          background: #f3f4f6;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 500;
          color: #374151;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .sv-onboarding-spending-btn:active {
          transform: scale(0.98);
        }

        .sv-onboarding-spending-btn.selected {
          background: #111827;
          color: white;
        }

        /* Category Groups */
        .sv-onboarding-category-groups {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .sv-onboarding-category-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .sv-onboarding-category-group-label {
          font-size: 11px;
          font-weight: 600;
          color: #9ca3af;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          padding-left: 2px;
        }

        /* Categories */
        .sv-onboarding-categories {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .sv-onboarding-category {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 6px;
          padding: 10px 14px;
          background: #f3f4f6;
          border: none;
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .sv-onboarding-category:active {
          transform: scale(0.95);
        }

        .sv-onboarding-category.selected {
          background: color-mix(in srgb, var(--category-color) 15%, white);
        }

        .sv-onboarding-category-icon {
          font-size: 18px;
          line-height: 1;
        }

        .sv-onboarding-category-label {
          font-size: 13px;
          font-weight: 500;
          color: #6b7280;
          text-align: center;
          line-height: 1;
        }

        .sv-onboarding-category.selected .sv-onboarding-category-label {
          color: var(--category-color);
          font-weight: 600;
        }

        /* Summary */
        .sv-onboarding-summary {
          text-align: center;
          padding-top: 24px;
        }

        .sv-onboarding-comparison {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 24px;
          margin: 24px 0;
        }

        .sv-onboarding-compare-item {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .sv-onboarding-compare-before {
          opacity: 0.6;
        }

        .sv-onboarding-compare-label {
          font-size: 13px;
          color: #6b7280;
          margin-bottom: 4px;
        }

        .sv-onboarding-compare-value {
          font-size: 28px;
          font-weight: 700;
          color: #374151;
        }

        .sv-onboarding-compare-after .sv-onboarding-compare-value {
          color: #059669;
        }

        .sv-onboarding-compare-rate {
          font-size: 12px;
          color: #9ca3af;
          margin-top: 4px;
        }

        .sv-onboarding-compare-arrow {
          font-size: 24px;
          color: #d1d5db;
        }

        .sv-onboarding-extra {
          margin: 24px 0;
        }

        .sv-onboarding-extra-label {
          display: block;
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 8px;
        }

        .sv-onboarding-extra-amount {
          font-size: 48px;
          font-weight: 700;
          color: #059669;
          line-height: 1;
        }

        .sv-onboarding-extra-period {
          font-size: 16px;
          font-weight: 500;
          color: #6b7280;
        }

        .sv-onboarding-summary-text {
          font-size: 14px;
          color: #6b7280;
          line-height: 1.6;
        }

        .sv-onboarding-disclaimer {
          font-size: 11px;
          color: #9ca3af;
          margin-top: 16px;
        }

        .sv-onboarding-footer {
          padding: 16px 24px;
          padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
        }

        .sv-onboarding-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          background: #111827;
          color: white;
          padding: 16px 32px;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .sv-onboarding-btn:active {
          transform: scale(0.98);
          opacity: 0.9;
        }

        .sv-onboarding-btn.disabled {
          background: #d1d5db;
          cursor: not-allowed;
        }

        .sv-onboarding-btn.disabled:active {
          transform: none;
          opacity: 1;
        }

        .sv-onboarding-btn .anticon {
          font-size: 14px;
        }

        /* Web only - limit button width and adjust layout */
        @media (min-width: 641px) {
          .sv-onboarding-main {
            flex: none;
          }
          .sv-onboarding-footer {
            padding: 32px 24px;
          }
          .sv-onboarding-btn {
            max-width: 280px;
            margin: 0 auto;
          }
        }

        /* Dark mode */
        html.dark-mode .sv-onboarding {
          background: #121212;
        }

        html.dark-mode .sv-onboarding-welcome {
          color: #a0a0a0;
        }

        html.dark-mode .sv-onboarding-progress-dot {
          background: #333;
        }

        html.dark-mode .sv-onboarding-progress-dot.active {
          background: #f5f5f5;
        }

        html.dark-mode .sv-onboarding-title {
          color: #f5f5f5;
        }

        html.dark-mode .sv-onboarding-desc,
        html.dark-mode .sv-onboarding-summary-text,
        html.dark-mode .sv-onboarding-disclaimer {
          color: #a0a0a0;
        }

        html.dark-mode .sv-onboarding-card-btn,
        html.dark-mode .sv-onboarding-spending-btn,
        html.dark-mode .sv-onboarding-category {
          background: #2a2a2a;
        }

        html.dark-mode .sv-onboarding-card-num,
        html.dark-mode .sv-onboarding-spending-btn {
          color: #e5e5e5;
        }

        html.dark-mode .sv-onboarding-card-btn.selected,
        html.dark-mode .sv-onboarding-spending-btn.selected {
          background: #f5f5f5;
        }

        html.dark-mode .sv-onboarding-card-btn.selected .sv-onboarding-card-num,
        html.dark-mode .sv-onboarding-spending-btn.selected {
          color: #111827;
        }

        html.dark-mode .sv-onboarding-category.selected {
          background: color-mix(in srgb, var(--category-color) 25%, #1a1a1a);
        }

        html.dark-mode .sv-onboarding-category-label {
          color: #a0a0a0;
        }

        html.dark-mode .sv-onboarding-compare-value {
          color: #e5e5e5;
        }

        html.dark-mode .sv-onboarding-compare-after .sv-onboarding-compare-value {
          color: #10b981;
        }

        html.dark-mode .sv-onboarding-extra-label {
          color: #a0a0a0;
        }

        html.dark-mode .sv-onboarding-extra-amount {
          color: #10b981;
        }

        html.dark-mode .sv-onboarding-extra-period {
          color: #a0a0a0;
        }

        html.dark-mode .sv-onboarding-btn {
          background: #f5f5f5;
          color: #111827;
        }

        html.dark-mode .sv-onboarding-btn.disabled {
          background: #333;
          color: #666;
        }
      `}</style>
    </div>
  )
}

export default Onboarding
