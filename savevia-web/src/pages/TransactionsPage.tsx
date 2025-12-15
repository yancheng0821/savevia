import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { message, Spin, Empty, Progress, Modal, Pagination } from 'antd'
import {
  SyncOutlined,
  RightOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  DeleteOutlined,
  CloseOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../stores/useAuthStore'
import { bankApi, transactionApi, userApi } from '../services/api'
import type {
  BankConnection,
  Transaction,
  MissedCashbackSummary,
  CategoryMissedCashback,
} from '../types'

// Bank logos mapping
const BANK_LOGOS: Record<string, string> = {
  // Short names
  'TD': '/logos/td.png',
  'RBC': '/logos/rbc.png',
  'Scotiabank': '/logos/scotiabank.png',
  'CIBC': '/logos/cibc.png',
  'BMO': '/logos/bmo.png',
  'National Bank': '/logos/nationalbank.png',
  'Desjardins': '/logos/desjardins.png',
  'HSBC': '/logos/hsbc.png',
  'Tangerine': '/logos/tangerine.png',
  'Simplii': '/logos/simplii.png',
  'EQ Bank': '/logos/eqbank.png',
  'Manulife': '/logos/manulife.png',
  'MBNA': '/logos/mbna.png',
  'Canadian Tire': '/logos/canadiantire.png',
  'Rogers': '/logos/rogers.png',
  'Neo': '/logos/neo.png',
  'PC Financial': '/logos/pc.png',
  'Home Trust': '/logos/hometrust.png',
  'Amex': '/logos/amex.png',
  'American Express': '/logos/amex.png',
  'Meridian': '/logos/meridian.png',
  'Coast Capital': '/logos/coastcapital.png',
  'ATB': '/logos/atb.png',
  'Laurentian': '/logos/laurentian.png',
  // Full names (from Flinks)
  'TD Canada Trust': '/logos/td.png',
  'RBC Royal Bank': '/logos/rbc.png',
  'Bank of Montreal': '/logos/bmo.png',
  'National Bank of Canada': '/logos/nationalbank.png',
  'Home Trust Company': '/logos/hometrust.png',
  'Simplii Financial': '/logos/simplii.png',
  'Canadian Tire Bank': '/logos/canadiantire.png',
  'Rogers Bank': '/logos/rogers.png',
  'Manulife Bank': '/logos/manulife.png',
  'Laurentian Bank': '/logos/laurentian.png',
  'ATB Financial': '/logos/atb.png',
  'HSBC Bank Canada': '/logos/hsbc.png',
  'Tangerine Bank': '/logos/tangerine.png',
  'American Express Canada': '/logos/amex.png',
  // Flinks test bank
  'FlinksCapital': '/logos/flinks.png',
  'Flinks': '/logos/flinks.png',
  'Flinks Capital': '/logos/flinks.png',
}

// Banks that issue credit cards (for bank connection)
// These are Canadian banks where users can have credit card accounts
const CREDIT_CARD_BANKS = [
  { id: 'TD', name: 'TD Canada Trust', fullName: 'TD Canada Trust' },
  { id: 'RBC', name: 'RBC Royal Bank', fullName: 'RBC Royal Bank' },
  { id: 'Scotiabank', name: 'Scotiabank', fullName: 'Scotiabank' },
  { id: 'CIBC', name: 'CIBC', fullName: 'CIBC' },
  { id: 'BMO', name: 'BMO', fullName: 'BMO Bank of Montreal' },
  { id: 'National Bank', name: 'National Bank', fullName: 'National Bank of Canada' },
  { id: 'Desjardins', name: 'Desjardins', fullName: 'Desjardins' },
  { id: 'HSBC', name: 'HSBC Canada', fullName: 'HSBC Bank Canada' },
  { id: 'Tangerine', name: 'Tangerine', fullName: 'Tangerine Bank' },
  { id: 'Simplii', name: 'Simplii Financial', fullName: 'Simplii Financial' },
  { id: 'MBNA', name: 'MBNA', fullName: 'MBNA Canada' },
  { id: 'Canadian Tire', name: 'Canadian Tire Bank', fullName: 'Canadian Tire Bank' },
  { id: 'Rogers', name: 'Rogers Bank', fullName: 'Rogers Bank' },
  { id: 'Home Trust', name: 'Home Trust', fullName: 'Home Trust Company' },
  { id: 'Manulife', name: 'Manulife Bank', fullName: 'Manulife Bank' },
  { id: 'Laurentian', name: 'Laurentian Bank', fullName: 'Laurentian Bank' },
  { id: 'ATB', name: 'ATB Financial', fullName: 'ATB Financial' },
  { id: 'Amex', name: 'American Express', fullName: 'American Express Canada' },
]

// Helper to get bank logo from bank name
const getBankLogo = (bankName: string | undefined): string => {
  if (!bankName) return '/logos/td.png'
  // Try exact match first
  if (BANK_LOGOS[bankName]) return BANK_LOGOS[bankName]
  // Try first word match
  const firstWord = bankName.split(' ')[0]
  if (BANK_LOGOS[firstWord]) return BANK_LOGOS[firstWord]
  return '/logos/td.png'
}

// Category icons
const CATEGORY_ICONS: Record<string, string> = {
  // Core categories
  'DINING': '🍽️',
  'GROCERY': '🛒',
  'GAS': '⛽',
  'TRAVEL': '✈️',
  'STREAMING': '📺',
  'TRANSIT': '🚇',
  'PHARMACY': '💊',
  'RENT': '🏠',
  'RECURRING': '🔄',
  'ONLINE_SHOPPING': '📦',
  'FOREIGN': '🌍',
  // Extended categories
  'RETAIL': '🛍️',
  'ENTERTAINMENT': '🎬',
  'PERSONAL_SERVICES': '💇',
  'HOME_IMPROVEMENT': '🔨',
  'WHOLESALE': '🏪',
  'INSURANCE': '📋',
  'TELECOM': '📱',
  'EV_CHARGING': '⚡',
  // Catch-all
  'OTHER': '💳',
}

// Connection limit info
interface ConnectionLimit {
  used: number
  max: number
  remaining: number
  canConnect: boolean
}

// Flinks Connect configuration
interface FlinksConfig {
  customerId: string
  iframeUrl: string
  sandbox: boolean
  connectUrl: string
  connectionLimit?: ConnectionLimit
}

function TransactionsPage() {
  const { t, i18n } = useTranslation()
  const { isAuthenticated, setPanelOpen } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [connections, setConnections] = useState<BankConnection[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [summary, setSummary] = useState<MissedCashbackSummary | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'transactions'>('summary')
  const [showConnectModal, setShowConnectModal] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [userCardIds, setUserCardIds] = useState<number[]>([])
  const [flinksConfig, setFlinksConfig] = useState<FlinksConfig | null>(null)
  const [flinksLoading, setFlinksLoading] = useState(false)
  const [showFlinksIframe, setShowFlinksIframe] = useState(false)
  const [iframeLoading, setIframeLoading] = useState(true)
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const pageSize = 10

  // Build Flinks iframe URL with language and demo parameters
  // Flinks only supports 'en' and 'fr', default to 'en' for other languages
  // Using Flinks public demo URL (demo.flinks.com) for testing
  const flinksConnectUrl = useMemo(() => {
    if (!flinksConfig) return ''
    const flinksLang = i18n.language === 'fr' ? 'fr' : 'en'
    // Use public Flinks demo URL for sandbox testing
    return `https://demo.flinks.com/v2/?demo=true&language=${flinksLang}`
  }, [flinksConfig, i18n.language])

  // Handle Flinks Connect message events
  const handleFlinksMessage = useCallback(async (event: MessageEvent) => {
    // Verify the message is from Flinks
    if (!event.data || typeof event.data !== 'object') return

    // Ignore messages from browser extensions (MetaMask, etc.)
    if (event.data.target && event.data.target.includes('metamask')) return
    if (event.data.type && event.data.type.includes('extension')) return

    const { step, loginId, institution } = event.data

    // Only log actual Flinks events
    if (step) {
      console.log('Flinks message:', event.data)
    }

    // Handle different Flinks events
    if (step === 'REDIRECT' || step === 'SUCCESS' || step === 'SUBMIT_CREDENTIAL') {
      // User successfully authenticated with bank
      if (loginId) {
        setShowFlinksIframe(false)
        setRefreshing(true)

        try {
          // Connect the bank account using the loginId from Flinks
          await bankApi.connect({
            loginId: loginId,
            institutionName: institution || 'Unknown Bank',
            userCardIds: userCardIds,
          })

          // Reload data
          await loadData()
          message.success(t('transactions.bankConnected'))
        } catch (error: any) {
          console.error('Bank connection error:', error)
          message.error(error.message || t('errors.unexpectedError'))
        } finally {
          setRefreshing(false)
        }
      }
    } else if (step === 'INSTITUTION_SELECTED') {
      console.log('User selected institution:', institution)
    } else if (step === 'APP_MOUNTED') {
      // Flinks widget is fully loaded and ready
      setIframeLoading(false)
    } else if (step === 'COMPONENT_CLOSE') {
      // User closed the Flinks widget
      setShowFlinksIframe(false)
      setIframeLoading(true)
    }
  }, [userCardIds, t])

  // Listen for Flinks postMessage events
  useEffect(() => {
    window.addEventListener('message', handleFlinksMessage)
    return () => {
      window.removeEventListener('message', handleFlinksMessage)
    }
  }, [handleFlinksMessage])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (showConnectModal || showFlinksIframe) {
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.width = '100%'
    } else {
      document.body.style.overflow = ''
      document.body.style.position = ''
      document.body.style.width = ''
    }
    return () => {
      document.body.style.overflow = ''
      document.body.style.position = ''
      document.body.style.width = ''
    }
  }, [showConnectModal, showFlinksIframe])

  // Load data on mount
  useEffect(() => {
    if (isAuthenticated) {
      loadData()
    } else {
      setLoading(false)
    }
  }, [isAuthenticated])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load user's saved card IDs first
      let cardIds: number[] = []
      try {
        const cardsRes = await userApi.getUserCards()
        if (cardsRes.code === 200 && cardsRes.data) {
          cardIds = cardsRes.data
          setUserCardIds(cardIds)
        }
      } catch (e) {
        console.error('Failed to load user cards:', e)
      }

      // Load Flinks config (for connection limit info)
      try {
        const configRes = await bankApi.getFlinksConfig()
        if (configRes.code === 200 && configRes.data) {
          setFlinksConfig(configRes.data)
        }
      } catch (e) {
        console.error('Failed to load Flinks config:', e)
      }

      // Load connections
      const connectionsRes = await bankApi.getConnections()
      if (connectionsRes.code === 200) {
        setConnections(connectionsRes.data || [])
      }

      // Only load transactions if we have connections
      if (connectionsRes.data && connectionsRes.data.length > 0) {
        const [transactionsRes, summaryRes] = await Promise.all([
          transactionApi.getRecent(50, cardIds),
          transactionApi.getSummary(cardIds),
        ])

        if (transactionsRes.code === 200) {
          setTransactions(transactionsRes.data || [])
        }
        if (summaryRes.code === 200) {
          setSummary(summaryRes.data)
        }
      }
    } catch (error: any) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    if (connections.length === 0) return

    setRefreshing(true)
    try {
      // Re-analyze transactions with user's card IDs (force re-analyze on refresh)
      // Note: This does NOT call Flinks API - it only re-analyzes existing local data
      await transactionApi.analyze(userCardIds, true)
      // Reload data from local database
      await loadData()
      message.success(t('transactions.analyzeSuccess'))
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    } finally {
      setRefreshing(false)
    }
  }

  const handleConnectBank = async () => {
    // Load Flinks config if not already loaded
    if (!flinksConfig) {
      setFlinksLoading(true)
      try {
        const res = await bankApi.getFlinksConfig()
        if (res.code === 200 && res.data) {
          setFlinksConfig(res.data)
        }
      } catch (error) {
        console.error('Failed to load Flinks config:', error)
      } finally {
        setFlinksLoading(false)
      }
    }
    // Always use demo mode - show local bank selection modal
    setShowConnectModal(true)
  }

  const handleDisconnect = (connectionId: number, bankName: string) => {
    Modal.confirm({
      title: t('transactions.disconnectConfirmTitle'),
      content: t('transactions.disconnectConfirmContent', { bank: bankName }),
      okText: t('transactions.disconnect'),
      cancelText: t('common.cancel'),
      okButtonProps: { danger: true },
      centered: true,
      onOk: async () => {
        try {
          await bankApi.disconnect(connectionId)
          setConnections(connections.filter(c => c.id !== connectionId))
          message.success(t('transactions.disconnected'))
        } catch (error: any) {
          message.error(error.message || t('errors.unexpectedError'))
        }
      },
    })
  }

  const handleResync = (connectionId: number, bankName: string) => {
    // Check connection limit first
    if (flinksConfig?.connectionLimit && !flinksConfig.connectionLimit.canConnect) {
      message.error(t('transactions.connectionLimitExceeded'))
      return
    }

    Modal.confirm({
      title: t('transactions.resyncConfirmTitle'),
      content: t('transactions.resyncConfirmContent', {
        bank: bankName,
        remaining: flinksConfig?.connectionLimit?.remaining || 0,
        max: flinksConfig?.connectionLimit?.max || 5
      }),
      okText: t('transactions.resync'),
      cancelText: t('common.cancel'),
      centered: true,
      onOk: async () => {
        setRefreshing(true)
        try {
          await bankApi.resync(connectionId, userCardIds)
          // Reload data
          await loadData()
          message.success(t('transactions.resyncSuccess'))
        } catch (error: any) {
          if (error.message?.includes('LIMIT_EXCEEDED')) {
            message.error(t('transactions.connectionLimitExceeded'))
          } else {
            message.error(error.message || t('errors.unexpectedError'))
          }
        } finally {
          setRefreshing(false)
        }
      },
    })
  }

  const handleDemoConnect = async (_bankId: string, fullName: string) => {
    // Check connection limit before attempting to connect
    if (flinksConfig?.connectionLimit && !flinksConfig.connectionLimit.canConnect) {
      message.error(t('transactions.connectionLimitExceeded'))
      return
    }

    setShowConnectModal(false)
    setRefreshing(true)
    try {
      // Connect with demo data (pass userCardIds for demo mode card assignment)
      await bankApi.connect({
        loginId: 'demo-login-' + Date.now(),
        institutionName: fullName,
        userCardIds: userCardIds,
      })
      await loadData()
      // Reload Flinks config to get updated connection limit
      const configRes = await bankApi.getFlinksConfig()
      if (configRes.code === 200 && configRes.data) {
        setFlinksConfig(configRes.data)
      }
      message.success(t('transactions.bankConnected'))
    } catch (error: any) {
      // Handle limit exceeded error from server
      if (error.message?.includes('LIMIT_EXCEEDED')) {
        message.error(t('transactions.connectionLimitExceeded'))
      } else {
        message.error(error.message || t('errors.unexpectedError'))
      }
    } finally {
      setRefreshing(false)
    }
  }

  // Not authenticated view
  if (!isAuthenticated) {
    return (
      <div className="sv-transactions-page">
        <div className="sv-txn-login-prompt" onClick={() => setPanelOpen(true)}>
          <span className="sv-txn-login-icon">🏦</span>
          <h2>{t('transactions.loginRequired')}</h2>
          <p>{t('transactions.loginDesc')}</p>
          <button className="sv-txn-login-btn">
            {t('auth.loginOrRegister')}
          </button>
        </div>
        <style>{styles}</style>
      </div>
    )
  }

  // Loading view
  if (loading) {
    return (
      <div className="sv-transactions-page">
        <div className="sv-txn-loading">
          <Spin size="large" />
          <p>{t('common.loading')}</p>
        </div>
        <style>{styles}</style>
      </div>
    )
  }

  // No bank connections view
  if (connections.length === 0) {
    return (
      <div className="sv-transactions-page">
        <div className="sv-txn-empty">
          <span className="sv-txn-empty-icon">🏦</span>
          <h2>{t('transactions.connectBank')}</h2>
          <p>{t('transactions.connectBankDesc')}</p>

          {/* Security Features */}
          <div className="sv-txn-security-features">
            <div className="sv-txn-security-item">
              <span className="sv-txn-security-emoji">🔒</span>
              <span>{t('transactions.security.encrypted')}</span>
            </div>
            <div className="sv-txn-security-item">
              <span className="sv-txn-security-emoji">👁️‍🗨️</span>
              <span>{t('transactions.security.readOnly')}</span>
            </div>
            <div className="sv-txn-security-item">
              <span className="sv-txn-security-emoji">🛡️</span>
              <span>{t('transactions.security.noPassword')}</span>
            </div>
          </div>

          {/* Startup Notice */}
          <div className="sv-txn-startup-notice">
            <span className="sv-txn-startup-icon">💡</span>
            <p>{t('transactions.startupNotice')}</p>
          </div>

          <button className="sv-txn-connect-btn" onClick={handleConnectBank} disabled={flinksLoading}>
            {flinksLoading ? t('common.loading') : t('transactions.connectBankBtn')}
          </button>

          {/* Connection limit info */}
          {flinksConfig?.connectionLimit && (
            <div className={`sv-txn-connection-limit-info ${!flinksConfig.connectionLimit.canConnect ? 'sv-limit-exceeded' : ''}`}>
              {flinksConfig.connectionLimit.canConnect ? (
                <span>
                  {t('transactions.connectionLimit', {
                    remaining: flinksConfig.connectionLimit.remaining,
                    max: flinksConfig.connectionLimit.max
                  })}
                </span>
              ) : (
                <span>{t('transactions.connectionLimitExceeded')}</span>
              )}
            </div>
          )}

          {/* Powered by Flinks */}
          <div className="sv-txn-flinks">
            <span className="sv-txn-flinks-text">{t('transactions.poweredByFlinks')}</span>
            <a href="https://www.flinks.com" target="_blank" rel="noopener noreferrer" className="sv-txn-flinks-logo">
              <img src="/logos/flinks.png" alt="Flinks" />
            </a>
          </div>
        </div>

        {/* Demo Connect Modal */}
        {showConnectModal && (
          <div className="sv-txn-modal-overlay" onClick={() => setShowConnectModal(false)}>
            <div className="sv-txn-modal sv-txn-modal-banks" onClick={(e) => e.stopPropagation()}>
              <div className="sv-txn-modal-header">
                <h3>{t('transactions.selectBank')}</h3>
                <button className="sv-txn-modal-close" onClick={() => setShowConnectModal(false)}>
                  <CloseOutlined />
                </button>
              </div>
              {/* Connection limit info */}
              {flinksConfig?.connectionLimit && (
                <p className={`sv-txn-modal-desc ${!flinksConfig.connectionLimit.canConnect ? 'sv-limit-exceeded' : ''}`}>
                  {flinksConfig.connectionLimit.canConnect ? (
                    t('transactions.connectionLimit', {
                      remaining: flinksConfig.connectionLimit.remaining,
                      max: flinksConfig.connectionLimit.max
                    })
                  ) : (
                    t('transactions.connectionLimitExceeded')
                  )}
                </p>
              )}
              <div className="sv-txn-bank-list">
                {CREDIT_CARD_BANKS.map((bank) => (
                  <div
                    key={bank.id}
                    className="sv-txn-bank-item"
                    onClick={() => handleDemoConnect(bank.id, bank.fullName)}
                  >
                    <img
                      src={BANK_LOGOS[bank.id] || '/logos/bank-default.png'}
                      alt={bank.name}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/logos/bank-default.png'
                      }}
                    />
                    <span>{bank.name}</span>
                    <RightOutlined />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Flinks Connect Iframe Modal */}
        {showFlinksIframe && flinksConfig && (
          <div className="sv-flinks-modal-overlay">
            <div className="sv-flinks-modal">
              <div className="sv-flinks-modal-header">
                <h3>{t('transactions.connectBank')}</h3>
                <button
                  className="sv-flinks-close-btn"
                  onClick={() => {
                    setShowFlinksIframe(false)
                    setIframeLoading(true)
                  }}
                >
                  <CloseOutlined />
                </button>
              </div>
              <div className="sv-flinks-iframe-container">
                {iframeLoading && (
                  <div className="sv-flinks-loading">
                    <Spin size="large" />
                    <p>{t('transactions.connectingBank')}</p>
                  </div>
                )}
                <iframe
                  ref={iframeRef}
                  src={flinksConnectUrl}
                  title="Flinks Connect"
                  className="sv-flinks-iframe"
                  style={{ opacity: iframeLoading ? 0 : 1 }}
                  allow="camera"
                />
              </div>
            </div>
          </div>
        )}

        <style>{styles}</style>
      </div>
    )
  }

  // Calculate missed cashback percentage
  const missedPercentage = summary
    ? (summary.totalMissedCashback / (summary.totalActualCashback + summary.totalMissedCashback)) * 100
    : 0

  return (
    <div className="sv-transactions-page">
      {/* Header */}
      <div className="sv-txn-header">
        <h1>{t('transactions.title')}</h1>
        <button
          className="sv-txn-refresh-btn"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <SyncOutlined spin={refreshing} />
        </button>
      </div>

      {/* Demo Mode Banner */}
      <div className="sv-txn-demo-banner">
        <span className="sv-txn-demo-icon">💡</span>
        <span>{t('transactions.startupNoticeShort')}</span>
      </div>

      {/* Summary Card */}
      {summary && (
        <div className="sv-txn-summary-card">
          <div className="sv-txn-summary-header">
            <span className="sv-txn-summary-title">{t('transactions.last90Days')}</span>
          </div>

          <div className="sv-txn-summary-stats">
            <div className="sv-txn-stat">
              <span className="sv-txn-stat-value">${summary.totalSpending.toFixed(0)}</span>
              <span className="sv-txn-stat-label">{t('transactions.totalSpent')}</span>
            </div>
            <div className="sv-txn-stat sv-txn-stat-highlight">
              <span className="sv-txn-stat-value sv-txn-missed">
                ${summary.totalMissedCashback.toFixed(2)}
              </span>
              <span className="sv-txn-stat-label">{t('transactions.missedCashback')}</span>
            </div>
            <div className="sv-txn-stat">
              <span className="sv-txn-stat-value">${summary.totalActualCashback.toFixed(2)}</span>
              <span className="sv-txn-stat-label">{t('transactions.earnedCashback')}</span>
            </div>
          </div>

          {summary.totalMissedCashback > 0 && (
            <div className="sv-txn-opportunity">
              <Progress
                percent={100 - missedPercentage}
                showInfo={false}
                strokeColor="#10b981"
                trailColor="#e5e0d5"
              />
              <p>
                {t('transactions.opportunityText', {
                  amount: summary.totalMissedCashback.toFixed(2),
                  percentage: missedPercentage.toFixed(0),
                })}
              </p>
            </div>
          )}

          {/* Debit Card Tip - Simplified */}
          {summary.debitTransactions && summary.debitTransactions > 0 && (
            <div className="sv-txn-debit-tip">
              <span className="sv-txn-debit-tip-icon">💡</span>
              <span className="sv-txn-debit-tip-text">
                {t('transactions.debitTip', {
                  count: summary.debitTransactions,
                  amount: summary.debitSpending?.toFixed(0) || '0',
                  missed: summary.debitMissedCashback?.toFixed(2) || '0.00'
                })}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="sv-txn-tabs">
        <button
          className={`sv-txn-tab ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          {t('transactions.tabSummary')}
        </button>
        <button
          className={`sv-txn-tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          {t('transactions.tabTransactions')}
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'summary' ? (
        <div className="sv-txn-content">
          {/* Category Breakdown */}
          <h3>{t('transactions.categoryBreakdown')}</h3>
          {summary?.categoryBreakdown && summary.categoryBreakdown.length > 0 ? (
            <div className="sv-txn-categories">
              {summary.categoryBreakdown.map((cat: CategoryMissedCashback) => (
                <div key={cat.category} className="sv-txn-category-card">
                  <div className="sv-txn-category-left">
                    <span className="sv-txn-category-icon">
                      {CATEGORY_ICONS[cat.category] || '📦'}
                    </span>
                    <div className="sv-txn-category-info">
                      <span className="sv-txn-category-name">
                        {t(`categories.${cat.category}`, cat.category)}
                      </span>
                      <span className="sv-txn-category-spending">
                        ${cat.spending.toFixed(0)} {t('transactions.spent')}
                      </span>
                    </div>
                  </div>
                  <div className="sv-txn-category-right">
                    {cat.missedCashback > 0 ? (
                      <>
                        <span className="sv-txn-category-missed">
                          -${cat.missedCashback.toFixed(2)}
                        </span>
                        {cat.bestCardName && (
                          <span className="sv-txn-category-tip">
                            {t('transactions.shouldUse')}:
                            <img
                              src={getBankLogo(cat.bestCardBank)}
                              alt={cat.bestCardBank || ''}
                              className="sv-txn-card-logo-sm"
                            />
                            {cat.bestCardName}
                          </span>
                        )}
                      </>
                    ) : (
                      <CheckCircleOutlined className="sv-txn-category-ok" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <Empty description={t('transactions.noCategories')} />
          )}

          {/* Top Recommendations */}
          {summary?.topRecommendations && summary.topRecommendations.length > 0 && (
            <>
              <h3>{t('transactions.recommendations')}</h3>
              <div className="sv-txn-recommendations">
                {summary.topRecommendations.map((rec) => (
                  <div key={rec.cardId} className="sv-txn-rec-card">
                    <img
                      src={getBankLogo(rec.bank)}
                      alt={rec.bank}
                      className="sv-txn-rec-logo"
                    />
                    <div className="sv-txn-rec-info">
                      <span className="sv-txn-rec-name">
                        {rec.bank} {rec.cardName}
                      </span>
                      <span className="sv-txn-rec-cats">
                        {t('transactions.bestFor')}: {rec.bestCategories.map(c => t(`categories.${c}`, c)).join(', ')}
                      </span>
                    </div>
                    <span className="sv-txn-rec-savings">
                      +${rec.potentialSavings.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="sv-txn-content">
          {/* Transaction List */}
          {transactions.length > 0 ? (
            <>
              <div className="sv-txn-list">
                {transactions
                  .slice((currentPage - 1) * pageSize, currentPage * pageSize)
                  .map((txn) => (
                  <div key={txn.id} className="sv-txn-item">
                    <div className="sv-txn-item-left">
                      <span className="sv-txn-item-icon">
                        {CATEGORY_ICONS[txn.category] || '📦'}
                      </span>
                      <div className="sv-txn-item-info">
                        <span className="sv-txn-item-merchant">{txn.merchant}</span>
                        <span className="sv-txn-item-date">
                          {new Date(txn.transactionDate).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                    <div className="sv-txn-item-right">
                      <span className="sv-txn-item-amount">
                        ${Math.abs(txn.amount).toFixed(2)}
                      </span>
                      {txn.missedCashback && txn.missedCashback > 0 ? (
                        <div className="sv-txn-card-compare">
                          <div className="sv-txn-card-used">
                            <span className="sv-txn-card-label">{t('transactions.used')}:</span>
                            {txn.cardUsedName ? (
                              <>
                                <img
                                  src={getBankLogo(txn.cardUsedName.split(' ')[0])}
                                  alt=""
                                  className="sv-txn-card-logo-xs"
                                />
                                <span className="sv-txn-card-name">{txn.cardUsedName}</span>
                              </>
                            ) : txn.isDebitTransaction ? (
                              <span className="sv-txn-card-name sv-txn-card-debit">{t('transactions.debitCard')}</span>
                            ) : (
                              <span className="sv-txn-card-name sv-txn-card-unknown">{t('transactions.unknownCard')}</span>
                            )}
                          </div>
                          <div className="sv-txn-card-best">
                            <span className="sv-txn-card-label">{t('transactions.shouldUse')}:</span>
                            <img
                              src={getBankLogo(txn.bestCardBank)}
                              alt={txn.bestCardBank || ''}
                              className="sv-txn-card-logo-xs"
                            />
                            <span className="sv-txn-card-name">{txn.bestCardName}</span>
                            <span className="sv-txn-card-rate">({((txn.bestCardRate || 0) * 100).toFixed(0)}%)</span>
                          </div>
                          <span className="sv-txn-item-missed-amount">
                            -{txn.missedCashback.toFixed(2)}
                          </span>
                        </div>
                      ) : (
                        <span className="sv-txn-item-earned">
                          <CheckCircleOutlined /> +${(txn.actualCashback || 0).toFixed(2)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {transactions.length > pageSize && (
                <div className="sv-txn-pagination">
                  <Pagination
                    current={currentPage}
                    total={transactions.length}
                    pageSize={pageSize}
                    onChange={(page) => setCurrentPage(page)}
                    showSizeChanger={false}
                    size="small"
                  />
                </div>
              )}
            </>
          ) : (
            <Empty description={t('transactions.noTransactions')} />
          )}
        </div>
      )}

      {/* Connected Banks */}
      <div className="sv-txn-banks">
        <h3>{t('transactions.connectedBanks')}</h3>
        {connections.map((conn) => (
          <div key={conn.id} className="sv-txn-bank-conn">
            <img
              src={getBankLogo(conn.institutionName)}
              alt={conn.institutionName}
            />
            <div className="sv-txn-bank-info">
              <span className="sv-txn-bank-name">{conn.institutionName}</span>
              <span className="sv-txn-bank-status">
                {conn.status === 'CONNECTED' && <CheckCircleOutlined className="status-ok" />}
                {conn.status === 'ERROR' && <ExclamationCircleOutlined className="status-error" />}
                {conn.lastSyncAt && (
                  <span>{t('transactions.lastSync')}: {new Date(conn.lastSyncAt + 'Z').toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                )}
              </span>
            </div>
            <div className="sv-txn-bank-actions">
              <button
                className="sv-txn-resync-btn"
                onClick={() => handleResync(conn.id, conn.institutionName)}
                title={t('transactions.resync')}
              >
                <SyncOutlined />
              </button>
              <button
                className="sv-txn-disconnect-btn"
                onClick={() => handleDisconnect(conn.id, conn.institutionName)}
                title={t('transactions.disconnect')}
              >
                <DeleteOutlined />
              </button>
            </div>
          </div>
        ))}
        <button className="sv-txn-add-bank" onClick={handleConnectBank}>
          <PlusOutlined /> {t('transactions.addBank')}
        </button>

        {/* Powered by Flinks */}
        <div className="sv-txn-flinks-footer">
          <span className="sv-txn-flinks-text">{t('transactions.openBankingBy')}</span>
          <a href="https://www.flinks.com" target="_blank" rel="noopener noreferrer" className="sv-txn-flinks-logo">
            <img src="/logos/flinks.png" alt="Flinks" />
          </a>
        </div>
      </div>

      {/* Bank Connect Modal */}
      {showConnectModal && (
        <div className="sv-txn-modal-overlay" onClick={() => setShowConnectModal(false)}>
          <div className="sv-txn-modal sv-txn-modal-banks" onClick={(e) => e.stopPropagation()}>
            <div className="sv-txn-modal-header">
              <h3>{t('transactions.selectBank')}</h3>
              <button className="sv-txn-modal-close" onClick={() => setShowConnectModal(false)}>
                <CloseOutlined />
              </button>
            </div>
            {/* Connection limit info */}
            {flinksConfig?.connectionLimit && (
              <p className={`sv-txn-modal-desc ${!flinksConfig.connectionLimit.canConnect ? 'sv-limit-exceeded' : ''}`}>
                {flinksConfig.connectionLimit.canConnect ? (
                  t('transactions.connectionLimit', {
                    remaining: flinksConfig.connectionLimit.remaining,
                    max: flinksConfig.connectionLimit.max
                  })
                ) : (
                  t('transactions.connectionLimitExceeded')
                )}
              </p>
            )}
            <div className="sv-txn-bank-list">
              {CREDIT_CARD_BANKS.map((bank) => (
                <div
                  key={bank.id}
                  className="sv-txn-bank-item"
                  onClick={() => handleDemoConnect(bank.id, bank.fullName)}
                >
                  <img
                    src={BANK_LOGOS[bank.id] || '/logos/bank-default.png'}
                    alt={bank.name}
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/logos/bank-default.png'
                    }}
                  />
                  <span>{bank.name}</span>
                  <RightOutlined />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Flinks Connect Iframe Modal */}
      {showFlinksIframe && flinksConfig && (
        <div className="sv-flinks-modal-overlay">
          <div className="sv-flinks-modal">
            <div className="sv-flinks-modal-header">
              <h3>{t('transactions.connectBank')}</h3>
              <button
                className="sv-flinks-close-btn"
                onClick={() => {
                  setShowFlinksIframe(false)
                  setIframeLoading(true)
                }}
              >
                <CloseOutlined />
              </button>
            </div>
            <div className="sv-flinks-iframe-container">
              {iframeLoading && (
                <div className="sv-flinks-loading">
                  <Spin size="large" />
                  <p>{t('transactions.connectingBank')}</p>
                </div>
              )}
              <iframe
                ref={iframeRef}
                src={flinksConnectUrl}
                title="Flinks Connect"
                className="sv-flinks-iframe"
                style={{ opacity: iframeLoading ? 0 : 1 }}
                allow="camera"
              />
            </div>
          </div>
        </div>
      )}

      <style>{styles}</style>
    </div>
  )
}

const styles = `
  .sv-transactions-page {
    padding: 20px;
    min-height: calc(100vh - 140px);
    max-width: 800px;
    margin: 0 auto;
  }

  @media (max-width: 640px) {
    .sv-transactions-page {
      padding: 16px 20px;
      min-height: calc(100vh - 70px);
    }
  }

  .sv-txn-login-prompt,
  .sv-txn-empty {
    text-align: center;
    padding: 40px 20px;
  }

  .sv-txn-login-icon {
    font-size: 48px;
    margin-bottom: 16px;
    display: block;
  }

  .sv-txn-empty-icon {
    font-size: 56px;
    display: block;
    margin-bottom: 16px;
  }

  .sv-txn-login-prompt h2,
  .sv-txn-empty h2 {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 8px;
  }

  .sv-txn-login-prompt p,
  .sv-txn-empty p {
    font-size: 14px;
    color: #6b7280;
    margin: 0 0 20px;
    line-height: 1.6;
  }

  .sv-txn-security-features {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 24px auto;
    max-width: 300px;
    text-align: left;
  }

  .sv-txn-security-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #4b5563;
  }

  .sv-txn-security-emoji {
    font-size: 18px;
    width: 24px;
    flex-shrink: 0;
  }

  .sv-txn-login-btn,
  .sv-txn-connect-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px 32px;
    background: #111827;
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .sv-txn-login-btn:hover,
  .sv-txn-connect-btn:hover {
    background: #1f2937;
  }

  .sv-txn-connection-limit-info {
    margin-top: 16px;
    font-size: 13px;
    color: #6b7280;
  }

  .sv-txn-connection-limit-info.sv-limit-exceeded {
    color: #dc2626;
  }

  .sv-txn-startup-notice {
    margin: 20px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .sv-txn-startup-icon {
    font-size: 14px;
    line-height: 1;
  }

  .sv-txn-startup-notice p {
    margin: 0;
    font-size: 12px;
    color: #9ca3af;
    line-height: 1.4;
  }

  .sv-txn-demo-banner {
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }

  .sv-txn-demo-icon {
    font-size: 12px;
    line-height: 1;
  }

  .sv-txn-demo-banner span:last-child {
    font-size: 12px;
    color: #9ca3af;
  }

  .sv-txn-flinks {
    margin-top: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .sv-txn-flinks-text {
    font-size: 11px;
    color: #9ca3af;
  }

  .sv-txn-flinks-logo {
    display: block;
  }

  .sv-txn-flinks-logo img {
    height: 24px;
    width: auto;
    opacity: 0.7;
    transition: opacity 0.2s;
    border-radius: 4px;
  }

  .sv-txn-flinks-logo:hover img {
    opacity: 1;
  }

  .sv-txn-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100px 20px;
    color: #6b7280;
  }

  .sv-txn-loading p {
    margin-top: 16px;
  }

  .sv-txn-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    margin-bottom: 8px;
  }

  .sv-txn-header h1 {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin: 0;
  }

  .sv-txn-refresh-btn {
    width: 36px;
    height: 36px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #6b7280;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .sv-txn-refresh-btn:hover:not(:disabled) {
    background: #f3f4f6;
  }

  .sv-txn-refresh-btn:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .sv-txn-summary-card {
    padding: 16px 0;
    margin-bottom: 16px;
  }

  .sv-txn-summary-header {
    margin-bottom: 12px;
  }

  .sv-txn-summary-title {
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .sv-txn-summary-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .sv-txn-stat {
    text-align: center;
    flex: 1;
  }

  .sv-txn-stat-value {
    display: block;
    font-size: 18px;
    font-weight: 700;
    color: #111827;
  }

  .sv-txn-stat-value.sv-txn-missed {
    color: #ef4444;
  }

  .sv-txn-stat-label {
    display: block;
    font-size: 11px;
    color: #9ca3af;
    margin-top: 4px;
  }

  .sv-txn-opportunity {
    padding: 12px 0;
  }

  .sv-txn-opportunity p {
    font-size: 12px;
    color: #374151;
    margin: 8px 0 0;
    text-align: center;
  }

  .sv-txn-debit-tip {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 10px 12px;
    background: #fffbeb;
    border-radius: 8px;
    border: 1px solid #fef3c7;
  }

  .sv-txn-debit-tip-icon {
    font-size: 14px;
    line-height: 1;
  }

  .sv-txn-debit-tip-text {
    font-size: 12px;
    color: #92400e;
    line-height: 1.4;
  }

  .sv-txn-tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 16px;
  }

  .sv-txn-tab {
    flex: 1;
    padding: 12px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    color: #6b7280;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: -1px;
  }

  .sv-txn-tab.active {
    color: #111827;
    border-bottom-color: #111827;
  }

  .sv-txn-content h3 {
    font-size: 12px;
    font-weight: 500;
    color: #9ca3af;
    margin: 16px 0 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .sv-txn-categories {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .sv-txn-category-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0;
    border-bottom: 1px solid rgba(0,0,0,0.04);
  }

  .sv-txn-category-card:last-child {
    border-bottom: none;
  }

  .sv-txn-category-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .sv-txn-category-icon {
    font-size: 20px;
  }

  .sv-txn-category-info {
    display: flex;
    flex-direction: column;
  }

  .sv-txn-category-name {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
  }

  .sv-txn-category-spending {
    font-size: 12px;
    color: #9ca3af;
  }

  .sv-txn-category-right {
    text-align: right;
  }

  .sv-txn-category-missed {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #ef4444;
  }

  .sv-txn-category-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: #6b7280;
    margin-top: 2px;
  }

  .sv-txn-card-logo-sm {
    width: 16px;
    height: 16px;
    object-fit: contain;
    flex-shrink: 0;
    border-radius: 3px;
  }

  .sv-txn-card-logo-xs {
    width: 14px;
    height: 14px;
    object-fit: contain;
    flex-shrink: 0;
    border-radius: 3px;
  }

  .sv-txn-category-ok {
    font-size: 18px;
    color: #10b981;
  }

  .sv-txn-recommendations {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 16px;
  }

  .sv-txn-rec-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(0,0,0,0.04);
  }

  .sv-txn-rec-card:last-child {
    border-bottom: none;
  }

  .sv-txn-rec-icon {
    font-size: 20px;
  }

  .sv-txn-rec-logo {
    width: 28px;
    height: 28px;
    object-fit: contain;
    flex-shrink: 0;
    border-radius: 6px;
  }

  .sv-txn-rec-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .sv-txn-rec-name {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
  }

  .sv-txn-rec-cats {
    font-size: 12px;
    color: #6b7280;
  }

  .sv-txn-rec-savings {
    font-size: 14px;
    font-weight: 600;
    color: #10b981;
  }

  .sv-txn-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .sv-txn-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .sv-txn-item:last-child {
    border-bottom: none;
  }

  .sv-txn-item-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .sv-txn-item-icon {
    font-size: 18px;
  }

  .sv-txn-item-info {
    display: flex;
    flex-direction: column;
  }

  .sv-txn-item-merchant {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
  }

  .sv-txn-item-date {
    font-size: 12px;
    color: #9ca3af;
  }

  .sv-txn-item-right {
    text-align: right;
  }

  .sv-txn-item-amount {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #111827;
  }

  .sv-txn-item-missed {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #ef4444;
    cursor: help;
  }

  .sv-txn-card-compare {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
  }

  .sv-txn-card-used,
  .sv-txn-card-best {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    white-space: nowrap;
    flex-wrap: nowrap;
  }

  .sv-txn-card-label {
    color: #9ca3af;
    flex-shrink: 0;
  }

  .sv-txn-card-name {
    color: #374151;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex-shrink: 1;
  }

  .sv-txn-card-unknown {
    color: #9ca3af;
    font-style: italic;
  }

  .sv-txn-card-debit {
    color: #f59e0b;
    font-weight: 500;
  }

  .sv-txn-card-rate {
    color: #10b981;
    font-weight: 500;
    flex-shrink: 0;
    white-space: nowrap;
  }

  .sv-txn-item-missed-amount {
    font-size: 12px;
    font-weight: 600;
    color: #ef4444;
    margin-top: 2px;
  }

  .sv-txn-item-earned {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #10b981;
  }

  .sv-txn-pagination {
    display: flex;
    justify-content: center;
    padding: 24px 0 32px;
  }

  .sv-txn-pagination .ant-pagination {
    display: flex;
    gap: 8px;
  }

  .sv-txn-pagination .ant-pagination-item,
  .sv-txn-pagination .ant-pagination-prev,
  .sv-txn-pagination .ant-pagination-next {
    min-width: 36px;
    height: 36px;
    line-height: 34px;
    border-radius: 8px;
    margin: 0;
  }

  .sv-txn-pagination .ant-pagination-item a {
    padding: 0;
  }

  .sv-txn-banks {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(0,0,0,0.06);
  }

  .sv-txn-banks h3 {
    font-size: 12px;
    font-weight: 500;
    color: #9ca3af;
    margin: 0 0 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .sv-txn-bank-conn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .sv-txn-bank-conn img {
    width: 36px;
    height: 36px;
    object-fit: contain;
    border-radius: 8px;
  }

  .sv-txn-bank-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .sv-txn-bank-name {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
  }

  .sv-txn-bank-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #9ca3af;
  }

  .sv-txn-bank-status .status-ok {
    font-size: 14px;
    color: #10b981;
  }

  .sv-txn-bank-status .status-error {
    font-size: 14px;
    color: #f59e0b;
  }

  .sv-txn-bank-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
  }

  .sv-txn-resync-btn,
  .sv-txn-disconnect-btn {
    padding: 8px;
    border: none;
    background: transparent;
    color: #9ca3af;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .sv-txn-resync-btn:hover {
    background: #f0fdf4;
    color: #22c55e;
  }

  .sv-txn-disconnect-btn:hover {
    background: #fef2f2;
    color: #ef4444;
  }

  .sv-txn-add-bank {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px;
    margin-top: 12px;
    border: 2px dashed #e5e7eb;
    border-radius: 10px;
    background: transparent;
    color: #6b7280;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .sv-txn-add-bank:hover {
    border-color: #9ca3af;
    color: #374151;
  }

  .sv-txn-flinks-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 24px;
    margin-bottom: 24px;
    padding-top: 16px;
    border-top: 1px solid rgba(0,0,0,0.04);
  }

  .sv-txn-flinks-footer .sv-txn-flinks-text {
    font-size: 11px;
    color: #9ca3af;
  }

  .sv-txn-flinks-footer .sv-txn-flinks-logo img {
    height: 18px;
    width: auto;
    opacity: 0.6;
    transition: opacity 0.2s;
    border-radius: 4px;
  }

  .sv-txn-flinks-footer .sv-txn-flinks-logo:hover img {
    opacity: 1;
  }

  .sv-txn-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
  }

  .sv-txn-modal {
    background: white;
    border-radius: 16px;
    padding: 24px;
    width: 100%;
    max-width: 480px;
  }

  .sv-txn-modal-banks {
    max-height: 85vh;
    display: flex;
    flex-direction: column;
  }

  .sv-txn-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    flex-shrink: 0;
  }

  .sv-txn-modal-close {
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
  }

  .sv-txn-modal-close:hover {
    background: #e5e7eb;
    color: #111827;
  }

  .sv-txn-modal-desc {
    flex-shrink: 0;
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 12px;
  }

  .sv-txn-modal-desc.sv-limit-exceeded {
    color: #dc2626;
  }

  .sv-txn-modal-banks .sv-txn-bank-list {
    overflow-y: auto;
    max-height: calc(85vh - 120px);
    margin: 0 -24px;
    padding: 0 24px;
  }

  @media (min-width: 641px) {
    .sv-txn-modal {
      padding: 32px;
      min-width: 420px;
    }

    .sv-txn-modal-banks .sv-txn-bank-list {
      margin: 0 -32px;
      padding: 0 32px;
      max-height: calc(85vh - 140px);
    }
  }

  @media (max-width: 640px) {
    .sv-txn-modal-overlay {
      padding: 0;
      overscroll-behavior: contain;
      align-items: center;
      justify-content: center;
    }

    .sv-txn-modal-banks {
      max-height: 70vh;
      border-radius: 16px;
      width: calc(100% - 32px);
      max-width: 100%;
      margin: 16px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      display: flex;
      flex-direction: column;
    }

    .sv-txn-modal-banks .sv-txn-modal-header {
      flex-shrink: 0;
    }

    .sv-txn-modal-banks .sv-txn-modal-desc {
      flex-shrink: 0;
    }

    .sv-txn-modal-banks .sv-txn-bank-list {
      flex: 1;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: contain;
      min-height: 0;
    }
  }

  .sv-txn-modal h3 {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    margin: 0;
    text-transform: none;
    letter-spacing: 0;
  }

  .sv-txn-modal p {
    font-size: 13px;
    color: #6b7280;
    margin: 0 0 16px;
  }

  .sv-txn-bank-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .sv-txn-bank-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .sv-txn-bank-item:hover {
    border-color: #9ca3af;
    background: #f9fafb;
  }

  .sv-txn-bank-item:active {
    opacity: 0.6;
  }

  .sv-txn-bank-item img {
    width: 32px;
    height: 32px;
    object-fit: contain;
  }

  .sv-txn-bank-item > span {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
  }

  .sv-txn-bank-item .anticon {
    color: #d1d5db;
    font-size: 10px;
    margin-left: auto;
    flex-shrink: 0;
  }

  .sv-txn-bank-item img {
    border-radius: 6px;
  }

  /* Dark mode for bank modal */
  html.dark-mode .sv-txn-modal {
    background: #1a1a1a;
  }

  html.dark-mode .sv-txn-modal h3 {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-modal p {
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-modal-close {
    background: #333;
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-modal-close:hover {
    background: #444;
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-bank-item {
    border-color: #333;
    background: transparent;
  }

  html.dark-mode .sv-txn-bank-item:hover {
    border-color: #555;
    background: #252525;
  }

  html.dark-mode .sv-txn-bank-item > span {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-bank-item .anticon {
    color: #666;
  }

  /* Flinks Connect Iframe Modal */
  .sv-flinks-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
  }

  .sv-flinks-modal {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 560px;
    height: 85vh;
    max-height: 700px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }

  .sv-flinks-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
  }

  .sv-flinks-modal-header h3 {
    font-size: 17px;
    font-weight: 600;
    color: #111827;
    margin: 0;
    text-transform: none;
    letter-spacing: 0;
  }

  .sv-flinks-close-btn {
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
  }

  .sv-flinks-close-btn:hover {
    background: #e5e7eb;
    color: #111827;
  }

  .sv-flinks-iframe-container {
    flex: 1;
    position: relative;
    overflow: hidden;
  }

  .sv-flinks-loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #f9fafb;
    gap: 16px;
  }

  .sv-flinks-loading p {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
  }

  .sv-flinks-iframe {
    width: 100%;
    height: 100%;
    border: none;
    transition: opacity 0.3s ease;
  }

  @media (max-width: 640px) {
    .sv-flinks-modal-overlay {
      padding: 16px;
      padding-top: calc(env(safe-area-inset-top, 20px) + 60px);
      padding-bottom: calc(env(safe-area-inset-bottom, 20px) + 70px);
    }

    .sv-flinks-modal {
      max-width: 100%;
      width: 100%;
      height: 100%;
      max-height: 100%;
      border-radius: 16px;
    }

    .sv-flinks-modal-header {
      padding: 12px 16px;
    }

    .sv-flinks-modal-header h3 {
      font-size: 16px;
    }
  }

  /* Dark mode for Flinks modal */
  html.dark-mode .sv-flinks-modal {
    background: #1a1a1a;
  }

  html.dark-mode .sv-flinks-modal-header {
    border-bottom-color: #333;
  }

  html.dark-mode .sv-flinks-modal-header h3 {
    color: #f5f5f5;
  }

  html.dark-mode .sv-flinks-close-btn {
    background: #333;
    color: #a0a0a0;
  }

  html.dark-mode .sv-flinks-close-btn:hover {
    background: #444;
    color: #f5f5f5;
  }

  /* Dark mode for debit tip */
  html.dark-mode .sv-txn-debit-tip {
    background: #2d2815;
    border-color: #78350f;
  }

  html.dark-mode .sv-txn-debit-tip-text {
    color: #fbbf24;
  }

  /* ========================================
     Dark Mode - Transactions Page
     ======================================== */
  html.dark-mode .sv-txn-header h1 {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-refresh-btn:hover:not(:disabled) {
    background: #333;
  }

  /* Summary stats */
  html.dark-mode .sv-txn-stat-value {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-opportunity p {
    color: #a0a0a0;
  }

  /* Tabs */
  html.dark-mode .sv-txn-tabs {
    border-bottom-color: #333;
  }

  html.dark-mode .sv-txn-tab {
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-tab.active {
    color: #f5f5f5;
    border-bottom-color: #f5f5f5;
  }

  /* Categories */
  html.dark-mode .sv-txn-category-name {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-category-card {
    border-bottom-color: #333;
  }

  /* Recommendations */
  html.dark-mode .sv-txn-rec-name {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-rec-cats {
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-rec-card {
    border-bottom-color: #333;
  }

  /* Transaction list */
  html.dark-mode .sv-txn-item {
    border-bottom-color: #333;
  }

  html.dark-mode .sv-txn-item-merchant {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-item-amount {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-card-name {
    color: #d0d0d0;
  }

  /* Banks */
  html.dark-mode .sv-txn-banks {
    border-top-color: #333;
  }

  html.dark-mode .sv-txn-bank-conn {
    border-bottom-color: #333;
  }

  html.dark-mode .sv-txn-bank-name {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-add-bank {
    border-color: #444;
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-add-bank:hover {
    border-color: #666;
    color: #f5f5f5;
  }

  /* Login/Empty prompts */
  html.dark-mode .sv-txn-login-prompt h2,
  html.dark-mode .sv-txn-empty h2 {
    color: #f5f5f5;
  }

  html.dark-mode .sv-txn-login-prompt p,
  html.dark-mode .sv-txn-empty p {
    color: #a0a0a0;
  }

  html.dark-mode .sv-txn-security-item {
    color: #d0d0d0;
  }
`

export default TransactionsPage
