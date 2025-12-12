import { useEffect, useLayoutEffect, useState, useRef } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import { Capacitor } from '@capacitor/core'
import { SplashScreen } from '@capacitor/splash-screen'
import HomePage from './pages/HomePage'
import CardsPage from './pages/CardsPage'
import CardDetailPage from './pages/CardDetailPage'
import OptimizerPage from './pages/OptimizerPage'
import ResultPage from './pages/ResultPage'
import SharedResultPage from './pages/SharedResultPage'
import MePage from './pages/MePage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import TransactionsPage from './pages/TransactionsPage'
import SubscriptionPage from './pages/SubscriptionPage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import SupportPage from './pages/SupportPage'
import AppHeader from './components/AppHeader'
import AuthPanel from './components/AuthPanel'
import Paywall from './components/Paywall'
import Onboarding from './components/Onboarding'
import { useAuthStore } from './stores/useAuthStore'
import { useOptimizerStore } from './stores/useOptimizerStore'
import { useSubscriptionStore } from './stores/useSubscriptionStore'
import { useOnboardingStore } from './stores/useOnboardingStore'
import { isNativePlatform, initializeIAP } from './services/iap'

// Preload bank logos to prevent flicker on navigation (lazy loaded)
const BANK_LOGOS = [
  '/logos/td.png', '/logos/rbc.png', '/logos/scotiabank.png',
  '/logos/cibc.png', '/logos/bmo.png', '/logos/amex.png',
  '/logos/rogers.png', '/logos/tangerine.png', '/logos/neo.png',
  '/logos/pc.png', '/logos/simplii.png', '/logos/mbna.png',
  '/logos/nationalbank.png', '/logos/hometrust.png'
]

function preloadImages(urls: string[]) {
  // Use requestIdleCallback to avoid blocking main thread
  const load = () => {
    urls.forEach(url => {
      const img = new Image()
      img.src = url
    })
  }

  if ('requestIdleCallback' in window) {
    (window as any).requestIdleCallback(load)
  } else {
    setTimeout(load, 100)
  }
}

// Scroll to top on route change
function ScrollToTop() {
  const { pathname } = useLocation()

  useLayoutEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname])

  return null
}

function App() {
  const { isAuthenticated } = useAuthStore()
  const { loadUserData } = useOptimizerStore()
  const { isSubscribed, checkSubscription } = useSubscriptionStore()
  const { hasSeenOnboarding, setHasSeenOnboarding } = useOnboardingStore()

  // Show onboarding and paywall state - only for native platforms
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showPaywall, setShowPaywall] = useState(false)
  const [iapReady, setIapReady] = useState(false)
  const [appReady, setAppReady] = useState(false)
  const splashHidden = useRef(false)
  const isNative = isNativePlatform()

  // Preload bank logos on app start
  useEffect(() => {
    preloadImages(BANK_LOGOS)
  }, [])

  // Initialize IAP in background - don't block app startup
  useEffect(() => {
    console.log('App: useEffect for IAP, isNative:', isNative)
    if (isNative) {
      // Mark IAP as ready immediately - don't wait for it
      setIapReady(true)
      console.log('App: Starting IAP initialization...')

      // Initialize IAP in background (non-blocking)
      initializeIAP()
        .then((success) => {
          console.log('App: IAP initialized:', success)
          // Check subscription in background
          checkSubscription().catch(console.error)
        })
        .catch((error) => {
          console.error('App: IAP initialization error:', error)
        })
    } else {
      // For web, mark as ready immediately
      setAppReady(true)
    }
  }, [isNative])

  // Show onboarding for first-time users, then go directly to app
  // Paywall is now shown when user hits AI usage limit (not after onboarding)
  useEffect(() => {
    // Web: show onboarding for first-time users
    if (!isNative && !hasSeenOnboarding) {
      setShowOnboarding(true)
      setAppReady(true)
      return
    }

    // Web: already seen onboarding, go to app
    if (!isNative && hasSeenOnboarding) {
      setShowOnboarding(false)
      setAppReady(true)
      return
    }

    // Native: wait for IAP to be ready (but not for subscription check)
    if (isNative && iapReady) {
      if (!hasSeenOnboarding) {
        // First time user - show onboarding
        setShowOnboarding(true)
        setShowPaywall(false)
        setAppReady(true)
      } else {
        // After onboarding, go directly to app (no paywall here)
        // Paywall will be triggered when user hits AI usage limit
        setShowOnboarding(false)
        setShowPaywall(false)
        setAppReady(true)
      }
    }
  }, [isNative, iapReady, hasSeenOnboarding])

  // Hide splash screen when app is ready (with delay to ensure UI is painted)
  useEffect(() => {
    if (appReady && Capacitor.isNativePlatform() && !splashHidden.current) {
      splashHidden.current = true
      // Wait for next frame to ensure UI is fully painted
      requestAnimationFrame(() => {
        setTimeout(() => {
          SplashScreen.hide()
        }, 100)
      })
    }
  }, [appReady])

  // Load user data from backend when app starts with authenticated user
  useEffect(() => {
    if (isAuthenticated) {
      loadUserData()
    }
  }, [isAuthenticated, loadUserData])

  const handleOnboardingComplete = () => {
    setHasSeenOnboarding(true)
    setShowOnboarding(false)
    // After onboarding, show paywall only on native platforms (not web)
    if (isNative && !isSubscribed) {
      setShowPaywall(true)
    }
  }

  const handleSubscribed = () => {
    setShowPaywall(false)
  }

  // Show loading screen while app initializes (native only)
  if (isNative && !appReady) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#FFFCF5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {/* Empty loading screen - splash screen covers this */}
      </div>
    )
  }

  // Show onboarding for first-time users on native platforms
  if (showOnboarding) {
    return <Onboarding onComplete={handleOnboardingComplete} />
  }

  // Show paywall for native platforms that haven't subscribed
  if (showPaywall) {
    return <Paywall onSubscribed={handleSubscribed} />
  }

  return (
    <div className="sv-app-wrapper">
      <ScrollToTop />
      <AppHeader />
      <AuthPanel />
      <main className="sv-main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/cards" element={<CardsPage />} />
          <Route path="/cards/:id" element={<CardDetailPage />} />
          <Route path="/optimizer" element={<OptimizerPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/share/:shareId" element={<SharedResultPage />} />
          <Route path="/me" element={<MePage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/subscription" element={<SubscriptionPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/support" element={<SupportPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
