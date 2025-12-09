import { useState, useMemo, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined } from '@ant-design/icons'
import { useAuthStore } from '../stores/useAuthStore'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { cardApi, userApi } from '../services/api'
import type { SpendingCategory, CreditCard } from '../types'

// Bank logo paths
const BANK_LOGOS: Record<string, string> = {
  'TD': '/logos/td.png',
  'RBC': '/logos/rbc.png',
  'Scotiabank': '/logos/scotiabank.png',
  'CIBC': '/logos/cibc.png',
  'BMO': '/logos/bmo.png',
  'American Express': '/logos/amex.png',
  'AMEX': '/logos/amex.png',
  'Rogers': '/logos/rogers.png',
  'Tangerine': '/logos/tangerine.png',
  'Neo': '/logos/neo.png',
  'PC Financial': '/logos/pc.png',
  'Simplii': '/logos/simplii.png',
  'MBNA': '/logos/mbna.png',
  'National Bank': '/logos/nationalbank.png',
  'Home Trust': '/logos/hometrust.png',
}

// Category icons and colors
const CATEGORY_CONFIG: Record<SpendingCategory, { icon: string; color: string }> = {
  DINING: { icon: '🍽️', color: '#f97316' },
  GROCERY: { icon: '🛒', color: '#22c55e' },
  GAS: { icon: '⛽', color: '#ef4444' },
  TRAVEL: { icon: '✈️', color: '#3b82f6' },
  STREAMING: { icon: '📺', color: '#8b5cf6' },
  TRANSIT: { icon: '🚇', color: '#06b6d4' },
  PHARMACY: { icon: '💊', color: '#ec4899' },
  RENT: { icon: '🏠', color: '#6366f1' },
  RECURRING: { icon: '🔄', color: '#14b8a6' },
  ONLINE_SHOPPING: { icon: '🛍️', color: '#f59e0b' },
  FOREIGN: { icon: '🌍', color: '#10b981' },
  OTHER: { icon: '💳', color: '#6b7280' },
}

