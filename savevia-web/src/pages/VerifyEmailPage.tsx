import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons'
import { authApi } from '../services/api'

function VerifyEmailPage() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setErrorMessage(t('auth.invalidVerificationLink'))
      return
    }

    const verifyEmail = async () => {
      try {
        await authApi.verifyEmail(token)
        setStatus('success')
      } catch (error: any) {
        setStatus('error')
        setErrorMessage(error.message || t('errors.unexpectedError'))
      }
    }

    verifyEmail()
  }, [token, t])

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
      {status === 'loading' && (
        <>
          <LoadingOutlined style={{ fontSize: '64px', color: '#4285F4', marginBottom: '24px' }} />
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: '0 0 12px' }}>
            {t('auth.verifyingEmail')}
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280' }}>
            {t('auth.pleaseWait')}
          </p>
        </>
      )}

      {status === 'success' && (
        <>
          <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '24px' }} />
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: '0 0 12px' }}>
            {t('auth.emailVerified')}
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
            {t('auth.emailVerifiedDesc')}
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
            {t('auth.continueToApp')}
          </button>
        </>
      )}

      {status === 'error' && (
        <>
          <CloseCircleOutlined style={{ fontSize: '64px', color: '#f5222d', marginBottom: '24px' }} />
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: '0 0 12px' }}>
            {t('auth.verificationFailed')}
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
            {errorMessage}
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
            {t('auth.backToHome')}
          </button>
        </>
      )}
    </div>
  )
}

export default VerifyEmailPage
