/**
 * SaveVia API Service
 * 所有前端请求统一通过 Gateway 访问后端服务
 */

import type {
  ApiResponse,
  CreditCard,
  OptimizationRequest,
  OptimizationResult,
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
      responseData = await response.json()
    } catch {
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
}

export default {
  auth: authApi,
  card: cardApi,
  optimizer: optimizerApi,
  user: userApi,
}
