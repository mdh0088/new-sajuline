/**
 * Counselor Auth Composable
 * 상담사 인증 관련 로직을 추상화한 컴포저블
 */

import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { counselorAPI } from '~/api/services/counselor'

// 타입 정의
export interface Counselor {
  counselor_id: string
  name: string
  email: string
  phone?: string
  profile_image_url?: string
  introduction?: string
  counselor_status: number
  is_authorized: boolean
  created_at: string
  specialties?: string[]
}

export interface CounselorLoginCredentials {
  email: string
  password: string
}

// 전역 상태
const currentCounselor: Ref<Counselor | null> = ref(null)
const isAuthenticated = computed(() => !!currentCounselor.value)
const isLoading = ref(false)
const error: Ref<string | null> = ref(null)
const accessToken: Ref<string | null> = ref(null)

export const useCounselorAuth = () => {
  /**
   * 상담사 로그인
   */
  const login = async (credentials: CounselorLoginCredentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await counselorAPI.login(credentials.email, credentials.password)
      
      // 토큰 저장
      if (response.access_token) {
        accessToken.value = response.access_token
        
        // 로컬 스토리지에도 저장 (선택사항)
        if (typeof window !== 'undefined') {
          localStorage.setItem('counselor_access_token', response.access_token)
        }
      }
      
      // 상담사 정보 설정
      if (response.counselor) {
        currentCounselor.value = response.counselor
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '상담사 로그인에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 상담사 로그아웃
   */
  const logout = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      if (accessToken.value) {
        await counselorAPI.logout(accessToken.value)
      }
    } catch (err: any) {
      // 로그아웃 API 실패해도 로컬 토큰은 삭제
      console.error('Counselor logout API error:', err)
    } finally {
      // 토큰 및 상담사 정보 초기화
      accessToken.value = null
      currentCounselor.value = null
      
      // 로컬 스토리지에서도 제거
      if (typeof window !== 'undefined') {
        localStorage.removeItem('counselor_access_token')
      }
      
      isLoading.value = false
    }
  }
  
  /**
   * 현재 상담사 정보 가져오기
   */
  const fetchCurrentCounselor = async () => {
    if (!accessToken.value) {
      // 로컬 스토리지에서 토큰 복구 시도
      if (typeof window !== 'undefined') {
        const storedToken = localStorage.getItem('counselor_access_token')
        if (storedToken) {
          accessToken.value = storedToken
        } else {
          currentCounselor.value = null
          return null
        }
      } else {
        currentCounselor.value = null
        return null
      }
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await counselorAPI.getProfile(accessToken.value!)
      currentCounselor.value = response.counselor || response
      return currentCounselor.value
    } catch (err: any) {
      error.value = err.message || '상담사 정보를 가져올 수 없습니다.'
      
      // 401 에러인 경우 로그아웃 처리
      if (err.status_code === 401) {
        await logout()
      }
      
      currentCounselor.value = null
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 상담사 상태 업데이트
   */
  const updateStatus = async (status: number) => {
    if (!accessToken.value) {
      throw new Error('인증이 필요합니다.')
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await counselorAPI.updateStatus(accessToken.value, status)
      
      // 상태 업데이트 성공 시 로컬 상태도 업데이트
      if (currentCounselor.value) {
        currentCounselor.value.counselor_status = status
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '상담사 상태 업데이트에 실패했습니다.'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 인증 상태 초기화 (앱 시작 시 호출)
   */
  const initAuth = async () => {
    // 로컬 스토리지에서 토큰 복구
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('counselor_access_token')
      if (storedToken) {
        accessToken.value = storedToken
        await fetchCurrentCounselor()
      }
    }
  }
  
  return {
    // 상태
    currentCounselor: readonly(currentCounselor),
    isAuthenticated: readonly(isAuthenticated),
    isLoading: readonly(isLoading),
    error: readonly(error),
    accessToken: readonly(accessToken),
    
    // 메서드
    login,
    logout,
    fetchCurrentCounselor,
    updateStatus,
    initAuth
  }
}

// 전역 인스턴스 (옵션)
export const globalCounselorAuth = useCounselorAuth()