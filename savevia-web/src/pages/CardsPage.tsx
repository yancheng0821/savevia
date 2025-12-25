import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import Loading from '../components/Loading'
import { useTranslation } from 'react-i18next'
import { CheckOutlined, ArrowRightOutlined, DownOutlined, RightOutlined, VerticalAlignTopOutlined, VerticalAlignBottomOutlined } from '@ant-design/icons'
import { cardApi, userApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import { useCardsPageStore } from '../stores/useCardsPageStore'
import type { CreditCard } from '../types'

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

// Bank logos/abbreviations
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

// Bank logo paths (local files)
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
  // Default to Visa for unknown
  return '4XXX'
}

// Sync read from localStorage to get scroll position before hydration
const getStoredScrollPosition = (): number => {
  try {
    const stored = localStorage.getItem('sv-cards-page-storage')
    if (stored) {
      const parsed = JSON.parse(stored)
      return parsed.state?.scrollPosition || 0
    }
  } catch {
    // Ignore errors
  }
  return 0
}

function CardsPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { selectedCards, addCard, removeCard, setSelectedCards } = useOptimizerStore()
  const { isAuthenticated } = useAuthStore()
  const { activeBank, setActiveBank, scrollPosition, setScrollPosition } = useCardsPageStore()
  const [collapsedBanks, setCollapsedBanks] = useState<Record<string, boolean>>({})
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isInitialLoadRef = useRef(true)
  // Get initial scroll position from localStorage synchronously to prevent flicker
  const initialScrollPosition = useRef(getStoredScrollPosition())
  // Initialize to true if we need to restore scroll - prevents early scroll events from resetting position
  const isRestoringScrollRef = useRef(initialScrollPosition.current > 0)
  const tabsRef = useRef<HTMLDivElement>(null)

  const toggleBank = (bank: string) => {
    setCollapsedBanks(prev => ({ ...prev, [bank]: !prev[bank] }))
  }

  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: cardApi.getAll,
  })

  // Auto-save with debounce
  const debouncedSave = useCallback((cardIds: number[]) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        await userApi.saveUserCards(cardIds)
      } catch (error) {
        console.error('Auto-save failed:', error)
      }
    }, 1000)
  }, [])

  // Load user's saved cards when authenticated
  useEffect(() => {
    const loadUserCards = async () => {
      if (isAuthenticated && cards && cards.length > 0) {
        try {
          const response = await userApi.getUserCards()
          if (response.code === 200 && response.data && response.data.length > 0) {
            const savedCardIds = response.data
            const savedCards = cards.filter(c => savedCardIds.includes(c.id))
            if (savedCards.length > 0) {
              setSelectedCards(savedCards)
            }
          }
        } catch (error) {
          console.error('Failed to load user cards:', error)
        }
      }
      isInitialLoadRef.current = false
    }
    loadUserCards()
  }, [isAuthenticated, cards, setSelectedCards])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])


  const isSelected = (cardId: number) => selectedCards.some((c) => c.id === cardId)

  const handleCardToggle = (card: CreditCard) => {
    let newCardIds: number[]
    if (isSelected(card.id)) {
      removeCard(card.id)
      newCardIds = selectedCards.filter(c => c.id !== card.id).map(c => c.id)
    } else {
      addCard(card)
      newCardIds = [...selectedCards.map(c => c.id), card.id]
    }
    // Auto-save if authenticated
    if (isAuthenticated && !isInitialLoadRef.current) {
      debouncedSave(newCardIds)
    }
  }

  const handleContinue = () => {
    if (selectedCards.length > 0) {
      navigate('/optimizer')
    }
  }

  // Restore scroll position on mount using the synchronously read value
  useEffect(() => {
    const storedPosition = initialScrollPosition.current
    if (storedPosition > 0) {
      // Restore scroll position immediately
      window.scrollTo(0, storedPosition)
      // Mark restoration complete after scroll settles
      setTimeout(() => {
        isRestoringScrollRef.current = false
      }, 100)
    } else {
      isRestoringScrollRef.current = false
    }
  }, []) // Only run on mount

  // Monitor scroll position and save in real-time
  useEffect(() => {
    const handleScroll = () => {
      // Skip updating during scroll restoration
      if (isRestoringScrollRef.current) return
      const newScrollY = window.scrollY
      // Don't save near-zero positions - prevents losing scroll position when
      // App.tsx ScrollToTop scrolls to 0 during navigation to detail page
      if (newScrollY > 50) {
        setScrollPosition(newScrollY)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [setScrollPosition])

  // Scroll to top
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Scroll to bottom
  const scrollToBottom = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    })
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Loading size="large" />
      </div>
    )
  }

  const groupedCards = cards?.reduce(
    (acc, card) => {
      if (!acc[card.bank]) {
        acc[card.bank] = []
      }
      acc[card.bank].push(card)
      return acc
    },
    {} as Record<string, CreditCard[]>
  )

  // Get list of banks for tabs
  const banks = groupedCards ? Object.keys(groupedCards) : []

  // Filter cards based on active bank (mobile only uses this)
  const filteredGroupedCards = activeBank && groupedCards
    ? { [activeBank]: groupedCards[activeBank] }
    : groupedCards

  return (
    <div style={{ paddingBottom: '120px' }}>
      {/* Header */}
      <h1 className="sv-cards-title">
        {t('cards.title')}
      </h1>

      {/* Mobile Bank Tabs */}
      <div className="sv-bank-tabs-wrapper">
        <div className="sv-bank-tabs" ref={tabsRef}>
          <button
            className={`sv-bank-tab ${activeBank === null ? 'active' : ''}`}
            onClick={() => setActiveBank(null)}
          >
            <span className="sv-bank-tab-icon sv-bank-tab-icon-all">
              <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                <path d="M3 4h4v4H3V4zm5 0h4v4H8V4zm5 0h4v4h-4V4zM3 9h4v4H3V9zm5 0h4v4H8V9zm5 0h4v4h-4V9z"/>
              </svg>
            </span>
            <span className="sv-bank-tab-name">{t('cards.all')}</span>
          </button>
          {banks.map((bank) => {
            const logoUrl = BANK_LOGOS[bank]
            const selectedCount = groupedCards?.[bank]?.filter(c => isSelected(c.id)).length || 0
            return (
              <button
                key={bank}
                className={`sv-bank-tab ${activeBank === bank ? 'active' : ''}`}
                onClick={() => setActiveBank(bank)}
              >
                <img className="sv-bank-tab-icon" src={logoUrl} alt={bank} />
                <span className="sv-bank-tab-name">{BANK_ABBR[bank] || bank}</span>
                {selectedCount > 0 && (
                  <span className="sv-bank-tab-badge">{selectedCount}</span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Cards Grid */}
      {filteredGroupedCards &&
        Object.entries(filteredGroupedCards).map(([bank, bankCards]) => {
          const isCollapsed = collapsedBanks[bank]
          const selectedCount = bankCards.filter(c => isSelected(c.id)).length
          return (
          <div key={bank} style={{ marginBottom: '32px' }}>
            <div
              onClick={() => toggleBank(bank)}
              className="sv-cards-bank-header"
              style={{ marginBottom: isCollapsed ? '0' : '16px' }}
            >
              <div className="sv-cards-bank-left">
                {isCollapsed ? (
                  <RightOutlined className="sv-cards-bank-arrow" />
                ) : (
                  <DownOutlined className="sv-cards-bank-arrow" />
                )}
                {BANK_LOGOS[bank] && (
                  <img
                    src={BANK_LOGOS[bank]}
                    alt={bank}
                    className="sv-cards-bank-logo"
                  />
                )}
                <span className="sv-cards-bank-name">
                  {bank}
                </span>
                <span className="sv-cards-bank-count">
                  {t('cards.cardCount', { count: bankCards.length })}
                </span>
              </div>
              {selectedCount > 0 && (
                <span className="sv-cards-selected-badge">
                  {t('cards.selectedCount', { count: selectedCount })}
                </span>
              )}
            </div>
            {!isCollapsed && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: '16px'
            }}>
              {bankCards.map((card) => {
                const style = getCardStyle(card)
                const selected = isSelected(card.id)
                return (
                  <div
                    key={card.id}
                    onClick={() => handleCardToggle(card)}
                    style={{
                      position: 'relative',
                      aspectRatio: '1.586',
                      background: style.gradient,
                      borderRadius: '12px',
                      padding: '16px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      transform: selected ? 'translateY(-4px)' : 'scale(1)',
                      boxShadow: selected
                        ? '0 12px 40px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.1)'
                        : '0 2px 12px rgba(0,0,0,0.1)',
                      overflow: 'hidden'
                    }}
                  >
                    {/* Selected checkmark - positioned at top left */}
                    {selected && (
                      <div style={{
                        position: 'absolute',
                        top: '12px',
                        left: '12px',
                        width: '24px',
                        height: '24px',
                        background: 'white',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 10,
                        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                      }}>
                        <CheckOutlined style={{ color: '#059669', fontSize: '12px' }} />
                      </div>
                    )}

                    {/* Top row: bank + annual fee */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start'
                    }}>
                      <div style={{
                        fontSize: '16px',
                        fontWeight: '800',
                        color: style.textColor,
                        letterSpacing: '0.5px',
                        marginLeft: selected ? '32px' : '0',
                        transition: 'margin-left 0.2s ease'
                      }}>
                        {BANK_ABBR[bank] || bank.substring(0, 4).toUpperCase()}
                      </div>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: '600',
                        color: style.textColor,
                        opacity: 0.7
                      }}>
                        {card.annualFee === 0 ? 'NO FEE' : `$${card.annualFee}/yr`}
                      </span>
                    </div>

                    {/* Card name - middle */}
                    <div style={{
                      position: 'absolute',
                      top: '45%',
                      left: '16px',
                      right: '16px',
                      transform: 'translateY(-50%)',
                      fontSize: '13px',
                      fontWeight: '600',
                      color: style.textColor,
                      lineHeight: '1.3'
                    }}>
                      {card.name}
                    </div>

                    {/* Bottom row: card number + details link */}
                    <div style={{
                      position: 'absolute',
                      bottom: '14px',
                      left: '16px',
                      right: '16px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: '500',
                        color: style.textColor,
                        opacity: 0.5,
                        letterSpacing: '1.5px'
                      }}>
                        {getCardNumberPrefix(card.name)} •••• •••• ••••
                      </span>
                      <Link
                        to={`/cards/${card.id}`}
                        state={{ card }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          fontSize: '11px',
                          fontWeight: '600',
                          color: style.textColor,
                          opacity: 0.7,
                          textDecoration: 'none',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = '1'
                          e.currentTarget.style.transform = 'translateX(2px)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = '0.7'
                          e.currentTarget.style.transform = 'translateX(0)'
                        }}
                      >
                        {t('cards.details')} →
                      </Link>
                    </div>
                  </div>
                )
              })}
            </div>
            )}
          </div>
          );
        })}

      {/* Fixed Bottom - Continue button */}
      {selectedCards.length > 0 && (
        <div className="sv-cards-bottom-btn" style={{
          position: 'fixed',
          bottom: '32px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 20
        }}>
          <button
            onClick={handleContinue}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              background: '#111827',
              color: 'white',
              padding: '16px 32px',
              borderRadius: '50px',
              fontSize: '15px',
              fontWeight: '600',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#1f2937'
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#111827'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 24px rgba(0,0,0,0.15)'
            }}
          >
            {t('cards.continueWith', { count: selectedCards.length })} <ArrowRightOutlined />
          </button>
        </div>
      )}

      {/* Scroll to Top/Bottom Buttons - Use sync-read value before hydration, store value after */}
      {(scrollPosition > 300 || (scrollPosition === 0 && initialScrollPosition.current > 300)) && (
        <div
          className="sv-scroll-buttons"
          style={{
            position: 'fixed',
            right: '16px',
            bottom: selectedCards.length > 0 ? '110px' : '90px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            zIndex: 20
          }}
        >
        <button
          onClick={scrollToTop}
          className="sv-scroll-btn"
          title={t('common.scrollTop') || 'Scroll to top'}
        >
          <VerticalAlignTopOutlined />
        </button>
        <button
          onClick={scrollToBottom}
          className="sv-scroll-btn"
          title={t('common.scrollBottom') || 'Scroll to bottom'}
        >
          <VerticalAlignBottomOutlined />
        </button>
        </div>
      )}
    </div>
  )
}

export default CardsPage
