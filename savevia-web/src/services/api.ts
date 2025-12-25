/**
 * SaveVia API Service
 * 所有前端请求统一通过 Gateway 访问后端服务
 */

import type {
  ApiResponse,
  CreditCard,
  OptimizationRequest,
  OptimizationResult,
  BankConnection,
  Transaction,
  MissedCashbackSummary,
  SubscriptionPlan,
  UserSubscription,
  VerifyReceiptRequest,
  VerifyReceiptResponse,
  CardUsageGuide,
} from '../types'

// API 基础地址 - 通过 Gateway 访问
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Token 管理
export const tokenManager = {
  setToken: (token: string): void => {
    localStorage.setItem('token', token)
  },

  getToken: (): string | null => {
    return localStorage.getItem('token')
  },

  setRefreshToken: (token: string): void => {
    localStorage.setItem('refreshToken', token)
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem('refreshToken')
  },

  clearAll: (): void => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  },
}

// Token 刷新状态
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: Error) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve(token!)
    }
  })
  failedQueue = []
}

/**
 * 统一请求处理器
 */
const createRequest = async (
  url: string,
  options: RequestInit = {},
  isRetry: boolean = false
): Promise<any> => {
  const token = tokenManager.getToken()

  // 处理 FormData 请求
  const isFileUpload = options.body instanceof FormData

  const defaultHeaders: Record<string, string> = {
    ...(isFileUpload ? {} : { 'Content-Type': 'application/json' }),
    ...(token && { Authorization: `Bearer ${token}` }),
    Accept: 'application/json',
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }

  try {
    // 添加 30 秒超时控制
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000)

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...config,
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    // 处理 401 - Token 过期，自动刷新
    if (response.status === 401 && !isRetry) {
      const refreshToken = tokenManager.getRefreshToken()
      if (!refreshToken) {
        tokenManager.clearAll()
        window.dispatchEvent(new CustomEvent('sessionExpired'))
        throw new Error('Session expired')
      }

      // 防止重复刷新 Token
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => {
          return createRequest(url, options, true)
        })
      }

      isRefreshing = true

      try {
        const refreshResponse = await fetch(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refreshToken }),
          }
        )

        if (refreshResponse.ok) {
          const result = await refreshResponse.json()
          if (result.code === 200 && result.data) {
            tokenManager.setToken(result.data.token)
            if (result.data.refreshToken) {
              tokenManager.setRefreshToken(result.data.refreshToken)
            }
            processQueue(null, result.data.token)
            isRefreshing = false
            return createRequest(url, options, true)
          }
        }
        throw new Error('Token refresh failed')
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        isRefreshing = false
        tokenManager.clearAll()
        window.dispatchEvent(new CustomEvent('sessionExpired'))
        throw refreshError
      }
    }

    // 解析响应
    let responseData
    try {
      const responseText = await response.text()
      try {
        responseData = JSON.parse(responseText)
      } catch (parseError) {
        console.error('JSON parse error:', parseError, 'Raw text:', responseText.substring(0, 200))
        responseData = {
          code: response.status,
          message: `HTTP ${response.status}: ${response.statusText}`,
          data: null,
        }
      }
    } catch (readError) {
      console.error('Response read error:', readError)
      responseData = {
        code: response.status,
        message: `HTTP ${response.status}: ${response.statusText}`,
        data: null,
      }
    }

    if (!response.ok) {
      const error = new Error(
        responseData.message || `HTTP error! status: ${response.status}`
      )
      ;(error as any).status = response.status
      ;(error as any).responseData = responseData
      throw error
    }

    // 检查业务码（某些 API 返回 HTTP 200 但业务逻辑失败）
    if (responseData.code && responseData.code !== 200 && responseData.success === false) {
      const error = new Error(responseData.message || 'Business logic error')
      ;(error as any).code = responseData.code
      ;(error as any).responseData = responseData
      throw error
    }

    return responseData
  } catch (error: any) {
    // 超时错误
    if (error.name === 'AbortError') {
      throw new Error('Request timeout')
    }
    console.error('API request failed:', url, error)
    throw error
  }
}

/**
 * 统一错误处理
 */
export const handleApiError = (error: any): string => {
  if (error.responseData?.message) {
    return error.responseData.message
  }

  if (error.status === 503) {
    return 'Service unavailable, please try again later'
  }

  if (error.status === 500) {
    return 'Server error, please try again later'
  }

  if (error.status === 404) {
    return 'Resource not found'
  }

  if (error.status === 403) {
    return 'Access forbidden'
  }

  if (error.status === 401) {
    return 'Please login again'
  }

  return error.message || 'An unexpected error occurred'
}

// ==================== API 模块 ====================

/**
 * 认证 API
 */
