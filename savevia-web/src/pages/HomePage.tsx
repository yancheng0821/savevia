import { useState, useMemo, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined, SafetyOutlined, CloseOutlined, WalletOutlined, CreditCardOutlined } from '@ant-design/icons'
import { Capacitor } from '@capacitor/core'
import { useAuthStore } from '../stores/useAuthStore'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { cardApi, userApi, bankApi } from '../services/api'
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
  'Brim': '/logos/brim.png',
  'Wealthsimple': '/logos/wealthsimple.png',
  'Desjardins': '/logos/desjardins.png',
  'Canadian Tire': '/logos/canadiantire.png',
  'Vancity': '/logos/vancity.png',
  'Meridian': '/logos/meridian.png',
  'Coast Capital': '/logos/coastcapital.png',
  'Walmart': '/logos/walmart.png',
}

// Category icons and colors
const CATEGORY_CONFIG: Record<SpendingCategory, { icon: string; color: string }> = {
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
    categories: ['DINING', 'GROCERY', 'PHARMACY'] as SpendingCategory[],
  },
  {
    key: 'transport',
    labelKey: 'categoryGroups.transport',
    categories: ['GAS', 'TRANSIT', 'EV_CHARGING'] as SpendingCategory[],
  },
  {
    key: 'shopping',
    labelKey: 'categoryGroups.shopping',
    categories: ['RETAIL', 'ONLINE_SHOPPING', 'WHOLESALE', 'HOME_IMPROVEMENT'] as SpendingCategory[],
  },
  {
    key: 'bills',
    labelKey: 'categoryGroups.bills',
    categories: ['RENT', 'RECURRING', 'TELECOM', 'INSURANCE', 'STREAMING'] as SpendingCategory[],
  },
  {
    key: 'lifestyle',
    labelKey: 'categoryGroups.lifestyle',
    categories: ['TRAVEL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'FOREIGN'] as SpendingCategory[],
  },
  {
    key: 'other',
    labelKey: 'categoryGroups.other',
    categories: ['OTHER'] as SpendingCategory[],
  },
]

