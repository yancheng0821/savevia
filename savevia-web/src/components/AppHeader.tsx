import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Dropdown, Modal, message } from 'antd'
import type { MenuProps } from 'antd'
import { UserOutlined, MailOutlined, LockOutlined, HomeOutlined, CreditCardOutlined, ThunderboltOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons'
import { useGoogleLogin } from '@react-oauth/google'
import { Capacitor } from '@capacitor/core'
import { GoogleAuth } from '@southdevs/capacitor-google-auth'
import { useAuthStore } from '../stores/useAuthStore'
import { useOptimizerStore } from '../stores/useOptimizerStore'

// Check if Google OAuth is configured
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const isGoogleEnabled = Boolean(GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID.length > 0)

// Check if running in native app
const isNativeApp = Capacitor.isNativePlatform()
console.log('isNativeApp:', isNativeApp, 'Platform:', Capacitor.getPlatform())

// Google Icon
const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
)

// Apple Icon
const AppleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
  </svg>
)

// Google Login Button
function GoogleLoginButton({ onSuccess }: { onSuccess: () => void }) {
  const { t } = useTranslation()
  const { loginWithGoogle } = useAuthStore()

  // Web-based Google login
  const webGoogleLogin = useGoogleLogin({
    flow: 'implicit',
    onSuccess: async (tokenResponse: any) => {
      try {
        await loginWithGoogle(tokenResponse.access_token)
        message.success(t('auth.loginSuccess'))
        onSuccess()
      } catch (error: any) {
        message.error(error.message || t('errors.unexpectedError'))
      }
    },
    onError: () => {
      message.error(t('errors.unexpectedError'))
    },
  })

  // Native Google login for mobile apps
  const nativeGoogleLogin = async () => {
    console.log('Starting native Google login...')
    try {
      // For Android: sign out from Google to force account picker
      if (Capacitor.getPlatform() === 'android') {
        try {
          await GoogleAuth.signOut()
          // Small delay to ensure sign out completes
          await new Promise(resolve => setTimeout(resolve, 100))
        } catch (e) {
          console.log('SignOut skipped:', e)
        }
      }

      // GoogleAuth is already initialized in main.tsx
      const result = await GoogleAuth.signIn({ scopes: ['profile', 'email'] })
      console.log('Google signIn result:', result)

      if (result.authentication?.accessToken) {
        console.log('Got access token, logging in...')
        await loginWithGoogle(result.authentication.accessToken)
        message.success(t('auth.loginSuccess'))
        onSuccess()
      } else if (result.authentication?.idToken) {
        // Some implementations return idToken instead
        console.log('Got id token, logging in...')
        await loginWithGoogle(result.authentication.idToken)
        message.success(t('auth.loginSuccess'))
        onSuccess()
      } else {
        console.error('No token in result:', result)
        message.error('Failed to get authentication token')
      }
    } catch (error: any) {
      console.error('Native Google login error:', error)
      console.error('Error details:', JSON.stringify(error, null, 2))
      // Show detailed error for debugging
      const errorMsg = error.message || error.error || JSON.stringify(error)
      message.error(`Login failed: ${errorMsg}`, 5)
    }
  }

  const handleGoogleLogin = () => {
    console.log('handleGoogleLogin called, isNativeApp:', isNativeApp)
    if (isNativeApp) {
      console.log('Using native Google login')
      nativeGoogleLogin()
    } else {
      console.log('Using web Google login')
      webGoogleLogin()
    }
  }

  return (
    <button onClick={handleGoogleLogin} className="auth-modal-social">
      <GoogleIcon />
      <span>Google</span>
    </button>
  )
}

type AuthMode = 'login' | 'register'

