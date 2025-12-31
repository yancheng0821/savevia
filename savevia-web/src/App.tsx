import { useEffect, useLayoutEffect, useState, useRef } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
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
import AdminPage from './pages/AdminPage'
import AppHeader from './components/AppHeader'
import AuthPanel from './components/AuthPanel'
import Paywall from './components/Paywall'
import Onboarding from './components/Onboarding'
import AnimatedSplash from './components/AnimatedSplash'
import ForceUpdate from './components/ForceUpdate'
import { useAuthStore } from './stores/useAuthStore'
import { useOptimizerStore } from './stores/useOptimizerStore'
import { useSubscriptionStore } from './stores/useSubscriptionStore'
import { useOnboardingStore } from './stores/useOnboardingStore'
import { useHomePageStore } from './stores/useHomePageStore'
import { useCardsPageStore } from './stores/useCardsPageStore'
import { isNativePlatform, initializeIAP } from './services/iap'
import { appApi, type AppVersionInfo } from './services/api'

// Current app version (synced with package.json via vite.config.ts)
// Fallback to "1.0.0" for old versions that don't have __APP_VERSION__ defined
const APP_VERSION = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '1.0.0'

// Compare version strings (e.g., "1.0.2" vs "1.0.0")
function compareVersions(v1: string, v2: string): number {
  const parts1 = v1.split('.').map(Number)
  const parts2 = v2.split('.').map(Number)
  for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
    const p1 = parts1[i] || 0
    const p2 = parts2[i] || 0
    if (p1 > p2) return 1
    if (p1 < p2) return -1
  }
  return 0
}

