import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LockOutlined, CheckCircleOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons'
import { message } from 'antd'
import { authApi } from '../services/api'

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

function ResetPasswordPage() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  useEffect(() => {
    if (!token) {
      message.error(t('auth.invalidResetLink'))
      navigate('/')
    }
  }, [token, navigate, t])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate password
    const pwdError = validatePassword(password)
    if (pwdError) {
      message.error(t(pwdError))
      return
    }

    if (password !== confirmPassword) {
      message.error(t('auth.passwordsDoNotMatch'))
      return
    }

    setIsLoading(true)
    try {
      await authApi.resetPassword({ token: token!, newPassword: password })
      setIsSuccess(true)
      message.success(t('auth.passwordResetSuccess'))
    } catch (error: any) {
      message.error(error.message || t('errors.unexpectedError'))
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <div style={{
        maxWidth: '400px',
        margin: '60px auto',
        padding: '40px 32px',
        background: 'white',
        borderRadius: '24px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        textAlign: 'center',
      }}>
        <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '24px' }} />
        <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: '0 0 12px' }}>
          {t('auth.passwordResetSuccess')}
        </h2>
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
          {t('auth.passwordResetSuccessDesc')}
        </p>
        <button
          onClick={() => navigate('/')}
          style={{
            width: '100%',
            padding: '14px 20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '12px',
            fontSize: '15px',
            fontWeight: '600',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          {t('auth.backToLogin')}
        </button>
      </div>
    )
  }

  return (
    <div style={{
      maxWidth: '400px',
      margin: '60px auto',
      padding: '40px 32px',
      background: 'white',
      borderRadius: '24px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
    }}>
      <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: '0 0 8px', textAlign: 'center' }}>
        {t('auth.resetPassword')}
      </h2>
      <p style={{ fontSize: '14px', color: '#6b7280', textAlign: 'center', marginBottom: '32px' }}>
        {t('auth.resetPasswordDesc')}
      </p>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
            {t('auth.newPassword')}
          </label>
          <div style={{ position: 'relative' }}>
            <LockOutlined style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#9ca3af',
              fontSize: '16px',
            }} />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(filterPassword(e.target.value))}
              placeholder={t('auth.newPasswordPlaceholder')}
              required
              minLength={8}
              style={{
                width: '100%',
                padding: '14px 44px 14px 44px',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '15px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
            <span
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: 'absolute',
                right: '1px',
                top: '1px',
                bottom: '1px',
                width: '40px',
                cursor: 'pointer',
                color: '#9ca3af',
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '0 11px 11px 0',
              }}
            >
              {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
            </span>
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
            {t('auth.confirmPassword')}
          </label>
          <div style={{ position: 'relative' }}>
            <LockOutlined style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#9ca3af',
              fontSize: '16px',
            }} />
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(filterPassword(e.target.value))}
              placeholder={t('auth.confirmPasswordPlaceholder')}
              required
              minLength={8}
              style={{
                width: '100%',
                padding: '14px 44px 14px 44px',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '15px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
            <span
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              style={{
                position: 'absolute',
                right: '1px',
                top: '1px',
                bottom: '1px',
                width: '40px',
                cursor: 'pointer',
                color: '#9ca3af',
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '0 11px 11px 0',
              }}
            >
              {showConfirmPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
            </span>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '14px 20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '12px',
            fontSize: '15px',
            fontWeight: '600',
            color: 'white',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          {isLoading ? t('common.loading') : t('auth.resetPassword')}
        </button>
      </form>
    </div>
  )
}

export default ResetPasswordPage
