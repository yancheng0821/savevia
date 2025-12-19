import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { cardApi } from '../services/api'
import type { OptimizationResult, CreditCard, SpendingCategory } from '../types'

interface CardUpgradeRecommendationProps {
  result: OptimizationResult
  selectedCardIds: number[]
  monthlySpending: Partial<Record<SpendingCategory, number>>
  compact?: boolean
}

interface CardUpgradeOpportunity {
  card: CreditCard
  categoriesImproved: string[]
  annualSavings: number
  currentRate: number
  newRate: number
}

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

// Bank fallback colors for card style (matching CardsPage)
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
  'Wealthsimple': { gradient: 'linear-gradient(135deg, #5b21b6 0%, #3f0f63 100%)', textColor: 'white' },
  'Desjardins': { gradient: 'linear-gradient(135deg, #004b87 0%, #003056 100%)', textColor: 'white' },
  'Canadian Tire': { gradient: 'linear-gradient(135deg, #c60c30 0%, #8b0820 100%)', textColor: 'white' },
  'Vancity': { gradient: 'linear-gradient(135deg, #1a5f3f 0%, #0d3d24 100%)', textColor: 'white' },
  'Meridian': { gradient: 'linear-gradient(135deg, #003087 0%, #001a50 100%)', textColor: 'white' },
  'Coast Capital': { gradient: 'linear-gradient(135deg, #0055b8 0%, #003a85 100%)', textColor: 'white' },
  'Walmart': { gradient: 'linear-gradient(135deg, #0071ce 0%, #004d96 100%)', textColor: 'white' },
}

const DEFAULT_CARD_STYLE = { gradient: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)', textColor: 'white' }

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