function HomePage() {
  const { t } = useTranslation()
  const { isAuthenticated } = useAuthStore()
  const { selectedCards, setSelectedCards } = useOptimizerStore()
  const [selectedCategory, setSelectedCategory] = useState<SpendingCategory | null>(null)
  const resultRef = useRef<HTMLDivElement>(null)

  const handleCategorySelect = (category: SpendingCategory) => {
    const isSelected = selectedCategory === category
    setSelectedCategory(isSelected ? null : category)
    // Scroll to result after a short delay if selecting (not deselecting)
    if (!isSelected) {
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 100)
    }
  }

  // Load saved cards for authenticated users
  useEffect(() => {
    const loadSavedCards = async () => {
      if (isAuthenticated && selectedCards.length === 0) {
        try {
          // First get all cards
          const allCards = await cardApi.getAll()
          // Then get user's saved card IDs
          const response = await userApi.getUserCards()
          if (response.code === 200 && response.data && response.data.length > 0) {
            const savedCardIds = response.data
            const savedCards = allCards.filter((c: CreditCard) => savedCardIds.includes(c.id))
            if (savedCards.length > 0) {
              setSelectedCards(savedCards)
            }
          }
        } catch (error) {
          console.error('Failed to load saved cards:', error)
        }
      }
    }
    loadSavedCards()
  }, [isAuthenticated, selectedCards.length, setSelectedCards])

  // Find best card for selected category
  const bestCard = useMemo(() => {
    if (!selectedCategory || selectedCards.length === 0) return null

    let best: { card: CreditCard; rate: number } | null = null

    for (const card of selectedCards) {
      // Find the reward rate for this category
      const rule = card.rewardRules.find(r => r.category === selectedCategory)
      const rate = rule?.rewardRate || card.baseRewardRate

      if (!best || rate > best.rate) {
        best = { card, rate }
      }
    }

    return best
  }, [selectedCategory, selectedCards])

  // Check if user can use quick select
  const canUseQuickSelect = isAuthenticated && selectedCards.length > 0

  return (
    <div className="sv-home-page" style={{ padding: '20px 0 60px', overflow: 'hidden' }}>
      {/* Hero - Asymmetric Layout */}
      <section className="sv-home-grid" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '60px',
        alignItems: 'center',
        minHeight: '70vh',
        marginBottom: '100px'
      }}>
        {/* Left - Text Content (order 1 on mobile) */}
        <div className="sv-home-text">
          {/* Savings Text */}
          <div style={{
            display: 'inline-block',
            background: '#ecfdf5',
            color: '#059669',
            fontSize: '14px',
            fontWeight: '600',
            padding: '8px 16px',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            {t('home.savingsBadge')}
          </div>

          <h1 className="sv-home-title" style={{
            fontSize: '52px',
            fontWeight: '700',
            color: '#111827',
            lineHeight: '1.15',
            marginBottom: '24px',
            letterSpacing: '-1px'
          }}>
            {t('home.title')}
          </h1>

          <p className="sv-home-subtitle" style={{
            fontSize: '18px',
            color: '#6b7280',
            lineHeight: '1.7',
            marginBottom: '40px',
            maxWidth: '440px'
          }}>
            {t('home.subtitle')}
          </p>

          {/* CTA Button - visible on desktop, hidden on mobile */}
          <Link
            to="/cards"
            className="sv-home-cta sv-home-cta-desktop"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              background: '#111827',
              color: 'white',
              padding: '16px 32px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              textDecoration: 'none',
              transition: 'transform 0.2s'
            }}
          >
            {t('home.getStarted')}
            <ArrowRightOutlined />
          </Link>
        </div>

        {/* Right - Visual Cards Stack */}
        <div className="sv-home-visual" style={{ position: 'relative', height: '400px' }}>
          {/* Background Card */}
          <div className="sv-card-back" style={{
            position: 'absolute',
            top: '40px',
            right: '20px',
            width: '280px',
            height: '170px',
            background: 'linear-gradient(135deg, #dbeafe 0%, #ede9fe 100%)',
            borderRadius: '16px',
            transform: 'rotate(6deg)',
          }} />

          {/* Middle Card */}
          <div className="sv-card-mid" style={{
            position: 'absolute',
            top: '80px',
            right: '60px',
            width: '280px',
            height: '170px',
            background: 'linear-gradient(135deg, #fef3c7 0%, #fce7f3 100%)',
            borderRadius: '16px',
            transform: 'rotate(-3deg)',
            boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
          }} />

          {/* Front Card */}
          <div className="sv-card-front" style={{
            position: 'absolute',
            top: '120px',
            right: '100px',
            width: '280px',
            height: '170px',
            background: 'linear-gradient(135deg, #111827 0%, #374151 100%)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
            color: 'white'
          }}>
            <div className="sv-card-label" style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>{t('home.cashbackLabel')}</div>
            <div className="sv-card-rate" style={{ fontSize: '32px', fontWeight: '700' }}>5%</div>
            <div className="sv-card-number" style={{
              position: 'absolute',
              bottom: '24px',
              left: '24px',
              fontSize: '13px',
              opacity: 0.8
            }}>
              •••• •••• •••• 4242
            </div>
          </div>

          {/* Floating Tagline - Top (positioned via CSS) */}
          <div className="sv-tagline-top" style={{
            background: 'white',
            borderRadius: '6px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
          }}>
            <div className="sv-tagline-label" style={{ fontSize: '12px', fontWeight: '500', color: '#9ca3af' }}>{t('home.tagline1')}</div>
            <div className="sv-tagline-value" style={{ fontSize: '20px', fontWeight: '700', color: '#059669' }}>+$847</div>
          </div>

          {/* Floating Tagline - Bottom (positioned via CSS) */}
          <div className="sv-tagline-bottom" style={{
            background: 'white',
            borderRadius: '6px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
          }}>
            <span style={{ fontSize: '13px', fontWeight: '500', color: '#6b7280' }}>{t('home.tagline2')}</span>
          </div>

          {/* Mobile Taglines Row - shown only on mobile */}
          <div className="sv-mobile-taglines" style={{
            display: 'none',
            position: 'absolute',
            bottom: '0',
            left: '0',
            right: '0',
            justifyContent: 'center',
            gap: '12px',
            padding: '0 10px'
          }}>
            <div style={{
              background: 'white',
              padding: '10px 14px',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '10px', fontWeight: '500', color: '#9ca3af' }}>{t('home.tagline1')}</div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: '#059669' }}>+$847</div>
            </div>
            <div style={{
              background: 'white',
              padding: '10px 14px',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              display: 'flex',
              alignItems: 'center'
            }}>
              <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>{t('home.tagline2')}</span>
            </div>
          </div>
        </div>

        {/* Mobile CTA Button - order 3, shown only on mobile */}
        <Link
          to="/cards"
          className="sv-home-cta sv-home-cta-mobile"
          style={{
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            background: '#111827',
            color: 'white',
            padding: '16px 32px',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            textDecoration: 'none',
            transition: 'transform 0.2s',
            width: '100%'
          }}
        >
          {t('home.getStarted')}
          <ArrowRightOutlined />
        </Link>
      </section>

      {/* Mobile Quick Select - Always show on mobile */}
      <section className="sv-quick-select">
        <h2 className="sv-quick-select-title">{t('home.quickSelect.title')}</h2>
        <p className="sv-quick-select-desc">{t('home.quickSelect.description')}</p>

        {canUseQuickSelect ? (
          <>
            {/* Category Grid */}
            <div className="sv-quick-select-grid">
              {(Object.keys(CATEGORY_CONFIG) as SpendingCategory[]).map((category) => {
                const config = CATEGORY_CONFIG[category]
                const isSelected = selectedCategory === category
                return (
                  <button
                    key={category}
                    className={`sv-quick-select-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleCategorySelect(category)}
                    style={{
                      '--item-color': config.color
                    } as React.CSSProperties}
                  >
                    <span className="sv-quick-select-icon">{config.icon}</span>
                    <span className="sv-quick-select-label">{t(`categories.${category}`)}</span>
                  </button>
                )
              })}
            </div>

            {/* Result Card */}
            {selectedCategory && bestCard && (
              <div ref={resultRef} className="sv-quick-result">
                {BANK_LOGOS[bestCard.card.bank] && (
                  <img
                    src={BANK_LOGOS[bestCard.card.bank]}
                    alt={bestCard.card.bank}
                    className="sv-quick-result-logo"
                  />
                )}
                <div className="sv-quick-result-info">
                  <div className="sv-quick-result-bank">{bestCard.card.bank}</div>
                  <div className="sv-quick-result-name">{bestCard.card.name}</div>
                </div>
                <div className="sv-quick-result-rate">
                  <span className="sv-quick-result-rate-value">{(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}%</span>
                  <span className="sv-quick-result-rate-label">{t('home.quickSelect.cashback')}</span>
                </div>
              </div>
            )}
          </>
        ) : (
          /* Prompt to login/select cards */
          <Link to={isAuthenticated ? "/cards" : "/me"} className="sv-quick-select-prompt">
            <span className="sv-quick-select-prompt-icon">💳</span>
            <span className="sv-quick-select-prompt-text">
              {isAuthenticated ? t('home.quickSelect.addCards') : t('home.quickSelect.loginFirst')}
            </span>
            <ArrowRightOutlined className="sv-quick-select-prompt-arrow" />
          </Link>
        )}
      </section>
    </div>
  )
}

export default HomePage
