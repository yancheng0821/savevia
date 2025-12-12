import { TermsContent, LAST_UPDATED } from '../content/legal'

function TermsPage() {
  return (
    <div className="sv-public-page">
      <div className="sv-public-content">
        <h1>Terms of Service</h1>
        <p className="sv-public-date">Last Updated: {LAST_UPDATED}</p>
        <TermsContent />
      </div>

      <style>{`
        .sv-public-page {
          min-height: 100vh;
          background: #fffcf5;
          padding: 40px 20px 80px;
        }

        .sv-public-content {
          max-width: 800px;
          margin: 0 auto;
        }

        .sv-public-content h1 {
          font-size: 32px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 8px;
        }

        .sv-public-date {
          font-size: 14px;
          color: #9ca3af;
          margin-bottom: 32px;
        }

        .sv-public-content h2 {
          font-size: 18px;
          font-weight: 600;
          color: #111827;
          margin: 24px 0 12px;
        }

        .sv-public-content p {
          font-size: 15px;
          color: #4b5563;
          line-height: 1.7;
          margin-bottom: 16px;
        }

        .sv-public-content a {
          color: #059669;
          text-decoration: none;
        }

        .sv-public-content a:hover {
          text-decoration: underline;
        }

        @media (max-width: 640px) {
          .sv-public-page {
            padding: 24px 16px 60px;
          }

          .sv-public-content h1 {
            font-size: 24px;
          }

          .sv-public-content h2 {
            font-size: 16px;
          }
        }
      `}</style>
    </div>
  )
}

export default TermsPage
