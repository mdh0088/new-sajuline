/**
 * Vue Query 기반 사용자 API 컴포저블
 * - TanStack Query의 강력한 캐싱과 상태 관리 활용
 * - 사주라인 프로젝트 특화 최적화
 */
import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions
} from '@tanstack/vue-query'
import { computed, unref, type ComputedRef, type Ref } from 'vue'
import { useNuxtApp } from 'nuxt/app'
import type { 
  UserCreateRequest, 
  UserUpdateRequest,
  UserResponse,
  UserListData,
  LoginRequest,
  LoginData,
  UserCreateResponse,
  UserDetailResponse,
  UserUpdateResponse,
  UserListResponse,
  LoginResponse,
  LogoutResponse,
  AuthenticateResponse,
  AvailabilityCheckResponse,
  UserMypageData,
  UserMypageResponse
} from '~/types/user/models'
import type { UserPointHistoryData, UserPointHistoryResponse, PointSearchType, PointOrderType } from '~/types/user/models'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 사용자 API 호출 함수들 (Vue Query에서 사용)
 */
const userApi = {
  // 사용자 조회 (ID)
  async getUserById(userId: string): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserDetailResponse>(`/api/v1/users/${userId}`)
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 정보를 찾을 수 없습니다.')
    }
    
    return response.data
  },

  // 사용자 조회 (이메일)
  async getUserByEmail(email: string): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserDetailResponse>(`/api/v1/users/email/${email}`)
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 정보를 찾을 수 없습니다.')
    }
    
    return response.data
  },

  // 사용자 목록 조회
  async getUserList(params: {
    page?: number
    size?: number  
    user_status?: string
  } = {}): Promise<UserListData> {
    const { $api } = useNuxtApp()
    const queryParams = new URLSearchParams()
    
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.size) queryParams.append('size', params.size.toString())
    if (params.user_status) queryParams.append('user_status', params.user_status)
    
    const url = queryParams.toString() ? `/api/v1/users?${queryParams}` : '/api/v1/users'
    const response = await $api<UserListResponse>(url)
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 목록 조회에 실패했습니다.')
    }
    
    return response.data
  },

  // 회원가입
  async signupUser(userData: UserCreateRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserCreateResponse>('/api/v1/users/signup', {
      method: 'POST',
      body: userData
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '회원가입에 실패했습니다.')
    }
    
    return response.data
  },

  // 로그인
  async login(credentials: LoginRequest): Promise<LoginData> {
    const { $api } = useNuxtApp()
    const response = await $api<LoginResponse>('/api/v1/users/login', {
      method: 'POST',
      body: credentials
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '로그인에 실패했습니다.')
    }
    
    return response.data
  },

  // 로그아웃
  async logout(): Promise<void> {
    const { $api } = useNuxtApp()
    const response = await $api<LogoutResponse>('/api/v1/users/logout', {
      method: 'POST'
    })
    
    if (!response.success) {
      throw new Error(response.error?.message || '로그아웃에 실패했습니다.')
    }
  },

  // 사용자 인증
  async authenticateUser(credentials: LoginRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<AuthenticateResponse>('/api/v1/users/authenticate', {
      method: 'POST',
      body: credentials
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '인증에 실패했습니다.')
    }
    
    return response.data
  },

  // 마이페이지 조회
  async getUserMypage(): Promise<UserMypageData> {
    const { $api } = useNuxtApp()
    const response = await $api<UserMypageResponse>('/api/v1/users/mypage')

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '마이페이지 정보를 불러오지 못했습니다.')
    }

    return response.data
  },

  // 포인트 내역 조회
  async getUserPointHistory(params: { start_dt: string; end_dt: string; search_type: PointSearchType; order_type?: PointOrderType }): Promise<UserPointHistoryData> {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('start_dt', params.start_dt)
    query.set('end_dt', params.end_dt)
    query.set('search_type', params.search_type)
    if (params.order_type) query.set('order_type', params.order_type)

    const response = await $api<UserPointHistoryResponse>(`/api/v1/users/points/history?${query.toString()}`)
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '포인트 내역 조회에 실패했습니다.')
    }
    return response.data
  },

  // 사용자 후기 요약 조회
  async getUserReviewSummary() {
    const { $api } = useNuxtApp()
    const response = await $api<import('~/types/user/models').UserReviewSummaryResponse>('/api/v1/users/reviews/summary')
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '후기 요약 조회에 실패했습니다.')
    }
    return response.data
  },

  // 사용자 후기 목록 조회 (작성/대기)
  async getUserReviews(params: { searchtype: 'my_reviews' | 'pending_reviews'; page?: number; limit?: number }) {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    query.set('searchtype', params.searchtype)
    if (params.page) query.set('page', String(params.page))
    if (params.limit) query.set('limit', String(params.limit))
    const response = await $api<APIResponse<any[]>>(`/api/v1/users/reviews?${query.toString()}`)
    if (!response.success) {
      throw new Error(response.error?.message || '후기 목록 조회에 실패했습니다.')
    }
    // APIResponseBuilder.paginated 사용 → data는 배열
    return response
  },

  // 전체 공개 후기 조회 (인증 불필요)
  async getAllPublicReviews(params: { page?: number; limit?: number }) {
    const { $api } = useNuxtApp()
    const query = new URLSearchParams()
    if (params.page) query.set('page', String(params.page))
    if (params.limit) query.set('limit', String(params.limit))
    const response = await $api<APIResponse<any[]>>(`/api/v1/users/public/reviews?${query.toString()}`)
    if (!response.success) {
      throw new Error(response.error?.message || '전체 후기 조회에 실패했습니다.')
    }
    return response
  },

  // 사용자 후기 생성
  async createUserReview(body: { session_id: number; rating: number; content?: string; review_tags?: string[] }) {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<import('~/types/user/models').UserReviewItemData>>('/api/v1/users/reviews', {
      method: 'POST',
      body
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '후기 작성에 실패했습니다.')
    }
    return response.data
  },

  // 사용자 후기 수정 (세션 기준)
  async updateUserReview(body: { session_id: number; rating?: number; content?: string; review_tags?: string[] }) {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<import('~/types/user/models').UserReviewItemData>>('/api/v1/users/reviews', {
      method: 'PUT',
      body
    })
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '후기 수정에 실패했습니다.')
    }
    return response.data
  },

  // 사용자 후기 삭제
  async deleteUserReview(reviewId: number) {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<boolean>>(`/api/v1/users/reviews/${reviewId}`, {
      method: 'DELETE'
    })
    if (!response.success) {
      throw new Error(response.error?.message || '후기 삭제에 실패했습니다.')
    }
    return response.data ?? false
  },

  // 중복 검사 API들
  async checkEmailAvailability(email: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const response = await $api<AvailabilityCheckResponse>(`/api/v1/users/check-availability/email?value=${encodeURIComponent(email)}`)
    
    if (!response.success) {
      throw new Error(response.error?.message || '이메일 중복 검사에 실패했습니다.')
    }
    
    return response.data ?? false
  },

  async checkUserIdAvailability(userId: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const response = await $api<AvailabilityCheckResponse>(`/api/v1/users/check-availability/user-id?value=${encodeURIComponent(userId)}`)
    
    if (!response.success) {
      throw new Error(response.error?.message || '사용자 ID 중복 검사에 실패했습니다.')
    }
    
    return response.data ?? false
  },

  async checkPhoneAvailability(phone: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const response = await $api<AvailabilityCheckResponse>(`/api/v1/users/check-availability/phone?value=${encodeURIComponent(phone)}`)
    
    if (!response.success) {
      throw new Error(response.error?.message || '전화번호 중복 검사에 실패했습니다.')
    }
    
    return response.data ?? false
  },

  async checkNicknameAvailability(nickname: string): Promise<boolean> {
    const { $api } = useNuxtApp()
    const response = await $api<AvailabilityCheckResponse>(`/api/v1/users/check-availability/nickname?value=${encodeURIComponent(nickname)}`)

    if (!response.success) {
      throw new Error(response.error?.message || '닉네임 중복 검사에 실패했습니다.')
    }

    return response.data ?? false
  },

  // 사용자 ID 찾기 (휴대폰 본인인증)
  async findUserId(phone: string): Promise<{ user_id: string; created_at: string }> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{ user_id: string; created_at: string }>>('/api/v1/users/find-id', {
      method: 'POST',
      body: { phone }
    })

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'ID 찾기에 실패했습니다.')
    }

    return response.data
  },

  // 비밀번호 찾기 (임시 비밀번호 발급)
  async findPassword(params: { user_id: string; phone: string }): Promise<{ user_id: string; email: string; message: string }> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{ user_id: string; email: string; message: string }>>('/api/v1/users/find-password', {
      method: 'POST',
      body: params
    })

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '비밀번호 찾기에 실패했습니다.')
    }

    return response.data
  },

  // 사용자 정보 수정
  async updateUser(userId: string, userData: UserUpdateRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserUpdateResponse>(`/api/v1/users/${userId}`, {
      method: 'PUT',
      body: userData
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 정보 수정에 실패했습니다.')
    }
    
    return response.data
  },

  // 사용자 삭제
  async deleteUser(userId: string): Promise<void> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<null>>(`/api/v1/users/${userId}`, {
      method: 'DELETE'
    })

    if (!response.success) {
      throw new Error(response.error?.message || '사용자 삭제에 실패했습니다.')
    }
  },

  // 비밀번호 변경
  async changePassword(params: { current_password: string; new_password: string }): Promise<{
    user_id: string
    password_changed_at: string
    message: string
  }> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{
      user_id: string
      password_changed_at: string
      message: string
    }>>('/api/v1/users/password', {
      method: 'PUT',
      body: params
    })

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '비밀번호 변경에 실패했습니다.')
    }

    return response.data
  },

  // 회원 탈퇴
  async withdrawUser(params: { password?: string; reason?: string }): Promise<{
    out_idx: number
    user_id: string | null
    withdrawal_id: string | null
    nickname: string | null
    phone: string | null
    email: string | null
    reason: string | null
    created_at: string
  }> {
    const { $api } = useNuxtApp()
    const response = await $api<APIResponse<{
      out_idx: number
      user_id: string | null
      withdrawal_id: string | null
      nickname: string | null
      phone: string | null
      email: string | null
      reason: string | null
      created_at: string
    }>>('/api/v1/users/withdraw', {
      method: 'POST',
      body: {
        password: params.password || null,
        reason: params.reason || null
      }
    })

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '회원 탈퇴에 실패했습니다.')
    }

    return response.data
  }
}

