export type SpendingCategory =
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
  | 'OTHER'

export interface CreditCard {
  id: number
  bank: string
  name: string
  cardType: string
  annualFee: number
  baseRewardRate: number
  imageUrl?: string
  applyUrl?: string
  noFxFee?: boolean
  signupBonus?: SignupBonus
  rewardRules: RewardRule[]
}

export interface SignupBonus {
  bonusAmount: number
  minSpend: number
  daysToComplete: number
  description?: string
}

export interface RewardRule {
  id: number
  category: SpendingCategory
  rewardRate: number
  monthlyCapAmount?: number
  description?: string
}

export interface OptimizationRequest {
  cardIds: number[]
  monthlySpending: Record<SpendingCategory, number>
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
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

export const CATEGORY_LABELS: Record<SpendingCategory, string> = {
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
  OTHER: 'Other',
}
