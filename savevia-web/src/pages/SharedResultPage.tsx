import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined, DownOutlined } from '@ant-design/icons'
import { optimizerApi } from '../services/api'
import type { OptimizationResult, SpendingCategory } from '../types'

// Category emoji mapping
const CATEGORY_ICONS: Record<string, string> = {
  // Daily Essentials
  'DINING': '🍽️',
  'GROCERY': '🛒',
  'PHARMACY': '💊',
  // Transportation
  'GAS': '⛽',
  'TRANSIT': '🚇',
  'EV_CHARGING': '⚡',
  // Shopping
  'RETAIL': '🛍️',
  'ONLINE_SHOPPING': '📦',
  'WHOLESALE': '🏪',
  'HOME_IMPROVEMENT': '🔨',
  // Bills & Services
  'RENT': '🏠',
  'RECURRING': '🔄',
  'TELECOM': '📱',
  'INSURANCE': '📋',
  'STREAMING': '📺',
  // Lifestyle
  'TRAVEL': '✈️',
  'ENTERTAINMENT': '🎬',
  'PERSONAL_SERVICES': '💇',
  'FOREIGN': '🌍',
  // Catch-all
  'OTHER': '💳',
}

// Category order for sorting results
const CATEGORY_ORDER: string[] = [
  // Daily Essentials
  'DINING', 'GROCERY', 'PHARMACY',
  // Transportation
  'GAS', 'TRANSIT', 'EV_CHARGING',
  // Shopping
  'RETAIL', 'ONLINE_SHOPPING', 'WHOLESALE', 'HOME_IMPROVEMENT',
  // Bills & Services
  'RENT', 'RECURRING', 'TELECOM', 'INSURANCE', 'STREAMING',
  // Lifestyle
  'TRAVEL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'FOREIGN',
  // Other
  'OTHER',
]

// Sort recommendations by category order
const sortByCategory = <T extends { category: string | SpendingCategory }>(items: T[]): T[] => {
  return [...items].sort((a, b) => {
    const indexA = CATEGORY_ORDER.indexOf(String(a.category))
    const indexB = CATEGORY_ORDER.indexOf(String(b.category))
    // If not found in order, put at end
    const orderA = indexA === -1 ? 999 : indexA
    const orderB = indexB === -1 ? 999 : indexB
    return orderA - orderB
  })
}

// Bank logo paths - include all variations
const BANK_LOGOS: Record<string, string> = {
  'TD': '/logos/td.png',
  'RBC': '/logos/rbc.png',
  'Scotiabank': '/logos/scotiabank.png',
  'CIBC': '/logos/cibc.png',
  'BMO': '/logos/bmo.png',
  'American Express': '/logos/amex.png',
  'AMEX': '/logos/amex.png',
  'Amex': '/logos/amex.png',
  'Rogers': '/logos/rogers.png',
  'Tangerine': '/logos/tangerine.png',
  'Neo': '/logos/neo.png',
  'PC Financial': '/logos/pc.png',
  'Simplii': '/logos/simplii.png',
  'MBNA': '/logos/mbna.png',
  'National Bank': '/logos/nationalbank.png',
  'Home Trust': '/logos/hometrust.png',
  'Desjardins': '/logos/desjardins.png',
  'HSBC': '/logos/hsbc.png',
  'Manulife': '/logos/manulife.png',
  'ATB': '/logos/atb.png',
  'Canadian Tire': '/logos/canadiantire.png',
  'Laurentian': '/logos/laurentian.png',
}

// Helper to safely get number value from potentially BigDecimal object
const toNumber = (value: unknown): number => {
  if (typeof value === 'number') return value
  if (typeof value === 'string') return parseFloat(value) || 0
  if (value && typeof value === 'object') {
    // Handle Java BigDecimal serialization
    if ('value' in value) return Number((value as { value: unknown }).value) || 0
  }
  return 0
}

// Helper to get bank logo with fallback
const getBankLogo = (bank: string | undefined): string | null => {
  if (!bank) return null
  // Try exact match first
  if (BANK_LOGOS[bank]) return BANK_LOGOS[bank]
  // Try case-insensitive match
  const lowerBank = bank.toLowerCase()
  for (const [key, value] of Object.entries(BANK_LOGOS)) {
    if (key.toLowerCase() === lowerBank) return value
  }
  return null
}

