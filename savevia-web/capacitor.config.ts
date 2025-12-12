import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.savevia.app',
  appName: 'SaveVia',
  webDir: 'dist',
  // Development: Live reload from Mac (uncomment for development)
  // server: {
  //   url: 'http://192.168.1.196:5173',
  //   cleartext: true
  // },
  ios: {
    // iOS settings
    scrollEnabled: true,
    allowsLinkPreview: false,
    backgroundColor: '#FFFCF5',
    // Bounce effect is enabled in MainViewController.swift
  },
  android: {
    // Android settings for status bar and edge-to-edge display
    backgroundColor: '#FFFCF5',
    allowMixedContent: true,
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: false,
      launchFadeOutDuration: 200,
      backgroundColor: '#FFFCF5',
      showSpinner: false,
    },
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '890444343202-ju6uie2f6vuk53ccbeoqa4eitrmtslhr.apps.googleusercontent.com',
      iosClientId: '890444343202-npol552p21etjqs53homftgo6430g4qo.apps.googleusercontent.com',
      androidClientId: '890444343202-t194ib3qbqfu4hcp3ln96hpmbijsqlnm.apps.googleusercontent.com',
      forceCodeForRefreshToken: false
    }
  }
};

export default config;
