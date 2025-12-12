import { SUPPORT_EMAIL } from '../content/legal'

function SupportPage() {
  return (
    <div className="sv-public-page">
      <div className="sv-public-content">
        <h1>Support</h1>
        <p className="sv-public-date">We're here to help you get the most out of SaveVia.</p>

        <div className="sv-section">
          <h2>Contact Us</h2>
          <p>For any questions, feedback, or issues, please reach out to us at: <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
        </div>

        <div className="sv-section">
          <h2>Frequently Asked Questions</h2>

          <h3>What is SaveVia?</h3>
          <p>SaveVia is a credit card cashback optimizer for Canadians. We help you maximize your rewards by recommending which card to use for each purchase category.</p>

          <h3>Is my data secure?</h3>
          <p>Yes. We use industry-standard encryption and never store your actual credit card numbers. Bank connections are powered by Flinks, a regulated financial data aggregator.</p>

          <h3>How do I cancel my subscription?</h3>
          <p>You can cancel your subscription anytime through your Apple ID account settings. Go to Settings → Apple ID → Subscriptions → SaveVia → Cancel Subscription.</p>

          <h3>How do I delete my account?</h3>
          <p>You can delete your account in the app by going to Me → Delete Account. This will permanently remove all your data.</p>
        </div>

        <div className="sv-section">
          <h2>App Information</h2>
          <p><strong>Developer:</strong> SwiftmindSystems Ltd.</p>
          <p><strong>Email:</strong> <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
        </div>
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

        .sv-section {
          padding: 24px 0;
          border-bottom: 1px solid #e5e7eb;
        }

        .sv-section:last-child {
          border-bottom: none;
        }

        .sv-public-content h2 {
          font-size: 18px;
          font-weight: 600;
          color: #111827;
          margin: 0 0 12px;
        }

        .sv-public-content h3 {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
          margin: 20px 0 8px;
        }

        .sv-public-content h3:first-of-type {
          margin-top: 0;
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

export default SupportPage
