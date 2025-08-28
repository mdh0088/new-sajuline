/**
 * API Client Base
 * HTTP 통신을 위한 기본 클라이언트
 */

import type { $Fetch } from 'nitropack'

// API 에러 타입
export interface ApiError {
  message: string
  status_code: number
  error_code: string
  details?: any
}

// API 클라이언트 옵션
export interface ApiClientOptions {
  baseUrl?: string
  fetch?: $Fetch
  defaultHeaders?: Record<string, string>
}

// API 기본 설정은 생성자에서 처리

/**
 * HTTP 클라이언트 클래스
 * Nuxt의 $fetch를 래핑하여 일관된 API 호출 제공
 */
export class ApiClient {
  private baseUrl: string
  private fetch: $Fetch
  private defaultHeaders: Record<string, string>

  constructor(options: ApiClientOptions = {}) {
    // 환경 변수에서 baseUrl 가져오기, 옵션으로 오버라이드 가능
    if (options.baseUrl) {
      this.baseUrl = options.baseUrl
    } else {
      // 안전한 기본값 사용 (composable 의존성 제거)
      this.baseUrl = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
    console.log('[ApiClient] baseUrl:', this.baseUrl)
    console.log('[ApiClient] using custom fetch:', !!options.fetch)
    this.fetch = options.fetch || $fetch.create({
      baseURL: this.baseUrl,
      credentials: 'include' // HttpOnly 쿠키 포함
    })
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.defaultHeaders
    }
  }

  /**
   * 인증 토큰 설정
   */
  setAuthToken(token: string | null) {
    if (token) {
      this.defaultHeaders['Authorization'] = `Bearer ${token}`
    } else {
      delete this.defaultHeaders['Authorization']
    }
  }

  /**
   * 기본 요청 처리
   */
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await this.fetch<any>(endpoint, {
        ...options,
        headers: {
          ...this.defaultHeaders,
          ...options.headers
        }
      })

      // 공통 래퍼 자동 해제
      if (response && typeof response === 'object' && 'success' in response && ('data' in response || 'error' in response)) {
        if (response.success) {
          return response.data as T
        }
        const err = response.error || { code: 'UNKNOWN_ERROR', message: '요청에 실패했습니다.' }
        throw {
          message: err.message || '요청에 실패했습니다.',
          status_code: (response.error && response.error.status_code) || 400,
          error_code: err.code || 'UNKNOWN_ERROR',
          details: err.details
        } as ApiError
      }

      return response as T
    } catch (error: any) {
      // Nuxt $fetch는 자체적으로 에러를 throw하므로 이를 ApiError로 변환
      if (error.data) {
        throw {
          message: error.data?.error?.message || error.data.detail || error.data.message || '서버 오류가 발생했습니다.',
          status_code: error.statusCode || 500,
          error_code: error.data?.error?.code || error.data.error_code || 'UNKNOWN_ERROR',
          details: error.data?.error?.details || error.data
        } as ApiError
      }
      
      // 네트워크 오류
      if (error.message?.includes('fetch') || error.message?.includes('network')) {
        throw {
          message: '네트워크 연결을 확인해주세요',
          status_code: 0,
          error_code: 'NETWORK_ERROR'
        } as ApiError
      }
      
      // 기타 오류
      throw {
        message: error.message || '알 수 없는 오류가 발생했습니다.',
        status_code: error.statusCode || 500,
        error_code: 'UNKNOWN_ERROR'
      } as ApiError
    }
  }

  // HTTP 메서드들
  async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { 
      ...options, 
      method: 'GET' 
    })
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data
    })
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data
    })
  }

  async patch<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data
    })
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'DELETE'
    })
  }
}