import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Modal, message, Switch, Dropdown } from 'antd'
import type { MenuProps } from 'antd'
import {
  UserOutlined,
  LockOutlined,
  RightOutlined,
  LogoutOutlined,
  GlobalOutlined,
  BellOutlined,
  MoonOutlined,
  CreditCardOutlined,
  DollarOutlined,
  QuestionCircleOutlined,
  FileTextOutlined,
  SafetyOutlined,
  StarOutlined,
  ShareAltOutlined,
  DeleteOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  MailOutlined,
  BankOutlined,
} from '@ant-design/icons'
import { Capacitor } from '@capacitor/core'
import { GoogleAuth } from '@southdevs/capacitor-google-auth'
import { Share } from '@capacitor/share'
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/useAuthStore'
import LegalModal, { type LegalType } from '../components/LegalModal'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import { userApi, authApi, transactionApi, bankApi } from '../services/api'
import type { MissedCashbackSummary } from '../types'
import { ExclamationCircleOutlined, KeyOutlined } from '@ant-design/icons'

// Platform detection
const isNativeApp = Capacitor.isNativePlatform()
const platform = Capacitor.getPlatform()
const isIOS = platform === 'ios'
const isAndroid = platform === 'android'

// App Store URLs (update these when apps are published)
const IOS_APP_STORE_URL = 'https://apps.apple.com/app/id6756332569'
const ANDROID_PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=app.savevia'

// Support email
const SUPPORT_EMAIL = 'support@savevia.app'

// API base URL for resolving relative paths
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Resolve avatar URL - relative paths need API base URL prefix
const resolveAvatarUrl = (url: string | undefined): string | undefined => {
  if (!url) return undefined
  // If it's a relative path (starts with /), prepend API base URL
  if (url.startsWith('/uploads/')) {
    return `${API_BASE_URL}${url}`
  }
  // Otherwise return as-is (external URLs like Google avatar)
  return url
}

