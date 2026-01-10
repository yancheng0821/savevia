import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { MailOutlined, LockOutlined, UserOutlined, EyeOutlined, EyeInvisibleOutlined, CheckOutlined } from '@ant-design/icons'
import { Modal, message } from 'antd'
import { Capacitor } from '@capacitor/core'
import { Keyboard } from '@capacitor/keyboard'
import { GoogleAuth } from '@southdevs/capacitor-google-auth'
import { useGoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../stores/useAuthStore'
import LegalModal, { type LegalType } from './LegalModal'

type AuthMode = 'login' | 'register'

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

// Check if Google OAuth is configured
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const isGoogleEnabled = Boolean(GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID.length > 0)

// Check if Apple Sign In is configured
const APPLE_CLIENT_ID = import.meta.env.VITE_APPLE_CLIENT_ID
const isAppleEnabled = Boolean(APPLE_CLIENT_ID && APPLE_CLIENT_ID.length > 0)

// Check if running on native platform (iOS/Android)
const isNativeApp = Capacitor.isNativePlatform()

// Check platform
const platform = Capacitor.getPlatform()
const isIOS = platform === 'ios'
const isAndroid = platform === 'android'

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

function AuthPanel() {
  const { t } = useTranslation()
  const { isPanelOpen, setPanelOpen, login, register, loginWithGoogle, loginWithApple, isLoading } = useAuthStore()
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [legalModal, setLegalModal] = useState<LegalType | null>(null)
  const [keyboardHeight, setKeyboardHeight] = useState(0)

  // Listen for keyboard events on native platforms
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return

    const showListener = Keyboard.addListener('keyboardWillShow', (info) => {
      setKeyboardHeight(info.keyboardHeight)
    })

    const hideListener = Keyboard.addListener('keyboardWillHide', () => {
      setKeyboardHeight(0)
    })

    return () => {
      showListener.then(l => l.remove())
      hideListener.then(l => l.remove())
    }
  }, [])

  // Handle input focus to scroll into view when keyboard opens
  const handleInputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    if (Capacitor.isNativePlatform()) {
      setTimeout(() => {
        e.target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
    }
  }

  // Load Apple Sign In JS SDK for web
  useEffect(() => {
    if (!isAppleEnabled || isNativeApp) return

    const script = document.createElement('script')
    script.src = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js'
    script.async = true
    script.onload = () => {
      if ((window as any).AppleID) {
        (window as any).AppleID.auth.init({
          clientId: APPLE_CLIENT_ID,
          scope: 'name email',
          redirectURI: window.location.origin,
          usePopup: true,
        })
      }
    }
    document.body.appendChild(script)

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  // Web Google login
  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse: any) => {
      try {
        await loginWithGoogle(tokenResponse.access_token)
        message.success(t('auth.loginSuccess'))
        handleClose()
      } catch (error: any) {
        message.error(error.message || t('errors.unexpectedError'))
      }
    },
    onError: () => {
      message.error(t('errors.unexpectedError'))
    },
  })

  const handleGoogleLogin = async () => {
    if (isNativeApp) {
      try {
        // Sign out first to force account picker
        try {
          await GoogleAuth.signOut()
        } catch (e) {
          // Ignore signOut errors - user might not be signed in
        }

        const result = await GoogleAuth.signIn({ scopes: ['profile', 'email'] })

        // Priority: idToken > accessToken > serverAuthCode
        const credential = result.authentication?.idToken
          || result.authentication?.accessToken
          || result.serverAuthCode

        if (credential) {
          await loginWithGoogle(credential)
          message.success(t('auth.loginSuccess'))
          handleClose()
        } else {
          console.error('Google login: no valid credential found in result', result)
          message.error(t('errors.unexpectedError'))
        }
      } catch (error: any) {
        if (error.message !== 'The user canceled the sign-in flow.') {
          message.error(error.message || t('errors.unexpectedError'))
        }
      }
    } else {
      googleLogin()
    }
  }

  const handleAppleLogin = async () => {
    try {
      if (isNativeApp && isIOS) {
        const { SignInWithApple }: any = await import('@capacitor-community/apple-sign-in')
        const result = await SignInWithApple.authorize({
          clientId: APPLE_CLIENT_ID,
          redirectURI: window.location.origin,
          scopes: 'email name',
        })
        console.log('Apple Sign In response:', JSON.stringify(result.response))
        const identityToken = result.response?.identityToken
        const email = result.response?.email
        const fullName = result.response?.givenName && result.response?.familyName
          ? `${result.response.givenName} ${result.response.familyName}`.trim()
          : (result.response?.givenName || result.response?.familyName || undefined)
        if (identityToken) {
          await loginWithApple(identityToken, fullName, email)
          message.success(t('auth.loginSuccess'))
          handleClose()
        }
      } else if ((window as any).AppleID) {
        const response = await (window as any).AppleID.auth.signIn()
        const identityToken = response.authorization?.id_token
        const fullName = response.user?.name
          ? `${response.user.name.firstName || ''} ${response.user.name.lastName || ''}`.trim()
          : undefined
        if (identityToken) {
          await loginWithApple(identityToken, fullName)
          message.success(t('auth.loginSuccess'))
          handleClose()
        }
      }
    } catch (error: any) {
      if (error.error !== 'popup_closed_by_user' && error.message !== 'The user canceled the sign-in flow.') {
        message.error(error.message || t('errors.unexpectedError'))
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate password for registration
    if (authMode === 'register') {
      const pwdError = validatePassword(password)
      if (pwdError) {
        message.error(t(pwdError))
        return
      }
      // Check terms agreement
      if (!agreedToTerms) {
        message.error(t('auth.pleaseAgreeTerms'))
        return
      }
    }

    try {
      if (authMode === 'login') {
        await login(email, password)
        message.success(t('auth.loginSuccess'))
      } else {
        await register(email, password, name)
        message.success(t('auth.registerSuccess'))
      }
      handleClose()
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    }
  }

  const handleClose = () => {
    setPanelOpen(false)
    setAuthMode('login')
    setEmail('')
    setPassword('')
    setName('')
    setShowPassword(false)
    setAgreedToTerms(false)
  }

  if (!isPanelOpen) return null

  return (
    <>
      <Modal
        open={isPanelOpen}
        onCancel={handleClose}
        footer={null}
        centered
        width={420}
        className="auth-modal sv-bottom-sheet-modal"
        wrapClassName="sv-bottom-sheet-wrap"
        destroyOnClose
        maskClosable
        style={keyboardHeight > 0 ? { paddingBottom: keyboardHeight } : undefined}
      >
        <div
          className="auth-modal-content"
          style={keyboardHeight > 0 ? { paddingBottom: keyboardHeight + 24 } : undefined}
        >
          <h2>{authMode === 'login' ? t('auth.welcomeBack') : t('auth.joinUs')}</h2>
          <p>
            {authMode === 'login'
              ? <>{t('auth.signInSubtitle')} <span className="sv-logo-gradient">SaveVia</span></>
              : <>{t('auth.signUpSubtitle')} <span className="sv-logo-gradient">SaveVia</span></>
            }
          </p>

          {/* Social Login */}
          <div className="auth-modal-socials">
            {(isGoogleEnabled || isNativeApp) && (
              <button onClick={handleGoogleLogin} className="auth-modal-social">
                <GoogleIcon />
                <span>Google</span>
              </button>
            )}
            {/* Apple Login - show on iOS native only, or web if configured (never on Android) */}
            {!isAndroid && ((isNativeApp && isIOS) || (!isNativeApp && isAppleEnabled)) && (
              <button className="auth-modal-social auth-apple" onClick={handleAppleLogin}>
                <AppleIcon />
                <span>Apple</span>
              </button>
            )}
          </div>
          <p className="auth-modal-social-terms">
            {t('auth.socialLoginTerms')}{' '}
            <button type="button" onClick={() => setLegalModal('terms')}>{t('me.termsOfService')}</button>
            {' '}{t('auth.and')}{' '}
            <button type="button" onClick={() => setLegalModal('privacy')}>{t('me.privacyPolicy')}</button>
          </p>

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
                    onFocus={handleInputFocus}
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
                  onFocus={handleInputFocus}
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
                  onChange={(e) => setPassword(authMode === 'register' ? filterPassword(e.target.value) : e.target.value)}
                  onFocus={handleInputFocus}
                  placeholder={t('auth.passwordPlaceholder')}
                  required
                  minLength={8}
                />
                <span
                  className="password-toggle"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                </span>
              </div>
            </div>

            {authMode === 'register' && (
              <div className="auth-modal-terms">
                <div
                  className={`auth-modal-checkbox ${agreedToTerms ? 'checked' : ''}`}
                  onClick={() => setAgreedToTerms(!agreedToTerms)}
                >
                  {agreedToTerms && <CheckOutlined />}
                </div>
                <span className="auth-modal-terms-text">
                  {t('auth.agreeToTerms')}{' '}
                  <button type="button" onClick={() => setLegalModal('terms')}>{t('me.termsOfService')}</button>
                  {' '}{t('auth.and')}{' '}
                  <button type="button" onClick={() => setLegalModal('privacy')}>{t('me.privacyPolicy')}</button>
                </span>
              </div>
            )}

            <button type="submit" className="auth-modal-submit" disabled={isLoading || (authMode === 'register' && !agreedToTerms)}>
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

      {/* Legal Modal */}
      {legalModal && (
        <LegalModal type={legalModal} onClose={() => setLegalModal(null)} />
      )}

      <style>{`
        /* Auth Modal Styles - same as MePage */
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
          font-size: 16px; /* Prevent iOS zoom on focus */
          outline: none;
          box-sizing: border-box;
          -webkit-appearance: none;
          -webkit-tap-highlight-color: transparent;
          /* No transitions on iOS to prevent keyboard input lag */
        }

        .auth-modal-input input:focus {
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Only apply transitions on non-touch devices */
        @media (hover: hover) and (pointer: fine) {
          .auth-modal-input input {
            transition: border-color 0.2s, box-shadow 0.2s;
          }
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

        .sv-logo-gradient {
          background: linear-gradient(90deg, #2563eb 0%, #0d9488 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 600;
        }

        /* Terms Checkbox */
        .auth-modal-terms {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-top: 4px;
        }

        .auth-modal-checkbox {
          width: 20px;
          height: 20px;
          border: 2px solid #d1d5db;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          flex-shrink: 0;
          margin-top: 1px;
        }

        .auth-modal-checkbox:hover {
          border-color: #9ca3af;
        }

        .auth-modal-checkbox.checked {
          background: #059669;
          border-color: #059669;
          color: white;
        }

        .auth-modal-checkbox .anticon {
          font-size: 12px;
        }

        .auth-modal-terms-text {
          font-size: 13px;
          color: #6b7280;
          line-height: 1.5;
        }

        .auth-modal-terms-text button {
          background: none;
          border: none;
          padding: 0;
          color: #059669;
          font-weight: 500;
          cursor: pointer;
          text-decoration: underline;
        }

        .auth-modal-terms-text button:hover {
          color: #047857;
        }

        .auth-modal-social-terms {
          font-size: 11px;
          color: #9ca3af;
          text-align: center;
          margin: 8px 0 0;
          line-height: 1.5;
        }

        .auth-modal-social-terms button {
          background: none;
          border: none;
          padding: 0;
          color: #6b7280;
          font-size: 11px;
          cursor: pointer;
          text-decoration: underline;
        }

        .auth-modal-social-terms button:hover {
          color: #374151;
        }

        /* Mobile Bottom Sheet Style */
        @media (max-width: 640px) {
          .sv-bottom-sheet-wrap {
            display: flex !important;
            align-items: flex-end !important;
            justify-content: center !important;
            z-index: 10000 !important;
          }

          .sv-bottom-sheet-wrap .ant-modal {
            top: auto !important;
            bottom: 0 !important;
            margin: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
            transform-origin: bottom center !important;
          }

          .sv-bottom-sheet-wrap .ant-modal-content {
            border-radius: 16px 16px 0 0 !important;
            max-height: 90vh;
            overflow-y: auto;
          }

          .sv-bottom-sheet-wrap.ant-modal-centered::before {
            display: none !important;
            content: none !important;
          }

          .sv-bottom-sheet-modal .auth-modal-content {
            padding: 28px 24px calc(40px + env(safe-area-inset-bottom));
          }

          .sv-bottom-sheet-modal .auth-modal-content h2 {
            font-size: 22px;
            margin-bottom: 8px;
          }

          .sv-bottom-sheet-modal .auth-modal-content > p {
            font-size: 14px;
            margin-bottom: 24px;
          }

          .sv-bottom-sheet-modal .auth-modal-socials {
            margin-bottom: 20px;
          }

          .sv-bottom-sheet-modal .auth-modal-social {
            padding: 14px 16px;
          }

          .sv-bottom-sheet-modal .auth-modal-divider {
            margin: 20px 0;
          }

          .sv-bottom-sheet-modal .auth-modal-form {
            gap: 16px;
          }

          .sv-bottom-sheet-modal .auth-modal-input input {
            padding: 14px 42px;
          }

          .sv-bottom-sheet-modal .auth-modal-submit {
            padding: 16px 20px;
            margin-top: 12px;
          }

          .sv-bottom-sheet-modal .auth-modal-switch {
            margin-top: 20px;
          }
        }
      `}</style>
    </>
  )
}

export default AuthPanel
