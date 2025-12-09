import { useParams, useNavigate, Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { Capacitor } from '@capacitor/core'
import { ArrowLeftOutlined, CheckCircleOutlined, ClockCircleOutlined, DollarOutlined, CreditCardOutlined } from '@ant-design/icons'
import { cardApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import type { SpendingCategory, CreditCard } from '../types'

// Swipe back gesture for Android only (iOS uses native gesture)
function useAndroidSwipeBack(onSwipeBack: () => void) {
  const touchStartX = useRef(0)
  const touchStartY = useRef(0)
  const isSwiping = useRef(false)

  useEffect(() => {
    // Only enable on Android
    if (Capacitor.getPlatform() !== 'android') return

    const handleTouchStart = (e: TouchEvent) => {
      const startX = e.touches[0].clientX
      touchStartX.current = startX
      touchStartY.current = e.touches[0].clientY
      isSwiping.current = startX < 30
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!isSwiping.current) return
      const deltaY = Math.abs(e.touches[0].clientY - touchStartY.current)
      if (deltaY > 30) isSwiping.current = false
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (!isSwiping.current) return
      const deltaX = e.changedTouches[0].clientX - touchStartX.current
      if (deltaX > 80) onSwipeBack()
      isSwiping.current = false
    }

    document.addEventListener('touchstart', handleTouchStart, { passive: true })
    document.addEventListener('touchmove', handleTouchMove, { passive: true })
    document.addEventListener('touchend', handleTouchEnd, { passive: true })

    return () => {
      document.removeEventListener('touchstart', handleTouchStart)
      document.removeEventListener('touchmove', handleTouchMove)
      document.removeEventListener('touchend', handleTouchEnd)
    }
  }, [onSwipeBack])
}

// Card visual styles - EXACT match with CardsPage.tsx
const CARD_STYLES: Record<string, { gradient: string; textColor: string }> = {
  // AMEX Cards (bank: 'AMEX')
  'Cobalt Card': { gradient: 'linear-gradient(135deg, #5b4b9e 0%, #3d3270 100%)', textColor: 'white' },
  'Gold Rewards Card': { gradient: 'linear-gradient(135deg, #c9a227 0%, #9a7b1c 100%)', textColor: '#1a1a1a' },
  'Platinum Card': { gradient: 'linear-gradient(135deg, #e5e4e2 0%, #c0c0c0 100%)', textColor: '#1a1a1a' },
  'SimplyCash Preferred': { gradient: 'linear-gradient(135deg, #016fd0 0%, #0055a5 100%)', textColor: 'white' },
  'SimplyCash': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'Aeroplan Card': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'Aeroplan Reserve Card': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: '#c0c0c0' },

  // TD Cards (bank: 'TD')
  'Cash Back Visa Infinite': { gradient: 'linear-gradient(135deg, #34a853 0%, #1e7e34 100%)', textColor: 'white' },
  'First Class Visa Infinite': { gradient: 'linear-gradient(135deg, #2c3e2d 0%, #1a261b 100%)', textColor: '#c5a572' },
  'Aeroplan Visa Infinite': { gradient: 'linear-gradient(135deg, #34a853 0%, #1e7e34 100%)', textColor: 'white' },
  'Aeroplan Visa Infinite Privilege': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)', textColor: '#34a853' },
  'Cash Back Visa': { gradient: 'linear-gradient(135deg, #34a853 0%, #2d8a45 100%)', textColor: 'white' },

  // RBC Cards (bank: 'RBC')
  'Avion Visa Infinite': { gradient: 'linear-gradient(135deg, #003168 0%, #001a3a 100%)', textColor: 'white' },
  'Avion Visa Infinite Privilege': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)', textColor: '#ffd700' },
  'WestJet World Elite Mastercard': { gradient: 'linear-gradient(135deg, #00a651 0%, #007a3d 100%)', textColor: 'white' },
  'Cash Back Mastercard': { gradient: 'linear-gradient(135deg, #0051a5 0%, #003a75 100%)', textColor: 'white' },
  'ION Visa': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5521b5 100%)', textColor: 'white' },

  // Scotiabank Cards (bank: 'Scotiabank')
  'Gold American Express': { gradient: 'linear-gradient(135deg, #c9a227 0%, #9a7b1c 100%)', textColor: '#1a1a1a' },
  'Passport Visa Infinite': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: '#c0c0c0' },
  'Momentum Visa Infinite': { gradient: 'linear-gradient(135deg, #ec111a 0%, #b30d14 100%)', textColor: 'white' },
  'Scene+ Visa': { gradient: 'linear-gradient(135deg, #ec111a 0%, #c70d14 100%)', textColor: 'white' },

  // CIBC Cards (bank: 'CIBC')
  'Aventura Visa Infinite': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)', textColor: '#c9a227' },
  'Aventura Visa Infinite Privilege': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)', textColor: '#ffd700' },
  'Dividend Visa Infinite': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: '#c0c0c0' },
  'Costco Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #005daa 100%)', textColor: 'white' },

  // BMO Cards (bank: 'BMO')
  'Eclipse Visa Infinite': { gradient: 'linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%)', textColor: '#a78bfa' },
  'CashBack World Elite Mastercard': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },
  'Air Miles World Elite Mastercard': { gradient: 'linear-gradient(135deg, #0079c1 0%, #004a73 100%)', textColor: 'white' },
  'CashBack Mastercard': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },

  // Rogers Cards (bank: 'Rogers')
  'World Elite Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Platinum Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #c41530 100%)', textColor: 'white' },

  // Tangerine Cards (bank: 'Tangerine')
  'Money-Back Credit Card': { gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)', textColor: 'white' },
  'World Mastercard': { gradient: 'linear-gradient(135deg, #ff6600 0%, #e65c00 100%)', textColor: 'white' },

  // Neo Financial Cards (bank: 'Neo')
  'Neo Mastercard': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', textColor: 'white' },
  'Neo World Mastercard': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)', textColor: 'white' },

  // PC Financial Cards (bank: 'PC Financial')
  'PC World Elite Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'PC World Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #c41530 100%)', textColor: 'white' },

  // Simplii Financial Cards (bank: 'Simplii')
  'Cash Back Visa Card': { gradient: 'linear-gradient(135deg, #ff6600 0%, #e65c00 100%)', textColor: 'white' },

  // MBNA Cards (bank: 'MBNA')
  'Rewards World Elite Mastercard': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
  'True Line Gold Mastercard': { gradient: 'linear-gradient(135deg, #c9a227 0%, #9a7b1c 100%)', textColor: '#1a1a1a' },

  // National Bank Cards (bank: 'National Bank')
  'National Bank World Elite Mastercard': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },

  // Home Trust Cards (bank: 'Home Trust')
  'Preferred Visa': { gradient: 'linear-gradient(135deg, #1e3a5f 0%, #152a45 100%)', textColor: 'white' },

  // Default
  'default': { gradient: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)', textColor: 'white' },
}

