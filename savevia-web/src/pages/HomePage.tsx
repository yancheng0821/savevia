import { useState, useMemo, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined, SafetyOutlined, CloseOutlined, WalletOutlined, CreditCardOutlined, AppleOutlined } from '@ant-design/icons'
import { Capacitor } from '@capacitor/core'

// Detect WeChat in-app browser on mobile only (not desktop WeChat)
const isWeChatMobile = (): boolean => {
  const ua = navigator.userAgent.toLowerCase()
  const isWeChat = ua.includes('micromessenger')
  const isMobile = /mobile|android|iphone|ipad|ipod/.test(ua)
  return isWeChat && isMobile
}
import { useAuthStore } from '../stores/useAuthStore'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useHomePageStore } from '../stores/useHomePageStore'
import { cardApi, userApi, bankApi, adminApi } from '../services/api'
import { getCardImageUrl } from '../utils/cardImages'
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
  'Brim': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
  'Wealthsimple': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
  'Desjardins': { gradient: 'linear-gradient(135deg, #00874e 0%, #005a34 100%)', textColor: 'white' },
  'Canadian Tire': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Vancity': { gradient: 'linear-gradient(135deg, #00874e 0%, #005a34 100%)', textColor: 'white' },
  'Meridian': { gradient: 'linear-gradient(135deg, #003168 0%, #001a3a 100%)', textColor: 'white' },
  'Coast Capital': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },
  'Walmart': { gradient: 'linear-gradient(135deg, #0071dc 0%, #004c9a 100%)', textColor: 'white' },
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

// Parse card style from imageUrl JSON or use fallback
function getCardStyle(card: CreditCard) {
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
  return BANK_FALLBACK_COLORS[card.bank] || DEFAULT_CARD_STYLE
}

