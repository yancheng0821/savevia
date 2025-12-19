import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowRightOutlined, ShareAltOutlined, LinkOutlined, RedoOutlined, MailOutlined, DownOutlined } from '@ant-design/icons'
import { Capacitor } from '@capacitor/core'
import { Share } from '@capacitor/share'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { useAuthStore } from '../stores/useAuthStore'
import { optimizerApi } from '../services/api'
import CardUpgradeRecommendation from '../components/CardUpgradeRecommendation'
import type { SpendingCategory } from '../types'

// Check if running on native platform
const isNativeApp = Capacitor.isNativePlatform()

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
    const orderA = indexA === -1 ? 999 : indexA
    const orderB = indexB === -1 ? 999 : indexB
    return orderA - orderB
  })
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

// Social Media Icons
const XIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#000000">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
)

const FacebookIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#1877F2">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
)

const LinkedInIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#0A66C2">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
)

const WhatsAppIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#25D366">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
)

const WeChatIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#07C160">
    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 00.167-.054l1.903-1.114a.864.864 0 01.717-.098 10.16 10.16 0 002.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178A1.17 1.17 0 014.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178 1.17 1.17 0 01-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 01.598.082l1.584.926a.272.272 0 00.14.045c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 01-.023-.156.49.49 0 01.201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.269-.03-.407-.03zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 01-.969.983.976.976 0 01-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 01-.969.983.976.976 0 01-.969-.983c0-.542.434-.982.969-.982z"/>
  </svg>
)

const TelegramIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#0088CC">
    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
  </svg>
)

const RedditIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="#FF4500">
    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
  </svg>
)

function ResultPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { result, reset, selectedCards, monthlySpending } = useOptimizerStore()
  const { isAuthenticated } = useAuthStore()
  const [sharing, setSharing] = useState(false)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [showShareMenu, setShowShareMenu] = useState(false)
  const [expandedAi, setExpandedAi] = useState<Set<SpendingCategory>>(new Set())
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 640)
  const shareMenuRef = useRef<HTMLDivElement>(null)

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
    if (!result) {
      navigate('/cards')
    }
  }, [result, navigate])

  // Close share menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (shareMenuRef.current && !shareMenuRef.current.contains(event.target as Node)) {
        setShowShareMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!result) {
    return null
  }

  const handleStartOver = () => {
    reset()
    navigate('/cards')
  }

  const getShareUrl = async (): Promise<string | null> => {
    if (shareUrl) return shareUrl
    if (!result || sharing) return null

    setSharing(true)
    try {
      const response = await optimizerApi.shareResult(result)
      if (response.code === 200 && response.data) {
        // Use frontend URL directly for better user experience (no redirect page)
        const url = `https://savevia.app/share/${response.data.shareId}`
        setShareUrl(url)
        return url
      }
    } catch (err) {
      console.error('Failed to share result:', err)
    } finally {
      setSharing(false)
    }
    return null
  }

  const handleShareClick = async () => {
    // On native app, use system share sheet directly
    if (isNativeApp) {
      const url = await getShareUrl()
      if (url) {
        try {
          await Share.share({
            title: 'SaveVia',
            text: `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia!`,
            url: url,
            dialogTitle: 'Share Results'
          })
        } catch (e) {
          // User cancelled - do nothing
        }
      }
    } else {
      // On web, show dropdown menu
      setShowShareMenu(!showShareMenu)
    }
  }

  const handleCopyLink = async () => {
    const url = await getShareUrl()
    if (url) {
      await navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 3000)
    }
    setShowShareMenu(false)
  }

  const shareToTwitter = async () => {
    const url = await getShareUrl()
    if (url) {
      const text = `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia!`
      window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareToFacebook = async () => {
    const url = await getShareUrl()
    if (url) {
      window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareToLinkedIn = async () => {
    const url = await getShareUrl()
    if (url) {
      window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareToWhatsApp = async () => {
    const url = await getShareUrl()
    if (url) {
      const text = `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia! Check it out: ${url}`
      window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareToWeChat = async () => {
    const url = await getShareUrl()
    if (url) {
      if (isNativeApp) {
        // On native app, use system share sheet which includes WeChat
        try {
          await Share.share({
            title: 'SaveVia',
            text: `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia!`,
            url: url,
            dialogTitle: 'Share to WeChat'
          })
        } catch (e) {
          // User cancelled or error - fallback to copy
          await navigator.clipboard.writeText(url)
          setCopied(true)
          setTimeout(() => setCopied(false), 3000)
        }
      } else {
        // On web, copy link (WeChat doesn't have web share URL)
        await navigator.clipboard.writeText(url)
        setCopied(true)
        setTimeout(() => setCopied(false), 3000)
      }
    }
    setShowShareMenu(false)
  }

  const shareToTelegram = async () => {
    const url = await getShareUrl()
    if (url) {
      const text = `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia!`
      window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareToReddit = async () => {
    const url = await getShareUrl()
    if (url) {
      const title = `I just saved $${result.netAnnualSavings.toFixed(0)}/year with SaveVia!`
      window.open(`https://www.reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`, '_blank')
    }
    setShowShareMenu(false)
  }

  const shareViaEmail = async () => {
    const url = await getShareUrl()
    if (url) {
      const subject = `Check out SaveVia - I saved $${result.netAnnualSavings.toFixed(0)}/year!`
      const body = `I just optimized my credit card rewards with SaveVia and I'm saving $${result.netAnnualSavings.toFixed(0)} per year!\n\nCheck it out: ${url}`
      window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    }
    setShowShareMenu(false)
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative' }}>
      {/* Top Bar - Logo (mobile only) and Share */}
      <div className="sv-result-top-bar">
        {/* Logo - Left (mobile only) */}
        <img src="/logo-full.svg" alt="SaveVia" className="sv-result-logo-mobile" />

        {/* Share Button - Right */}
        <div ref={shareMenuRef} style={{ position: 'relative', marginLeft: 'auto' }}>
        <button
          onClick={handleShareClick}
          disabled={sharing}
          className="share-btn"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 0',
            fontSize: '14px',
            fontWeight: '500',
            border: 'none',
            background: 'transparent',
            color: '#6b7280',
            cursor: sharing ? 'not-allowed' : 'pointer',
            opacity: sharing ? 0.7 : 1,
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#111827'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6b7280'}
        >
          <ShareAltOutlined /> {sharing ? t('result.sharing') : t('result.share')}
        </button>

        {/* Share Menu Dropdown */}
        {showShareMenu && (
          <div className="sv-share-menu">
            <button
              onClick={handleCopyLink}
              className={`share-menu-item ${copied ? 'copied' : ''}`}
            >
              <LinkOutlined />
              {copied ? t('result.copied') : t('result.copyLink')}
            </button>
            <button onClick={shareToTwitter} className="share-menu-item">
              <XIcon /> X
            </button>
            <button onClick={shareToFacebook} className="share-menu-item">
              <FacebookIcon /> Facebook
            </button>
            <button onClick={shareToLinkedIn} className="share-menu-item">
              <LinkedInIcon /> LinkedIn
            </button>
            <button onClick={shareToWhatsApp} className="share-menu-item">
              <WhatsAppIcon /> WhatsApp
            </button>
            <button onClick={shareToWeChat} className="share-menu-item">
              <WeChatIcon /> WeChat
            </button>
            <button onClick={shareToTelegram} className="share-menu-item">
              <TelegramIcon /> Telegram
            </button>
            <button onClick={shareToReddit} className="share-menu-item">
              <RedditIcon /> Reddit
            </button>
            <div className="sv-share-menu-divider" />
            <button onClick={shareViaEmail} className="share-menu-item">
              <MailOutlined /> Email
            </button>
          </div>
        )}
        </div>
      </div>

      {/* Net Annual Savings + Stats Row + Card Upgrade Recommendation */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : '1fr 340px',
        gap: isMobile ? '0' : '32px',
        marginBottom: isMobile ? '24px' : '48px'
      }}>
        {/* Left Column - Net Savings + Stats */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: isMobile ? '24px' : '48px'
        }}>
          {/* Net Annual Savings */}
          <div className="sv-result-hero">
            <div className="sv-result-savings-label">
              {t('result.netSavings')}
            </div>
            <div className="sv-result-amount">
              ${result.netAnnualSavings.toFixed(0)}
              <span className="sv-result-unit">{t('common.perYear')}</span>
            </div>
          </div>

          {/* Stats Row */}
          <div className="sv-result-stats-row">
            <div className="sv-result-stat-item">
              <div className="sv-result-stat-label">{t('result.monthlyReward')}</div>
              <div className="sv-result-stat-value">${result.monthlyReward.toFixed(2)}</div>
            </div>
            <div className="sv-result-stat-divider" />
            <div className="sv-result-stat-item">
              <div className="sv-result-stat-label">{t('result.annualReward')}</div>
              <div className="sv-result-stat-value">${result.annualReward.toFixed(0)}</div>
            </div>
            <div className="sv-result-stat-divider" />
            <div className="sv-result-stat-item">
              <div className="sv-result-stat-label">{t('result.annualFees')}</div>
              <div className="sv-result-stat-value sv-result-stat-fees">-${result.totalAnnualFees.toFixed(0)}</div>
            </div>
          </div>
        </div>

        {/* Right Column - Card Upgrade Recommendation on Desktop */}
        {result && !isMobile && (
          <CardUpgradeRecommendation
            result={result}
            selectedCardIds={selectedCards.map(c => c.id)}
            monthlySpending={monthlySpending}
            compact={true}
          />
        )}
      </div>

      {/* Card Upgrade Recommendation - Card style on Mobile */}
      {result && isMobile && (
        <div style={{ marginBottom: '48px' }}>
          <CardUpgradeRecommendation
            result={result}
            selectedCardIds={selectedCards.map(c => c.id)}
            monthlySpending={monthlySpending}
            compact={true}
          />
        </div>
      )}

      {/* Recommendations - Simple List */}
      <div style={{ marginBottom: '48px' }}>
        <h2 className="sv-result-section-title">
          {t('result.quickReference')}
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {sortByCategory(result.recommendations).map((rec) => (
              <div
                key={rec.category}
                className="sv-result-rec-item"
                onClick={() => rec.aiExplanation && isMobile && toggleAiExpanded(rec.category as SpendingCategory)}
                style={{
                  cursor: isMobile && rec.aiExplanation ? 'pointer' : 'default'
                }}
              >
                <div className="sv-result-rec-row">
                  <div className="sv-result-rec-category">
                    <span style={{ fontSize: '16px' }}>{CATEGORY_ICONS[rec.category] || '💳'}</span>
                    <span className="sv-result-category-name">
                      {t(`categories.${rec.category}`)}
                    </span>
                    {/* Mobile: show expand indicator */}
                    {isMobile && rec.aiExplanation && (
                      <DownOutlined style={{
                        fontSize: '10px',
                        color: '#9ca3af',
                        transform: isAiExpanded(rec.category as SpendingCategory) ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s',
                        marginLeft: 'auto'
                      }} />
                    )}
                  </div>
                  <div className="sv-result-rec-details">
                    {BANK_LOGOS[rec.recommendedCard.bank] && (
                      <img
                        src={BANK_LOGOS[rec.recommendedCard.bank]}
                        alt={rec.recommendedCard.bank}
                        style={{ width: '20px', height: '20px', objectFit: 'contain', borderRadius: '4px' }}
                      />
                    )}
                    <span className="sv-result-card-name">
                      {rec.recommendedCard.name}
                    </span>
                    <span className="sv-result-rate">
                      {(rec.rewardRate * 100).toFixed(0)}%
                    </span>
                    <span className="sv-result-reward">
                      ${rec.monthlyReward.toFixed(2)}/mo
                    </span>
                  </div>
                </div>
                {rec.aiExplanation && (
                  <div
                    className="sv-ai-content"
                    style={{
                      maxHeight: isAiExpanded(rec.category as SpendingCategory) ? '200px' : '0',
                      overflow: 'hidden',
                      transition: isMobile ? 'max-height 0.3s ease, opacity 0.3s ease' : 'none',
                      opacity: isAiExpanded(rec.category as SpendingCategory) ? 1 : 0
                    }}
                  >
                    <p className="sv-result-ai-tip">
                      <img src="/logo.svg" alt="" style={{ width: '14px', height: '14px', marginTop: '3px', flexShrink: 0 }} />
                      <span><span className="sv-result-ai-label">{t('result.aiTip')}:</span> {rec.aiExplanation}</span>
                    </p>
                  </div>
                )}
              </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="sv-result-actions">
        <button
          onClick={() => navigate('/optimizer')}
          className="sv-result-btn-primary"
        >
          {t('result.adjustSpending')} <ArrowRightOutlined />
        </button>
        {!isAuthenticated && (
          <button
            onClick={handleStartOver}
            className="sv-result-btn-secondary"
          >
            <RedoOutlined /> {t('result.startOver')}
          </button>
        )}
      </div>
    </div>
  )
}

export default ResultPage
