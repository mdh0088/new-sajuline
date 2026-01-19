/**
 * Counselor Store
 * 상담사 상태 관리 (Pinia)
 */

import { defineStore } from 'pinia'
import { useCounselorAPI } from '~/api'
import { useAuthToken } from '~/utils/auth-token'
import type { Counselor, CounselorStatus } from '~/types/models/counselor'
import type { CounselorLoginRequest } from '~/types/api/requests'
import type { CounselorLoginResponse } from '~/types/api/responses'

export interface CounselorState {
  counselor: Counselor | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

export const useCounselorStore = defineStore('counselor', {
  state: (): CounselorState => ({
    counselor: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  getters: {
    getCounselorInfo: (state) => state.counselor,
    isLoggedIn: (state) => state.isAuthenticated,
    isOnline: (state) => state.counselor?.is_online || false,
    isAuthorized: (state) => state.counselor?.is_authorized || false,
    getCounselorStatus: (state) => state.counselor?.counselor_status || 0,
    getCounselorCode: (state) => state.counselor?.counselor_code || '',
  },

  actions: {
    /**
     * 상담사 로그인
     */
    async login(credentials: CounselorLoginRequest): Promise<CounselorLoginResponse> {
      this.loading = true
      this.error = null

      try {
        const counselorAPI = useCounselorAPI()
        const response = await counselorAPI.login(credentials)

        // 토큰을 메모리에 저장
        const { setTokens } = useAuthToken()
        setTokens(response.tokens.access_token, response.tokens.refresh_token)
        
        // 상담사 정보 설정
        this.counselor = response.counselor
        this.isAuthenticated = true
        this.error = null
        
        return response
      } catch (error: any) {
        this.error = error.message || '로그인에 실패했습니다.'
        this.isAuthenticated = false
        this.counselor = null
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 로그아웃
     */
    async logout() {
      this.loading = true
      this.error = null

      try {
        const counselorAPI = useCounselorAPI()
        await counselorAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // 로컬 상태 초기화
        this.counselor = null
        this.isAuthenticated = false
        
        // 토큰 제거
        const { clearTokens } = useAuthToken()
        clearTokens()
        
        this.loading = false
        
        // 상담사 로그인 페이지로 리다이렉트
        await navigateTo('/counselor/login')
      }
    },

    /**
     * 상담사 프로필 조회
     */
    async fetchCounselor() {
      if (!this.isAuthenticated && !useAuthToken().getAccessToken()) {
        return
      }

      this.loading = true
      this.error = null

      try {
        const counselorAPI = useCounselorAPI()
        const counselor = await counselorAPI.getProfile()
        
        this.counselor = counselor
        this.isAuthenticated = true
      } catch (error: any) {
        this.error = error.message || '상담사 정보 조회에 실패했습니다.'
        
        // 인증 오류인 경우 로그아웃 처리
        if (error.status_code === 401) {
          await this.logout()
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * 상담사 상태 업데이트
     */
    async updateStatus(status: number) {
      if (!this.counselor) return

      this.loading = true
      this.error = null

      try {
        const counselorAPI = useCounselorAPI()
        await counselorAPI.updateStatus(status)
        
        // 로컬 상태 업데이트
        if (this.counselor) {
          this.counselor.counselor_status = status
          this.counselor.is_online = status !== 0 // 0: OFFLINE
        }
        
        return { success: true }
      } catch (error: any) {
        this.error = error.message || '상태 업데이트에 실패했습니다.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 온라인 상태 토글
     */
    async toggleOnlineStatus() {
      if (!this.counselor) return

      const newStatus = this.counselor.is_online ? 0 : 1 // 0: OFFLINE, 1: ONLINE
      return this.updateStatus(newStatus)
    },

    /**
     * 상담 시작
     */
    async startConsultation() {
      return this.updateStatus(2) // 2: IN_CONSULTATION
    },

    /**
     * 상담 종료
     */
    async endConsultation() {
      return this.updateStatus(1) // 1: ONLINE
    },

    /**
     * 휴식 시작
     */
    async startBreak() {
      return this.updateStatus(3) // 3: BREAK
    },

    /**
     * 휴식 종료
     */
    async endBreak() {
      return this.updateStatus(1) // 1: ONLINE
    },

    /**
     * 세션 복원 (쿠키 기반)
     */
    async restoreSession() {
      this.loading = true

      try {
        const counselorAPI = useCounselorAPI()
        const counselor = await counselorAPI.getProfile()
        
        this.counselor = counselor
        this.isAuthenticated = true
        return true
      } catch (error: any) {
        console.error('Session restore error:', error)
        
        // 401 에러가 아닌 경우에만 에러 메시지 설정
        if (error.status_code !== 401) {
          this.error = error.message || '세션 복원에 실패했습니다.'
        }
        
        // 인증 실패 시 로그아웃 처리
        await this.logout()
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * 에러 초기화
     */
    clearError() {
      this.error = null
    },

    /**
     * 상태 초기화
     */
    reset() {
      this.counselor = null
      this.isAuthenticated = false
      this.loading = false
      this.error = null
    }
  }
})