// Password validation: only letters, numbers, and special symbols, min 8 chars
const PASSWORD_PATTERN = /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]+$/
const ALLOWED_PASSWORD_CHARS = /[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/g

// Filter password input to only allow valid characters
const filterPassword = (value: string): string => {
  return (value.match(ALLOWED_PASSWORD_CHARS) || []).join('')
}

const validatePassword = (pwd: string): string | null => {
  if (pwd.length < 8) {
    return 'auth.passwordTooShort'
  }
  if (!PASSWORD_PATTERN.test(pwd)) {
    return 'auth.passwordInvalidChars'
  }
  return null
}

function MePage() {
  const { t, i18n } = useTranslation()
  const { user, isAuthenticated, logout, updateUserAvatar, setPanelOpen } = useAuthStore()
  const { selectedCards, result } = useOptimizerStore()
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('sv_notifications')
    return saved !== null ? saved === 'true' : true
  })
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('sv_darkMode')
    return saved === 'true'
  })
  const [policyModal, setPolicyModal] = useState<LegalType | null>(null)
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [deletePassword, setDeletePassword] = useState('')
  const [deleteLoading, setDeleteLoading] = useState(false)

  // Password change/set modal states
  const [passwordModalOpen, setPasswordModalOpen] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmNewPassword, setConfirmNewPassword] = useState('')
  const [passwordLoading, setPasswordLoading] = useState(false)

  // Show/hide password states
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [showDeletePassword, setShowDeletePassword] = useState(false)

  // Missed cashback summary state - initialize from cache
  const [missedCashbackSummary, setMissedCashbackSummary] = useState<MissedCashbackSummary | null>(() => {
    const cached = localStorage.getItem('sv_missedCashbackSummary')
    if (cached) {
      try {
        return JSON.parse(cached)
      } catch {
        return null
      }
    }
    return null
  })
  const [hasBankConnection, setHasBankConnection] = useState(() => {
    return localStorage.getItem('sv_hasBankConnection') === 'true'
  })

  // Load missed cashback summary on mount
  useEffect(() => {
    if (isAuthenticated) {
      loadMissedCashbackSummary()
    }
  }, [isAuthenticated])

  const loadMissedCashbackSummary = async () => {
    try {
      // First check if user has bank connections
      const connectionsRes = await bankApi.getConnections()
      const hasConnection = connectionsRes.code === 200 && connectionsRes.data && connectionsRes.data.length > 0
      setHasBankConnection(hasConnection)
      localStorage.setItem('sv_hasBankConnection', String(hasConnection))

      if (hasConnection) {
        // Load user's card IDs for analysis
        let cardIds: number[] = []
        try {
          const cardsRes = await userApi.getUserCards()
          if (cardsRes.code === 200 && cardsRes.data) {
            cardIds = cardsRes.data
          }
        } catch (e) {
          // Ignore
        }
        // Get summary
        const summaryRes = await transactionApi.getSummary(cardIds)
        if (summaryRes.code === 200 && summaryRes.data) {
          setMissedCashbackSummary(summaryRes.data)
          localStorage.setItem('sv_missedCashbackSummary', JSON.stringify(summaryRes.data))
        }
      } else {
        setMissedCashbackSummary(null)
        localStorage.removeItem('sv_missedCashbackSummary')
      }
    } catch (error) {
      console.error('Failed to load missed cashback summary:', error)
    }
  }

  // Get annual savings from result (fallback to manual calculation for old data)
  const annualSavings = result
    ? (result.netAnnualSavings ?? (result.annualReward - result.totalAnnualFees))
    : 0

  // Handle notifications toggle
  const handleNotificationsChange = (checked: boolean) => {
    setNotifications(checked)
    localStorage.setItem('sv_notifications', String(checked))
    if (checked) {
      // Request notification permission
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission()
      }
    }
  }

  // Handle dark mode toggle
  const handleDarkModeChange = (checked: boolean) => {
    setDarkMode(checked)
    localStorage.setItem('sv_darkMode', String(checked))
    if (checked) {
      document.documentElement.classList.add('dark-mode')
    } else {
      document.documentElement.classList.remove('dark-mode')
    }
  }

  // Handle avatar upload - use native camera on mobile, file input on web
  const handleAvatarClick = async () => {
    if (!isAuthenticated) return

    const isNative = Capacitor.isNativePlatform()

    if (isNative) {
      // Use native camera/photo picker
      try {
        const image = await Camera.getPhoto({
          quality: 80,
          allowEditing: true,
          resultType: CameraResultType.Base64,
          source: CameraSource.Prompt, // Let user choose camera or gallery
          width: 512,
          height: 512,
          // Internationalized prompt labels
          promptLabelHeader: t('me.camera.header'),
          promptLabelPhoto: t('me.camera.photo'),
          promptLabelPicture: t('me.camera.picture'),
          promptLabelCancel: t('me.camera.cancel'),
        })

        if (image.base64String) {
          // Convert base64 to blob
          const byteString = atob(image.base64String)
          const arrayBuffer = new ArrayBuffer(byteString.length)
          const uint8Array = new Uint8Array(arrayBuffer)
          for (let i = 0; i < byteString.length; i++) {
            uint8Array[i] = byteString.charCodeAt(i)
          }
          const blob = new Blob([uint8Array], { type: `image/${image.format || 'jpeg'}` })
          const file = new File([blob], `avatar.${image.format || 'jpg'}`, { type: `image/${image.format || 'jpeg'}` })

          await uploadAvatarFile(file)
        }
      } catch (error: any) {
        // User cancelled or permission denied - don't show error
        if (error.message?.includes('cancelled') || error.message?.includes('User cancelled')) {
          return
        }
        console.error('Camera error:', error)
        message.error(t('errors.unexpectedError'))
      }
    } else {
      // Use file input on web
      if (fileInputRef.current) {
        fileInputRef.current.click()
      }
    }
  }

  // Upload avatar file (shared by both native and web)
  const uploadAvatarFile = async (file: File) => {
    setUploadingAvatar(true)
    try {
      const response = await userApi.uploadAvatar(file)
      if (response.code === 200 && response.data) {
        updateUserAvatar(response.data.avatarUrl)
        message.success(t('me.avatarUpdated'))
      }
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      message.error(t('me.invalidImageType'))
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      message.error(t('me.imageTooLarge'))
      return
    }

    await uploadAvatarFile(file)

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Apply dark mode on mount
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark-mode')
    }
  }, [])

  const langLabels: Record<string, string> = {
    en: 'English',
    zh: '中文',
    fr: 'Français',
    es: 'Español',
    ko: '한국어',
    ja: '日本語',
  }

  const langItems: MenuProps['items'] = [
    { key: 'en', label: 'English' },
    { key: 'zh', label: '中文' },
    { key: 'fr', label: 'Français' },
    { key: 'es', label: 'Español' },
    { key: 'ko', label: '한국어' },
    { key: 'ja', label: '日本語' },
  ]

  const handleLangChange: MenuProps['onClick'] = ({ key }) => {
    i18n.changeLanguage(key)
  }

  const handleLogout = async () => {
    // On Android, also sign out from Google to allow account selection next time
    if (Capacitor.getPlatform() === 'android') {
      try {
        await GoogleAuth.signOut()
      } catch (e) {
        // Ignore errors
      }
    }
    logout()
    useOptimizerStore.getState().reset()
    // Clear missed cashback cache
    localStorage.removeItem('sv_missedCashbackSummary')
    localStorage.removeItem('sv_hasBankConnection')
    message.success(t('nav.logout'))
  }

  // Handle Rate Us - open app store based on platform
  const handleRateUs = () => {
    if (isNativeApp) {
      if (isIOS) {
        window.open(IOS_APP_STORE_URL, '_blank')
      } else if (isAndroid) {
        window.open(ANDROID_PLAY_STORE_URL, '_blank')
      }
    } else {
      // On web, detect device and open appropriate store
      const userAgent = navigator.userAgent.toLowerCase()
      if (/iphone|ipad|ipod/.test(userAgent)) {
        window.open(IOS_APP_STORE_URL, '_blank')
      } else if (/android/.test(userAgent)) {
        window.open(ANDROID_PLAY_STORE_URL, '_blank')
      } else {
        // Desktop - default to iOS App Store
        window.open(IOS_APP_STORE_URL, '_blank')
      }
    }
  }

  // Handle Help & Feedback
  const handleFeedback = () => {
    setFeedbackModalOpen(true)
  }

  // Handle share app - share website link (uses OG image and description)
  const handleShare = async () => {
    const shareUrl = 'https://savevia.app'
    const shareText = t('me.shareText')

    if (isNativeApp) {
      // Use Capacitor Share for native apps
      try {
        await Share.share({
          title: 'SaveVia',
          text: shareText,
          url: shareUrl,
          dialogTitle: t('me.shareApp')
        })
      } catch (e) {
        // User cancelled or error
      }
    } else if (navigator.share) {
      // Use Web Share API for web
      try {
        await navigator.share({
          title: 'SaveVia',
          text: shareText,
          url: shareUrl
        })
      } catch (e) {
        // User cancelled or error
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(shareUrl)
      message.success(t('me.linkCopied'))
    }
  }

  const handleDeleteAccount = () => {
    setDeleteModalOpen(true)
    setDeletePassword('')
  }

  const handleConfirmDelete = async () => {
    // Only require password for users who have one (email/password users)
    if (user?.hasPassword && !deletePassword) {
      message.error(t('me.passwordRequired'))
      return
    }
    setDeleteLoading(true)
    try {
      await userApi.deleteAccount(deletePassword)
      logout()
      useOptimizerStore.getState().reset()
      message.success(t('me.accountDeleted'))
      setDeleteModalOpen(false)
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    } finally {
      setDeleteLoading(false)
    }
  }

  // Handle password change/set modal
  const handlePasswordModal = () => {
    setPasswordModalOpen(true)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmNewPassword('')
  }

  const handlePasswordSubmit = async () => {
    // Validate new password
    const pwdError = validatePassword(newPassword)
    if (pwdError) {
      message.error(t(pwdError))
      return
    }
    if (newPassword !== confirmNewPassword) {
      message.error(t('auth.passwordsDoNotMatch'))
      return
    }

    setPasswordLoading(true)
    try {
      if (user?.hasPassword) {
        // Change password (requires current password)
        if (!currentPassword) {
          message.error(t('me.passwordRequired'))
          setPasswordLoading(false)
          return
        }
        await authApi.changePassword({ currentPassword, newPassword })
      } else {
        // Set password (for OAuth users)
        await authApi.setPassword({ newPassword })
      }
      message.success(t('auth.passwordChanged'))
      setPasswordModalOpen(false)
      // Update user state to reflect they now have a password
      if (user) {
        useAuthStore.getState().setUser({ ...user, hasPassword: true })
      }
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    } finally {
      setPasswordLoading(false)
    }
  }

  return (
    <div className="sv-me-page">
      {/* Hidden file input for avatar upload */}
      <input
        type="file"
        ref={fileInputRef}
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleAvatarChange}
      />

      {/* User Profile Section */}
      {isAuthenticated ? (
        <div className="sv-me-profile">
          <div className="sv-me-avatar sv-me-avatar-editable" onClick={handleAvatarClick}>
            {user?.avatarUrl ? (
              <img src={resolveAvatarUrl(user.avatarUrl)} alt="" referrerPolicy="no-referrer" />
            ) : (
              <UserOutlined />
            )}
            {uploadingAvatar && (
              <div className="sv-me-avatar-overlay">
                <span className="sv-me-avatar-loading" />
              </div>
            )}
          </div>
          <div className="sv-me-info">
            <h2>{user?.name || t('auth.guest')}</h2>
            <p>{user?.email}</p>
          </div>
        </div>
      ) : (
        <div className="sv-me-login-prompt" onClick={() => setPanelOpen(true)}>
          <div className="sv-me-avatar">
            <UserOutlined />
          </div>
          <div className="sv-me-info">
            <h2>{t('auth.loginOrRegister')}</h2>
            <p>{t('auth.loginToSaveData')}</p>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>
      )}

      {/* Quick Stats - Only for logged in users with data */}
      {isAuthenticated && (selectedCards.length > 0 || result || hasBankConnection) && (
        <div className="sv-me-stats">
          <Link to="/cards" className="sv-me-stat-card">
            <CreditCardOutlined />
            <div className="sv-me-stat-value">{selectedCards.length}</div>
            <div className="sv-me-stat-label">{t('me.myCards')}</div>
          </Link>
          <Link to="/result" className="sv-me-stat-card">
            <DollarOutlined />
            <div className="sv-me-stat-value">${result ? annualSavings.toFixed(0) : '—'}</div>
            <div className="sv-me-stat-label">{t('me.annualSavings')}</div>
          </Link>
          <Link to="/transactions" className="sv-me-stat-card sv-me-stat-missed">
            <BankOutlined />
            <div className="sv-me-stat-value">
              {hasBankConnection && missedCashbackSummary
                ? `$${missedCashbackSummary.totalMissedCashback.toFixed(0)}`
                : '—'}
            </div>
            <div className="sv-me-stat-label">{t('me.missedCashback')}</div>
          </Link>
        </div>
      )}


      {/* Settings Section */}
      <div className="sv-me-section">
        <h3>{t('me.settings')}</h3>

        {/* Language */}
        <Dropdown menu={{ items: langItems, onClick: handleLangChange }} trigger={['click']}>
          <div className="sv-me-item">
            <div className="sv-me-item-left">
              <GlobalOutlined />
              <span>{t('me.language')}</span>
            </div>
            <div className="sv-me-item-right">
              <span>{langLabels[i18n.language?.split('-')[0]] || 'English'}</span>
              <RightOutlined />
            </div>
          </div>
        </Dropdown>

        {/* Notifications */}
        <div className="sv-me-item">
          <div className="sv-me-item-left">
            <BellOutlined />
            <span>{t('me.notifications')}</span>
          </div>
          <Switch
            checked={notifications}
            onChange={handleNotificationsChange}
            size="small"
          />
        </div>

        {/* Dark Mode */}
        <div className="sv-me-item">
          <div className="sv-me-item-left">
            <MoonOutlined />
            <span>{t('me.darkMode')}</span>
          </div>
          <Switch
            checked={darkMode}
            onChange={handleDarkModeChange}
            size="small"
          />
        </div>

        {/* Password Change/Set - Only for logged in users */}
        {isAuthenticated && (
          <div className="sv-me-item" onClick={handlePasswordModal}>
            <div className="sv-me-item-left">
              <KeyOutlined />
              <span>{user?.hasPassword ? t('auth.changePassword') : t('auth.setPassword')}</span>
            </div>
            <RightOutlined className="sv-me-arrow" />
          </div>
        )}
      </div>

      {/* Support Section */}
      <div className="sv-me-section">
        <h3>{t('me.support')}</h3>

        <div className="sv-me-item" onClick={handleFeedback}>
          <div className="sv-me-item-left">
            <QuestionCircleOutlined />
            <span>{t('me.helpFeedback')}</span>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>

        <div className="sv-me-item" onClick={handleRateUs}>
          <div className="sv-me-item-left">
            <StarOutlined />
            <span>{t('me.rateUs')}</span>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>

        <div className="sv-me-item" onClick={handleShare}>
          <div className="sv-me-item-left">
            <ShareAltOutlined />
            <span>{t('me.shareApp')}</span>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>
      </div>

      {/* Legal Section */}
      <div className="sv-me-section">
        <h3>{t('me.legal')}</h3>

        <div className="sv-me-item" onClick={() => setPolicyModal('privacy')}>
          <div className="sv-me-item-left">
            <SafetyOutlined />
            <span>{t('me.privacyPolicy')}</span>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>

        <div className="sv-me-item" onClick={() => setPolicyModal('terms')}>
          <div className="sv-me-item-left">
            <FileTextOutlined />
            <span>{t('me.termsOfService')}</span>
          </div>
          <RightOutlined className="sv-me-arrow" />
        </div>
      </div>

      {/* Data Section - Only for logged in users */}
      {isAuthenticated && (
        <div className="sv-me-section">
          <h3>{t('me.data')}</h3>
          <div className="sv-me-item" onClick={() => {
            useOptimizerStore.getState().reset()
            message.success(t('me.cacheCleared'))
          }}>
            <div className="sv-me-item-left">
              <DeleteOutlined />
              <span>{t('me.clearCache')}</span>
            </div>
          </div>
          <div className="sv-me-item sv-me-danger" onClick={handleDeleteAccount}>
            <div className="sv-me-item-left">
              <ExclamationCircleOutlined />
              <span>{t('me.deleteAccount')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Logout Button */}
      {isAuthenticated && (
        <div className="sv-me-section">
          <div className="sv-me-item sv-me-logout" onClick={handleLogout}>
            <div className="sv-me-item-left">
              <LogoutOutlined />
              <span>{t('nav.logout')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Logo & Version - Mobile only */}
      <div className="sv-me-footer">
        <img src="/logo-full.svg" alt="SaveVia" className="sv-me-logo-mobile" />
        <div className="sv-me-version">
          v1.0.0
        </div>
      </div>

      {/* Help & Feedback Modal */}
      <Modal
        open={feedbackModalOpen}
        onCancel={() => setFeedbackModalOpen(false)}
        footer={null}
        centered
        width={420}
        className="auth-modal sv-simple-modal"
      >
        <div className="auth-modal-content">
          <h2>{t('me.helpFeedback')}</h2>
          <p>{t('me.feedbackDesc')}</p>

          <div className="feedback-options">
            <a
              href={`mailto:${SUPPORT_EMAIL}?subject=SaveVia Feedback`}
              className="feedback-option"
              onClick={() => setFeedbackModalOpen(false)}
            >
              <MailOutlined />
              <div className="feedback-option-text">
                <span className="feedback-option-title">{t('me.emailUs')}</span>
                <span className="feedback-option-desc">{SUPPORT_EMAIL}</span>
              </div>
              <RightOutlined />
            </a>

          </div>
        </div>
      </Modal>

      {/* Privacy Policy / Terms Modal */}
      {policyModal && (
        <LegalModal type={policyModal} onClose={() => setPolicyModal(null)} />
      )}

      {/* Delete Account Modal */}
      <Modal
        open={deleteModalOpen}
        onCancel={() => setDeleteModalOpen(false)}
        footer={null}
        centered
        width={400}
        className="auth-modal sv-simple-modal"
      >
        <div className="auth-modal-content">
          <h2>{t('me.deleteAccountTitle')}</h2>
          <p>{t('me.deleteAccountConfirm')}</p>

          {user?.hasPassword && (
            <div className="auth-modal-form">
              <div className="auth-modal-field">
                <label>{t('auth.password')}</label>
                <div className="auth-modal-input">
                  <LockOutlined />
                  <input
                    type={showDeletePassword ? 'text' : 'password'}
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder={t('auth.passwordPlaceholder')}
                  />
                  <span className="password-toggle" onClick={() => setShowDeletePassword(!showDeletePassword)}>
                    {showDeletePassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  </span>
                </div>
              </div>
            </div>
          )}

          <button
            className="auth-modal-submit auth-modal-submit-danger"
            onClick={handleConfirmDelete}
            disabled={deleteLoading}
          >
            {deleteLoading ? t('common.loading') : t('me.deleteAccountOk')}
          </button>

          <p className="auth-modal-switch">
            <button onClick={() => setDeleteModalOpen(false)}>
              {t('common.cancel')}
            </button>
          </p>
        </div>
      </Modal>

      {/* Password Change/Set Modal */}
      <Modal
        open={passwordModalOpen}
        onCancel={() => setPasswordModalOpen(false)}
        footer={null}
        centered
        width={400}
        className="auth-modal sv-simple-modal"
      >
        <div className="auth-modal-content">
          <h2>{user?.hasPassword ? t('auth.changePassword') : t('auth.setPassword')}</h2>
          {!user?.hasPassword && (
            <p>{t('auth.setPasswordDesc')}</p>
          )}

          <div className="auth-modal-form">
            {/* Current password - only for users who already have one */}
            {user?.hasPassword && (
              <div className="auth-modal-field">
                <label>{t('auth.currentPassword')}</label>
                <div className="auth-modal-input">
                  <LockOutlined />
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder={t('auth.currentPasswordPlaceholder')}
                  />
                  <span className="password-toggle" onClick={() => setShowCurrentPassword(!showCurrentPassword)}>
                    {showCurrentPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  </span>
                </div>
              </div>
            )}

            <div className="auth-modal-field">
              <label>{t('auth.newPassword')}</label>
              <div className="auth-modal-input">
                <LockOutlined />
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(filterPassword(e.target.value))}
                  placeholder={t('auth.newPasswordPlaceholder')}
                  minLength={8}
                />
                <span className="password-toggle" onClick={() => setShowNewPassword(!showNewPassword)}>
                  {showNewPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                </span>
              </div>
            </div>

            <div className="auth-modal-field">
              <label>{t('auth.confirmPassword')}</label>
              <div className="auth-modal-input">
                <LockOutlined />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(filterPassword(e.target.value))}
                  placeholder={t('auth.confirmPasswordPlaceholder')}
                  minLength={8}
                />
                <span className="password-toggle" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                  {showConfirmPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                </span>
              </div>
            </div>
          </div>

          <button
            className="auth-modal-submit"
            onClick={handlePasswordSubmit}
            disabled={passwordLoading}
          >
            {passwordLoading ? t('common.loading') : t('common.save')}
          </button>

          <p className="auth-modal-switch">
            <button onClick={() => setPasswordModalOpen(false)}>
              {t('common.cancel')}
            </button>
          </p>
        </div>
      </Modal>

      <style>{`
        .sv-me-page {
          padding: 20px;
          min-height: calc(100vh - 140px);
          background: var(--app-bg);
        }

        @media (min-width: 641px) {
          .sv-me-page {
            max-width: 800px;
            margin: 0 auto;
          }
        }

        @media (max-width: 640px) {
          .sv-me-page {
            padding: 16px 20px;
            min-height: calc(100vh - 70px);
          }
        }

        .sv-me-profile,
        .sv-me-login-prompt {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 24px 0 20px;
          margin-bottom: 8px;
          position: relative;
        }

        .sv-me-login-prompt {
          cursor: pointer;
          transition: all 0.2s;
        }

        .sv-me-login-prompt:active {
          opacity: 0.7;
        }

        .sv-me-avatar {
          width: 52px;
          height: 52px;
          border-radius: 50%;
          background: #f3f4f6;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #9ca3af;
          font-size: 20px;
          overflow: hidden;
          flex-shrink: 0;
        }

        .sv-me-avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .sv-me-info {
          flex: 1;
        }

        .sv-me-info h2 {
          font-size: 17px;
          font-weight: 600;
          color: #111827;
          margin: 0 0 4px;
        }

        .sv-me-info p {
          font-size: 13px;
          color: #6b7280;
          margin: 0;
        }

        .sv-me-pro-badge {
          position: absolute;
          top: 20px;
          right: 0;
          display: flex;
          align-items: center;
          gap: 3px;
          text-decoration: none;
          transition: all 0.2s;
        }

        .sv-me-pro-badge:active {
          opacity: 0.6;
        }

        .sv-me-pro-logo {
          width: 36px;
          height: 36px;
        }

        .sv-me-pro-text {
          font-size: 13px;
          font-weight: 700;
          background: linear-gradient(135deg, #2563eb 0%, #0d9488 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .sv-me-arrow {
          color: #d1d5db;
          font-size: 12px;
        }

        .sv-me-section {
          margin-bottom: 0;
        }

        .sv-me-section h3 {
          font-size: 12px;
          font-weight: 500;
          color: #9ca3af;
          padding: 20px 0 10px;
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .sv-me-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 0;
          cursor: pointer;
          transition: opacity 0.2s;
          border-bottom: 1px solid rgba(0,0,0,0.04);
        }

        .sv-me-item:last-child {
          border-bottom: none;
        }

        .sv-me-item:active {
          opacity: 0.6;
        }

        .sv-me-item-left {
          display: flex;
          align-items: center;
          gap: 14px;
          color: #374151;
          font-size: 15px;
        }

        .sv-me-item-left .anticon {
          font-size: 18px;
          color: #9ca3af;
          width: 24px;
          text-align: center;
        }

        .sv-me-item-right {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #9ca3af;
          font-size: 14px;
        }

        .sv-me-item-right .anticon {
          font-size: 10px;
          color: #d1d5db;
        }

        .sv-me-item-link {
          text-decoration: none;
          color: inherit;
        }

        .sv-me-item-emoji {
          font-size: 18px;
          width: 24px;
          text-align: center;
        }

        .sv-me-logout .sv-me-item-left {
          color: #ef4444;
        }

        .sv-me-logout .sv-me-item-left .anticon {
          color: #ef4444;
        }

        .sv-me-danger .sv-me-item-left {
          color: #ef4444;
        }

        .sv-me-danger .sv-me-item-left .anticon {
          color: #ef4444;
        }

        .sv-me-subscription-card {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 16px;
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-radius: 16px;
          text-decoration: none;
          color: inherit;
          transition: all 0.2s;
        }

        .sv-me-subscription-card:active {
          opacity: 0.8;
          transform: scale(0.99);
        }

        .sv-me-subscription-icon {
          width: 44px;
          height: 44px;
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: white;
          box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
        }

        .sv-me-subscription-info {
          flex: 1;
        }

        .sv-me-subscription-info h3 {
          font-size: 16px;
          font-weight: 600;
          color: #92400e;
          margin: 0 0 2px;
        }

        .sv-me-subscription-info p {
          font-size: 13px;
          color: #a16207;
          margin: 0;
        }

        .sv-me-footer {
          display: none;
          flex-direction: column;
          align-items: center;
          padding: 32px 0 16px;
        }

        .sv-me-logo-mobile {
          width: 120px;
          height: auto;
          margin-bottom: 8px;
        }

        .sv-me-version {
          text-align: center;
          color: #d1d5db;
          font-size: 11px;
        }

        @media (max-width: 640px) {
          .sv-me-footer {
            display: flex;
          }
        }

        .sv-me-stats {
          display: flex;
          gap: 0;
          padding: 16px 0;
          margin-bottom: 8px;
        }

        .sv-me-stat-card {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 12px 0;
          text-decoration: none;
          transition: opacity 0.2s;
        }

        .sv-me-stat-card:active {
          opacity: 0.6;
        }

        .sv-me-stat-card .anticon {
          font-size: 20px;
          margin-bottom: 8px;
        }

        .sv-me-stat-card:first-child .anticon {
          color: #2563eb;
        }

        .sv-me-stat-card:nth-child(2) .anticon {
          color: #059669;
        }

        .sv-me-stat-card.sv-me-stat-missed .anticon {
          color: #f59e0b;
        }

        .sv-me-stat-card.sv-me-stat-missed .sv-me-stat-value {
          color: #f59e0b;
        }

        .sv-me-stat-value {
          font-size: 20px;
          font-weight: 700;
          color: #111827;
        }

        .sv-me-stat-label {
          font-size: 11px;
          color: #9ca3af;
          margin-top: 4px;
        }

        /* Auth Modal Styles (same as AppHeader) */
        .auth-modal .ant-modal-content {
          border-radius: 20px;
          padding: 0;
          overflow: hidden;
        }

        .auth-modal .ant-modal-body {
          padding: 0;
        }

        .auth-modal-content {
          padding: 40px;
        }

        .auth-modal-content h2 {
          font-size: 24px;
          font-weight: 700;
          color: #111827;
          margin: 0 0 8px;
          text-align: center;
        }

        .auth-modal-content > p {
          font-size: 14px;
          color: #6b7280;
          margin: 0 0 28px;
          text-align: center;
        }

        .auth-modal-socials {
          display: flex;
          gap: 12px;
          margin-bottom: 24px;
        }

        .auth-modal-social {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 12px 16px;
          border-radius: 10px;
          border: 1px solid #e5e7eb;
          background: white;
          font-size: 14px;
          font-weight: 600;
          color: #374151;
          cursor: pointer;
          transition: all 0.2s;
        }

        .auth-modal-social:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .auth-modal-divider {
          display: flex;
          align-items: center;
          margin: 24px 0;
          color: #9ca3af;
          font-size: 12px;
        }

        .auth-modal-divider::before,
        .auth-modal-divider::after {
          content: '';
          flex: 1;
          height: 1px;
          background: #e5e7eb;
        }

        .auth-modal-divider span {
          padding: 0 16px;
        }

        .auth-modal-form {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .auth-modal-field label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: #374151;
          margin-bottom: 6px;
        }

        .auth-modal-input {
          position: relative;
        }

        .auth-modal-input .anticon {
          position: absolute;
          left: 14px;
          top: 50%;
          transform: translateY(-50%);
          color: #9ca3af;
          font-size: 15px;
        }

        .auth-modal-input input {
          width: 100%;
          padding: 12px 42px 12px 42px;
          border: 1px solid #e5e7eb;
          border-radius: 10px;
          font-size: 14px;
          outline: none;
          transition: all 0.2s;
          box-sizing: border-box;
        }

        .auth-modal-input input:focus {
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .password-toggle {
          position: absolute;
          right: 1px;
          top: 1px;
          bottom: 1px;
          width: 40px;
          cursor: pointer;
          color: #9ca3af;
          font-size: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1;
          border-radius: 0 9px 9px 0;
        }

        .password-toggle:hover {
          color: #6b7280;
        }

        .password-toggle:active {
          color: #4b5563;
        }

        .auth-modal-submit {
          width: 100%;
          padding: 14px 20px;
          background: #111827;
          border: none;
          border-radius: 10px;
          color: white;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 8px;
        }

        .auth-modal-submit:hover:not(:disabled) {
          background: #1f2937;
        }

        .auth-modal-submit:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .auth-modal-submit-danger {
          background: #ef4444;
        }

        .auth-modal-submit-danger:hover:not(:disabled) {
          background: #dc2626;
        }

        .auth-modal-switch {
          text-align: center;
          margin-top: 24px;
          font-size: 14px;
          color: #6b7280;
        }

        .auth-modal-switch button {
          background: none;
          border: none;
          color: #667eea;
          font-weight: 600;
          cursor: pointer;
          padding: 0;
        }

        /* Simple Modal - smaller padding, tighter layout */
        .sv-simple-modal .auth-modal-content {
          padding: 32px;
        }

        .sv-simple-modal .auth-modal-content h2 {
          font-size: 20px;
          margin-bottom: 8px;
        }

        .sv-simple-modal .auth-modal-content > p {
          margin-bottom: 20px;
        }

        .sv-simple-modal .auth-modal-form {
          margin-top: 0;
        }

        .sv-logo-gradient {
          background: linear-gradient(90deg, #2563eb 0%, #0d9488 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 600;
        }

        /* Policy Modal */
        .policy-modal .ant-modal-content {
          border-radius: 20px;
          max-height: 85vh;
          overflow: hidden;
          background: #fffcf5;
        }

        .policy-modal-content {
          padding: 40px;
          max-height: 75vh;
          overflow-y: auto;
        }

        .policy-modal-content h2 {
          font-size: 26px;
          font-weight: 700;
          color: #111827;
          margin: 0 0 28px;
          text-align: center;
        }

        .policy-text h3 {
          font-size: 16px;
          font-weight: 600;
          color: #111827;
          margin: 24px 0 12px;
        }

        .policy-text h3:first-child {
          margin-top: 0;
        }

        .policy-text p {
          font-size: 15px;
          color: #4b5563;
          line-height: 1.7;
          margin: 0;
        }

        .policy-text ul {
          margin: 12px 0;
          padding-left: 24px;
        }

        .policy-text li {
          font-size: 15px;
          color: #4b5563;
          line-height: 1.7;
          margin-bottom: 8px;
        }

        .policy-text a {
          color: #667eea;
          text-decoration: none;
        }

        .policy-text a:hover {
          text-decoration: underline;
        }

        .policy-date {
          font-size: 13px;
          color: #9ca3af;
          margin-bottom: 24px !important;
        }

        /* Feedback Modal Styles */
        .feedback-options {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .feedback-option {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 16px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          text-decoration: none;
          color: inherit;
          transition: all 0.2s;
        }

        .feedback-option:hover {
          border-color: #667eea;
          background: #f9fafb;
        }

        .feedback-option .anticon:first-child {
          font-size: 22px;
          color: #667eea;
        }

        .feedback-option-text {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .feedback-option-title {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
        }

        .feedback-option-desc {
          font-size: 13px;
          color: #6b7280;
        }

        .feedback-option .anticon:last-child {
          font-size: 12px;
          color: #d1d5db;
        }

        @media (max-width: 640px) {
          .auth-modal .ant-modal-content {
            border-radius: 16px;
          }
          .auth-modal-content {
            padding: 24px 20px;
          }
          .auth-modal-content h2 {
            font-size: 18px;
            margin-bottom: 6px;
          }
          .auth-modal-content > p {
            font-size: 13px;
            margin-bottom: 20px;
          }
          .auth-modal-form {
            gap: 12px;
          }
          .auth-modal-field label {
            font-size: 12px;
          }
          .auth-modal-input input {
            padding: 10px 12px 10px 38px;
            font-size: 14px;
          }
          .auth-modal-submit {
            padding: 12px 16px;
            font-size: 14px;
          }
          .auth-modal-switch {
            margin-top: 16px;
            font-size: 13px;
          }
          .policy-modal-content {
            padding: 24px;
          }
          .policy-modal-content h2 {
            font-size: 20px;
            margin-bottom: 20px;
          }
          .policy-text h3 {
            font-size: 14px;
            margin: 16px 0 8px;
          }
          .policy-text p {
            font-size: 13px;
          }
          .feedback-options {
            gap: 10px;
          }
          .feedback-option {
            padding: 12px;
            gap: 12px;
          }
          .feedback-option .anticon:first-child {
            font-size: 18px;
          }
          .feedback-option-title {
            font-size: 14px;
          }
          .feedback-option-desc {
            font-size: 12px;
          }
          .sv-simple-modal .auth-modal-content {
            padding: 24px 20px;
          }
          .sv-simple-modal .auth-modal-content h2 {
            font-size: 18px;
          }
          .sv-simple-modal .auth-modal-content > p {
            font-size: 13px;
            margin-bottom: 16px;
          }
        }

        /* Dark mode for Pro badge */
        html.dark-mode .sv-me-pro-text {
          background: linear-gradient(135deg, #3b82f6 0%, #14b8a6 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
      `}</style>
    </div>
  )
}

export default MePage