function AppHeader() {
  const location = useLocation()
  const { t, i18n } = useTranslation()
  const { user, isAuthenticated, login, register, isLoading, setPanelOpen } = useAuthStore()
  const { result } = useOptimizerStore()
  const [modalOpen, setModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [avatarError, setAvatarError] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  // Reset avatar error when user changes
  useEffect(() => {
    setAvatarError(false)
  }, [user?.avatarUrl])

  const navItems = [
    { path: '/', label: t('nav.home') },
    { path: '/cards', label: t('nav.myCards') },
    { path: '/optimizer', label: result ? t('nav.savings') : t('nav.optimizer') },
  ]

  const langItems: MenuProps['items'] = [
    { key: 'en', label: 'English' },
    { key: 'zh', label: '中文' },
    { key: 'fr', label: 'Français' },
    { key: 'es', label: 'Español' },
    { key: 'ko', label: '한국어' },
    { key: 'ja', label: '日本語' },
  ]

  const langLabels: Record<string, string> = {
    en: 'EN',
    zh: '中文',
    fr: 'FR',
    es: 'ES',
    ko: '한국어',
    ja: '日本語',
  }

  const handleLangChange: MenuProps['onClick'] = ({ key }) => {
    i18n.changeLanguage(key)
  }

  const resetForm = () => {
    setEmail('')
    setPassword('')
    setName('')
    setAuthMode('login')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (authMode === 'login') {
        await login(email, password)
        message.success(t('auth.loginSuccess'))
      } else {
        await register(email, password, name)
        message.success(t('auth.registerSuccess'))
      }
      setModalOpen(false)
      resetForm()
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    }
  }

  const getInitials = (name?: string) => {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  return (
    <>
      <header className="sv-app-header">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
            <img src="/logo-full.svg" alt="SaveVia" style={{ height: '40px', width: 'auto' }} />
          </Link>

          <nav className="sv-header-nav" style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
            {navItems.map((item) => {
              // If result exists and clicking optimizer, go to result page instead
              const targetPath = item.path === '/optimizer' && result ? '/result' : item.path
              const isActive = item.path === '/optimizer'
                ? (location.pathname === '/optimizer' || location.pathname === '/result')
                : location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={targetPath}
                  className={`sv-header-nav-link ${isActive ? 'active' : ''}`}
                >
                  {item.label}
                </Link>
              )
            })}

            {/* Language Selector */}
            <div className="sv-header-lang-divider">
              <Dropdown menu={{ items: langItems, onClick: handleLangChange }} placement="bottomRight">
                <button className="sv-header-lang-btn">
                  {langLabels[i18n.language] || 'EN'}
                </button>
              </Dropdown>
            </div>

            {/* User / Login */}
            <div style={{ marginLeft: '8px' }}>
              {isAuthenticated ? (
                <Link to="/me" className="header-user-btn">
                  {user?.avatarUrl && !avatarError ? (
                    <img
                      src={user.avatarUrl}
                      alt=""
                      className="header-avatar"
                      onError={() => setAvatarError(true)}
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <span className="header-avatar-text">{getInitials(user?.name)}</span>
                  )}
                </Link>
              ) : (
                <button onClick={() => setPanelOpen(true)} className="header-login-btn">
                  {t('nav.login')}
                </button>
              )}
            </div>
          </nav>
        </div>
      </header>

      {/* Mobile Bottom Navigation - hide on share page */}
      {!location.pathname.startsWith('/share') && (
      <nav className="sv-mobile-nav">
        {navItems.map((item) => {
          // If result exists and clicking optimizer, go to result page instead
          const targetPath = item.path === '/optimizer' && result ? '/result' : item.path
          const isActive = item.path === '/optimizer'
            ? (location.pathname === '/optimizer' || location.pathname === '/result')
            : location.pathname === item.path
          const icons: Record<string, React.ReactNode> = {
            '/': <HomeOutlined />,
            '/cards': <CreditCardOutlined />,
            '/optimizer': <ThunderboltOutlined />
          }
          return (
            <Link
              key={item.path}
              to={targetPath}
              className={`sv-mobile-nav-item ${isActive ? 'active' : ''}`}
            >
              {icons[item.path]}
              <span>{item.label}</span>
            </Link>
          )
        })}
        {/* Me / Profile */}
        <Link
          to="/me"
          className={`sv-mobile-nav-item ${location.pathname === '/me' ? 'active' : ''}`}
        >
          <UserOutlined />
          <span>{t('nav.me')}</span>
        </Link>
      </nav>
      )}

      {/* Auth Modal */}
      <Modal
        open={modalOpen}
        onCancel={() => { setModalOpen(false); resetForm(); }}
        footer={null}
        centered
        width={420}
        className="auth-modal"
      >
        <div className="auth-modal-content">
          <h2>{authMode === 'login' ? t('auth.welcomeBack') : t('auth.joinUs')}</h2>
          <p>
            {authMode === 'login'
              ? <>Sign in to continue to <span className="sv-logo-gradient">SaveVia</span></>
              : <>Create an account to get started with <span className="sv-logo-gradient">SaveVia</span></>
            }
          </p>

          {/* Social Login */}
          <div className="auth-modal-socials">
            {isGoogleEnabled && (
              <GoogleLoginButton onSuccess={() => { setModalOpen(false); resetForm(); }} />
            )}
            <button className="auth-modal-social auth-apple">
              <AppleIcon />
              <span>Apple</span>
            </button>
          </div>

          <div className="auth-modal-divider">
            <span>{t('auth.or')}</span>
          </div>

          {/* Email Form */}
          <form onSubmit={handleSubmit} className="auth-modal-form">
            {authMode === 'register' && (
              <div className="auth-modal-field">
                <label>{t('auth.name')}</label>
                <div className="auth-modal-input">
                  <UserOutlined />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t('auth.namePlaceholder')}
                    required
                  />
                </div>
              </div>
            )}

            <div className="auth-modal-field">
              <label>{t('auth.email')}</label>
              <div className="auth-modal-input">
                <MailOutlined />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('auth.emailPlaceholder')}
                  required
                />
              </div>
            </div>

            <div className="auth-modal-field">
              <label>{t('auth.password')}</label>
              <div className="auth-modal-input">
                <LockOutlined />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t('auth.passwordPlaceholder')}
                  required
                  minLength={8}
                />
                <span className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                </span>
              </div>
            </div>

            <button type="submit" className="auth-modal-submit" disabled={isLoading}>
              {isLoading ? t('common.loading') : (authMode === 'login' ? t('auth.signIn') : t('auth.signUp'))}
            </button>
          </form>

          <p className="auth-modal-switch">
            {authMode === 'login' ? t('auth.noAccount') : t('auth.hasAccount')}{' '}
            <button onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}>
              {authMode === 'login' ? t('auth.signUp') : t('auth.signIn')}
            </button>
          </p>
        </div>
      </Modal>

      <style>{`
        .header-login-btn {
          padding: 8px 20px;
          background: #111827;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          text-decoration: none;
        }

        .header-login-btn:hover {
          background: #1f2937;
          text-decoration: none;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }

        .header-user-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: none;
          background: #111827;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          transition: all 0.2s;
        }

        .header-user-btn:hover {
          background: #1f2937;
        }

        .header-avatar {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .header-avatar-text {
          color: white;
          font-size: 13px;
          font-weight: 600;
        }

        /* Modal Styles */
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

        .auth-modal-social.auth-apple {
          color: #000;
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

        .password-toggle {
          position: absolute;
          right: 1px;
          top: 1px;
          bottom: 1px;
          width: 40px;
          cursor: pointer;
          color: #9ca3af;
          font-size: 15px;
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

        .auth-modal-input input:focus {
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .auth-modal-input input::placeholder {
          color: #9ca3af;
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

        .auth-modal-switch button:hover {
          text-decoration: underline;
        }

        .sv-logo-gradient {
          background: linear-gradient(90deg, #2563eb 0%, #0d9488 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 600;
        }
      `}</style>
    </>
  )
}

export default AppHeader