// Bank abbreviations
const BANK_ABBR: Record<string, string> = {
  'TD': 'TD',
  'RBC': 'RBC',
  'Scotiabank': 'Scotia',
  'CIBC': 'CIBC',
  'BMO': 'BMO',
  'American Express': 'AMEX',
  'AMEX': 'AMEX',
  'Rogers': 'Rogers',
  'Tangerine': 'Tang',
  'Neo': 'Neo',
  'PC Financial': 'PC',
  'Simplii': 'Simplii',
  'MBNA': 'MBNA',
  'National Bank': 'NBC',
  'Home Trust': 'HT',
}

// Bank logos
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


// Category icons
const CATEGORY_ICONS: Record<SpendingCategory, string> = {
  DINING: '🍽️',
  GROCERY: '🛒',
  GAS: '⛽',
  TRAVEL: '✈️',
  STREAMING: '📺',
  TRANSIT: '🚇',
  PHARMACY: '💊',
  RENT: '🏠',
  RECURRING: '🔄',
  ONLINE_SHOPPING: '📦',
  FOREIGN: '🌍',
  OTHER: '💳',
}

function getCardStyle(cardName: string, bankName: string) {
  if (CARD_STYLES[cardName]) {
    return CARD_STYLES[cardName]
  }
  const bankColors: Record<string, { gradient: string; textColor: string }> = {
    'AMEX': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
    'TD': { gradient: 'linear-gradient(135deg, #34a853 0%, #1e7e34 100%)', textColor: 'white' },
    'RBC': { gradient: 'linear-gradient(135deg, #003168 0%, #001a3a 100%)', textColor: 'white' },
    'Scotiabank': { gradient: 'linear-gradient(135deg, #ec111a 0%, #b30d14 100%)', textColor: 'white' },
    'CIBC': { gradient: 'linear-gradient(135deg, #8b1538 0%, #6b1029 100%)', textColor: 'white' },
    'BMO': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },
    'Rogers': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
    'Tangerine': { gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)', textColor: 'white' },
    'Neo': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', textColor: 'white' },
    'PC Financial': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
    'Simplii': { gradient: 'linear-gradient(135deg, #ff6600 0%, #e65c00 100%)', textColor: 'white' },
    'MBNA': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
    'National Bank': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
    'Home Trust': { gradient: 'linear-gradient(135deg, #1e3a5f 0%, #152a45 100%)', textColor: 'white' },
  }
  return bankColors[bankName] || CARD_STYLES['default']
}

function CardDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const { selectedCards, addCard, removeCard } = useOptimizerStore()

  // Get card from router state if available (passed from CardsPage)
  const passedCard = (location.state as { card?: CreditCard })?.card

  // Android swipe back gesture
  const handleSwipeBack = useCallback(() => navigate(-1), [navigate])
  useAndroidSwipeBack(handleSwipeBack)

  const { data: fetchedCard, isLoading, error } = useQuery({
    queryKey: ['card', id],
    queryFn: () => cardApi.getById(Number(id)),
    enabled: !!id && !passedCard, // Skip fetch if we have card from state
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  })

  // Use passed card if available, otherwise use fetched card
  const card = passedCard || fetchedCard

  // Only show loading if we don't have a passed card and are still fetching
  if (isLoading && !passedCard) {
    return (
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        paddingBottom: '100px'
      }}>
        {/* Back button placeholder */}
        <div style={{ height: '40px', marginBottom: '24px' }} />
        {/* Card placeholder - same structure as real card */}
        <div style={{
          position: 'relative',
          aspectRatio: '1.586',
          maxWidth: '400px',
          margin: '0 auto 32px',
          background: 'linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%)',
          borderRadius: '20px',
          padding: '24px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.1)'
        }} />
        {/* Card info placeholder */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: '#e5e7eb' }} />
              <div>
                <div style={{ width: '180px', height: '24px', background: '#e5e7eb', borderRadius: '4px', marginBottom: '8px' }} />
                <div style={{ width: '80px', height: '14px', background: '#e5e7eb', borderRadius: '4px' }} />
              </div>
            </div>
            <div style={{ width: '70px', height: '32px', background: '#e5e7eb', borderRadius: '20px' }} />
          </div>
        </div>
      </div>
    )
  }

  if (error || !card) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
        <h2 style={{ color: '#111827', marginBottom: '8px' }}>{t('cardDetail.notFound')}</h2>
        <p style={{ color: '#6b7280', marginBottom: '24px' }}>{t('cardDetail.notFoundDesc')}</p>
        <Link to="/cards" style={{ color: '#059669', fontWeight: '600' }}>
          <ArrowLeftOutlined /> {t('cardDetail.backToCards')}
        </Link>
      </div>
    )
  }

  const style = getCardStyle(card.name, card.bank)
  const isSelected = selectedCards.some(c => c.id === card.id)
  const hasNoFxFee = card.noFxFee === true

  const handleToggleCard = () => {
    if (isSelected) {
      removeCard(card.id)
    } else {
      addCard(card)
    }
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      paddingBottom: '100px'
    }}>
      {/* Back Button - hidden on mobile (use swipe gesture) */}
      <button
        className="sv-card-detail-back"
        onClick={() => navigate(-1)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'none',
          border: 'none',
          color: '#6b7280',
          fontSize: '14px',
          fontWeight: '500',
          cursor: 'pointer',
          padding: '8px 0',
          marginBottom: '24px'
        }}
      >
        <ArrowLeftOutlined /> {t('common.back')}
      </button>

      {/* Card Visual */}
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '400px',
        height: '252px',
        margin: '0 auto 32px',
        background: style.gradient,
        borderRadius: '20px',
        padding: '24px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
        color: style.textColor
      }}>
        {/* Bank Name */}
        <div style={{
          fontSize: '20px',
          fontWeight: '800',
          letterSpacing: '0.5px'
        }}>
          {BANK_ABBR[card.bank] || card.bank}
        </div>

        {/* Card Name */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '24px',
          right: '24px',
          transform: 'translateY(-50%)',
          fontSize: '16px',
          fontWeight: '600',
          lineHeight: '1.3'
        }}>
          {card.name}
        </div>

        {/* Card Type Badge */}
        <div style={{
          position: 'absolute',
          bottom: '24px',
          left: '24px',
          fontSize: '11px',
          fontWeight: '600',
          opacity: 0.8
        }}>
          {card.cardType}
        </div>

        {/* Annual Fee */}
        <div style={{
          position: 'absolute',
          top: '24px',
          right: '24px',
          fontSize: '12px',
          fontWeight: '600',
          opacity: 0.8
        }}>
          {card.annualFee === 0 ? t('cardDetail.noFee') : `$${card.annualFee}${t('common.perYear')}`}
        </div>
      </div>

      {/* Card Info */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              background: '#f3f4f6',
              flexShrink: 0
            }}>
              {BANK_LOGOS[card.bank] && (
                <img
                  src={BANK_LOGOS[card.bank]}
                  alt={card.bank}
                  loading="eager"
                  decoding="sync"
                  style={{ width: '32px', height: '32px', objectFit: 'contain', borderRadius: '6px' }}
                />
              )}
            </div>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: 0 }}>
                {card.name}
              </h1>
              <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>{card.bank}</p>
            </div>
          </div>
          <button
            onClick={handleToggleCard}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              padding: '8px 16px',
              borderRadius: '20px',
              fontSize: '13px',
              fontWeight: '600',
              border: 'none',
              cursor: 'pointer',
              background: isSelected ? '#f3f4f6' : '#111827',
              color: isSelected ? '#374151' : 'white',
              whiteSpace: 'nowrap',
              flexShrink: 0
            }}
          >
            {isSelected ? (
              <>
                <CheckCircleOutlined style={{ color: '#059669' }} />
                {t('cardDetail.added')}
              </>
            ) : (
              <>+ {t('cardDetail.add')}</>
            )}
          </button>
        </div>

        {/* Tags */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '16px' }}>
          {card.annualFee === 0 && (
            <span style={{
              background: '#ecfdf5',
              color: '#059669',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {t('cardDetail.noAnnualFee')}
            </span>
          )}
          {hasNoFxFee && (
            <span style={{
              background: '#eff6ff',
              color: '#2563eb',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {t('cardDetail.noFxFee')}
            </span>
          )}
          <span style={{
            background: '#f3f4f6',
            color: '#374151',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            {(card.baseRewardRate * 100).toFixed(1)}% {t('cardDetail.baseRate')}
          </span>
        </div>
      </div>

      {/* Signup Bonus */}
      {card.signupBonus && (
        <div style={{
          marginBottom: '24px'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#9ca3af',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '12px'
          }}>
            {t('cardDetail.welcomeBonus')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '12px' }}>
            {typeof card.signupBonus.bonusAmount === 'number' && card.signupBonus.bonusAmount > 1000
              ? `${card.signupBonus.bonusAmount.toLocaleString()} ${t('cardDetail.points')}`
              : `$${card.signupBonus.bonusAmount}`}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '13px', color: '#6b7280' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <DollarOutlined /> {t('cardDetail.minSpend')}: ${card.signupBonus.minSpend.toLocaleString()}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ClockCircleOutlined /> {card.signupBonus.daysToComplete} {t('cardDetail.days')}
            </span>
          </div>
          {card.signupBonus.description && (
            <p style={{ fontSize: '13px', color: '#6b7280', marginTop: '12px', marginBottom: 0 }}>
              {card.signupBonus.description}
            </p>
          )}
        </div>
      )}

      {/* Reward Rules */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px'
        }}>
          {t('cardDetail.rewardRates')}
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {card.rewardRules.length > 0 ? (
            card.rewardRules.map((rule, index) => (
              <div
                key={rule.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 0',
                  borderBottom: index < card.rewardRules.length - 1 ? '1px solid rgba(0,0,0,0.06)' : 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '20px' }}>{CATEGORY_ICONS[rule.category]}</span>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                      {t(`categories.${rule.category}`)}
                    </div>
                    {rule.description && (
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                        {rule.description}
                      </div>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '18px', fontWeight: '700', color: '#059669' }}>
                    {(rule.rewardRate * 100).toFixed(0)}%
                  </div>
                  {rule.monthlyCapAmount && (
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>
                      {t('cardDetail.capAmount', { amount: rule.monthlyCapAmount })}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{
              padding: '20px 0',
              textAlign: 'center',
              color: '#6b7280'
            }}>
              <CreditCardOutlined style={{ fontSize: '24px', marginBottom: '8px', display: 'block' }} />
              {(card.baseRewardRate * 100).toFixed(1)}% {t('cardDetail.onAllPurchases')}
            </div>
          )}
        </div>
      </div>

      {/* Apply URL */}
      {card.applyUrl && (
        <a
          href={card.applyUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'block',
            textAlign: 'center',
            padding: '14px',
            background: '#f3f4f6',
            borderRadius: '12px',
            color: '#374151',
            fontSize: '14px',
            fontWeight: '600',
            textDecoration: 'none',
            marginBottom: '16px'
          }}
        >
          {t('cardDetail.applyNow')} →
        </a>
      )}

    </div>
  )
}

export default CardDetailPage
