import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { Capacitor } from '@capacitor/core'
import { GoogleAuth } from '@southdevs/capacitor-google-auth'
import App from './App'
import './i18n'
import './index.css'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

// Initialize Google Auth for native platforms (iOS/Android)
if (Capacitor.isNativePlatform()) {
  const platform = Capacitor.getPlatform()

  if (platform === 'android') {
    // Android: Use Web Client ID (serverClientId) for authentication
    // The Android Client ID is configured via SHA-1 in Google Cloud Console
    GoogleAuth.initialize({
      clientId: '890444343202-ju6uie2f6vuk53ccbeoqa4eitrmtslhr.apps.googleusercontent.com', // Web Client ID
      scopes: ['profile', 'email'],
      grantOfflineAccess: true,
    })
  } else {
    // iOS: Use iOS Client ID
    GoogleAuth.initialize({
      clientId: '890444343202-npol552p21etjqs53homftgo6430g4qo.apps.googleusercontent.com',
      scopes: ['profile', 'email'],
      grantOfflineAccess: true,
    })
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider
          theme={{
            token: {
              colorPrimary: '#1890ff',
            },
          }}
        >
          <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <App />
          </BrowserRouter>
        </ConfigProvider>
      </QueryClientProvider>
    </GoogleOAuthProvider>
  </React.StrictMode>
)
