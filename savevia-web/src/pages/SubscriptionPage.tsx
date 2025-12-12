import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { message } from 'antd'
import {
  CheckOutlined,
  LoadingOutlined,
} from '@ant-design/icons'
import { useSubscriptionStore } from '../stores/useSubscriptionStore'
import {
  isNativePlatform,
  getProducts,
  purchaseSubscription,
  restorePurchases,
  checkSubscriptionStatus,
  PRODUCT_IDS,
  type IAPProduct,
} from '../services/iap'

function SubscriptionPage() {
  const { t } = useTranslation()
  const { isSubscribed, setSubscribed } = useSubscriptionStore()

  const [loading, setLoading] = useState(true)
  const [products, setProducts] = useState<IAPProduct[]>([])
  const [purchasing, setPurchasing] = useState<string | null>(null)
  const [restoring, setRestoring] = useState(false)

  const isNative = isNativePlatform()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load products and check subscription status
      const [productsData, subscribed] = await Promise.all([
        getProducts(),
        checkSubscriptionStatus(),
      ])

      setProducts(productsData)
      setSubscribed(subscribed)
    } catch (error) {
      console.error('Failed to load subscription data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async (productId: string) => {
    if (!isNative) {
      message.info(t('subscription.nativeOnly'))
      return
    }

    setPurchasing(productId)
    try {
      const result = await purchaseSubscription(productId)

      if (result.success) {
        setSubscribed(true)
        message.success(t('subscription.purchaseSuccess'))
      } else {
        if (result.error !== 'Purchase cancelled') {
          message.error(result.error || t('subscription.purchaseFailed'))
        }
      }
    } catch (error: any) {
      message.error(error.message || t('subscription.purchaseFailed'))
    } finally {
      setPurchasing(null)
    }
  }

  const handleRestore = async () => {
    if (!isNative) {
      message.info(t('subscription.nativeOnly'))
      return
    }

    setRestoring(true)
    try {
      const result = await restorePurchases()

      if (result.success) {
        setSubscribed(true)
        message.success(t('subscription.restoreSuccess'))
      } else {
        message.warning(result.error || t('subscription.noSubscription'))
      }
    } catch (error: any) {
      message.error(error.message || t('subscription.restoreFailed'))
    } finally {
      setRestoring(false)
    }
  }

  if (loading) {
    return (
      <div className="sv-sub-page sv-sub-loading">
        <LoadingOutlined style={{ fontSize: 32, color: '#111827' }} />
      </div>
    )
  }

  return (
    <div className="sv-sub-page">
      {/* Header with Full Logo */}
      <div className="sv-sub-header">
        <img src="/logo-full.svg" alt="SaveVia" className="sv-sub-logo-full" />
        <p className="sv-sub-tagline">{t('subscription.subtitle')}</p>
      </div>

      {/* Current Subscription Status */}
      {isSubscribed && (
        <div className="sv-sub-active">
          <div className="sv-sub-active-badge">
            <CheckOutlined /> {t('subscription.active')}
          </div>
          <div className="sv-sub-active-info">
            <span className="sv-sub-plan-name">SaveVia Pro</span>
          </div>
        </div>
      )}

      {/* Plans */}
      {!isSubscribed && (
        <div className="sv-sub-plans">
          {products.map((product) => {
            const isYearly = product.productId === PRODUCT_IDS.YEARLY
            const isPurchasing = purchasing === product.productId

            return (
              <div
                key={product.productId}
                className={`sv-sub-plan ${isYearly ? 'sv-sub-plan-yearly' : ''}`}
                onClick={() => !purchasing && handlePurchase(product.productId)}
              >
                {isYearly && (
                  <div className="sv-sub-plan-badge">{t('subscription.bestValue')}</div>
                )}
                <div className="sv-sub-plan-left">
                  <div className="sv-sub-plan-title">{product.title}</div>
                  <div className="sv-sub-plan-price">
                    <span className="sv-sub-plan-amount">{product.price}</span>
                    <span className="sv-sub-plan-period">
                      /{isYearly ? t('subscription.year') : t('subscription.month')}
                    </span>
                  </div>
                </div>
                <div className="sv-sub-plan-right">
                  {isPurchasing ? (
                    <LoadingOutlined className="sv-sub-plan-loading" />
                  ) : isYearly ? (
                    <span className="sv-sub-save-tag">{t('subscription.save20')}</span>
                  ) : null}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Trial Info */}
      {!isSubscribed && (
        <p className="sv-sub-trial">{t('subscription.trialInfo')}</p>
      )}

      {/* Restore Button */}
      {isNative && !isSubscribed && (
        <button
          className="sv-sub-restore"
          onClick={handleRestore}
          disabled={restoring}
        >
          {restoring ? <LoadingOutlined /> : t('subscription.restore')}
        </button>
      )}

      {/* Web Message */}
      {!isNative && !isSubscribed && (
        <p className="sv-sub-web-notice">{t('subscription.webNotice')}</p>
      )}

      {/* Legal Links - Required by App Store */}
      <div className="sv-sub-legal">
        <a href="/terms" className="sv-sub-legal-link">{t('me.termsOfService')}</a>
        <span className="sv-sub-legal-divider">|</span>
        <a href="/privacy" className="sv-sub-legal-link">{t('me.privacyPolicy')}</a>
      </div>

      {/* Subscription Info - Required by App Store */}
      {!isSubscribed && (
        <p className="sv-sub-info">
          {t('subscription.autoRenewInfo')}
        </p>
      )}

      <style>{`
        .sv-sub-page {
          padding: 24px 20px;
          min-height: calc(100vh - 140px);
          background: #fffcf5;
        }

        .sv-sub-loading {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        @media (min-width: 641px) {
          .sv-sub-page {
            max-width: 480px;
            margin: 0 auto;
            padding: 40px 20px;
          }
        }

        @media (max-width: 640px) {
          .sv-sub-page {
            min-height: calc(100vh - 70px);
          }
        }

        /* Header */
        .sv-sub-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .sv-sub-logo-full {
          height: 40px;
          width: auto;
          margin-bottom: 12px;
        }

        .sv-sub-tagline {
          font-size: 15px;
          color: #6b7280;
          margin: 0;
        }

        /* Active Status */
        .sv-sub-active {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          border-radius: 12px;
          padding: 16px;
          color: white;
          margin-bottom: 24px;
        }

        .sv-sub-active-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: rgba(255,255,255,0.2);
          padding: 4px 10px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .sv-sub-active-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .sv-sub-active-info .sv-sub-plan-name {
          font-size: 16px;
          font-weight: 600;
        }

        /* Plans */
        .sv-sub-plans {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 20px;
        }

        .sv-sub-plan {
          background: #f3f4f6;
          border: none;
          border-radius: 12px;
          padding: 16px 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          transition: all 0.2s;
          position: relative;
        }

        .sv-sub-plan:active {
          transform: scale(0.98);
        }

        .sv-sub-plan-yearly {
          background: #f3f4f6;
        }

        .sv-sub-plan-badge {
          position: absolute;
          top: -10px;
          left: 16px;
          background: #6b7280;
          color: white;
          font-size: 10px;
          font-weight: 600;
          padding: 3px 8px;
          border-radius: 10px;
          text-transform: uppercase;
        }

        .sv-sub-plan-left {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .sv-sub-plan-title {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
        }

        .sv-sub-plan-price {
          display: flex;
          align-items: baseline;
          gap: 2px;
        }

        .sv-sub-plan-amount {
          font-size: 24px;
          font-weight: 700;
          color: #111827;
        }

        .sv-sub-plan-period {
          font-size: 14px;
          color: #6b7280;
        }

        .sv-sub-plan-right {
          display: flex;
          align-items: center;
        }

        .sv-sub-plan-loading {
          font-size: 20px;
          color: #111827;
        }

        .sv-sub-save-tag {
          background: #dcfce7;
          color: #16a34a;
          font-size: 12px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 8px;
        }

        /* Trial Info */
        .sv-sub-trial {
          text-align: center;
          font-size: 13px;
          color: #9ca3af;
          margin: 0 0 16px;
        }

        /* Restore */
        .sv-sub-restore {
          display: block;
          width: 100%;
          padding: 12px;
          background: none;
          border: none;
          color: #6b7280;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          text-align: center;
        }

        .sv-sub-restore:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        /* Web Notice */
        .sv-sub-web-notice {
          text-align: center;
          font-size: 13px;
          color: #9ca3af;
          margin: 8px 0 0;
          padding-bottom: 80px;
        }

        @media (min-width: 641px) {
          .sv-sub-web-notice {
            padding-bottom: 16px;
          }
        }

        /* Dark Mode */
        html.dark-mode .sv-sub-page {
          background: var(--bg-primary);
        }

        html.dark-mode .sv-sub-tagline {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-sub-plan {
          background: var(--bg-tertiary);
        }

        html.dark-mode .sv-sub-plan-title,
        html.dark-mode .sv-sub-plan-amount {
          color: var(--text-primary);
        }

        html.dark-mode .sv-sub-plan-period {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-sub-trial {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-sub-restore {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-sub-web-notice {
          color: var(--text-secondary);
        }

        /* Legal Links */
        .sv-sub-legal {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 8px;
          margin-top: 24px;
          padding-bottom: 16px;
        }

        .sv-sub-legal-link {
          font-size: 13px;
          color: #6b7280;
          text-decoration: none;
        }

        .sv-sub-legal-link:hover {
          text-decoration: underline;
        }

        .sv-sub-legal-divider {
          color: #d1d5db;
          font-size: 12px;
        }

        /* Subscription Info */
        .sv-sub-info {
          text-align: center;
          font-size: 11px;
          color: #9ca3af;
          margin: 8px 20px 0;
          line-height: 1.5;
          padding-bottom: 80px;
        }

        @media (min-width: 641px) {
          .sv-sub-info {
            padding-bottom: 16px;
          }
        }

        html.dark-mode .sv-sub-legal-link {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-sub-legal-divider {
          color: var(--border-color);
        }

        html.dark-mode .sv-sub-info {
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  )
}

export default SubscriptionPage
