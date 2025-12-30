import { useParams, useNavigate, Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef, useCallback, useState, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Capacitor } from '@capacitor/core'
import { ArrowLeftOutlined, CheckCircleOutlined, ClockCircleOutlined, DollarOutlined } from '@ant-design/icons'
import { cardApi, affiliateApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import type { SpendingCategory, CreditCard, TipType } from '../types'
import { getCardImageUrl } from '../utils/cardImages'

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

// Default card style fallback
const DEFAULT_CARD_STYLE = { gradient: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)', textColor: 'white' }

// Bank fallback colors (used when imageUrl is not set)
const BANK_FALLBACK_COLORS: Record<string, { gradient: string; textColor: string }> = {
  'AMEX': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'American Express': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
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
  'Brim': 'Brim',
  'Wealthsimple': 'WS',
  'Desjardins': 'Desj',
  'Canadian Tire': 'CT',
  'Vancity': 'Vancity',
  'Meridian': 'Merid',
  'Coast Capital': 'Coast',
  'Walmart': 'Walmart',
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
  'Brim': '/logos/brim.png',
  'Wealthsimple': '/logos/wealthsimple.png',
  'Desjardins': '/logos/desjardins.png',
  'Canadian Tire': '/logos/canadiantire.png',
  'Vancity': '/logos/vancity.png',
  'Meridian': '/logos/meridian.png',
  'Coast Capital': '/logos/coastcapital.png',
  'Walmart': '/logos/walmart.png',
}

// Category icons
const CATEGORY_ICONS: Record<SpendingCategory, string> = {
  // Core categories
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
  // Extended categories
  RETAIL: '🛍️',
  ENTERTAINMENT: '🎬',
  PERSONAL_SERVICES: '💇',
  HOME_IMPROVEMENT: '🔨',
  WHOLESALE: '🏪',
  INSURANCE: '📋',
  TELECOM: '📱',
  EV_CHARGING: '⚡',
  LIQUOR: '🍷',
  // Catch-all
  OTHER: '💳',
}

// Format reward rate based on card type (POINTS shows "Xx", CASHBACK shows "X%")
function formatRewardRate(rate: number, rewardType?: 'CASHBACK' | 'POINTS'): string {
  const value = rate * 100
  // Smart formatting: show minimum necessary decimal places (0, 1, or 2)
  let formatted: string
  if (value % 1 === 0) {
    formatted = value.toFixed(0)  // e.g., 1, 2, 3
  } else if ((value * 10) % 1 === 0) {
    formatted = value.toFixed(1)  // e.g., 1.5, 2.5
  } else {
    formatted = value.toFixed(2)  // e.g., 1.25, 1.75
  }

  return rewardType === 'POINTS' ? `${formatted}x` : `${formatted}%`
}

// Parse card style from imageUrl JSON or use fallback
function getCardStyle(card: CreditCard) {
  // Try to parse imageUrl as JSON with gradient/textColor
  if (card.imageUrl) {
    try {
      const parsed = JSON.parse(card.imageUrl)
      if (parsed.gradient && parsed.textColor) {
        return { gradient: parsed.gradient, textColor: parsed.textColor }
      }
    } catch {
      // Not JSON, ignore
    }
  }
  // Fallback to bank colors
  return BANK_FALLBACK_COLORS[card.bank] || DEFAULT_CARD_STYLE
}

// Usage Guide Tabs Component
function UsageGuideTabs({ usageGuide, t }: { usageGuide: any; t: any }) {
  const typeIcons: Record<TipType, string> = {
    BEST_USE: '💡',
    REDEMPTION: '🎁',
    TRAVEL_BENEFIT: '✈️',
    INSURANCE: '🛡️',
    PERK: '🎉',
    STACKING: '🔗',
    AVOID: '⚠️',
    TRANSFER_PARTNER: '🔄'
  }

  // Build available tabs from usage guide data
  const availableTabs = useMemo(() => {
    if (!usageGuide) return []

    const tabs: { key: string; label: string; icon: string }[] = []
    const typeOrder: TipType[] = ['BEST_USE', 'REDEMPTION', 'TRAVEL_BENEFIT', 'INSURANCE', 'PERK', 'STACKING', 'AVOID']

    if (usageGuide.tips && usageGuide.tips.length > 0) {
      const tipsByType = usageGuide.tips.reduce((acc: Record<string, any[]>, tip: any) => {
        if (!acc[tip.tipType]) acc[tip.tipType] = []
        acc[tip.tipType].push(tip)
        return acc
      }, {})

      typeOrder.forEach(tipType => {
        if (tipsByType[tipType] && tipsByType[tipType].length > 0) {
          tabs.push({
            key: tipType,
            label: t(`cardDetail.usageGuide.tipTypes.${tipType}`),
            icon: typeIcons[tipType]
          })
        }
      })
    }

    if (usageGuide.transferPartners && usageGuide.transferPartners.length > 0) {
      tabs.push({
        key: 'TRANSFER_PARTNER',
        label: t('cardDetail.usageGuide.transferPartners'),
        icon: '🔄'
      })
    }

    return tabs
  }, [usageGuide, t])

  const [activeTab, setActiveTab] = useState<string>('')

  // Set initial active tab when availableTabs changes
  useEffect(() => {
    if (availableTabs.length > 0 && !activeTab) {
      setActiveTab(availableTabs[0].key)
    }
  }, [availableTabs, activeTab])

  if (!usageGuide || availableTabs.length === 0) return null

  const tipsByType = usageGuide.tips?.reduce((acc: Record<string, any[]>, tip: any) => {
    if (!acc[tip.tipType]) acc[tip.tipType] = []
    acc[tip.tipType].push(tip)
    return acc
  }, {}) || {}

  return (
    <div className="sv-card-detail-usage-guide">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h2 className="sv-card-detail-section-title" style={{ margin: 0 }}>
          {t('cardDetail.usageGuide.title')}
        </h2>
        <span style={{
          fontSize: '11px',
          color: '#9ca3af',
          fontStyle: 'italic'
        }}>
          {t('cardDetail.usageGuide.disclaimer')}
        </span>
      </div>

      {/* Tab Navigation */}
      <div className="sv-usage-guide-tabs">
        {availableTabs.map(tab => (
          <button
            key={tab.key}
            className={`sv-usage-guide-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            <span className="sv-usage-guide-tab-icon">{tab.icon}</span>
            <span className="sv-usage-guide-tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="sv-usage-guide-tab-content">
        {activeTab === 'TRANSFER_PARTNER' ? (
          // Transfer Partners content
          <div className="sv-card-detail-partners-list">
            {usageGuide.transferPartners?.map((partner: any, idx: number) => (
              <div key={idx} className="sv-card-detail-partner-tag">
                <span className="sv-card-detail-partner-tag-name">{partner.name}</span>
                <span className="sv-card-detail-partner-tag-ratio sv-highlight-number">{partner.ratio}</span>
              </div>
            ))}
          </div>
        ) : (
          // Tips content
          <div className="sv-card-detail-tip-list">
            {tipsByType[activeTab]?.map((tip: any) => (
              <div key={tip.id} className="sv-card-detail-tip-entry">
                <div className="sv-card-detail-tip-entry-title">{tip.title}</div>
                {tip.content && (
                  <div className="sv-card-detail-tip-entry-content">{tip.content}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// Card Visual Component with image loading and fallback
function CardVisual({ card, style, t, realCardImages }: { card: CreditCard; style: { gradient: string; textColor: string }; t: any; realCardImages: boolean }) {
  const [imageError, setImageError] = useState(false)
  const cardImageUrl = realCardImages ? getCardImageUrl(card.bank, card.name) : null

  // Reset error state when card changes
  useEffect(() => {
    setImageError(false)
  }, [card.id])

  // Show image if available and not failed
  if (cardImageUrl && !imageError) {
    return (
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '400px',
        margin: '0 auto 32px',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
        // Gradient as loading placeholder
        background: style.gradient,
        aspectRatio: '1.586'
      }}>
        <img
          src={cardImageUrl}
          alt={`${card.bank} ${card.name}`}
          loading="eager"
          onError={() => setImageError(true)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block',
          }}
        />
        {/* Full overlay to soften the card image */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0,0,0,0.05)',
          borderRadius: '16px',
          zIndex: 2
        }} />
      </div>
    )
  }

  // Fallback: gradient card style
  return (
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
  )
}

function CardDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { t, i18n } = useTranslation()
  // Get base language code (e.g., 'zh' from 'zh-CN')
  const lang = i18n.language?.split('-')[0] || 'en'
  const { selectedCards, addCard, removeCard } = useOptimizerStore()
  const { user } = useAuthStore()

  // Real card images setting
  const [realCardImages, setRealCardImages] = useState(() => {
    const saved = localStorage.getItem('sv_realCardImages')
    return saved !== null ? saved === 'true' : true
  })

  // Listen for storage changes (when setting is updated in MePage)
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('sv_realCardImages')
      setRealCardImages(saved !== null ? saved === 'true' : true)
    }
    window.addEventListener('storage', handleStorageChange)
    const handleFocus = () => {
      const saved = localStorage.getItem('sv_realCardImages')
      setRealCardImages(saved !== null ? saved === 'true' : true)
    }
    window.addEventListener('focus', handleFocus)
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleFocus)
    }
  }, [])

  // Get card from router state if available (passed from CardsPage)
  const passedCard = (location.state as { card?: CreditCard })?.card

  // Android swipe back gesture
  const handleSwipeBack = useCallback(() => navigate(-1), [navigate])
  useAndroidSwipeBack(handleSwipeBack)

  // 处理申卡链接点击
  const handleApplyClick = useCallback(async (card: CreditCard) => {
    try {
      // 异步追踪点击，不阻塞用户跳转
      if (card.affiliateLink?.id) {
        affiliateApi.trackClick(
          Number(card.id),
          Number(card.affiliateLink.id),
          card.bank,
          user?.id
        ).catch(err => console.error('Failed to track click:', err))
      }

      // 获取联盟链接或使用原始 applyUrl
      let applyUrl = card.applyUrl

      if (card.affiliateLink?.affiliateUrl) {
        applyUrl = card.affiliateLink.affiliateUrl
      }

      if (applyUrl) {
        window.open(applyUrl, '_blank', 'noopener,noreferrer')
      }
    } catch (error) {
      console.error('Error in apply click:', error)
      // 如果追踪失败，仍然打开链接
      if (card.applyUrl) {
        window.open(card.applyUrl, '_blank', 'noopener,noreferrer')
      }
    }
  }, [user?.id])

  const { data: fetchedCard, isLoading, error } = useQuery({
    queryKey: ['card', id],
    queryFn: () => cardApi.getById(Number(id)),
    enabled: !!id && !passedCard, // Skip fetch if we have card from state
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  })

  // Fetch usage guide
  const { data: usageGuide } = useQuery({
    queryKey: ['cardUsageGuide', id, lang],
    queryFn: () => cardApi.getUsageGuide(Number(id), lang),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
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

  const style = getCardStyle(card)
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

      {/* Card Visual - with image or gradient fallback */}
      <CardVisual card={card} style={style} t={t} realCardImages={realCardImages} />

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
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '16px', alignItems: 'center' }}>
          {/* Annual fee tag - green for no fee, gray for has fee */}
          <span style={{
            background: card.annualFee === 0 ? '#ecfdf5' : '#f3f4f6',
            color: card.annualFee === 0 ? '#059669' : '#374151',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            {card.annualFee === 0 ? t('cardDetail.noAnnualFee') : `$${card.annualFee}${t('common.perYear')}`}
          </span>
          {hasNoFxFee && (
            <span style={{
              background: '#f3f4f6',
              color: '#374151',
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
            {t(card.rewardType === 'POINTS' ? 'cardDetail.pointsCard' : 'cardDetail.cashbackCard')}
          </span>
          {/* Update time - pushed to the right */}
          <span style={{
            marginLeft: 'auto',
            color: '#9ca3af',
            fontSize: '11px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <ClockCircleOutlined style={{ fontSize: '10px' }} />
            {t('cardDetail.lastUpdated')}: {card.updatedAt
              ? new Date(card.updatedAt).toLocaleDateString(lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : lang === 'ko' ? 'ko-KR' : 'en-CA', { year: 'numeric', month: 'short' })
              : new Date().toLocaleDateString(lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : lang === 'ko' ? 'ko-KR' : 'en-CA', { year: 'numeric', month: 'short' })}
          </span>
        </div>
      </div>

      {/* Signup Bonus */}
      {card.signupBonus && (
        <div className="sv-card-detail-bonus">
          <div className="sv-card-detail-section-title">
            {t('cardDetail.welcomeBonus')}
          </div>
          <div className="sv-card-detail-bonus-amount">
            {typeof card.signupBonus.bonusAmount === 'number' && card.signupBonus.bonusAmount > 1000
              ? `${card.signupBonus.bonusAmount.toLocaleString()} ${t('cardDetail.points')}`
              : `$${card.signupBonus.bonusAmount}`}
          </div>
          <div className="sv-card-detail-bonus-meta">
            <span>
              <DollarOutlined /> {t('cardDetail.minSpend')}: ${card.signupBonus.minSpend.toLocaleString()}
            </span>
            <span>
              <ClockCircleOutlined /> {card.signupBonus.daysToComplete} {t('cardDetail.days')}
            </span>
          </div>
          {(card.signupBonus.descriptionI18n || card.signupBonus.description) && (
            <p className="sv-card-detail-bonus-desc">
              {card.signupBonus.descriptionI18n
                ? (card.signupBonus.descriptionI18n[lang] || card.signupBonus.descriptionI18n['en'])
                : card.signupBonus.description}
            </p>
          )}
        </div>
      )}

      {/* Reward Rules */}
      <div className="sv-card-detail-rules">
        <h2 className="sv-card-detail-section-title">
          {t(card.rewardType === 'POINTS' ? 'cardDetail.rewardRatesPoints' : 'cardDetail.rewardRatesCashback')}
        </h2>
        <div className="sv-card-detail-rules-list">
          {card.rewardRules.map((rule) => (
            <div
              key={rule.id}
              className="sv-card-detail-rule-item"
              style={{
                borderBottom: '1px solid var(--border-color, rgba(0,0,0,0.06))'
              }}
            >
              <div className="sv-card-detail-rule-left">
                <span style={{ fontSize: '20px' }}>{CATEGORY_ICONS[rule.category]}</span>
                <div>
                  <div className="sv-card-detail-rule-category">
                    {t(`categories.${rule.category}`)}
                  </div>
                  {rule.description && (
                    <div className="sv-card-detail-rule-desc">
                      {rule.description}
                    </div>
                  )}
                </div>
              </div>
              <div className="sv-card-detail-rule-right">
                <div className="sv-card-detail-rule-rate">
                  {formatRewardRate(rule.rewardRate, card.rewardType)}
                </div>
                {rule.monthlyCapAmount && (
                  <div className="sv-card-detail-rule-cap">
                    {t('cardDetail.capAmount', { amount: rule.monthlyCapAmount })}
                  </div>
                )}
              </div>
            </div>
          ))}
          {/* Amex Travel Online bonus - only show if card has this benefit */}
          {card.amexTravelBonusRate && card.amexTravelBonusRate > 0 && (
            <div className="sv-card-detail-rule-item" style={{ borderBottom: '1px solid var(--border-color, rgba(0,0,0,0.06))' }}>
              <div className="sv-card-detail-rule-left">
                <span style={{ fontSize: '20px' }}>🌐</span>
                <div>
                  <div className="sv-card-detail-rule-category">
                    {t('cardDetail.amexTravelOnline')}
                  </div>
                  <div className="sv-card-detail-rule-desc">
                    {t('cardDetail.amexTravelOnlineDesc')}
                  </div>
                </div>
              </div>
              <div className="sv-card-detail-rule-right">
                <div className="sv-card-detail-rule-rate">
                  +{formatRewardRate(card.amexTravelBonusRate, card.rewardType)}
                </div>
              </div>
            </div>
          )}
          {/* OTHER category - base reward rate for all other purchases (always last) */}
          <div className="sv-card-detail-rule-item">
            <div className="sv-card-detail-rule-left">
              <span style={{ fontSize: '20px' }}>{CATEGORY_ICONS['OTHER']}</span>
              <div>
                <div className="sv-card-detail-rule-category">
                  {t('categories.OTHER')}
                </div>
              </div>
            </div>
            <div className="sv-card-detail-rule-right">
              <div className="sv-card-detail-rule-rate">
                {formatRewardRate(card.baseRewardRate, card.rewardType)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Usage Guide with Tabs */}
      <UsageGuideTabs usageGuide={usageGuide} t={t} />

      {/* Apply URL */}
      {(card.applyUrl || card.affiliateLink?.affiliateUrl) && (
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault()
            handleApplyClick(card)
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#e5e7eb'
            e.currentTarget.style.color = '#1f2937'
            e.currentTarget.style.transform = 'translateY(-2px)'
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#f3f4f6'
            e.currentTarget.style.color = '#374151'
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = 'none'
          }}
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
            marginBottom: '16px',
            transition: 'all 0.3s ease',
            cursor: 'pointer'
          }}
        >
          {t('cardDetail.applyNow')} →
        </a>
      )}

    </div>
  )
}

export default CardDetailPage
