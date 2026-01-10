export type SpendingCategory =
  // Core categories
  | 'DINING'
  | 'GROCERY'
  | 'GAS'
  | 'TRAVEL'
  | 'STREAMING'
  | 'TRANSIT'
  | 'PHARMACY'
  | 'RENT'
  | 'RECURRING'
  | 'ONLINE_SHOPPING'
  | 'FOREIGN'
  // Extended categories
  | 'RETAIL'
  | 'ENTERTAINMENT'
  | 'PERSONAL_SERVICES'
  | 'HOME_IMPROVEMENT'
  | 'WHOLESALE'
  | 'INSURANCE'
  | 'TELECOM'
  | 'EV_CHARGING'
  | 'LIQUOR'
  // Catch-all
  | 'OTHER'

export interface AffiliateLink {
  id: number
  cardId: number
  bankName: string
  affiliateType: string
  affiliateUrl: string
  commissionAmount?: number
  isActive?: boolean
}

export interface CreditCard {
  id: number
  bank: string
  name: string
  cardType: string
  annualFee: number
  baseRewardRate: number
  rewardType?: 'CASHBACK' | 'POINTS'  // CASHBACK shows %, POINTS shows x
  pointProgram?: string  // e.g., "AIR MILES", "Aeroplan", "MR Points"
  pointValue?: number  // Value per point in dollars (e.g., 0.018 = 1.8¢/point)
  imageUrl?: string
  applyUrl?: string
  noFxFee?: boolean
  signupBonus?: SignupBonus
  rewardRules: RewardRule[]
  amexTravelBonusRate?: number  // Additional points when booking via Amex Travel Online
  affiliateLink?: AffiliateLink
  updatedAt?: string  // Last update time for card data
}

export interface SignupBonus {
  bonusAmount: number
  minSpend: number
  daysToComplete: number
  description?: string                        // 英文描述（旧前端兼容）
  descriptionI18n?: Record<string, string>    // 多语言描述（新前端用）
}

export interface RewardRule {
  id: number
  category: SpendingCategory
  rewardRate: number
  monthlyCapAmount?: number
  description?: string
}

export interface OptimizationRequest {
  userId?: number
  cardIds: number[]
  monthlySpending: Record<SpendingCategory, number>
  locale?: string
  enableAiExplanation?: boolean
}

export interface OptimizationResult {
  recommendations: CategoryRecommendation[]
  monthlyReward: number
  annualReward: number
  totalAnnualFees: number
  netAnnualSavings: number
  summary: string
}

export interface CategoryRecommendation {
  category: SpendingCategory
  monthlySpend: number
  recommendedCard: CreditCard
  rewardRate: number
  monthlyReward: number
  explanation: string
  aiExplanation?: string
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

export const CATEGORY_LABELS: Record<SpendingCategory, string> = {
  // Core categories
  DINING: 'Dining',
  GROCERY: 'Grocery',
  GAS: 'Gas',
  TRAVEL: 'Travel',
  STREAMING: 'Streaming',
  TRANSIT: 'Transit',
  PHARMACY: 'Pharmacy',
  RENT: 'Rent',
  RECURRING: 'Recurring Bills',
  ONLINE_SHOPPING: 'Online Shopping',
  FOREIGN: 'Foreign Currency',
  // Extended categories
  RETAIL: 'Retail',
  ENTERTAINMENT: 'Entertainment',
  PERSONAL_SERVICES: 'Personal Services',
  HOME_IMPROVEMENT: 'Home Improvement',
  WHOLESALE: 'Wholesale',
  INSURANCE: 'Insurance',
  TELECOM: 'Telecom',
  EV_CHARGING: 'EV Charging',
  LIQUOR: 'Liquor',
  // Catch-all
  OTHER: 'Other',
}

// V2: Bank Connection Types
export interface BankConnection {
  id: number
  institutionName: string
  status: 'PENDING' | 'CONNECTED' | 'REFRESHING' | 'ERROR' | 'DISCONNECTED'
  lastSyncAt?: string
  errorMessage?: string
  accounts: BankAccount[]
  createdAt: string
}

export interface BankAccount {
  id: number
  accountType: string
  accountName: string
  accountNumberMasked: string
  balance: number
  isActive: boolean
}

// V2: Transaction Types
export interface Transaction {
  id: number
  amount: number
  merchant: string
  description?: string
  category: SpendingCategory
  transactionDate: string
  cardUsedId?: number
  cardUsedName?: string
  bestCardId?: number
  bestCardName?: string
  bestCardBank?: string
  bestCardRate?: number
  actualCashback?: number
  optimalCashback?: number
  missedCashback?: number
  isAnalyzed: boolean
  isDebitTransaction?: boolean // true if paid with debit card (no cashback)
}

export interface MissedCashbackSummary {
  totalTransactions: number
  totalSpending: number
  totalActualCashback: number
  totalOptimalCashback: number
  totalMissedCashback: number
  // Debit card analysis
  debitTransactions?: number      // Count of debit/checking transactions
  debitSpending?: number          // Total spending via debit cards
  debitMissedCashback?: number    // Cashback lost by not using credit cards
  categoryBreakdown: CategoryMissedCashback[]
  topRecommendations: CardRecommendation[]
}

export interface CategoryMissedCashback {
  category: string
  spending: number
  missedCashback: number
  bestCardName?: string
  bestCardBank?: string
  bestCardRate?: number
}

export interface CardRecommendation {
  cardId: number
  cardName: string
  bank: string
  potentialSavings: number
  bestCategories: string[]
}

// Subscription Types
export type SubscriptionPlatform = 'APPLE' | 'GOOGLE'
export type SubscriptionStatus = 'ACTIVE' | 'TRIALING' | 'EXPIRED' | 'CANCELLED' | 'GRACE_PERIOD' | 'ON_HOLD' | 'PAUSED'
export type BillingPeriod = 'WEEKLY' | 'MONTHLY' | 'YEARLY'

export interface SubscriptionPlan {
  id: number
  planId: string
  name: string
  description?: string
  price: number
  currency: string
  billingPeriod: BillingPeriod
  trialDays: number
  aiMonthlyLimit: number
  isActive: boolean
}

export interface UserSubscription {
  id: number
  userId: number
  planId: string
  planName: string
  price: number
  currency: string
  billingPeriod: BillingPeriod
  platform: SubscriptionPlatform
  status: SubscriptionStatus
  startsAt: string
  expiresAt: string
  isTrial: boolean
  trialEndsAt?: string
  autoRenew: boolean
  aiMonthlyLimit: number
}

export interface VerifyReceiptRequest {
  platform: SubscriptionPlatform
  receiptData?: string
  purchaseToken?: string
  productId?: string
  transactionId?: string
  originalTransactionId?: string
}

export interface VerifyReceiptResponse {
  valid: boolean
  message: string
  subscription?: UserSubscription
}

// Card Usage Guide Types
export type TipType = 'BEST_USE' | 'REDEMPTION' | 'TRAVEL_BENEFIT' | 'INSURANCE' | 'PERK' | 'TRANSFER_PARTNER' | 'STACKING' | 'AVOID'
export type RewardType = 'CASHBACK' | 'POINTS' | 'MILES'

export interface CardUsageTip {
  id: number
  tipType: TipType
  title: string
  content: string
  icon?: string
}

export interface TransferPartner {
  name: string
  ratio: string
  value: string
}

export interface CardUsageGuide {
  cardId: number
  rewardType: RewardType
  pointValue?: number
  pointProgram?: string
  transferPartners?: TransferPartner[]
  tips: CardUsageTip[]
}
