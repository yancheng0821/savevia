import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined } from '@ant-design/icons'
import { optimizerApi } from '../services/api'
import type { OptimizationResult } from '../types'

function SharedResultPage() {
  const { shareId } = useParams<{ shareId: string }>()
  const { t } = useTranslation()
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
        <div style={{ fontSize: '16px', color: '#6b7280' }}>Loading...</div>
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
          {error || 'Result not found'}
        </h2>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          marginBottom: '32px'
        }}>
          This shared result may have expired or doesn't exist.
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
          {t('result.startOver')} <ArrowRightOutlined />
        </Link>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      {/* Shared Badge */}
      <div style={{
        display: 'inline-block',
        background: '#f0fdf4',
        color: '#059669',
        fontSize: '12px',
        fontWeight: '600',
        padding: '4px 12px',
        borderRadius: '20px',
        marginBottom: '16px'
      }}>
        Shared Result
      </div>

      {/* Big Number */}
      <div style={{ marginBottom: '64px' }}>
        <div style={{ fontSize: '14px', color: '#059669', fontWeight: '500', marginBottom: '8px' }}>
          {t('result.netSavings')}
        </div>
        <div style={{
          fontSize: '72px',
          fontWeight: '800',
          color: '#111827',
          letterSpacing: '-3px',
          lineHeight: 1
        }}>
          ${result.netAnnualSavings.toFixed(0)}
          <span style={{ fontSize: '24px', fontWeight: '500', color: '#6b7280', letterSpacing: '0' }}>{t('common.perYear')}</span>
        </div>
      </div>

      {/* Stats Row */}
      <div style={{
        display: 'flex',
        gap: '48px',
        marginBottom: '64px',
        paddingBottom: '32px',
        borderBottom: '1px solid #f3f4f6'
      }}>
        <div>
          <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
            {t('result.monthlyReward')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>
            ${result.monthlyReward.toFixed(2)}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
            {t('result.annualReward')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>
            ${result.annualReward.toFixed(0)}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
            {t('result.annualFees')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#ef4444' }}>
            -${result.totalAnnualFees.toFixed(0)}
          </div>
        </div>
      </div>

      {/* Recommendations - Simple List */}
      <div style={{ marginBottom: '64px' }}>
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
          {result.recommendations.map((rec) => (
            <div
              key={rec.category}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '20px 0',
                borderBottom: '1px solid #f3f4f6'
              }}
            >
              <span style={{ fontSize: '17px', fontWeight: '500', color: '#111827' }}>
                {t(`categories.${rec.category}`)}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '15px', color: '#6b7280' }}>
                  {rec.recommendedCard.name}
                </span>
                <span style={{ fontSize: '15px', fontWeight: '600', color: '#059669' }}>
                  {(rec.rewardRate * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div style={{ textAlign: 'center' }}>
        <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '24px' }}>
          Want to optimize your own credit card rewards?
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
          Get Started <ArrowRightOutlined />
        </Link>
      </div>
    </div>
  )
}

export default SharedResultPage