function CardUpgradeRecommendation({
  result,
  selectedCardIds,
  monthlySpending,
  compact = false
}: CardUpgradeRecommendationProps) {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [bestRecommendation, setBestRecommendation] = useState<CardUpgradeOpportunity | null>(null)

  const { data: allCards } = useQuery({
    queryKey: ['cards'],
    queryFn: () => cardApi.getAll(),
  })

  // Calculate the best upgrade opportunity
  useEffect(() => {
    if (!allCards || allCards.length === 0 || !result) {
      setBestRecommendation(null)
      return
    }

    // Filter cards that user doesn't have
    const unselectedCards = allCards.filter(card => !selectedCardIds.includes(card.id))

    if (unselectedCards.length === 0) {
      setBestRecommendation(null)
      return
    }

    // For each unselected card, calculate potential savings
    const opportunities = unselectedCards.map(newCard => {
      let totalCurrentReward = 0
      let totalNewReward = 0
      let totalNewFees = 0
      const categoriesImproved: string[] = []

      // For each spending category, check if new card provides better rewards
      result.recommendations.forEach(rec => {
        const monthlySpendAmount = monthlySpending[rec.category] || rec.monthlySpend || 0

        // Recalculate current reward based on actual spending (using rec.rewardRate which is the best rate from current cards)
        const currentMonthlyReward = monthlySpendAmount * rec.rewardRate

        totalCurrentReward += currentMonthlyReward

        // Find matching reward rule for new card
        const matchingRule = newCard.rewardRules.find(rule => rule.category === rec.category)
        const newCardMonthlyReward = matchingRule ? monthlySpendAmount * matchingRule.rewardRate : 0

        if (newCardMonthlyReward > currentMonthlyReward) {
          // New card is better for this category - add the extra reward
          totalNewReward += newCardMonthlyReward

          if (!categoriesImproved.includes(rec.category)) {
            categoriesImproved.push(rec.category)
          }
        } else {
          // Keep current reward
          totalNewReward += currentMonthlyReward
        }
      })

      // Add annual fees
      totalNewFees = newCard.annualFee || 0

      // Calculate annual savings difference
      const currentAnnualReward = totalCurrentReward * 12
      const newAnnualReward = totalNewReward * 12
      const currentTotalFees = result.totalAnnualFees
      const newTotalFees = currentTotalFees + totalNewFees

      const currentNetSavings = currentAnnualReward - currentTotalFees
      const newNetSavings = newAnnualReward - newTotalFees
      const annualSavingsDifference = newNetSavings - currentNetSavings

      // Calculate overall reward rate
      const totalSpending = Object.values(monthlySpending).reduce((a, b) => a + (b || 0), 0)
      const currentRate = totalSpending > 0 ? (totalCurrentReward * 12) / (totalSpending * 12) : 0
      const newRate = totalSpending > 0 ? (totalNewReward * 12) / (totalSpending * 12) : 0

      return {
        card: newCard,
        categoriesImproved,
        annualSavings: annualSavingsDifference,
        currentRate,
        newRate,
      }
    })

    // Sort by annual savings and filter positive opportunities
    const positiveOpportunities = opportunities.filter(opp => opp.annualSavings > 1) // At least $1 annual savings

    if (positiveOpportunities.length > 0) {
      positiveOpportunities.sort((a, b) => b.annualSavings - a.annualSavings)
      setBestRecommendation(positiveOpportunities[0])
    } else {
      setBestRecommendation(null)
    }
  }, [allCards, selectedCardIds, result, monthlySpending])

  if (!bestRecommendation) {
    return null
  }

  const card = bestRecommendation.card
  const bankLogo = BANK_LOGOS[card.bank]
  const rateIncrease = ((bestRecommendation.newRate - bestRecommendation.currentRate) * 100).toFixed(2)

  if (compact) {
    // Card face style version matching CardsPage
    const style = getCardStyle(card)

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Recommendation label */}
        <div style={{
          fontSize: '12px',
          fontWeight: '600',
          color: '#6b7280',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          💳 {t('result.recommendedCard') || 'Recommended Card'}
        </div>

        {/* Card face - matching CardsPage style */}
        <div
          onClick={() => navigate(`/cards/${card.id}`, { state: { card } })}
          style={{
            position: 'relative',
            aspectRatio: '1.586',
            background: style.gradient,
            borderRadius: '12px',
            padding: '16px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
            overflow: 'hidden'
          }}
        >
          {/* Top row: bank logo/abbr + annual fee */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              {bankLogo && (
                <img
                  src={bankLogo}
                  alt={card.bank}
                  style={{
                    width: '24px',
                    height: '24px',
                    objectFit: 'contain',
                    borderRadius: '4px'
                  }}
                />
              )}
              <div style={{
                fontSize: '14px',
                fontWeight: '800',
                color: style.textColor,
                letterSpacing: '0.5px'
              }}>
                {BANK_ABBR[card.bank] || card.bank.substring(0, 4).toUpperCase()}
              </div>
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
            top: '40%',
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

          {/* Bottom row: key metrics */}
          <div style={{
            position: 'absolute',
            bottom: '12px',
            left: '16px',
            right: '16px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ fontSize: '9px', color: style.textColor, opacity: 0.8, fontWeight: '500' }}>
                {t('result.rewardRateIncrease') || 'Rate Increase'}
              </div>
              <div style={{ fontSize: '12px', fontWeight: '700', color: style.textColor }}>
                +{rateIncrease}%
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', textAlign: 'right' }}>
              <div style={{ fontSize: '9px', color: style.textColor, opacity: 0.8, fontWeight: '500' }}>
                {t('result.annualSavings') || 'Annual Savings'}
              </div>
              <div style={{ fontSize: '12px', fontWeight: '700', color: style.textColor }}>
                +${bestRecommendation.annualSavings.toFixed(0)}
              </div>
            </div>
          </div>
        </div>

        {/* Info text below card */}
        {bestRecommendation.categoriesImproved.length > 0 && (
          <div style={{
            fontSize: '12px',
            color: '#6b7280',
            lineHeight: '1.4',
            padding: '0 4px'
          }}>
            <span style={{ fontWeight: '500' }}>{t('result.bestFor') || 'Best for'}:</span>
            {' '}
            {bestRecommendation.categoriesImproved.map((cat, idx) => (
              <span key={cat}>
                {idx > 0 && ', '}
                {t(`categories.${cat}`) || cat}
              </span>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{
      marginBottom: '48px'
    }}>
      {/* Header */}
      <h2 className="sv-result-section-title">
        {t('result.recommendedCard') || 'Recommended Card'}
      </h2>

      {/* Card Item - matching quick reference style */}
      <div className="sv-result-rec-item">
        <div className="sv-result-rec-row">
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            {bankLogo && (
              <img
                src={bankLogo}
                alt={card.bank}
                style={{ width: '32px', height: '32px', objectFit: 'contain', borderRadius: '8px', flexShrink: 0, marginTop: '2px' }}
              />
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: '15px',
                fontWeight: '600',
                color: '#111827',
                marginBottom: '4px'
              }}>
                {card.name}
              </div>
              <div style={{
                fontSize: '13px',
                color: '#6b7280',
                marginBottom: '6px'
              }}>
                {card.bank}
              </div>

              {/* Benefits grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                marginBottom: '8px'
              }}>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    marginBottom: '2px',
                    fontWeight: '500'
                  }}>
                    {t('result.rewardRateIncrease') || 'Rate Increase'}
                  </div>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: '700',
                    color: '#059669'
                  }}>
                    +{rateIncrease}%
                  </div>
                </div>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    marginBottom: '2px',
                    fontWeight: '500'
                  }}>
                    {t('result.annualSavings') || 'Savings/Year'}
                  </div>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: '700',
                    color: '#059669'
                  }}>
                    +${bestRecommendation.annualSavings.toFixed(0)}
                  </div>
                </div>
              </div>

              {/* Categories improved */}
              {bestRecommendation.categoriesImproved.length > 0 && (
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  <span style={{ fontWeight: '500' }}>{t('result.bestFor') || 'Best for'}: </span>
                  {bestRecommendation.categoriesImproved.slice(0, 2).map((cat, idx) => (
                    <span key={cat}>
                      {idx > 0 && ', '}
                      {t(`categories.${cat}`) || cat}
                    </span>
                  ))}
                  {bestRecommendation.categoriesImproved.length > 2 && (
                    <span> +{bestRecommendation.categoriesImproved.length - 2}</span>
                  )}
                </div>
              )}

              {/* Annual fee */}
              {card.annualFee > 0 && (
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  marginTop: '4px'
                }}>
                  {t('cards.annualFee') || 'Annual Fee'}: ${card.annualFee}/yr
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Action button */}
        <div style={{ paddingLeft: '44px', paddingTop: '8px' }}>
          <button
            onClick={() => navigate(`/cards/${card.id}`, { state: { card } })}
            className="sv-result-btn-secondary"
            style={{ padding: '4px 0' }}
          >
            {t('result.viewCardDetails') || 'View Card Details'} <ArrowRightOutlined style={{ fontSize: '12px' }} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default CardUpgradeRecommendation