function SharedResultPage() {
  const { shareId } = useParams<{ shareId: string }>()
  const { t } = useTranslation()
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedAi, setExpandedAi] = useState<Set<SpendingCategory>>(new Set())
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 640)

  // Check if mobile on resize
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 640)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const toggleAiExpanded = (category: SpendingCategory) => {
    if (!isMobile) return // Desktop always shows expanded
    setExpandedAi(prev => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  const isAiExpanded = (category: SpendingCategory) => {
    return !isMobile || expandedAi.has(category)
  }

  useEffect(() => {
    const loadSharedResult = async () => {
      if (!shareId) {
        setError('Invalid share link')
        setLoading(false)
        return
      }

      try {
        const response = await optimizerApi.getSharedResult(shareId)
        if (response.code === 200 && response.data) {
          setResult(response.data)
        } else {
          setError(response.message || 'Result not found or expired')
        }
      } catch (err) {
        setError('Failed to load shared result')
      } finally {
        setLoading(false)
      }
    }

    loadSharedResult()
  }, [shareId])

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh'
      }}>
        <div style={{ fontSize: '16px', color: '#6b7280' }}>{t('common.loading')}...</div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '12px'
        }}>
          {error || t('share.notFound')}
        </h2>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          marginBottom: '32px'
        }}>
          {t('share.expiredOrNotExist')}
        </p>
        <Link
          to="/cards"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#111827',
            color: 'white',
            padding: '14px 28px',
            borderRadius: '50px',
            fontSize: '15px',
            fontWeight: '600',
            textDecoration: 'none'
          }}
        >
          {t('share.getStarted')} <ArrowRightOutlined />
        </Link>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative' }}>
      {/* Top Bar - Logo and Shared Badge */}
      <div className="sv-result-top-bar">
        {/* Logo - Left (mobile only) */}
        <img src="/logo-full.svg" alt="SaveVia" className="sv-result-logo-mobile" />
      </div>

      {/* Big Number */}
      <div className="sv-result-hero" style={{ marginBottom: '48px' }}>
        <div style={{ fontSize: '14px', color: '#059669', fontWeight: '500', marginBottom: '8px' }}>
          {t('result.netSavings')}
        </div>
        <div className="sv-result-amount" style={{
          fontWeight: '800',
          color: '#111827',
          letterSpacing: '-3px',
          lineHeight: 1
        }}>
          ${toNumber(result.netAnnualSavings).toFixed(0)}
          <span className="sv-result-unit" style={{ fontWeight: '500', color: '#6b7280', letterSpacing: '0' }}>{t('common.perYear')}</span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="sv-result-stats-row">
        <div className="sv-result-stat-item">
          <div className="sv-result-stat-label">{t('result.monthlyReward')}</div>
          <div className="sv-result-stat-value">${toNumber(result.monthlyReward).toFixed(2)}</div>
        </div>
        <div className="sv-result-stat-divider" />
        <div className="sv-result-stat-item">
          <div className="sv-result-stat-label">{t('result.annualReward')}</div>
          <div className="sv-result-stat-value">${toNumber(result.annualReward).toFixed(0)}</div>
        </div>
        <div className="sv-result-stat-divider" />
        <div className="sv-result-stat-item">
          <div className="sv-result-stat-label">{t('result.annualFees')}</div>
          <div className="sv-result-stat-value" style={{ color: '#ef4444' }}>-${toNumber(result.totalAnnualFees).toFixed(0)}</div>
        </div>
      </div>

      {/* Recommendations - Simple List */}
      <div style={{ marginBottom: '48px' }}>
        <h2 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '24px'
        }}>
          {t('result.quickReference')}
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {sortByCategory(result.recommendations).map((rec) => {
            const category = String(rec.category || '')
            const bankName = rec.recommendedCard?.bank || ''
            const cardName = rec.recommendedCard?.name || ''
            const bankLogo = getBankLogo(bankName)
            const rewardRate = toNumber(rec.rewardRate)
            const monthlyReward = toNumber(rec.monthlyReward)
            const aiExplanation = rec.aiExplanation || ''

            return (
              <div
                key={category}
                className="sv-result-rec-item"
                onClick={() => aiExplanation && isMobile && toggleAiExpanded(category as SpendingCategory)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '16px 0',
                  borderBottom: '1px solid #f3f4f6',
                  gap: '8px',
                  cursor: isMobile && aiExplanation ? 'pointer' : 'default'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '12px',
                  flexWrap: 'wrap'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>{CATEGORY_ICONS[category] || '💳'}</span>
                    <span style={{ fontSize: '16px', fontWeight: '500', color: '#111827' }}>
                      {t(`categories.${category}`)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    {bankLogo && (
                      <img
                        src={bankLogo}
                        alt={bankName}
                        style={{ width: '20px', height: '20px', objectFit: 'contain', borderRadius: '4px' }}
                      />
                    )}
                    <span className="sv-result-card-name" style={{ fontSize: '14px', color: '#6b7280' }}>
                      {cardName}
                    </span>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#059669' }}>
                      {(rewardRate * 100).toFixed(0)}%
                    </span>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                      ${monthlyReward.toFixed(2)}/mo
                    </span>
                    {/* Mobile: show expand indicator at far right */}
                    {isMobile && aiExplanation && (
                      <DownOutlined style={{
                        fontSize: '10px',
                        color: '#9ca3af',
                        transform: isAiExpanded(category as SpendingCategory) ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s',
                        marginLeft: '4px'
                      }} />
                    )}
                  </div>
                </div>
                {aiExplanation && (
                  <div
                    className="sv-ai-content"
                    style={{
                      maxHeight: isAiExpanded(category as SpendingCategory) ? '200px' : '0',
                      overflow: 'hidden',
                      transition: isMobile ? 'max-height 0.3s ease, opacity 0.3s ease' : 'none',
                      opacity: isAiExpanded(category as SpendingCategory) ? 1 : 0
                    }}
                  >
                    <p style={{
                      margin: '4px 0 0 0',
                      fontSize: '13px',
                      color: '#6b7280',
                      lineHeight: '1.6',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '6px'
                    }}>
                      <img src="/logo.svg" alt="" style={{ width: '14px', height: '14px', marginTop: '3px', flexShrink: 0 }} />
                      <span><span style={{ color: '#9ca3af' }}>{t('result.aiTip')}:</span> {aiExplanation}</span>
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* CTA - Invite to try */}
      <div style={{
        textAlign: 'center',
        padding: '32px 24px',
        marginBottom: '32px'
      }}>
        <p style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '8px'
        }}>
          {t('share.wantToOptimize')}
        </p>
        <p style={{
          fontSize: '14px',
          color: '#6b7280',
          marginBottom: '24px'
        }}>
          {t('share.freeToUse')}
        </p>
        <Link
          to="/cards"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#111827',
            color: 'white',
            padding: '14px 28px',
            borderRadius: '50px',
            fontSize: '15px',
            fontWeight: '600',
            textDecoration: 'none'
          }}
        >
          {t('share.getStarted')} <ArrowRightOutlined />
        </Link>
      </div>
    </div>
  )
}

export default SharedResultPage