function HomePage() {
  const { t } = useTranslation()
  const { isAuthenticated } = useAuthStore()
  const { selectedCards, setSelectedCards } = useOptimizerStore()
  const [selectedCategory, setSelectedCategory] = useState<SpendingCategory | null>(null)
  const [hasBankConnection, setHasBankConnection] = useState(false)
  const [bankConnectionChecked, setBankConnectionChecked] = useState(false)
  const [showCardModal, setShowCardModal] = useState(false)
  const resultRef = useRef<HTMLDivElement>(null)

  // Check if user has bank connection
  useEffect(() => {
    const checkBankConnection = async () => {
      if (isAuthenticated) {
        try {
          const res = await bankApi.getConnections()
          if (res.code === 200 && res.data && res.data.length > 0) {
            setHasBankConnection(true)
          }
        } catch (e) {
          // Ignore
        } finally {
          setBankConnectionChecked(true)
        }
      } else {
        // Not authenticated, no need to check
        setBankConnectionChecked(true)
      }
    }
    checkBankConnection()
  }, [isAuthenticated])

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

  // Open Apple Wallet
  const openWallet = () => {
    const platform = Capacitor.getPlatform()
    if (platform === 'ios') {
      // iOS: Open Apple Wallet
      window.location.href = 'shoebox://'
    } else if (platform === 'android') {
      // Android: Open Google Pay
      window.location.href = 'intent://pay#Intent;scheme=google;package=com.google.android.apps.walletnfcrel;end'
    }
    setShowCardModal(false)
  }

  // Handle card click
  const handleCardClick = () => {
    setShowCardModal(true)
  }

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
            {t('home.title').split('SaveVia').map((part, index, arr) => (
              <span key={index}>
                {part}
                {index < arr.length - 1 && <span className="sv-logo-gradient">SaveVia</span>}
              </span>
            ))}
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

          {/* CTA Buttons - visible on desktop, hidden on mobile */}
          <div className="sv-home-cta-group">
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
                transition: 'transform 0.2s',
                whiteSpace: 'nowrap'
              }}
            >
              {t('home.getStarted')}
              <ArrowRightOutlined />
            </Link>

            {/* Bank Connect Button - Desktop only */}
            {/* For authenticated users: hide until we confirm they DON'T have bank connection */}
            {/* For unauthenticated users: always show */}
            {(!isAuthenticated || (bankConnectionChecked && !hasBankConnection)) && (
              <div className="sv-home-bank-group">
                <Link
                  to={isAuthenticated ? "/transactions" : "/me"}
                  className="sv-home-bank-btn"
                >
                  {t('home.bankConnect.cta')}
                  <ArrowRightOutlined />
                </Link>
                <div className="sv-home-bank-meta">
                  <span className="sv-home-bank-security">
                    <SafetyOutlined /> {t('home.bankConnect.security')}
                  </span>
                  <span className="sv-home-bank-hint">
                    {t('home.bankConnect.poweredBy')} <img src="/logos/flinks.png" alt="Flinks" style={{ height: '14px', verticalAlign: 'middle', marginLeft: '4px' }} /> Flinks
                  </span>
                </div>
              </div>
            )}
          </div>
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
            background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
            color: 'white'
          }}>
            {/* Chip and Label Row */}
            <div className="sv-card-chip-row" style={{ display: 'flex' }}>
              {/* Chip */}
              <div className="sv-card-chip" style={{
                width: '40px',
                height: '30px',
                background: 'linear-gradient(135deg, #fbbf24 0%, #d97706 100%)',
                borderRadius: '4px',
                position: 'relative',
                flexShrink: 0
              }}>
                {/* Chip lines */}
                <div style={{ position: 'absolute', top: '10px', left: '0', right: '0', height: '1px', background: 'rgba(201, 162, 39, 0.5)' }} />
                <div style={{ position: 'absolute', top: '18px', left: '0', right: '0', height: '1px', background: 'rgba(201, 162, 39, 0.5)' }} />
                <div style={{ position: 'absolute', top: '0', bottom: '0', left: '50%', width: '1px', background: 'rgba(201, 162, 39, 0.5)' }} />
              </div>
              <div className="sv-card-label" style={{ fontSize: '10px', opacity: 0.7, letterSpacing: '0.5px' }}>{t('home.cashbackLabel')}</div>
              <div className="sv-card-rate" style={{ fontSize: '28px', fontWeight: '700' }}>5%</div>
            </div>
            {/* Sparkle - positioned to the right side of card */}
            <svg className="sv-card-sparkle" style={{ position: 'absolute', top: '20px', right: '24px', width: '16px', height: '16px' }} viewBox="0 0 16 16" fill="none">
              <path d="M8 0 L9 6 L15 8 L9 10 L8 16 L7 10 L1 8 L7 6 Z" fill="white" opacity="0.8"/>
            </svg>
            <div className="sv-card-number" style={{
              position: 'absolute',
              bottom: '20px',
              left: '24px',
              fontSize: '13px',
              opacity: 0.6,
              letterSpacing: '1px'
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
            {/* Category Groups */}
            <div className="sv-quick-select-groups">
              {CATEGORY_GROUPS.map((group) => (
                <div key={group.key} className="sv-quick-select-group">
                  <div className="sv-quick-select-group-label">{t(group.labelKey)}</div>
                  <div className="sv-quick-select-grid">
                    {group.categories.map((category) => {
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
                </div>
              ))}
            </div>

            {/* Result Card - Clickable */}
            {selectedCategory && bestCard && (
              <div
                ref={resultRef}
                className="sv-quick-result"
                onClick={handleCardClick}
                role="button"
                tabIndex={0}
              >
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

      {/* Bank Connect Section - Mobile only */}
      {/* For authenticated users: hide until we confirm they DON'T have bank connection */}
      {/* For unauthenticated users: always show */}
      {(!isAuthenticated || (bankConnectionChecked && !hasBankConnection)) && (
        <section className="sv-bank-connect">
          <h2 className="sv-bank-connect-title">{t('home.bankConnect.title')}</h2>
          <p className="sv-bank-connect-desc">{t('home.bankConnect.description')}</p>

          {/* Demo Notice */}
          <div className="sv-bank-connect-demo">
            ⚠️ {t('home.bankConnect.demoNotice')}
          </div>

          <Link to={isAuthenticated ? "/transactions" : "/me"} className="sv-bank-connect-link">
            {t('home.bankConnect.cta')} <ArrowRightOutlined />
          </Link>

          <div className="sv-bank-connect-meta">
            <span className="sv-bank-connect-security">
              <SafetyOutlined />
              {t('home.bankConnect.security')}
            </span>
            <span className="sv-bank-connect-powered">
              {t('home.bankConnect.poweredBy')} <img src="/logos/flinks.png" alt="Flinks" style={{ height: '16px', verticalAlign: 'middle', marginLeft: '4px' }} /> <strong>Flinks</strong>
            </span>
          </div>
        </section>
      )}

      {/* Card Detail Modal */}
      {showCardModal && bestCard && (
        <div className="sv-card-modal-overlay" onClick={() => setShowCardModal(false)}>
          <div className="sv-card-modal" onClick={e => e.stopPropagation()}>
            <button className="sv-card-modal-close" onClick={() => setShowCardModal(false)}>
              <CloseOutlined />
            </button>

            <div className="sv-card-modal-header">
              {BANK_LOGOS[bestCard.card.bank] && (
                <img
                  src={BANK_LOGOS[bestCard.card.bank]}
                  alt={bestCard.card.bank}
                  className="sv-card-modal-logo"
                />
              )}
              <div className="sv-card-modal-title">
                <h3>{bestCard.card.name}</h3>
                <span>{bestCard.card.bank}</span>
              </div>
            </div>

            <div className="sv-card-modal-info">
              <div className="sv-card-modal-category">
                <span className="sv-card-modal-category-icon">
                  {selectedCategory && CATEGORY_CONFIG[selectedCategory]?.icon}
                </span>
                <span>{selectedCategory && t(`categories.${selectedCategory}`)}</span>
              </div>
              <div className="sv-card-modal-rate">
                <span className="sv-card-modal-rate-value">
                  {(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}%
                </span>
                <span className="sv-card-modal-rate-label">{t('home.quickSelect.cashback')}</span>
              </div>
            </div>

            <p className="sv-card-modal-hint">
              <CreditCardOutlined /> {t('home.cardModal.hint')}
            </p>

            {Capacitor.isNativePlatform() && (
              <button className="sv-card-modal-wallet-btn" onClick={openWallet}>
                <WalletOutlined />
                {Capacitor.getPlatform() === 'ios' ? t('home.cardModal.openAppleWallet') : t('home.cardModal.openGooglePay')}
              </button>
            )}

            <Link
              to={`/cards/${bestCard.card.id}`}
              className="sv-card-modal-detail-link"
              onClick={() => setShowCardModal(false)}
            >
              {t('home.cardModal.viewDetails')} <ArrowRightOutlined />
            </Link>
          </div>
        </div>
      )}

      <style>{`
        /* Desktop: Bank link in hero area */
        .sv-home-cta-group {
          display: flex;
          align-items: flex-start;
          gap: 32px;
        }

        .sv-home-bank-group {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
        }

        .sv-home-bank-btn {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: transparent;
          color: #111827;
          padding: 15px 30px;
          border-radius: 12px;
          border: 2px solid #111827;
          font-size: 16px;
          font-weight: 600;
          text-decoration: none;
          transition: all 0.2s;
        }

        .sv-home-bank-btn:hover {
          background: #111827;
          color: white;
        }

        .sv-home-bank-meta {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding-left: 4px;
        }

        .sv-home-bank-security {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 12px;
          color: #059669;
        }

        .sv-home-bank-security .anticon {
          font-size: 11px;
        }

        .sv-home-bank-hint {
          font-size: 11px;
          color: #9ca3af;
        }

        /* Mobile: Bank connect section hidden on desktop */
        .sv-bank-connect {
          display: none;
        }

        @media (max-width: 640px) {
          /* Hide desktop bank button on mobile */
          .sv-home-bank-group {
            display: none;
          }

          .sv-home-cta-group {
            flex-direction: column;
            gap: 16px;
          }

          /* Show mobile bank connect section */
          .sv-bank-connect {
            display: block;
            text-align: center;
            padding: 40px 20px 100px;
          }

          .sv-bank-connect-title {
            font-size: 20px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
          }

          .sv-bank-connect-desc {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 12px;
          }

          .sv-bank-connect-demo {
            display: block;
            font-size: 12px;
            color: #d97706;
            background: #fef3c7;
            padding: 8px 14px;
            border-radius: 8px;
            margin: 0 auto 16px;
            max-width: fit-content;
          }

          .sv-bank-connect-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #111827;
            font-size: 15px;
            font-weight: 600;
            text-decoration: none;
            margin-bottom: 16px;
            transition: all 0.2s;
          }

          .sv-bank-connect-meta {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            font-size: 12px;
          }

          .sv-bank-connect-security {
            display: flex;
            align-items: flex-start;
            gap: 5px;
            color: #059669;
            text-align: left;
          }

          .sv-bank-connect-security .anticon {
            flex-shrink: 0;
            margin-top: 2px;
          }

          .sv-bank-connect-powered {
            color: #9ca3af;
          }

          .sv-bank-connect-powered strong {
            color: #6b7280;
          }
        }

        /* Dark mode */
        html.dark-mode .sv-home-bank-btn {
          color: #f5f5f5;
          border-color: #f5f5f5;
        }

        html.dark-mode .sv-home-bank-btn:hover {
          background: #f5f5f5;
          color: #111827;
        }

        html.dark-mode .sv-home-bank-security {
          color: #10b981;
        }

        html.dark-mode .sv-home-bank-hint {
          color: #6b7280;
        }

        html.dark-mode .sv-bank-connect-demo {
          background: #422006;
          color: #fbbf24;
        }

        html.dark-mode .sv-bank-connect-title {
          color: #f5f5f5;
        }

        html.dark-mode .sv-bank-connect-desc {
          color: #a0a0a0;
        }

        html.dark-mode .sv-bank-connect-link {
          color: #f5f5f5;
        }

        html.dark-mode .sv-bank-connect-security {
          color: #10b981;
        }

        html.dark-mode .sv-bank-connect-powered {
          color: #6b7280;
        }

        html.dark-mode .sv-bank-connect-powered strong {
          color: #a0a0a0;
        }

        /* Quick Result Card - clickable */
        .sv-quick-result {
          cursor: pointer;
          position: relative;
        }

        .sv-quick-result:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }

        .sv-quick-result:active {
          transform: translateY(0);
        }

        /* Card Modal */
        .sv-card-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .sv-card-modal {
          background: white;
          border-radius: 20px;
          padding: 24px;
          width: 100%;
          max-width: 360px;
          position: relative;
          animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .sv-card-modal-close {
          position: absolute;
          top: 16px;
          right: 16px;
          width: 32px;
          height: 32px;
          border: none;
          background: #f3f4f6;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6b7280;
          transition: all 0.2s;
        }

        .sv-card-modal-close:hover {
          background: #e5e7eb;
          color: #111827;
        }

        .sv-card-modal-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
          padding-right: 40px;
        }

        .sv-card-modal-logo {
          width: 48px;
          height: 48px;
          object-fit: contain;
          border-radius: 10px;
        }

        .sv-card-modal-title h3 {
          font-size: 18px;
          font-weight: 700;
          color: #111827;
          margin: 0 0 4px;
        }

        .sv-card-modal-title span {
          font-size: 14px;
          color: #6b7280;
        }

        .sv-card-modal-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .sv-card-modal-category {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 15px;
          color: #374151;
        }

        .sv-card-modal-category-icon {
          font-size: 20px;
        }

        .sv-card-modal-rate {
          text-align: right;
        }

        .sv-card-modal-rate-value {
          font-size: 24px;
          font-weight: 700;
          color: #059669;
        }

        .sv-card-modal-rate-label {
          display: block;
          font-size: 12px;
          color: #6b7280;
        }

        .sv-card-modal-hint {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #6b7280;
          margin-bottom: 20px;
          padding: 0 4px;
        }

        .sv-card-modal-hint .anticon {
          color: #9ca3af;
        }

        .sv-card-modal-wallet-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          background: #111827;
          color: white;
          padding: 14px 24px;
          border-radius: 12px;
          border: none;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin-bottom: 12px;
        }

        .sv-card-modal-wallet-btn:hover {
          background: #374151;
        }

        .sv-card-modal-detail-link {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          color: #6b7280;
          font-size: 14px;
          text-decoration: none;
          padding: 8px;
          transition: all 0.2s;
        }

        .sv-card-modal-detail-link:hover {
          color: #111827;
        }

        /* Dark mode modal */
        html.dark-mode .sv-card-modal {
          background: #1a1a1a;
        }

        html.dark-mode .sv-card-modal-close {
          background: #333;
          color: #a0a0a0;
        }

        html.dark-mode .sv-card-modal-close:hover {
          background: #444;
          color: #f5f5f5;
        }

        html.dark-mode .sv-card-modal-title h3 {
          color: #f5f5f5;
        }

        html.dark-mode .sv-card-modal-title span {
          color: #a0a0a0;
        }

        html.dark-mode .sv-card-modal-info {
          background: #252525;
        }

        html.dark-mode .sv-card-modal-category {
          color: #e5e5e5;
        }

        html.dark-mode .sv-card-modal-rate-value {
          color: #10b981;
        }

        html.dark-mode .sv-card-modal-rate-label {
          color: #a0a0a0;
        }

        html.dark-mode .sv-card-modal-hint {
          color: #a0a0a0;
        }

        html.dark-mode .sv-card-modal-wallet-btn {
          background: #f5f5f5;
          color: #111827;
        }

        html.dark-mode .sv-card-modal-wallet-btn:hover {
          background: #e5e5e5;
        }

        html.dark-mode .sv-card-modal-detail-link {
          color: #a0a0a0;
        }

        html.dark-mode .sv-card-modal-detail-link:hover {
          color: #f5f5f5;
        }
      `}</style>
    </div>
  )
}

export default HomePage