export const authApi = {
  // 注册
  register: async (data: {
    email: string
    password: string
    name: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 登录
  login: async (data: {
    email: string
    password: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 刷新 Token
  refreshToken: async (refreshToken: string): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    })
  },

  // Google 登录
  googleLogin: async (data: {
    credential: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/google', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // Apple 登录
  appleLogin: async (data: {
    identityToken: string
    fullName?: string
    email?: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/apple', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 修改密码
  changePassword: async (data: {
    currentPassword: string
    newPassword: string
  }): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // 设置密码 (OAuth用户)
  setPassword: async (data: {
    newPassword: string
  }): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/auth/set-password', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // 忘记密码
  forgotPassword: async (data: {
    email: string
  }): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 重置密码
  resetPassword: async (data: {
    token: string
    newPassword: string
  }): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // 发送邮箱验证
  sendVerification: async (): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/auth/send-verification', {
      method: 'POST',
    })
  },

  // 验证邮箱
  verifyEmail: async (token: string): Promise<ApiResponse<void>> => {
    return createRequest(`/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`, {
      method: 'POST',
    })
  },

  // 更新订阅状态 (购买成功后调用)
  updateSubscription: async (data: {
    subscriptionType: string  // FREE or PRO
    expiresAt?: string        // ISO 8601 format
    platform: string          // ios, android, web
    productId?: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/subscription', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // 获取订阅状态
  getSubscription: async (): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/auth/subscription', {
      method: 'GET',
    })
  },
}

/**
 * 信用卡 API
 */
export const cardApi = {
  // 获取所有信用卡
  getAll: async (): Promise<CreditCard[]> => {
    const response = await createRequest('/api/v1/cards', {
      method: 'GET',
    })
    return response.data
  },

  // 根据 ID 获取信用卡
  getById: async (id: number): Promise<CreditCard> => {
    const response = await createRequest(`/api/v1/cards/${id}`, {
      method: 'GET',
    })
    return response.data
  },

  // 根据银行获取信用卡
  getByBank: async (bank: string): Promise<CreditCard[]> => {
    const response = await createRequest(`/api/v1/cards/bank/${bank}`, {
      method: 'GET',
    })
    return response.data
  },

  // 批量获取信用卡
  getByIds: async (ids: number[]): Promise<CreditCard[]> => {
    const response = await createRequest('/api/v1/cards/batch', {
      method: 'POST',
      body: JSON.stringify(ids),
    })
    return response.data
  },

  // 获取卡片使用指南
  getUsageGuide: async (id: number, lang: string = 'en'): Promise<CardUsageGuide> => {
    const response = await createRequest(`/api/v1/cards/${id}/usage-guide?lang=${lang}`, {
      method: 'GET',
    })
    return response.data
  },
}

/**
 * 优化器 API
 */
export const optimizerApi = {
  // 计算最优返现方案
  calculate: async (
    request: OptimizationRequest
  ): Promise<OptimizationResult> => {
    const response = await createRequest('/api/v1/optimize/calculate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
    return response.data
  },

  // 分享/保存结果
  shareResult: async (result: OptimizationResult): Promise<ApiResponse<{ shareId: string; shareUrl: string }>> => {
    return createRequest('/api/v1/optimize/share', {
      method: 'POST',
      body: JSON.stringify({ result }),
    })
  },

  // 获取分享的结果
  getSharedResult: async (shareId: string): Promise<ApiResponse<OptimizationResult>> => {
    return createRequest(`/api/v1/optimize/share/${shareId}`, {
      method: 'GET',
    })
  },

  // 保存用户当前结果
  saveUserResult: async (result: OptimizationResult): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/optimize/user-result', {
      method: 'POST',
      body: JSON.stringify({ result }),
    })
  },

  // 获取用户保存的结果
  getUserResult: async (): Promise<ApiResponse<OptimizationResult | null>> => {
    return createRequest('/api/v1/optimize/user-result', {
      method: 'GET',
    })
  },
}

/**
 * 用户 API
 */
