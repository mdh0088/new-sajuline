/**
 * API Services Index
 * 모든 API 서비스 인스턴스를 생성하고 export
 */

import { ApiClient } from './client'
import { AuthAPI } from './services/auth'
import { UserAPI } from './services/user'
import { CounselorAPI } from './services/counselor'

// API 클라이언트 인스턴스 생성 (Nuxt 플러그인에서 설정될 예정)
let apiClient: ApiClient | null = null
let authAPI: AuthAPI | null = null
let userAPI: UserAPI | null = null
let counselorAPI: CounselorAPI | null = null

/**
 * API 서비스 초기화
 * Nuxt 플러그인에서 호출됨
 */
export function initializeApi(options?: { fetch?: any }) {
  console.log('[initializeApi] called with options:', options)
  apiClient = new ApiClient({
    fetch: options?.fetch
  })
  
  authAPI = new AuthAPI(apiClient)
  userAPI = new UserAPI(apiClient)
  counselorAPI = new CounselorAPI(apiClient)
}

/**
 * API 서비스 getter
 */
export function useApi() {
  if (!apiClient) {
    // 클라이언트 사이드에서 자동 초기화 (fetch 옵션을 전달하지 않음)
    if (process.client) {
      initializeApi()
    } else {
      throw new Error('API not initialized. Call initializeApi() first.')
    }
  }
  
  return {
    client: apiClient!,
    auth: authAPI!,
    user: userAPI!,
    counselor: counselorAPI!
  }
}

// 개별 API 서비스 접근을 위한 컴포저블
export const useAuthAPI = () => useApi().auth
export const useUserAPI = () => useApi().user
export const useCounselorAPI = () => useApi().counselor

// 타입 export
export type { ApiClient } from './client'
export type { AuthAPI } from './services/auth'
export type { UserAPI } from './services/user'
export type { CounselorAPI } from './services/counselor'