/**
 * Vue Query 기반 상담사 API 컴포저블
 * - TanStack Query의 강력한 캐싱과 상태 관리 활용
 * - 상담사 도메인 특화 API 호출
 */
import { 
  useMutation, 
  useQueryClient,
  type UseMutationOptions
} from '@tanstack/vue-query'
import type { 
  LoginRequest,
  LoginData,
  LoginResponse,
  LogoutResponse
} from '~/types/user/models'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 상담사 API 호출 함수들 (Vue Query에서 사용)
 */
const counselorApi = {
  // 상담사 로그인
  async login(credentials: LoginRequest): Promise<LoginData> {
    const { $api } = useNuxtApp()
    const response = await $api<LoginResponse>('/api/v1/counselors/login', {
      method: 'POST',
      body: credentials
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '상담사 로그인에 실패했습니다.')
    }
    
    return response.data
  },

  // 상담사 로그아웃
  async logout(): Promise<void> {
    const { $api } = useNuxtApp()
    const response = await $api<LogoutResponse>('/api/v1/counselors/logout', {
      method: 'POST'
    })
    
    if (!response.success) {
      throw new Error(response.error?.message || '상담사 로그아웃에 실패했습니다.')
    }
  }
}

/**
 * Vue Query 기반 상담사 API 훅들
 */
export const useCounselorQueries = () => {
  const queryClient = useQueryClient()

  // 상담사 로그인 뮤테이션
  const useLogin = (
    options?: UseMutationOptions<LoginData, APIError, LoginRequest>
  ) => {
    return useMutation({
      mutationFn: counselorApi.login,
      onSuccess: (data) => {
        // 로그인 성공 시 상담사 관련 쿼리들 무효화 (최신 정보 로드)
        queryClient.invalidateQueries({ queryKey: ['counselor'] })
      },
      ...options
    })
  }

  // 상담사 로그아웃 뮤테이션  
  const useLogout = (
    options?: UseMutationOptions<void, APIError, void>
  ) => {
    return useMutation({
      mutationFn: counselorApi.logout,
      onSuccess: () => {
        // 로그아웃 시 모든 상담사 관련 캐시 클리어
        queryClient.removeQueries({ queryKey: ['counselor'] })
      },
      ...options
    })
  }

  return {
    // Mutations
    useLogin,
    useLogout
  }
}