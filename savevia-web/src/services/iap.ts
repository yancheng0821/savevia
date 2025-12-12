/**
 * In-App Purchase Service
 * Handles Apple App Store and Google Play subscriptions via RevenueCat
 *
 * Architecture: Frontend-only subscription management
 * - RevenueCat handles all payment processing and receipt validation
 * - No backend verification needed
 * - Subscription status is checked directly via RevenueCat SDK
 */

import { Capacitor } from '@capacitor/core'
import { Purchases } from '@revenuecat/purchases-capacitor'

// Product IDs (must match RevenueCat / App Store Connect / Google Play Console)
export const PRODUCT_IDS = {
  MONTHLY: 'savevia_pro_monthly',
  YEARLY: 'savevia_pro_yearly',
}

export type Platform = 'ios' | 'android' | 'web'

export interface IAPProduct {
  productId: string
  title: string
  description: string
  price: string
  priceAsNumber: number
  currency: string
}

export interface IAPPurchaseResult {
  success: boolean
  error?: string
  productId?: string
  expiresAt?: string  // ISO 8601 format
}

/**
 * Check if running on native platform
 */
export const isNativePlatform = (): boolean => {
  return Capacitor.isNativePlatform()
}

/**
 * Get current platform
 */
export const getPlatform = (): Platform => {
  const platform = Capacitor.getPlatform()
  if (platform === 'ios') return 'ios'
  if (platform === 'android') return 'android'
  return 'web'
}

/**
 * Initialize IAP plugin (must be called before any purchases)
 */
export const initializeIAP = async (): Promise<boolean> => {
  console.log('IAP: initializeIAP called')
  if (!isNativePlatform()) {
    console.log('IAP: Not on native platform, skipping initialization')
    return false
  }

  try {
    const platform = getPlatform()
    const apiKey = platform === 'ios'
      ? import.meta.env.VITE_REVENUECAT_IOS_API_KEY
      : import.meta.env.VITE_REVENUECAT_ANDROID_API_KEY

    console.log('IAP: Platform:', platform, 'API Key exists:', !!apiKey)

    if (!apiKey) {
      console.warn('IAP: RevenueCat API key not configured')
      return false
    }

    console.log('IAP: Calling Purchases.configure...')
    await Purchases.configure({ apiKey })

    console.log('IAP: Initialized successfully')
    return true
  } catch (error) {
    console.error('IAP: Failed to initialize', error)
    return false
  }
}

/**
 * Get available products from RevenueCat
 */
export const getProducts = async (): Promise<IAPProduct[]> => {
  // Fallback products for web or when RevenueCat is not available
  const fallbackProducts: IAPProduct[] = [
    {
      productId: PRODUCT_IDS.MONTHLY,
      title: 'SaveVia Pro Monthly',
      description: 'Unlimited AI optimization and premium features',
      price: 'CA$5.99',
      priceAsNumber: 5.99,
      currency: 'CAD',
    },
    {
      productId: PRODUCT_IDS.YEARLY,
      title: 'SaveVia Pro Annual',
      description: 'Save 20% with annual billing',
      price: 'CA$59.99',
      priceAsNumber: 59.99,
      currency: 'CAD',
    },
  ]

  if (!isNativePlatform()) {
    return fallbackProducts
  }

  // Add timeout to prevent hanging when StoreKit/RevenueCat is not ready
  const timeoutPromise = new Promise<IAPProduct[]>((resolve) => {
    setTimeout(() => {
      console.log('IAP: getProducts timed out, using fallback')
      resolve(fallbackProducts)
    }, 3000)
  })

  const fetchPromise = (async () => {
    try {
      const offerings = await Purchases.getOfferings()

      if (!offerings.current?.availablePackages?.length) {
        console.log('IAP: No offerings available, using fallback products')
        return fallbackProducts
      }

      return offerings.current.availablePackages.map((pkg: any) => ({
        productId: pkg.product.identifier,
        title: pkg.product.title || (pkg.product.identifier.includes('yearly') ? 'SaveVia Pro Annual' : 'SaveVia Pro Monthly'),
        description: pkg.product.description || 'Premium features',
        price: pkg.product.priceString,
        priceAsNumber: pkg.product.price,
        currency: pkg.product.currencyCode,
      }))
    } catch (error) {
      console.error('IAP: Failed to get products, using fallback', error)
      return fallbackProducts
    }
  })()

  return Promise.race([fetchPromise, timeoutPromise])
}