// Get card number prefix based on card network
function getCardNumberPrefix(cardName: string): string {
  const name = cardName.toLowerCase()
  if (name.includes('visa')) {
    return '4XXX'
  } else if (name.includes('mastercard')) {
    return '52XX'
  } else if (name.includes('amex') || name.includes('cobalt') || name.includes('gold rewards') || name.includes('platinum') || name.includes('simplycash')) {
    return '37XX'
  }
  return '4XXX'
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
  LIQUOR: { icon: '🍷', color: '#7c2d12' },
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
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { isAuthenticated } = useAuthStore()
  const { selectedCards, setSelectedCards } = useOptimizerStore()

  // Use global store for modal and category state - persists across navigation
  const { showCardModal, setShowCardModal, selectedCategory, setSelectedCategory } = useHomePageStore()

  // Detect WeChat mobile browser (not desktop)
  const isWeChat = useMemo(() => isWeChatMobile(), [])

  // Track if modal is closing (for fade-out animation)
  const [isModalClosing, setIsModalClosing] = useState(false)

  // Real card images setting
  const [realCardImages, setRealCardImages] = useState(() => {
    const saved = localStorage.getItem('sv_realCardImages')
    return saved !== null ? saved === 'true' : true
  })
  const [cardImageError, setCardImageError] = useState(false)

  // Listen for storage changes (when setting is updated in MePage)
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('sv_realCardImages')
      setRealCardImages(saved !== null ? saved === 'true' : true)
    }
    window.addEventListener('storage', handleStorageChange)
    // Also check on focus (for same-tab updates)
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

  // Sync selectedCategory with localStorage on first mount
  useEffect(() => {
    if (selectedCategory === null) {
      try {
        const saved = localStorage.getItem('homePageSelectedCategory')
        if (saved) {
          setSelectedCategory(saved as SpendingCategory)
        }
      } catch {
        // Ignore
      }
    }
  }, [])

  const [hasBankConnection, setHasBankConnection] = useState(false)
  const [bankConnectionChecked, setBankConnectionChecked] = useState(false)
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

    // Track quick card finder usage (only when selecting, not deselecting)
    if (!isSelected) {
      adminApi.track('quick_card_finder')
    }
  }

  // Sync selectedCategory to localStorage whenever it changes
  useEffect(() => {
    if (selectedCategory) {
      localStorage.setItem('homePageSelectedCategory', selectedCategory)
    } else {
      localStorage.removeItem('homePageSelectedCategory')
    }
  }, [selectedCategory])


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

  // Reset card image error when bestCard changes
  useEffect(() => {
    setCardImageError(false)
  }, [bestCard?.card.id])

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

  // Handle card click - open modal
  const handleCardClick = () => {
    setShowCardModal(true)
  }

  // Handle view details click - fade out modal, then navigate
  const handleViewDetails = () => {
    // Save scroll position immediately before any animation
    // This is stored in window for App.tsx to read
    (window as any).__savedHomeScrollPosition = window.scrollY
    // Start fade-out animation
    setIsModalClosing(true)
    // After animation completes, close modal and navigate
    setTimeout(() => {
      setShowCardModal(false)
      setIsModalClosing(false)
      // Pass card data to avoid loading delay on detail page
      navigate(`/cards/${bestCard!.card.id}`, { state: { card: bestCard!.card } })
    }, 150)
  }

  return (
    <div className="sv-home-page" style={{ padding: '20px 0 60px', overflow: 'hidden' }}>
      {/* WeChat Browser Banner */}
      {isWeChat && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: 'calc(56px + env(safe-area-inset-top, 0px))',
          background: 'linear-gradient(135deg, #111827 0%, #1f2937 100%)',
          padding: '0 16px',
          paddingTop: 'env(safe-area-inset-top, 0px)',
          zIndex: 10000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          boxSizing: 'border-box'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
            <AppleOutlined style={{ fontSize: '20px', color: 'white', flexShrink: 0 }} />
            <span style={{ fontSize: '13px', color: 'white', lineHeight: 1.4 }}>
              {t('share.wechatTip')}
            </span>
          </div>
          <a
            href="https://apps.apple.com/app/id6756332569"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: '8px 16px',
              background: 'white',
              color: '#111827',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: '600',
              textDecoration: 'none',
              whiteSpace: 'nowrap',
              flexShrink: 0
            }}
          >
            {t('share.openAppStore')}
          </a>
        </div>
      )}

      {/* Hero - Asymmetric Layout */}
      <section className="sv-home-grid" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '60px',
        alignItems: 'center',
        minHeight: '55vh',
        marginBottom: '60px'
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
                transition: 'all 0.3s ease',
                whiteSpace: 'nowrap'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#1f2937'
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.15)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#111827'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
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
        <div className="sv-home-visual" style={{ position: 'relative', height: '400px', minHeight: '320px' }}>
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

      {/* Mobile Quick Select */}
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

          <Link
            to={isAuthenticated ? "/transactions" : "/me"}
            className="sv-bank-connect-link"
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#1f2937'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '#111827'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
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

      {/* Bottom Floating Result Card */}
      {canUseQuickSelect && (
        <div className={`sv-quick-result-float ${selectedCategory && bestCard ? 'visible' : ''}`}>
          {selectedCategory && bestCard && (
            <div className="sv-quick-result-float-inner">
              <div className="sv-quick-result-float-category">
                <span className="sv-quick-result-float-category-icon">
                  {CATEGORY_CONFIG[selectedCategory]?.icon}
                </span>
                <span className="sv-quick-result-float-category-text">
                  {t(`categories.${selectedCategory}`)}
                </span>
              </div>
              <div className="sv-quick-result-float-card" onClick={handleCardClick}>
                {BANK_LOGOS[bestCard.card.bank] && (
                  <img
                    src={BANK_LOGOS[bestCard.card.bank]}
                    alt={bestCard.card.bank}
                    className="sv-quick-result-float-logo"
                  />
                )}
                <div className="sv-quick-result-float-info">
                  <div className="sv-quick-result-float-name">{bestCard.card.name}</div>
                  <div className="sv-quick-result-float-bank">{bestCard.card.bank}</div>
                </div>
                <div className="sv-quick-result-float-rate">
                  <span className="sv-quick-result-float-rate-value">
                    {bestCard.card.rewardType === 'POINTS'
                      ? `${(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}X`
                      : `${(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}%`
                    }
                  </span>
                  <span className="sv-quick-result-float-rate-label">
                    {bestCard.card.rewardType === 'POINTS' ? t('home.quickSelect.points') : t('home.quickSelect.cashback')}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Card Detail Modal */}
      {showCardModal && bestCard && (() => {
        const cardStyle = getCardStyle(bestCard.card)
        const cardImageUrl = realCardImages && !cardImageError ? getCardImageUrl(bestCard.card.bank, bestCard.card.name) : null
        return (
        <div className={`sv-card-modal-overlay ${isModalClosing ? 'closing' : ''}`} onClick={() => setShowCardModal(false)}>
          <div className={`sv-card-modal ${isModalClosing ? 'closing' : ''}`} onClick={e => e.stopPropagation()}>
            <button className="sv-card-modal-close" onClick={() => setShowCardModal(false)}>
              <CloseOutlined />
            </button>

            {/* Card Visual Preview */}
            <div className="sv-card-modal-card-wrapper">
              <div
                className="sv-card-modal-card-visual"
                style={{
                  background: cardImageUrl ? 'transparent' : cardStyle.gradient,
                  color: cardStyle.textColor,
                  overflow: 'hidden'
                }}
              >
                {cardImageUrl ? (
                  <img
                    src={cardImageUrl}
                    alt={`${bestCard.card.bank} ${bestCard.card.name}`}
                    onError={() => setCardImageError(true)}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      borderRadius: '12px'
                    }}
                  />
                ) : (
                  <>
                    {/* Top row: bank abbr + annual fee */}
                    <div className="sv-card-modal-card-top">
                      <span className="sv-card-modal-card-bank">
                        {BANK_ABBR[bestCard.card.bank] || bestCard.card.bank.substring(0, 4).toUpperCase()}
                      </span>
                      <span className="sv-card-modal-card-fee">
                        {bestCard.card.annualFee === 0 ? t('cardDetail.noFee') : `$${bestCard.card.annualFee}${t('common.perYear')}`}
                      </span>
                    </div>
                    {/* Card name - middle */}
                    <div className="sv-card-modal-card-name">
                      {bestCard.card.name}
                    </div>
                    {/* Bottom row: card number */}
                    <div className="sv-card-modal-card-bottom">
                      <span className="sv-card-modal-card-number">
                        {getCardNumberPrefix(bestCard.card.name)} XXXX XXXX XXXX
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Category & Rate Row */}
            <div className="sv-card-modal-info-row">
              <div className="sv-card-modal-category-simple">
                <span>{selectedCategory && CATEGORY_CONFIG[selectedCategory]?.icon}</span>
                <span>{selectedCategory && t(`categories.${selectedCategory}`)}</span>
              </div>
              <div className="sv-card-modal-rate-simple">
                <span className="sv-card-modal-rate-value-simple">
                  {bestCard.card.rewardType === 'POINTS'
                    ? `${(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}X`
                    : `${(bestCard.rate * 100).toFixed(bestCard.rate * 100 % 1 === 0 ? 0 : 1)}%`
                  }
                </span>
                <span className="sv-card-modal-rate-label-simple">
                  {bestCard.card.rewardType === 'POINTS' ? t('home.quickSelect.points') : t('home.quickSelect.cashback')}
                </span>
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

            <button
              className="sv-card-modal-detail-link"
              onClick={handleViewDetails}
            >
              {t('home.cardModal.viewDetails')} <ArrowRightOutlined />
            </button>
          </div>
        </div>
        )
      })()}

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

        /* Hide bank group button - show bank connect section instead */
        .sv-home-bank-group {
          display: none;
        }

        /* Show bank connect section on all devices */
        .sv-bank-connect {
          display: block;
          text-align: center;
          padding: 40px 20px;
          max-width: 1200px;
          margin: 0 auto 48px;
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

        @media (max-width: 640px) {

          .sv-home-cta-group {
            flex-direction: column;
            gap: 16px;
          }

          /* Mobile bank connect section styling */
          .sv-bank-connect {
            padding: 40px 20px 100px;
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

        .sv-quick-result:active {
          opacity: 0.8;
          transform: scale(0.98);
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
          width: calc(100% - 40px);
          max-width: 360px;
          position: relative;
          animation: slideUp 0.3s ease;
        }

        @media (min-width: 641px) {
          .sv-card-modal {
            width: 100%;
            max-width: 560px;
            padding: 32px;
            border-radius: 24px;
          }
        }

        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        /* Closing animation */
        .sv-card-modal-overlay.closing {
          animation: fadeOut 0.15s ease forwards;
        }

        .sv-card-modal.closing {
          animation: slideDown 0.15s ease forwards;
        }

        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }

        @keyframes slideDown {
          from { transform: translateY(0); opacity: 1; }
          to { transform: translateY(20px); opacity: 0; }
        }

        .sv-card-modal-close {
          position: absolute;
          top: 16px;
          right: 6px;
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
          z-index: 10;
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

        @media (min-width: 641px) {
          .sv-card-modal-logo {
            width: 60px;
            height: 60px;
            border-radius: 12px;
          }
        }

        .sv-card-modal-title h3 {
          font-size: 18px;
          font-weight: 700;
          color: #111827;
          margin: 0 0 4px;
        }

        @media (min-width: 641px) {
          .sv-card-modal-title h3 {
            font-size: 22px;
          }
        }

        .sv-card-modal-title span {
          font-size: 14px;
          color: #6b7280;
        }

        @media (min-width: 641px) {
          .sv-card-modal-title span {
            font-size: 15px;
          }
        }

        /* Card Visual Preview */
        .sv-card-modal-card-wrapper {
          display: flex;
          justify-content: center;
          margin-bottom: 16px;
        }

        .sv-card-modal-card-visual {
          width: 100%;
          max-width: 260px;
          aspect-ratio: 1.586;
          border-radius: 12px;
          padding: 16px;
          position: relative;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        }

        @media (min-width: 641px) {
          .sv-card-modal-card-visual {
            max-width: 280px;
          }
        }

        .sv-card-modal-card-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .sv-card-modal-card-bank {
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.3px;
          opacity: 0.95;
        }

        .sv-card-modal-card-fee {
          font-size: 10px;
          font-weight: 600;
          opacity: 0.7;
        }

        .sv-card-modal-card-name {
          position: absolute;
          top: 45%;
          left: 16px;
          right: 16px;
          transform: translateY(-50%);
          font-size: 13px;
          font-weight: 600;
          line-height: 1.3;
        }

        .sv-card-modal-card-bottom {
          position: absolute;
          bottom: 14px;
          left: 16px;
          right: 16px;
        }

        .sv-card-modal-card-number {
          font-size: 10px;
          font-weight: 500;
          letter-spacing: 1px;
          opacity: 0.8;
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

        @media (min-width: 641px) {
          .sv-card-modal-info {
            padding: 20px;
            border-radius: 16px;
          }
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

        @media (min-width: 641px) {
          .sv-card-modal-rate-value {
            font-size: 32px;
          }
        }

        .sv-card-modal-rate-label {
          display: block;
          font-size: 12px;
          color: #6b7280;
        }

        @media (min-width: 641px) {
          .sv-card-modal-rate-label {
            font-size: 13px;
          }
        }

        /* Category & Rate Row - simple layout */
        .sv-card-modal-info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 4px;
          margin-bottom: 16px;
        }

        .sv-card-modal-category-simple {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 15px;
          color: #374151;
        }

        .sv-card-modal-rate-simple {
          text-align: right;
        }

        .sv-card-modal-rate-value-simple {
          font-size: 20px;
          font-weight: 700;
          color: #059669;
        }

        .sv-card-modal-rate-label-simple {
          display: block;
          font-size: 12px;
          color: #6b7280;
        }

        html.dark-mode .sv-card-modal-category-simple {
          color: #e5e7eb;
        }

        html.dark-mode .sv-card-modal-rate-label-simple {
          color: #9ca3af;
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

        @media (min-width: 641px) {
          .sv-card-modal-hint {
            font-size: 14px;
            margin-bottom: 24px;
          }
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

        @media (min-width: 641px) {
          .sv-card-modal-wallet-btn {
            padding: 16px 28px;
            font-size: 17px;
          }
        }

        .sv-card-modal-wallet-btn:hover {
          background: #374151;
        }

        @media (min-width: 641px) {
          .sv-card-modal-wallet-btn:hover {
            background: #1f2937;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
          }
        }

        .sv-card-modal-detail-link {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          color: #6b7280;
          font-size: 14px;
          text-decoration: none;
          padding: 12px 8px;
          transition: all 0.2s;
          background: none;
          border: none;
          cursor: pointer;
          font-family: inherit;
          width: 100%;
        }

        @media (min-width: 641px) {
          .sv-card-modal-detail-link {
            font-size: 15px;
            padding: 10px;
          }
        }

        .sv-card-modal-detail-link:active {
          opacity: 0.7;
          transform: scale(0.98);
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

        html.dark-mode .sv-card-modal-detail-link:active {
          opacity: 0.7;
          transform: scale(0.98);
        }

        /* Bottom Floating Result Card */
        .sv-quick-result-float {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          z-index: 9997;
          padding: 0 16px 16px 16px;
          pointer-events: none;
          transform: translateY(100%);
          opacity: 0;
          transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.25s ease;
        }

        /* Mobile: position above bottom nav bar */
        @media (max-width: 640px) {
          .sv-quick-result-float {
            bottom: calc(77px + env(safe-area-inset-bottom, 0px));
            padding: 0 20px 0 20px;
          }

          .sv-quick-result-float-inner {
            width: calc(100% - 40px);
            max-width: 360px;
            margin: 0 auto;
          }
        }

        .sv-quick-result-float.visible {
          transform: translateY(0);
          opacity: 1;
          pointer-events: auto;
        }

        .sv-quick-result-float-inner {
          max-width: 480px;
          margin: 0 auto;
          background: white;
          border-radius: 12px;
          padding: 10px 12px;
          box-shadow: 0 2px 16px rgba(0, 0, 0, 0.1), 0 4px 24px rgba(0, 0, 0, 0.06);
          transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .sv-quick-result-float-card {
          cursor: pointer;
        }

        .sv-quick-result-float-card:active {
          opacity: 0.8;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float {
            padding: 0 24px 24px 24px;
          }

          .sv-quick-result-float-inner {
            max-width: 560px;
            padding: 16px 20px;
            border-radius: 20px;
            box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.12), 0 8px 32px rgba(0, 0, 0, 0.08);
          }

          .sv-quick-result-float-inner:hover {
            box-shadow: 0 -6px 32px rgba(0, 0, 0, 0.15), 0 12px 40px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
          }

          .sv-quick-result-float-inner:active {
            transform: scale(1) translateY(-2px);
          }
        }

        .sv-quick-result-float-category {
          display: none;
        }

        .sv-quick-result-float-category-icon {
          font-size: 16px;
        }

        .sv-quick-result-float-category-text {
          font-size: 12px;
          font-weight: 600;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .sv-quick-result-float-card {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-card {
            gap: 12px;
          }
        }

        .sv-quick-result-float-logo {
          width: 32px;
          height: 32px;
          object-fit: contain;
          border-radius: 6px;
          flex-shrink: 0;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-logo {
            width: 48px;
            height: 48px;
            border-radius: 10px;
          }
        }

        .sv-quick-result-float-info {
          flex: 1;
          min-width: 0;
        }

        .sv-quick-result-float-name {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-name {
            font-size: 16px;
          }
        }

        .sv-quick-result-float-bank {
          font-size: 11px;
          color: #9ca3af;
          margin-top: 1px;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-bank {
            font-size: 12px;
            margin-top: 2px;
          }
        }

        .sv-quick-result-float-rate {
          text-align: center;
          flex-shrink: 0;
        }

        .sv-quick-result-float-rate-value {
          font-size: 18px;
          font-weight: 700;
          color: #059669;
          line-height: 1;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-rate-value {
            font-size: 26px;
          }
        }

        .sv-quick-result-float-rate-label {
          display: block;
          font-size: 9px;
          color: #9ca3af;
          margin-top: 1px;
        }

        @media (min-width: 641px) {
          .sv-quick-result-float-rate-label {
            font-size: 10px;
            margin-top: 2px;
          }
        }

        /* Dark mode floating result */
        html.dark-mode .sv-quick-result-float-inner {
          background: #1a1a1a;
          box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.3), 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        html.dark-mode .sv-quick-result-float-name {
          color: #f5f5f5;
        }

        html.dark-mode .sv-quick-result-float-bank {
          color: #6b7280;
        }

        html.dark-mode .sv-quick-result-float-rate-value {
          color: #10b981;
        }

        html.dark-mode .sv-quick-result-float-arrow {
          color: #6b7280;
        }
      `}</style>
    </div>
  )
}

export default HomePage
