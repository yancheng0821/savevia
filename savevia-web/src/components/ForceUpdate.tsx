import { useTranslation } from 'react-i18next'
import { Capacitor } from '@capacitor/core'

interface ForceUpdateProps {
  iosStoreUrl: string
  androidStoreUrl: string
  latestVersion: string
}

/**
 * Force Update Modal - Minimal design
 */
export function ForceUpdate({ iosStoreUrl, androidStoreUrl }: ForceUpdateProps) {
  const { t } = useTranslation()
  const platform = Capacitor.getPlatform()

  const handleUpdate = () => {
    const url = platform === 'ios' ? iosStoreUrl : androidStoreUrl
    window.open(url, '_blank')
  }

  return (
    <div className="force-update-overlay">
      <div className="force-update-modal">
        <h2>{t('forceUpdate.title')}</h2>
        <p>{t('forceUpdate.message')}</p>
        <button className="force-update-button" onClick={handleUpdate}>
          {t('forceUpdate.updateNow')}
        </button>
      </div>

      <style>{`
        .force-update-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
          padding: 24px;
        }

        .force-update-modal {
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 300px;
          width: 100%;
          text-align: center;
        }

        .force-update-modal h2 {
          font-size: 18px;
          font-weight: 600;
          color: #111;
          margin: 0 0 8px;
        }

        .force-update-modal p {
          font-size: 14px;
          color: #666;
          line-height: 1.5;
          margin: 0 0 20px;
        }

        .force-update-button {
          width: 100%;
          padding: 12px;
          background: #111;
          border: none;
          border-radius: 10px;
          color: white;
          font-size: 15px;
          font-weight: 500;
          cursor: pointer;
        }

        .force-update-button:active {
          opacity: 0.8;
        }
      `}</style>
    </div>
  )
}

export default ForceUpdate