/**
 * Purchase a subscription via RevenueCat
 */
export const purchaseSubscription = async (productId: string): Promise<IAPPurchaseResult> => {
  if (!isNativePlatform()) {
    return {
      success: false,
      error: 'In-app purchases are only available on mobile devices',
    }
  }

  try {
    
    // Get the package to purchase
    const offerings = await Purchases.getOfferings()
    const pkg = offerings.current?.availablePackages.find(
      (p: any) => p.product.identifier === productId
    )

    if (!pkg) {
      return { success: false, error: 'Product not found' }
    }

    // Make the purchase - RevenueCat handles all validation
    const { customerInfo } = await Purchases.purchasePackage({ aPackage: pkg })

    // Check if purchase was successful
    const hasActiveEntitlement = Object.keys(customerInfo.entitlements?.active || {}).length > 0
    const hasActiveSubscription = customerInfo.activeSubscriptions?.length > 0
    const hasPurchasedProduct = customerInfo.allPurchasedProductIdentifiers?.includes(productId)
    const purchaseSuccessful = hasActiveEntitlement || hasActiveSubscription || hasPurchasedProduct

    console.log('IAP: Purchase result -', {
      hasActiveEntitlement,
      hasActiveSubscription,
      hasPurchasedProduct,
    })

    if (purchaseSuccessful) {
      // Get expiration date from entitlements
      const entitlement = Object.values(customerInfo.entitlements?.active || {})[0] as any
      const expiresAt = entitlement?.expirationDate || undefined

      return {
        success: true,
        productId,
        expiresAt,
      }
    } else {
      return { success: false, error: 'Purchase not confirmed' }
    }
  } catch (error: any) {
    console.error('IAP: Purchase failed', error)

    if (error.code === 'ITEM_ALREADY_OWNED') {
      return restorePurchases()
    }

    if (error.userCancelled) {
      return { success: false, error: 'Purchase cancelled' }
    }

    return { success: false, error: error.message || 'Purchase failed' }
  }
}

/**
 * Restore previous purchases via RevenueCat
 */
export const restorePurchases = async (): Promise<IAPPurchaseResult> => {
  if (!isNativePlatform()) {
    return { success: false, error: 'Restore is only available on mobile devices' }
  }

  try {
        const { customerInfo } = await Purchases.restorePurchases()

    // Check if there are any active subscriptions
    const hasActiveEntitlement = Object.keys(customerInfo.entitlements?.active || {}).length > 0
    const hasActiveSubscription = customerInfo.activeSubscriptions?.length > 0

    if (hasActiveEntitlement || hasActiveSubscription) {
      // Get expiration date and product ID from entitlements
      const entitlement = Object.values(customerInfo.entitlements?.active || {})[0] as any
      const expiresAt = entitlement?.expirationDate || undefined
      const productId = entitlement?.productIdentifier || customerInfo.activeSubscriptions?.[0]

      return {
        success: true,
        productId,
        expiresAt,
      }
    } else {
      return { success: false, error: 'No previous purchases found' }
    }
  } catch (error: any) {
    console.error('IAP: Restore failed', error)
    return { success: false, error: error.message || 'Restore failed' }
  }
}

/**
 * Check if user has active subscription via RevenueCat
 */
export const checkSubscriptionStatus = async (): Promise<boolean> => {
  if (!isNativePlatform()) {
    return false
  }

  // Add timeout to prevent hanging
  const timeoutPromise = new Promise<boolean>((resolve) => {
    setTimeout(() => {
      console.warn('IAP: Subscription check timed out')
      resolve(false)
    }, 5000)
  })

  const checkPromise = (async () => {
    try {
            const { customerInfo } = await Purchases.getCustomerInfo()

      const hasActiveEntitlement = Object.keys(customerInfo.entitlements?.active || {}).length > 0
      const hasActiveSubscription = customerInfo.activeSubscriptions?.length > 0

      return hasActiveEntitlement || hasActiveSubscription
    } catch (error) {
      console.error('IAP: Failed to check subscription status', error)
      return false
    }
  })()

  return Promise.race([checkPromise, timeoutPromise])
}

export default {
  isNativePlatform,
  getPlatform,
  initializeIAP,
  getProducts,
  purchaseSubscription,
  restorePurchases,
  checkSubscriptionStatus,
  PRODUCT_IDS,
}