export const userApi = {
  // 获取当前用户信息
  getCurrentUser: async (): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/users/me', {
      method: 'GET',
    })
  },

  // 更新用户信息
  updateProfile: async (data: {
    name?: string
    email?: string
  }): Promise<ApiResponse<any>> => {
    return createRequest('/api/v1/users/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // 获取用户持有的信用卡
  getUserCards: async (): Promise<ApiResponse<number[]>> => {
    return createRequest('/api/v1/users/me/cards', {
      method: 'GET',
    })
  },

  // 保存用户持有的信用卡
  saveUserCards: async (cardIds: number[]): Promise<ApiResponse<number[]>> => {
    return createRequest('/api/v1/users/me/cards', {
      method: 'POST',
      body: JSON.stringify({ cardIds }),
    })
  },

  // 获取用户消费数据
  getUserSpending: async (): Promise<ApiResponse<Record<string, number>>> => {
    return createRequest('/api/v1/users/me/spending', {
      method: 'GET',
    })
  },

  // 保存用户消费数据
  saveUserSpending: async (spending: Record<string, number>): Promise<ApiResponse<Record<string, number>>> => {
    return createRequest('/api/v1/users/me/spending', {
      method: 'POST',
      body: JSON.stringify({ spending }),
    })
  },

  // 上传并更新头像
  uploadAvatar: async (file: File): Promise<ApiResponse<any>> => {
    const formData = new FormData()
    formData.append('file', file)
    return createRequest('/api/v1/users/me/avatar', {
      method: 'POST',
      body: formData,
    })
  },

  // 注销账户 (需要验证密码)
  deleteAccount: async (password: string): Promise<ApiResponse<void>> => {
    return createRequest('/api/v1/users/me', {
      method: 'DELETE',
      body: JSON.stringify({ password }),
    })
  },

  // 获取AI使用情况
  getAiUsage: async (): Promise<ApiResponse<{ used: number; limit: number; remaining: number; isProUser: boolean }>> => {
    return createRequest('/api/v1/users/ai-usage', {
      method: 'GET',
    })
  },
}

/**
 * Connection limit info type
 */
export interface ConnectionLimit {
  used: number
  max: number
  remaining: number
  canConnect: boolean
  yearMonth?: string
}

/**
 * Bank Connection API (V2)
 */
export const bankApi = {
  // Get Flinks Connect configuration (includes connection limit)
  getFlinksConfig: async (): Promise<ApiResponse<{
    customerId: string
    iframeUrl: string
    sandbox: boolean
    connectUrl: string
    connectionLimit: ConnectionLimit
  }>> => {
    return createRequest('/api/v1/optimize/bank/flinks-config', {
      method: 'GET',
    })
  },

  // Get connection limit status
  getConnectionLimit: async (): Promise<ApiResponse<ConnectionLimit>> => {
    return createRequest('/api/v1/optimize/bank/connection-limit', {
      method: 'GET',
    })
  },

  // Connect bank via Flinks
  connect: async (data: {
    loginId: string
    institutionName: string
    accountId?: string
    userCardIds?: number[]
  }): Promise<ApiResponse<BankConnection>> => {
    return createRequest('/api/v1/optimize/bank/connect', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // Get all bank connections
  getConnections: async (): Promise<ApiResponse<BankConnection[]>> => {
    return createRequest('/api/v1/optimize/bank/connections', {
      method: 'GET',
    })
  },

  // Refresh bank data (local only, no Flinks API call)
  refresh: async (connectionId: number): Promise<ApiResponse<BankConnection>> => {
    return createRequest(`/api/v1/optimize/bank/connections/${connectionId}/refresh`, {
      method: 'POST',
    })
  },

  // Resync bank data from Flinks (costs connection quota!)
  resync: async (connectionId: number, userCardIds?: number[]): Promise<ApiResponse<BankConnection>> => {
    return createRequest(`/api/v1/optimize/bank/connections/${connectionId}/resync`, {
      method: 'POST',
      body: JSON.stringify({ userCardIds }),
    })
  },

  // Disconnect bank
  disconnect: async (connectionId: number): Promise<ApiResponse<void>> => {
    return createRequest(`/api/v1/optimize/bank/connections/${connectionId}`, {
      method: 'DELETE',
    })
  },
}

/**
 * Transaction API (V2)
 */
export const transactionApi = {
  // Get recent transactions with recommendations
  getRecent: async (limit: number = 50, cardIds?: number[]): Promise<ApiResponse<Transaction[]>> => {
    const headers: Record<string, string> = {}
    if (cardIds && cardIds.length > 0) {
      headers['X-User-Card-Ids'] = cardIds.join(',')
    }
    return createRequest(`/api/v1/optimize/transactions?limit=${limit}`, {
      method: 'GET',
      headers,
    })
  },

  // Get missed cashback summary
  getSummary: async (cardIds?: number[]): Promise<ApiResponse<MissedCashbackSummary>> => {
    const headers: Record<string, string> = {}
    if (cardIds && cardIds.length > 0) {
      headers['X-User-Card-Ids'] = cardIds.join(',')
    }
    return createRequest('/api/v1/optimize/transactions/summary', {
      method: 'GET',
      headers,
    })
  },

  // Trigger transaction analysis
  analyze: async (cardIds?: number[], force: boolean = false): Promise<ApiResponse<void>> => {
    const headers: Record<string, string> = {}
    if (cardIds && cardIds.length > 0) {
      headers['X-User-Card-Ids'] = cardIds.join(',')
    }
    const url = force
      ? '/api/v1/optimize/transactions/analyze?force=true'
      : '/api/v1/optimize/transactions/analyze'
    return createRequest(url, {
      method: 'POST',
      headers,
    })
  },
}

/**
 * Subscription API
 */
export const subscriptionApi = {
  // Get available subscription plans
  getPlans: async (): Promise<ApiResponse<SubscriptionPlan[]>> => {
    return createRequest('/api/v1/subscriptions/plans', {
      method: 'GET',
    })
  },

  // Get current user's subscription
  getMySubscription: async (): Promise<ApiResponse<UserSubscription | null>> => {
    return createRequest('/api/v1/subscriptions/me', {
      method: 'GET',
    })
  },

  // Verify and process receipt
  verifyReceipt: async (request: VerifyReceiptRequest): Promise<ApiResponse<VerifyReceiptResponse>> => {
    return createRequest('/api/v1/subscriptions/verify', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Restore purchases
  restorePurchases: async (request: VerifyReceiptRequest): Promise<ApiResponse<VerifyReceiptResponse>> => {
    return createRequest('/api/v1/subscriptions/restore', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Cancel subscription
  cancel: async (): Promise<ApiResponse<boolean>> => {
    return createRequest('/api/v1/subscriptions/cancel', {
      method: 'POST',
    })
  },

  // Get subscription history
  getHistory: async (): Promise<ApiResponse<UserSubscription[]>> => {
    return createRequest('/api/v1/subscriptions/history', {
      method: 'GET',
    })
  },
}

/**
 * 联盟链接 API
 */
export const affiliateApi = {
  // 获取卡片的联盟申卡链接（返回第一个活跃的）
  getAffiliateLink: async (cardId: number): Promise<any> => {
    const response = await createRequest(`/api/v1/affiliate/links/${cardId}`, {
      method: 'GET',
    })
    return response.data
  },

  // 获取卡片的所有联盟申卡链接
  getAllAffiliateLinks: async (cardId: number): Promise<any[]> => {
    const response = await createRequest(`/api/v1/affiliate/links-all/${cardId}`, {
      method: 'GET',
    })
    return response.data || []
  },

  // 追踪用户点击申卡链接
  trackClick: async (
    cardId: number,
    affiliateLinkId: number,
    bankName: string,
    userId?: number
  ): Promise<void> => {
    await createRequest('/api/v1/affiliate/track-click', {
      method: 'POST',
      body: JSON.stringify({
        cardId,
        affiliateLinkId,
        bankName,
        userId: userId || null,
      }),
    })
  },

  // 获取卡片的今日点击统计
  getClickCountToday: async (cardId: number): Promise<number> => {
    const response = await createRequest(`/api/v1/affiliate/stats/${cardId}/today`, {
      method: 'GET',
    })
    return response.data || 0
  },

  // 获取特定银行的今日点击统计
  getClickCountTodayByBank: async (cardId: number, bankName: string): Promise<number> => {
    const response = await createRequest(
      `/api/v1/affiliate/stats/${cardId}/bank/${bankName}/today`,
      {
        method: 'GET',
      }
    )
    return response.data || 0
  },

  // ==================== 管理接口 ====================

  // 添加新的联盟链接
  addAffiliateLink: async (data: {
    cardId: number
    bankName: string
    affiliateType: string
    affiliateUrl: string
    commissionAmount?: number
  }): Promise<number> => {
    const response = await createRequest('/api/v1/affiliate/admin/links', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return response.data
  },

  // 更新联盟链接
  updateAffiliateLink: async (
    id: number,
    data: {
      bankName: string
      affiliateType: string
      affiliateUrl: string
      commissionAmount?: number
      isActive?: boolean
    }
  ): Promise<void> => {
    await createRequest(`/api/v1/affiliate/admin/links/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // 删除联盟链接
  deleteAffiliateLink: async (id: number): Promise<void> => {
    await createRequest(`/api/v1/affiliate/admin/links/${id}`, {
      method: 'DELETE',
    })
  },

  // 获取所有活跃的联盟链接
  getAllActiveLinks: async (): Promise<any[]> => {
    const response = await createRequest('/api/v1/affiliate/admin/links-all', {
      method: 'GET',
    })
    return response.data || []
  },

  // 获取特定银行的所有活跃链接
  getLinksByBank: async (bankName: string): Promise<any[]> => {
    const response = await createRequest(`/api/v1/affiliate/admin/bank/${bankName}`, {
      method: 'GET',
    })
    return response.data || []
  },
}

export default {
  auth: authApi,
  card: cardApi,
  optimizer: optimizerApi,
  user: userApi,
  bank: bankApi,
  transaction: transactionApi,
  subscription: subscriptionApi,
  affiliate: affiliateApi,
}