/**
 * Vue Query 기반 사용자 API 훅들
 */
export const useUserQueries = () => {
  const queryClient = useQueryClient()

  // 사용자 조회 (ID) 쿼리
  const useUserById = (
    userId: string, 
    options?: Partial<UseQueryOptions<UserResponse, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', userId],
      queryFn: () => userApi.getUserById(userId),
      enabled: !!userId,
      staleTime: 10 * 60 * 1000, // 10분 - 사용자 정보는 자주 변하지 않음
      ...options
    })
  }

  // 사용자 조회 (이메일) 쿼리  
  const useUserByEmail = (
    email: string,
    options?: Partial<UseQueryOptions<UserResponse, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', 'email', email],
      queryFn: () => userApi.getUserByEmail(email),
      enabled: !!email,
      staleTime: 10 * 60 * 1000,
      ...options
    })
  }

  // 사용자 목록 쿼리
  const useUserList = (
    params: { page?: number; size?: number; user_status?: string } = {},
    options?: Partial<UseQueryOptions<UserListData, APIError>>
  ) => {
    return useQuery({
      queryKey: ['users', 'list', params],
      queryFn: () => userApi.getUserList(params),
      staleTime: 2 * 60 * 1000, // 2분 - 목록은 비교적 자주 업데이트
      ...options
    })
  }

  // 마이페이지 쿼리
  const useUserMypage = (
    options?: Partial<UseQueryOptions<UserMypageData, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', 'mypage'],
      queryFn: () => userApi.getUserMypage(),
      staleTime: 60 * 1000, // 1분
      ...options
    })
  }

  // 사용자 후기 요약 쿼리
  const useUserReviewSummary = (
    options?: Partial<UseQueryOptions<import('~/types/user/models').UserReviewSummaryData, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', 'reviews', 'summary'],
      queryFn: () => userApi.getUserReviewSummary(),
      staleTime: 30 * 1000,
      ...options
    })
  }

  // 사용자 후기 목록 쿼리 (작성/대기)
  const useUserReviews = (
    params: { searchtype: 'my_reviews' | 'pending_reviews'; page?: number; limit?: number },
    options?: Partial<UseQueryOptions<APIResponse<any[]>, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', 'reviews', params],
      queryFn: () => userApi.getUserReviews(params),
      staleTime: 30 * 1000,
      ...options
    })
  }

  // 후기 생성 뮤테이션
  const useCreateUserReview = (
    options?: UseMutationOptions<import('~/types/user/models').UserReviewItemData, APIError, { session_id: number; rating: number; content?: string; review_tags?: string[] }>
  ) => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: userApi.createUserReview,
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: ['user', 'reviews'] })
        qc.invalidateQueries({ queryKey: ['user', 'reviews', 'summary'] })
      },
      ...options
    })
  }

  // 후기 수정 뮤테이션
  const useUpdateUserReview = (
    options?: UseMutationOptions<import('~/types/user/models').UserReviewItemData, APIError, { session_id: number; rating?: number; content?: string; review_tags?: string[] }>
  ) => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: userApi.updateUserReview,
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: ['user', 'reviews'] })
        qc.invalidateQueries({ queryKey: ['user', 'reviews', 'summary'] })
      },
      ...options
    })
  }

  // 후기 삭제 뮤테이션
  const useDeleteUserReview = (
    options?: UseMutationOptions<boolean, APIError, number>
  ) => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: userApi.deleteUserReview,
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: ['user', 'reviews'] })
        qc.invalidateQueries({ queryKey: ['user', 'reviews', 'summary'] })
      },
      ...options
    })
  }

  // 포인트 내역 쿼리
  const useUserPointHistory = (
    params: { start_dt: string; end_dt: string; search_type: PointSearchType; order_type?: PointOrderType } | ComputedRef<{ start_dt: string; end_dt: string; search_type: PointSearchType; order_type?: PointOrderType }> | Ref<{ start_dt: string; end_dt: string; search_type: PointSearchType; order_type?: PointOrderType }>,
    options?: Partial<UseQueryOptions<UserPointHistoryData, APIError>>
  ) => {
    return useQuery({
      queryKey: ['user', 'point-history', unref(params)],
      queryFn: () => userApi.getUserPointHistory(unref(params) as any),
      enabled: computed(() => {
        const p = unref(params) as any
        return Boolean(p?.start_dt && p?.end_dt && p?.search_type)
      }),
      staleTime: 60 * 1000,
      ...options
    })
  }

  // 중복 검사 쿼리들 (실시간 검증용)
  const useEmailAvailability = (
    email: ComputedRef<string> | Ref<string> | string,
    options?: Partial<UseQueryOptions<boolean, APIError>>
  ) => {
    return useQuery({
      queryKey: ['availability', 'email', email],
      queryFn: () => {
        const emailValue = unref(email)
        return userApi.checkEmailAvailability(emailValue)
      },
      enabled: computed(() => {
        const emailValue = unref(email)
        return !!emailValue && typeof emailValue === 'string' && emailValue.includes('@')
      }),
      staleTime: 30 * 1000, // 30초 - 중복 검사는 짧은 캐시
      retry: 1, // 재시도 최소화 (빠른 피드백)
      ...options
    })
  }

  const useUserIdAvailability = (
    userId: ComputedRef<string> | Ref<string> | string,
    options?: Partial<UseQueryOptions<boolean, APIError>>
  ) => {
    return useQuery({
      queryKey: ['availability', 'user-id', userId],
      queryFn: () => {
        const userIdValue = unref(userId)
        return userApi.checkUserIdAvailability(userIdValue)
      },
      enabled: computed(() => {
        const userIdValue = unref(userId)
        return !!userIdValue && typeof userIdValue === 'string' && userIdValue.length >= 4
      }),
      staleTime: 30 * 1000,
      retry: 1,
      ...options
    })
  }

  const usePhoneAvailability = (
    phone: ComputedRef<string> | Ref<string> | string,
    options?: Partial<UseQueryOptions<boolean, APIError>>
  ) => {
    return useQuery({
      queryKey: ['availability', 'phone', phone],
      queryFn: () => {
        const phoneValue = unref(phone)
        return userApi.checkPhoneAvailability(phoneValue)
      },
      enabled: computed(() => {
        const phoneValue = unref(phone)
        return !!phoneValue && typeof phoneValue === 'string' && /^01[0-9]\d{7,8}$/.test(phoneValue)
      }),
      staleTime: 30 * 1000,
      retry: 1,
      ...options
    })
  }

  const useNicknameAvailability = (
    nickname: ComputedRef<string> | Ref<string> | string,
    options?: Partial<UseQueryOptions<boolean, APIError>>
  ) => {
    return useQuery({
      queryKey: ['availability', 'nickname', nickname],
      queryFn: () => {
        const nicknameValue = unref(nickname)
        return userApi.checkNicknameAvailability(nicknameValue)
      },
      enabled: computed(() => {
        const nicknameValue = unref(nickname)
        return !!nicknameValue && typeof nicknameValue === 'string' && nicknameValue.length >= 2
      }),
      staleTime: 30 * 1000,
      retry: 1,
      ...options
    })
  }

  // 회원가입 뮤테이션
  const useSignupUser = (
    options?: UseMutationOptions<UserResponse, APIError, UserCreateRequest>
  ) => {
    return useMutation({
      mutationFn: userApi.signupUser,
      onSuccess: (data) => {
        // 사용자 목록 쿼리 무효화
        queryClient.invalidateQueries({ queryKey: ['users', 'list'] })
        // 새로운 사용자 데이터 캐시에 추가
        queryClient.setQueryData(['user', data.user_id], data)
      },
      ...options
    })
  }

  // 사용자 정보 수정 뮤테이션
  const useUpdateUser = (
    options?: UseMutationOptions<UserResponse, APIError, { userId: string; userData: UserUpdateRequest }>
  ) => {
    return useMutation({
      mutationFn: ({ userId, userData }) => userApi.updateUser(userId, userData),
      onSuccess: (data, variables) => {
        // 해당 사용자 쿼리들 무효화
        queryClient.invalidateQueries({ queryKey: ['user', variables.userId] })
        // 사용자 목록도 무효화 (변경된 정보 반영)
        queryClient.invalidateQueries({ queryKey: ['users', 'list'] })
        // 업데이트된 데이터로 캐시 업데이트
        queryClient.setQueryData(['user', variables.userId], data)
      },
      ...options
    })
  }

  // 사용자 삭제 뮤테이션
  const useDeleteUser = (
    options?: UseMutationOptions<void, APIError, string>
  ) => {
    return useMutation({
      mutationFn: userApi.deleteUser,
      onSuccess: (_, userId) => {
        // 삭제된 사용자 관련 캐시 모두 제거
        queryClient.removeQueries({ queryKey: ['user', userId] })
        queryClient.removeQueries({ queryKey: ['user', 'email'] })
        // 사용자 목록 무효화
        queryClient.invalidateQueries({ queryKey: ['users', 'list'] })
      },
      ...options
    })
  }

  // 로그인 뮤테이션
  const useLogin = (
    options?: UseMutationOptions<LoginData, APIError, LoginRequest>
  ) => {
    return useMutation({
      mutationFn: userApi.login,
      onSuccess: (data) => {
        // 로그인 성공 시 사용자 관련 쿼리들 무효화 (최신 정보 로드)
        queryClient.invalidateQueries({ queryKey: ['user'] })
      },
      ...options
    })
  }

  // 로그아웃 뮤테이션  
  const useLogout = (
    options?: UseMutationOptions<void, APIError, void>
  ) => {
    return useMutation({
      mutationFn: userApi.logout,
      onSuccess: () => {
        // 로그아웃 시 모든 사용자 관련 캐시 클리어
        queryClient.removeQueries({ queryKey: ['user'] })
        queryClient.removeQueries({ queryKey: ['users'] })
      },
      ...options
    })
  }

  // 사용자 인증 뮤테이션
  const useAuthenticateUser = (
    options?: UseMutationOptions<UserResponse, APIError, LoginRequest>
  ) => {
    return useMutation({
      mutationFn: userApi.authenticateUser,
      ...options
    })
  }

  // 사용자 ID 찾기 뮤테이션 (휴대폰 본인인증)
  const useFindUserId = (
    options?: UseMutationOptions<{ user_id: string; created_at: string }, APIError, string>
  ) => {
    return useMutation({
      mutationFn: userApi.findUserId,
      ...options
    })
  }

  // 비밀번호 찾기 뮤테이션 (임시 비밀번호 발급)
  const useFindPassword = (
    options?: UseMutationOptions<{ user_id: string; email: string; message: string }, APIError, { user_id: string; phone: string }>
  ) => {
    return useMutation({
      mutationFn: userApi.findPassword,
      ...options
    })
  }

  // 비밀번호 변경 뮤테이션
  const useChangePassword = (
    options?: UseMutationOptions<{
      user_id: string
      password_changed_at: string
      message: string
    }, APIError, { current_password: string; new_password: string }>
  ) => {
    return useMutation({
      mutationFn: userApi.changePassword,
      ...options
    })
  }

  // 회원 탈퇴 뮤테이션
  const useWithdrawUser = (
    options?: UseMutationOptions<{
      out_idx: number
      user_id: string | null
      withdrawal_id: string | null
      nickname: string | null
      phone: string | null
      email: string | null
      reason: string | null
      created_at: string
    }, APIError, { password?: string; reason?: string }>
  ) => {
    return useMutation({
      mutationFn: userApi.withdrawUser,
      onSuccess: () => {
        // 탈퇴 성공 시 모든 사용자 관련 캐시 클리어
        queryClient.removeQueries({ queryKey: ['user'] })
        queryClient.removeQueries({ queryKey: ['users'] })
      },
      ...options
    })
  }

  // 토큰 갱신 뮤테이션
  // (이전 위치에서 이동됨) refreshToken은 useAuthQueries로 분리됨

  return {
    // Queries
    useUserById,
    useUserByEmail, 
    useUserList,
    useUserMypage,
    useUserPointHistory,
    useUserReviewSummary,
    useUserReviews,
    // Direct fetch helpers (for imperative flows like infinite scroll)
    fetchUserReviewSummary: userApi.getUserReviewSummary,
    fetchUserReviews: userApi.getUserReviews,
    fetchAllPublicReviews: userApi.getAllPublicReviews,
    // Direct mutation helpers (simple imperative calls)
    createUserReview: userApi.createUserReview,
    updateUserReview: userApi.updateUserReview,
    deleteUserReview: userApi.deleteUserReview,

    // Availability Checks (실시간 검증용)
    useEmailAvailability,
    useUserIdAvailability,
    usePhoneAvailability,
    useNicknameAvailability,

    // Mutations
    useSignupUser,
    useUpdateUser,
    useDeleteUser,
    useLogin,
    useLogout,
    useAuthenticateUser,
    useFindUserId,
    useFindPassword,
    useChangePassword,
    useWithdrawUser,
    useCreateUserReview,
    useUpdateUserReview,
    useDeleteUserReview
  }
}