import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { message } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import { useSubscriptionStore } from '../stores/useSubscriptionStore'
import { useAuthStore } from '../stores/useAuthStore'
import { authApi } from '../services/api'
import {
  isNativePlatform,
  getProducts,
  purchaseSubscription,
  restorePurchases,
  PRODUCT_IDS,
  type IAPProduct,
} from '../services/iap'
import { Capacitor } from '@capacitor/core'
import LegalModal, { type LegalType } from './LegalModal'

interface PaywallProps {
  onSubscribed: () => void
  onClose?: () => void  // Optional close handler for modal usage
}

function Paywall({ onSubscribed, onClose }: PaywallProps) {
  console.log('Paywall component mounted')
  const { t } = useTranslation()
  const { setSubscribed } = useSubscriptionStore()
  const { isAuthenticated } = useAuthStore()

  const [products, setProducts] = useState<IAPProduct[]>([])
  const [purchasing, setPurchasing] = useState<string | null>(null)
  const [restoring, setRestoring] = useState(false)
  const [legalModal, setLegalModal] = useState<LegalType | null>(null)

  const isNative = isNativePlatform()

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    console.log('Paywall: loadProducts started')
    try {
      const productsData = await getProducts()
      console.log('Paywall: products loaded', productsData)
      setProducts(productsData)
    } catch (error) {
      console.error('Paywall: Failed to load products:', error)
    }
  }

  // Sync subscription status to backend
  const syncSubscriptionToBackend = async (productId: string, expiresAt?: string) => {
    if (!isAuthenticated) {
      console.log('User not authenticated, skipping subscription sync')
      return
    }

    try {
      const platform = Capacitor.getPlatform()
      await authApi.updateSubscription({
        subscriptionType: 'PRO',
        expiresAt: expiresAt,
        platform: platform,
        productId: productId,
      })
      console.log('Subscription synced to backend successfully')
    } catch (error) {
      console.error('Failed to sync subscription to backend:', error)
      // Don't fail the purchase flow, just log the error
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
        // Sync subscription to backend
        await syncSubscriptionToBackend(productId, result.expiresAt)
        // Don't show success message - just proceed to app
        onSubscribed()
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
        // Sync restored subscription to backend
        await syncSubscriptionToBackend(result.productId || 'restored', result.expiresAt)
        message.success(t('subscription.restoreSuccess'))
        onSubscribed()
      } else {
        message.warning(result.error || t('subscription.noSubscription'))
      }
    } catch (error: any) {
      message.error(error.message || t('subscription.restoreFailed'))
    } finally {
      setRestoring(false)
    }
  }

  // For web development, allow skip
  const handleSkipForDev = () => {
    if (!isNative) {
      onSubscribed()
    }
  }

  console.log('Paywall loaded, products:', products.length)

  return (
    <div className="sv-paywall">
      {/* Header with Full Logo */}
      <div className="sv-paywall-header">
        <img src="/logo-full.svg" alt="SaveVia" className="sv-paywall-logo-full" />
        <p className="sv-paywall-tagline">{t('subscription.subtitle')}</p>
      </div>

      {/* Plans */}
      <div className="sv-paywall-plans">
        {products.map((product) => {
          const isYearly = product.productId === PRODUCT_IDS.YEARLY
          const isPurchasing = purchasing === product.productId

          return (
            <div
              key={product.productId}
              className={`sv-paywall-plan ${isYearly ? 'sv-paywall-plan-yearly' : ''}`}
              onClick={() => !purchasing && handlePurchase(product.productId)}
            >
              {isYearly && (
                <div className="sv-paywall-plan-badge">{t('subscription.bestValue')}</div>
              )}
              <div className="sv-paywall-plan-left">
                <div className="sv-paywall-plan-title">{product.title}</div>
                <div className="sv-paywall-plan-price">
                  <span className="sv-paywall-plan-amount">{product.price}</span>
                  <span className="sv-paywall-plan-period">
                    /{isYearly ? t('subscription.year') : t('subscription.month')}
                  </span>
                </div>
              </div>
              <div className="sv-paywall-plan-right">
                {isPurchasing ? (
                  <LoadingOutlined className="sv-paywall-plan-loading" />
                ) : isYearly ? (
                  <span className="sv-paywall-save-tag">{t('subscription.save20')}</span>
                ) : null}
              </div>
            </div>
          )
        })}
      </div>

      {/* Trial Info */}
      <p className="sv-paywall-trial">{t('subscription.trialInfo')}</p>

      {/* Restore Button */}
      {isNative && (
        <button
          className="sv-paywall-restore"
          onClick={handleRestore}
          disabled={restoring}
        >
          {restoring ? <LoadingOutlined /> : t('subscription.restore')}
        </button>
      )}

      {/* Skip for now button (shown on native) */}
      {isNative && (
        <button className="sv-paywall-skip" onClick={onClose || onSubscribed}>
          {t('subscription.skipForNow')}
        </button>
      )}

      {/* Web development skip (only shown on web) */}
      {!isNative && (
        <button className="sv-paywall-skip" onClick={onClose || handleSkipForDev}>
          {t('subscription.webNotice')}
        </button>
      )}

      {/* Legal Links - Required by App Store */}
      <div className="sv-paywall-legal">
        <span className="sv-paywall-legal-link" onClick={() => setLegalModal('terms')}>{t('me.termsOfService')}</span>
        <span className="sv-paywall-legal-divider">|</span>
        <span className="sv-paywall-legal-link" onClick={() => setLegalModal('privacy')}>{t('me.privacyPolicy')}</span>
      </div>

      {/* Subscription Info - Required by App Store */}
      <p className="sv-paywall-info">
        {t('subscription.autoRenewInfo')}
      </p>

      {/* Legal Modal */}
      {legalModal && (
        <LegalModal type={legalModal} onClose={() => setLegalModal(null)} />
      )}

      <style>{`
        .sv-paywall {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: #fffcf5;
          z-index: 9999;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 24px 20px;
        }

        /* Header */
        .sv-paywall-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .sv-paywall-logo-full {
          height: 48px;
          width: auto;
          margin-bottom: 12px;
        }

        .sv-paywall-tagline {
          font-size: 16px;
          color: #6b7280;
          margin: 0;
        }

        /* Plans */
        .sv-paywall-plans {
          display: flex;
          flex-direction: column;
          gap: 12px;
          width: 100%;
          max-width: 400px;
          margin-bottom: 20px;
        }

        .sv-paywall-plan {
          background: #f3f4f6;
          border: none;
          border-radius: 12px;
          padding: 18px 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          transition: all 0.2s;
          position: relative;
        }

        .sv-paywall-plan:active {
          transform: scale(0.98);
        }

        .sv-paywall-plan-yearly {
          background: #f3f4f6;
        }

        .sv-paywall-plan-badge {
          position: absolute;
          top: -10px;
          left: 16px;
          background: #111827;
          color: white;
          font-size: 10px;
          font-weight: 600;
          padding: 3px 8px;
          border-radius: 10px;
          text-transform: uppercase;
        }

        .sv-paywall-plan-left {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .sv-paywall-plan-title {
          font-size: 16px;
          font-weight: 600;
          color: #111827;
        }

        .sv-paywall-plan-price {
          display: flex;
          align-items: baseline;
          gap: 2px;
        }

        .sv-paywall-plan-amount {
          font-size: 26px;
          font-weight: 700;
          color: #111827;
        }

        .sv-paywall-plan-period {
          font-size: 14px;
          color: #6b7280;
        }

        .sv-paywall-plan-right {
          display: flex;
          align-items: center;
        }

        .sv-paywall-plan-loading {
          font-size: 20px;
          color: #111827;
        }

        .sv-paywall-save-tag {
          background: #dcfce7;
          color: #16a34a;
          font-size: 12px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 8px;
        }

        /* Trial Info */
        .sv-paywall-trial {
          text-align: center;
          font-size: 13px;
          color: #9ca3af;
          margin: 0 0 16px;
        }

        /* Restore */
        .sv-paywall-restore {
          display: block;
          padding: 12px 24px;
          background: none;
          border: none;
          color: #6b7280;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          text-align: center;
        }

        .sv-paywall-restore:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        /* Web skip button */
        .sv-paywall-skip {
          display: block;
          padding: 12px 24px;
          background: none;
          border: none;
          color: #9ca3af;
          font-size: 13px;
          cursor: pointer;
          text-align: center;
          text-decoration: underline;
        }

        /* Legal Links */
        .sv-paywall-legal {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 8px;
          margin-top: 16px;
        }

        .sv-paywall-legal-link {
          font-size: 13px;
          color: #6b7280;
          text-decoration: none;
          cursor: pointer;
        }

        .sv-paywall-legal-link:active {
          text-decoration: underline;
        }

        .sv-paywall-legal-divider {
          color: #d1d5db;
          font-size: 12px;
        }

        /* Subscription Info */
        .sv-paywall-info {
          text-align: center;
          font-size: 11px;
          color: #9ca3af;
          margin: 12px 20px 0;
          line-height: 1.5;
        }

        /* Dark Mode */
        html.dark-mode .sv-paywall {
          background: var(--bg-primary);
        }

        html.dark-mode .sv-paywall-tagline {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-plan {
          background: var(--bg-tertiary);
        }

        html.dark-mode .sv-paywall-plan-title,
        html.dark-mode .sv-paywall-plan-amount {
          color: var(--text-primary);
        }

        html.dark-mode .sv-paywall-plan-period {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-trial {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-restore {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-skip {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-legal-link {
          color: var(--text-secondary);
        }

        html.dark-mode .sv-paywall-legal-divider {
          color: var(--border-color);
        }

        html.dark-mode .sv-paywall-info {
          color: var(--text-secondary);
        }

      `}</style>
    </div>
  )
}

export default Paywall
