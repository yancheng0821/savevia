import { useEffect, useLayoutEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CardsPage from './pages/CardsPage'
import CardDetailPage from './pages/CardDetailPage'
import OptimizerPage from './pages/OptimizerPage'
import ResultPage from './pages/ResultPage'
import SharedResultPage from './pages/SharedResultPage'
import MePage from './pages/MePage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import AppHeader from './components/AppHeader'
import AuthPanel from './components/AuthPanel'
import { useAuthStore } from './stores/useAuthStore'
import { useOptimizerStore } from './stores/useOptimizerStore'

// Preload bank logos to prevent flicker on navigation
const BANK_LOGOS = [
  '/logos/td.png', '/logos/rbc.png', '/logos/scotiabank.png',
  '/logos/cibc.png', '/logos/bmo.png', '/logos/amex.png',
  '/logos/rogers.png', '/logos/tangerine.png', '/logos/neo.png',
  '/logos/pc.png', '/logos/simplii.png', '/logos/mbna.png',
  '/logos/nationalbank.png', '/logos/hometrust.png'
]

function preloadImages(urls: string[]) {
  urls.forEach(url => {
    const img = new Image()
    img.src = url
  })
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

  // Preload bank logos on app start
  useEffect(() => {
    preloadImages(BANK_LOGOS)
  }, [])

  // Load user data from backend when app starts with authenticated user
  useEffect(() => {
    if (isAuthenticated) {
      loadUserData()
    }
  }, [isAuthenticated, loadUserData])

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
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
