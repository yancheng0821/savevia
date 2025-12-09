import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Spin } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { CheckOutlined, ArrowRightOutlined, DownOutlined, RightOutlined } from '@ant-design/icons'
import { cardApi, userApi } from '../services/api'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import type { CreditCard } from '../types'

// Card visual styles - EXACT match with database card names
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
  // Note: CIBC 'Aeroplan Visa Infinite' uses bank default color (same name as TD card)
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
  'Neo World Elite Mastercard': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', textColor: 'white' },
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
}

function getCardStyle(cardName: string, bankName: string) {
  // Try exact match first
  if (CARD_STYLES[cardName]) {
    return CARD_STYLES[cardName]
  }

  // Fallback based on bank with default colors
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

function CardsPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { selectedCards, addCard, removeCard, setSelectedCards } = useOptimizerStore()
  const { isAuthenticated } = useAuthStore()
  const [collapsedBanks, setCollapsedBanks] = useState<Record<string, boolean>>({})
  const [activeBank, setActiveBank] = useState<string | null>(null) // null = show all
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isInitialLoadRef = useRef(true)
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

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Spin size="large" />
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
      <h1 className="sv-cards-title" style={{
        fontSize: '42px',
        fontWeight: '700',
        color: '#111827',
        marginBottom: '48px',
        letterSpacing: '-1px'
      }}>
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
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                padding: '12px 0',
                borderBottom: '1px solid #f3f4f6',
                marginBottom: isCollapsed ? '0' : '16px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {isCollapsed ? (
                  <RightOutlined style={{ fontSize: '10px', color: '#9ca3af' }} />
                ) : (
                  <DownOutlined style={{ fontSize: '10px', color: '#9ca3af' }} />
                )}
                {BANK_LOGOS[bank] && (
                  <img
                    src={BANK_LOGOS[bank]}
                    alt={bank}
                    style={{ width: '24px', height: '24px', objectFit: 'contain', borderRadius: '4px' }}
                  />
                )}
                <span style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#111827',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  {bank}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: '#9ca3af'
                }}>
                  {t('cards.cardCount', { count: bankCards.length })}
                </span>
              </div>
              {selectedCount > 0 && (
                <span style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#111827',
                  background: '#f3f4f6',
                  padding: '4px 12px',
                  borderRadius: '20px'
                }}>
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
                const style = getCardStyle(card.name, bank)
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
                    {/* Selected checkmark */}
                    {selected && (
                      <div style={{
                        position: 'absolute',
                        top: '12px',
                        right: '12px',
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
                        letterSpacing: '0.5px'
                      }}>
                        {BANK_ABBR[bank] || bank.substring(0, 4).toUpperCase()}
                      </div>
                      {!selected && (
                        <span style={{
                          fontSize: '10px',
                          fontWeight: '600',
                          color: style.textColor,
                          opacity: 0.7
                        }}>
                          {card.annualFee === 0 ? 'NO FEE' : `$${card.annualFee}/yr`}
                        </span>
                      )}
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
                          textDecoration: 'none'
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

      {/* Fixed Bottom */}
      {selectedCards.length > 0 && (
        <div className="sv-cards-bottom-btn" style={{
          position: 'fixed',
          bottom: '32px',
          left: '50%',
          transform: 'translateX(-50%)'
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
              boxShadow: '0 4px 24px rgba(0,0,0,0.15)'
            }}
          >
            {t('cards.continueWith', { count: selectedCards.length })} <ArrowRightOutlined />
          </button>
        </div>
      )}
    </div>
  )
}

export default CardsPage