// Preload bank logos to prevent flicker on navigation (lazy loaded)
const BANK_LOGOS = [
  '/logos/td.png', '/logos/rbc.png', '/logos/scotiabank.png',
  '/logos/cibc.png', '/logos/bmo.png', '/logos/amex.png',
  '/logos/rogers.png', '/logos/tangerine.png', '/logos/neo.png',
  '/logos/pc.png', '/logos/simplii.png', '/logos/mbna.png',
  '/logos/nationalbank.png', '/logos/hometrust.png',
  '/logos/brim.png', '/logos/wealthsimple.png', '/logos/desjardins.png',
  '/logos/canadiantire.png', '/logos/vancity.png', '/logos/meridian.png',
  '/logos/coastcapital.png', '/logos/walmart.png'
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

// Create a global scroll position manager
const scrollPositions = new Map<string, number>()

// Scroll handler for route change
function ScrollToTop() {
  const { pathname } = useLocation()
  const prevPathnameRef = useRef<string>('')
  const { setShowCardModal } = useHomePageStore()

  // Save scroll position before leaving a route
  useEffect(() => {
    const handleScroll = () => {
      if (prevPathnameRef.current) {
        scrollPositions.set(prevPathnameRef.current, window.scrollY)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [pathname])

  // Restore or reset scroll position on route change
  // Close home page modal when navigating away (not swipe back)
  useLayoutEffect(() => {
    // Only process when pathname actually changes
    if (prevPathnameRef.current === pathname) {
      return
    }

    // Save scroll position of the page we're leaving
    if (prevPathnameRef.current) {
      scrollPositions.set(prevPathnameRef.current, window.scrollY)
    }

    // Close modal when leaving home page via navigation (prevents flicker when returning)
    // Swipe back doesn't trigger this because it uses iOS native gesture
    if (prevPathnameRef.current === '/' && pathname !== '/') {
      setShowCardModal(false)
    }

    prevPathnameRef.current = pathname

    // For home route, restore previous scroll position if it exists
    // Note: /cards uses its own scroll restoration in CardsPage via useCardsPageStore
    if (pathname === '/') {
      // For home page, prefer the manually saved position (from modal view details click)
      let savedPosition = scrollPositions.get(pathname) || 0
      if ((window as any).__savedHomeScrollPosition !== undefined) {
        savedPosition = (window as any).__savedHomeScrollPosition
        delete (window as any).__savedHomeScrollPosition
      }
      // Scroll synchronously in useLayoutEffect to prevent flash
      window.scrollTo(0, savedPosition)
    } else if (pathname === '/cards') {
      // CardsPage handles its own scroll restoration - do nothing here
    } else {
      // For all other routes, scroll to top
      window.scrollTo(0, 0)
    }
  }, [pathname, setShowCardModal])

  return null
}

function App() {
  const { isAuthenticated } = useAuthStore()
  const { loadUserData } = useOptimizerStore()
  const { isSubscribed, checkSubscription } = useSubscriptionStore()
  const { hasSeenOnboarding, setHasSeenOnboarding, loadOnboardingState, isLoading: isOnboardingLoading } = useOnboardingStore()
  // Pre-hydrate CardsPageStore to prevent scroll button flicker on iOS swipe back
  useCardsPageStore()

  // Show onboarding and paywall state - only for native platforms
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showPaywall, setShowPaywall] = useState(false)
  const [iapReady, setIapReady] = useState(false)
  const [showAnimatedSplash, setShowAnimatedSplash] = useState(true)
  const [forceUpdateInfo, setForceUpdateInfo] = useState<AppVersionInfo | null>(null)
  const splashHidden = useRef(false)
  const isNative = isNativePlatform()

  // Preload bank logos on app start
  useEffect(() => {
    preloadImages(BANK_LOGOS)
  }, [])

  // Check app version immediately on native platforms (during splash screen)
  useEffect(() => {
    if (!isNative) return

    const checkVersion = async () => {
      try {
        const response = await appApi.getVersion()
        if (response.code === 200 && response.data) {
          const { minVersion } = response.data
          // If current version is below minimum, show force update
          if (compareVersions(APP_VERSION, minVersion) < 0) {
            setForceUpdateInfo(response.data)
          }
        }
      } catch (error) {
        // Silently fail - don't block app if version check fails
        console.error('Version check failed:', error)
      }
    }

    // Check version immediately, don't wait for splash to finish
    checkVersion()
  }, []) // Remove isNative dependency to run only once on mount

  // Load onboarding state from Keychain on app start (native only)
  useEffect(() => {
    if (isNative) {
      loadOnboardingState()
    }
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
    }
  }, [isNative])

  // Show onboarding only for native app first-time users
  // Web: never show onboarding
  useEffect(() => {
    // Web: never show onboarding
    if (!isNative) {
      setShowOnboarding(false)
      return
    }

    // Native: wait for IAP to be ready AND onboarding state to load from Keychain
    if (isNative && iapReady && !isOnboardingLoading) {
      if (!hasSeenOnboarding) {
        // First time user - show onboarding
        setShowOnboarding(true)
        setShowPaywall(false)
      } else {
        // After onboarding, go directly to app
        setShowOnboarding(false)
        setShowPaywall(false)
      }
    }
  }, [isNative, iapReady, hasSeenOnboarding, isOnboardingLoading])

  
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

  // Show animated splash screen on native platforms
  if (isNative && showAnimatedSplash) {
    // Hide native splash immediately when showing animated splash
    if (!splashHidden.current) {
      splashHidden.current = true
      SplashScreen.hide()
    }
    return (
      <AnimatedSplash
        duration={2800}
        onComplete={() => setShowAnimatedSplash(false)}
      />
    )
  }

  // Show force update modal if version is too old (blocks all interaction)
  if (forceUpdateInfo) {
    return (
      <ForceUpdate
        iosStoreUrl={forceUpdateInfo.iosStoreUrl}
        androidStoreUrl={forceUpdateInfo.androidStoreUrl}
        latestVersion={forceUpdateInfo.latestVersion}
      />
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
          {/* Admin page - web only */}
          {!isNative && <Route path="/admin" element={<AdminPage />} />}
        </Routes>
      </main>
    </div>
  )
}

export default App
