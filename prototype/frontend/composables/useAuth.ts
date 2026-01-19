/**
 * Auth Composable
 * 인증 관련 로직을 추상화한 컴포저블
 */

import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { authAPI } from '~/api/services/auth'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '~/utils/auth-token'

// 타입 정의
export interface User {
  user_id: string
  email: string
  name: string
  nickname?: string
  phone?: string
  is_active: boolean
  is_premium?: boolean
  created_at: string
}

export interface LoginCredentials {
  user_id: string
  password: string
}

export interface SignupData {
  user_id: string
  email: string
  password: string
  phone: string
  name: string
  gender?: string
  agree_terms: boolean
  agree_privacy: boolean
  agree_marketing: boolean
}

// 전역 상태
const currentUser: Ref<User | null> = ref(null)
const isAuthenticated = computed(() => !!currentUser.value)
const isLoading = ref(false)
const error: Ref<string | null> = ref(null)

export const useAuth = () => {
  /**
   * 로그인
   */
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.login(credentials.user_id, credentials.password)
      
      // 토큰 저장
      if (response.access_token && response.refresh_token) {
        setTokens(response.access_token, response.refresh_token)
      }
      
      // 사용자 정보 설정
      if (response.user) {
        currentUser.value = response.user
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '로그인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 회원가입
   */
  const signup = async (data: SignupData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.signup(data)
      return response
    } catch (err: any) {
      error.value = err.message || '회원가입에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 로그아웃
   */
  const logout = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const accessToken = getAccessToken()
      if (accessToken) {
        await authAPI.logout(accessToken)
      }
    } catch (err: any) {
      // 로그아웃 API 실패해도 로컬 토큰은 삭제
      console.error('Logout API error:', err)
    } finally {
      // 토큰 및 사용자 정보 초기화
      clearTokens()
      currentUser.value = null
      isLoading.value = false
    }
  }
  
  /**
   * 현재 사용자 정보 가져오기
   */
  const fetchCurrentUser = async () => {
    const accessToken = getAccessToken()
    if (!accessToken) {
      currentUser.value = null
      return null
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.getCurrentUser(accessToken)
      currentUser.value = response.user || response
      return currentUser.value
    } catch (err: any) {
      error.value = err.message || '사용자 정보를 가져올 수 없습니다.'
      
      // 401 에러인 경우 토큰 리프레시 시도
      if (err.status_code === 401) {
        const refreshSuccess = await refreshAccessToken()
        if (refreshSuccess) {
          // 리프레시 성공 시 재시도
          return fetchCurrentUser()
        }
      }
      
      currentUser.value = null
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 액세스 토큰 리프레시
   */
  const refreshAccessToken = async (): Promise<boolean> => {
    const refreshToken = getRefreshToken()
    if (!refreshToken) {
      return false
    }
    
    try {
      const response = await authAPI.refreshToken(refreshToken)
      
      if (response.access_token) {
        // 새 액세스 토큰만 업데이트 (리프레시 토큰은 유지)
        const currentRefreshToken = getRefreshToken()
        setTokens(response.access_token, currentRefreshToken || '')
        return true
      }
      
      return false
    } catch (err) {
      console.error('Token refresh failed:', err)
      // 리프레시 실패 시 로그아웃 처리
      await logout()
      return false
    }
  }
  
  /**
   * 인증 상태 초기화 (앱 시작 시 호출)
   */
  const initAuth = async () => {
    const accessToken = getAccessToken()
    if (accessToken) {
      await fetchCurrentUser()
    }
  }
  
  return {
    // 상태
    currentUser: readonly(currentUser),
    isAuthenticated: readonly(isAuthenticated),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // 메서드
    login,
    signup,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
    initAuth
  }
}

// 전역 인스턴스 (옵션)
export const globalAuth = useAuth()