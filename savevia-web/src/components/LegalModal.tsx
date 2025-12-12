import { useTranslation } from 'react-i18next'
import { CloseOutlined } from '@ant-design/icons'
import { PrivacyContent, TermsContent, LAST_UPDATED } from '../content/legal'

export type LegalType = 'privacy' | 'terms'

interface LegalModalProps {
  type: LegalType
  onClose: () => void
}

function LegalModal({ type, onClose }: LegalModalProps) {
  const { t } = useTranslation()

  return (
    <div className="sv-legal-modal-overlay" onClick={onClose}>
      <div className="sv-legal-modal" onClick={e => e.stopPropagation()}>
        <div className="sv-legal-modal-header">
          <h3>{type === 'privacy' ? t('me.privacyPolicy') : t('me.termsOfService')}</h3>
          <button className="sv-legal-modal-close" onClick={onClose}>
            <CloseOutlined />
          </button>
        </div>
        <div className="sv-legal-modal-content">
          <p className="sv-legal-date"><strong>Last Updated: {LAST_UPDATED}</strong></p>
          {type === 'privacy' ? <PrivacyContent /> : <TermsContent />}
        </div>
      </div>

      <style>{`
        .sv-legal-modal-overlay {
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

        .sv-legal-modal {
          background: white;
          border-radius: 16px;
          width: calc(100% - 40px);
          max-width: 720px;
          max-height: 80vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        @media (min-width: 641px) {
          .sv-legal-modal {
            min-width: 600px;
          }
        }

        @media (max-width: 640px) {
          .sv-legal-modal-overlay {
            padding: 0;
            align-items: flex-end;
          }

          .sv-legal-modal {
            width: 100%;
            max-height: 85vh;
            border-radius: 16px 16px 0 0;
          }
        }

        .sv-legal-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          border-bottom: 1px solid #e5e7eb;
        }

        .sv-legal-modal-header h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #111827;
        }

        .sv-legal-modal-close {
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
        }

        .sv-legal-modal-close:active {
          background: #e5e7eb;
        }

        .sv-legal-modal-content {
          padding: 20px;
          overflow-y: auto;
          -webkit-overflow-scrolling: touch;
        }

        .sv-legal-modal-content h2 {
          font-size: 16px;
          font-weight: 600;
          color: #111827;
          margin: 20px 0 10px;
        }

        .sv-legal-modal-content h2:first-of-type {
          margin-top: 0;
        }

        .sv-legal-modal-content p {
          font-size: 15px;
          color: #4b5563;
          line-height: 1.7;
          margin: 0 0 16px;
        }

        .sv-legal-modal-content a {
          color: #059669;
          text-decoration: none;
        }

        .sv-legal-modal-content a:hover {
          text-decoration: underline;
        }

        /* Dark Mode */
        html.dark-mode .sv-legal-modal {
          background: var(--bg-secondary);
        }

        html.dark-mode .sv-legal-modal-header {
          border-bottom-color: var(--border-color);
        }

        html.dark-mode .sv-legal-modal-header h3 {
          color: var(--text-primary);
        }

        html.dark-mode .sv-legal-modal-close {
          background: var(--bg-tertiary);
          color: var(--text-secondary);
        }

        html.dark-mode .sv-legal-modal-content h2 {
          color: var(--text-primary);
        }

        html.dark-mode .sv-legal-modal-content p {
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  )
}

export default LegalModal
