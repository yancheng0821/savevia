// Legal content - Privacy Policy and Terms of Service
// Update content here, it will be used in both modal and public pages

export const SUPPORT_EMAIL = 'support@savevia.app'
export const LAST_UPDATED = 'December 2025'

// Privacy Policy Content
export const PrivacyContent = () => (
  <>
    <h2>1. Information We Collect</h2>
    <p>We collect information you provide directly, including email address, name, and credit card preferences. We do not store your actual credit card numbers or banking credentials.</p>

    <h2>2. How We Use Your Information</h2>
    <p>We use your information to provide personalized credit card recommendations, optimize your cashback rewards, and improve our services.</p>

    <h2>3. Data Security</h2>
    <p>We implement industry-standard security measures to protect your personal information. All data transmission is encrypted using SSL/TLS.</p>

    <h2>4. Third-Party Services</h2>
    <p>We use Flinks for secure bank connections. Flinks is a regulated financial data aggregator that follows strict security protocols. We also use Google Sign-In and Apple Sign-In for authentication.</p>

    <h2>5. Your Rights</h2>
    <p>You can request access to, correction of, or deletion of your personal data at any time by contacting us at <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>.</p>

    <h2>6. Contact Us</h2>
    <p>For privacy-related questions, contact us at: <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
  </>
)

// Terms of Service Content
export const TermsContent = () => (
  <>
    <h2>1. Acceptance of Terms</h2>
    <p>By using SaveVia, you agree to these Terms of Service. If you do not agree, please do not use our services.</p>

    <h2>2. Service Description</h2>
    <p>SaveVia provides credit card cashback optimization recommendations. Our recommendations are for informational purposes only and should not be considered financial advice.</p>

    <h2>3. Subscription</h2>
    <p>SaveVia Pro subscription provides access to premium features. Subscriptions auto-renew unless cancelled at least 24 hours before the end of the current period. You can manage your subscription in your Apple ID account settings.</p>

    <h2>4. Refund Policy</h2>
    <p>Subscription refunds are handled by Apple App Store according to their refund policies.</p>

    <h2>5. Limitation of Liability</h2>
    <p>SaveVia is not responsible for any financial decisions made based on our recommendations. Always verify information with your credit card issuer.</p>

    <h2>6. User Responsibilities</h2>
    <p>You are responsible for maintaining the confidentiality of your account credentials. You agree to provide accurate information and use the service for personal, non-commercial purposes only.</p>

    <h2>7. Changes to Terms</h2>
    <p>We may update these terms from time to time. Continued use of the service constitutes acceptance of any changes.</p>

    <h2>8. Contact</h2>
    <p>Questions about these terms? Contact us at: <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
  </>
)
