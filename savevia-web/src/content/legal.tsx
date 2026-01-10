// Legal content - Privacy Policy and Terms of Service
// Update content here, it will be used in both modal and public pages

export const SUPPORT_EMAIL = 'support@savevia.app'
export const LAST_UPDATED = 'January 2026'

// Privacy Policy Content
export const PrivacyContent = () => (
  <>
    <h2>1. Information We Collect</h2>
    <p>We collect information you provide directly, including email address, name, and credit card preferences. We do not store your actual credit card numbers or banking credentials.</p>
    <p>When you use our AI assistant feature, we collect and store your chat messages and conversation history to provide personalized responses and improve our services.</p>
    <p>For push notifications, we collect your device token and device information (such as device type and language preference) to deliver relevant notifications to you.</p>

    <h2>2. How We Use Your Information</h2>
    <p>We use your information to provide personalized credit card recommendations, optimize your cashback rewards, and improve our services.</p>
    <p>Your chat conversations with our AI assistant are used to provide you with personalized credit card advice and spending insights. We may use aggregated and anonymized conversation data to improve our AI service quality.</p>
    <p>We use push notifications to send you spending reminders, reward optimization tips, and service updates. You can manage your notification preferences in your device settings at any time.</p>

    <h2>3. Data Security</h2>
    <p>We implement industry-standard security measures to protect your personal information. All data transmission is encrypted using SSL/TLS.</p>

    <h2>4. Third-Party Services</h2>
    <p>We use Flinks for secure bank connections. Flinks is a regulated financial data aggregator that follows strict security protocols. We also use Google Sign-In and Apple Sign-In for authentication.</p>
    <p>Our AI assistant feature is powered by OpenAI. When you use the AI chat, your messages are processed by OpenAI's services to generate responses. OpenAI's use of this data is governed by their privacy policy.</p>
    <p>We use Apple Push Notification Service (APNs) to deliver push notifications to iOS devices.</p>

    <h2>5. Data Retention</h2>
    <p>Your chat conversation history is retained for up to 12 months to provide continuity in your interactions with our AI assistant. You can request deletion of your chat history at any time.</p>

    <h2>6. Your Rights</h2>
    <p>You can request access to, correction of, or deletion of your personal data at any time by contacting us at <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a>.</p>
    <p>You can disable push notifications at any time through your device settings or within the app.</p>

    <h2>7. Contact Us</h2>
    <p>For privacy-related questions, contact us at: <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
  </>
)

// Terms of Service Content
export const TermsContent = () => (
  <>
    <h2>1. Acceptance of Terms</h2>
    <p>By using SaveVia, you agree to these Terms of Service. If you do not agree, please do not use our services.</p>

    <h2>2. Service Description</h2>
    <p>SaveVia provides credit card cashback optimization recommendations. Our recommendations are for informational purposes only and should not be considered financial advice. We do not issue credit cards. Applications are handled by the card issuer.</p>

    <h2>3. AI Assistant</h2>
    <p>SaveVia includes an AI-powered assistant that can answer questions about credit cards and spending optimization. Please note:</p>
    <ul>
      <li>AI responses are for informational purposes only and do not constitute professional financial, legal, or tax advice.</li>
      <li>AI-generated content may contain inaccuracies or errors. Always verify important information with official sources or qualified professionals.</li>
      <li>You agree not to use the AI assistant for any unlawful purposes or to generate harmful, abusive, or misleading content.</li>
      <li>We reserve the right to limit or suspend AI assistant access if we detect misuse.</li>
    </ul>

    <h2>4. Push Notifications</h2>
    <p>SaveVia may send you push notifications including spending reminders, reward optimization tips, and service updates. You can opt out of push notifications at any time through your device settings.</p>

    <h2>5. Subscription</h2>
    <p>SaveVia Pro subscription provides access to premium features. Subscriptions auto-renew unless cancelled at least 24 hours before the end of the current period. You can manage your subscription in your Apple ID account settings.</p>

    <h2>6. Refund Policy</h2>
    <p>Subscription refunds are handled by Apple App Store according to their refund policies.</p>

    <h2>7. Limitation of Liability</h2>
    <p>SaveVia is not responsible for any financial decisions made based on our recommendations or AI assistant responses. Always verify information with your credit card issuer or qualified financial professionals.</p>

    <h2>8. User Responsibilities</h2>
    <p>You are responsible for maintaining the confidentiality of your account credentials. You agree to provide accurate information and use the service for personal, non-commercial purposes only.</p>

    <h2>9. Changes to Terms</h2>
    <p>We may update these terms from time to time. Continued use of the service constitutes acceptance of any changes.</p>

    <h2>10. Contact</h2>
    <p>Questions about these terms? Contact us at: <a href={`mailto:${SUPPORT_EMAIL}`}>{SUPPORT_EMAIL}</a></p>
  </>
)
