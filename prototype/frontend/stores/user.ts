/**
 * User Store
 * 사용자 상태 관리 (Pinia)
 */

import { defineStore } from 'pinia'
import { useAuthAPI, useUserAPI } from '~/api'
import { useAuthToken } from '~/utils/auth-token'
import type { User } from '~/types/models/user'
import type { LoginRequest, SignupRequest } from '~/types/api/requests'
import type { LoginResponse, SignupResponse } from '~/types/api/responses'

export interface UserState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  getters: {
    getUserInfo: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated,
    getUserPoints: (state) => state.user?.point_balance || 0,
    isPremium: (state) => state.user?.is_premium || false,
    getUserId: (state) => state.user?.user_id || '',
  },

  actions: {
    /**
     * 사용자 로그인
     */
    async login(credentials: LoginRequest): Promise<LoginResponse> {
      this.loading = true
      this.error = null

      try {
        const authAPI = useAuthAPI()
        const response = await authAPI.login(credentials)

        // 토큰을 메모리에 저장
        const { setTokens } = useAuthToken()
        setTokens(response.tokens.access_token, response.tokens.refresh_token)
        
        // 로그인 후 전체 사용자 프로필 가져오기
        await this.fetchUser()
        
        this.isAuthenticated = true
        this.error = null
        
        return response
      } catch (error: any) {
        this.error = error.message || '로그인에 실패했습니다.'
        this.isAuthenticated = false
        this.user = null
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 회원가입
     */
    async signup(data: SignupRequest): Promise<SignupResponse> {
      this.loading = true
      this.error = null

      try {
        const authAPI = useAuthAPI()
        const response = await authAPI.signup(data)
        
        // 자동 로그인이 포함된 경우
        if (response.tokens) {
          const { setTokens } = useAuthToken()
          setTokens(response.tokens.access_token, response.tokens.refresh_token)
          await this.fetchUser()
          this.isAuthenticated = true
        }
        
        return response
      } catch (error: any) {
        this.error = error.message || '회원가입에 실패했습니다.'
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
        const authAPI = useAuthAPI()
        await authAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // 로컬 상태 초기화
        this.user = null
        this.isAuthenticated = false
        
        // 토큰 제거
        const { clearTokens } = useAuthToken()
        clearTokens()
        
        this.loading = false
        
        // 로그인 페이지로 리다이렉트
        await navigateTo('/login')
      }
    },

    /**
     * 사용자 프로필 조회
     */
    async fetchUser() {
      if (!this.isAuthenticated && !useAuthToken().getAccessToken()) {
        return
      }

      this.loading = true
      this.error = null

      try {
        const authAPI = useAuthAPI()
        const userAPI = useUserAPI()
        
        // 먼저 인증된 사용자 정보 조회
        const authUser = await authAPI.getCurrentUser()
        
        // 상세 프로필 조회
        const profileResponse = await userAPI.getProfile(authUser.user_id)
        
        this.user = profileResponse.user
        this.isAuthenticated = true
      } catch (error: any) {
        this.error = error.message || '사용자 정보 조회에 실패했습니다.'
        
        // 인증 오류인 경우 로그아웃 처리
        if (error.status_code === 401) {
          await this.logout()
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * 프로필 업데이트
     */
    async updateProfile(updates: Partial<User>) {
      if (!this.user) return

      this.loading = true
      this.error = null

      try {
        const userAPI = useUserAPI()
        const updatedUser = await userAPI.updateProfile(this.user.user_id, updates)
        
        this.user = updatedUser
        return updatedUser
      } catch (error: any) {
        this.error = error.message || '프로필 업데이트에 실패했습니다.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 포인트 사용
     */
    async usePoints(amount: number, description: string) {
      if (!this.user) return

      this.loading = true
      this.error = null

      try {
        const userAPI = useUserAPI()
        const result = await userAPI.usePoints(this.user.user_id, { amount, description })
        
        // 로컬 상태 업데이트
        if (this.user) {
          this.user.point_balance = result.new_balance
        }
        
        return result
      } catch (error: any) {
        this.error = error.message || '포인트 사용에 실패했습니다.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 포인트 추가
     */
    async addPoints(amount: number, description: string) {
      if (!this.user) return

      this.loading = true
      this.error = null

      try {
        const userAPI = useUserAPI()
        const result = await userAPI.addPoints(this.user.user_id, amount, description)
        
        // 로컬 상태 업데이트
        if (this.user) {
          this.user.point_balance = result.new_balance
        }
        
        return result
      } catch (error: any) {
        this.error = error.message || '포인트 추가에 실패했습니다.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 사용자 정보 직접 설정 (소셜 로그인용)
     */
    setUser(userData: any) {
      // 기존 User 타입에 맞게 변환
      this.user = {
        user_id: userData.id || userData.user_id,
        email: userData.email,
        name: userData.name,
        nickname: userData.nickname || userData.name,
        phone: userData.phone || userData.phone_number,
        gender: userData.gender,
        birth_date: userData.birth_date,
        profile_image_url: userData.profile_image_url,
        point_balance: userData.point_balance || 0,
        is_active: userData.is_active ?? true,
        is_premium: userData.is_premium ?? false,
        join_type: userData.join_type || 'COMMON',
        created_at: userData.created_at || new Date().toISOString(),
        updated_at: userData.updated_at
      }
      this.isAuthenticated = true
      this.error = null
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
      this.user = null
      this.isAuthenticated = false
      this.loading = false
      this.error = null
    }
  }
})