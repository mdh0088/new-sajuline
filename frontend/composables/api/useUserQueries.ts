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
import type { 
  UserCreateRequest, 
  UserUpdateRequest,
  UserResponse,
  UserListData,
  LoginRequest,
  LoginData,
  RefreshTokenRequest,
  TokenResponse,
  UserCreateResponse,
  UserDetailResponse,
  UserUpdateResponse,
  UserListResponse,
  LoginResponse,
  LogoutResponse,
  RefreshTokenResponse,
  AuthenticateResponse,
  AvailabilityCheckResponse
} from '~/types/user/models'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 사용자 API 호출 함수들 (Vue Query에서 사용)
 */
const userApi = {
  // 사용자 조회 (ID)
  async getUserById(userId: string): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserDetailResponse>(`/users/${userId}`)
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 정보를 찾을 수 없습니다.')
    }
    
    return response.data
  },

  // 사용자 조회 (이메일)
  async getUserByEmail(email: string): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserDetailResponse>(`/users/email/${email}`)
    
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
    
    const url = queryParams.toString() ? `/users?${queryParams}` : '/users'
    const response = await $api<UserListResponse>(url)
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 목록 조회에 실패했습니다.')
    }
    
    return response.data
  },

  // 사용자 생성
  async createUser(userData: UserCreateRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserCreateResponse>('/users', {
      method: 'POST',
      body: userData
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '사용자 생성에 실패했습니다.')
    }
    
    return response.data
  },

  // 사용자 정보 수정
  async updateUser(userId: string, userData: UserUpdateRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<UserUpdateResponse>(`/users/${userId}`, {
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
    const response = await $api<APIResponse<null>>(`/users/${userId}`, {
      method: 'DELETE'
    })
    
    if (!response.success) {
      throw new Error(response.error?.message || '사용자 삭제에 실패했습니다.')
    }
  },

  // 로그인
  async login(credentials: LoginRequest): Promise<LoginData> {
    const { $api } = useNuxtApp()
    const response = await $api<LoginResponse>('/users/login', {
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
    const response = await $api<LogoutResponse>('/users/logout', {
      method: 'POST'
    })
    
    if (!response.success) {
      throw new Error(response.error?.message || '로그아웃에 실패했습니다.')
    }
  },

  // 토큰 갱신
  async refreshToken(refreshTokenData?: RefreshTokenRequest): Promise<TokenResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<RefreshTokenResponse>('/users/refresh', {
      method: 'POST',
      body: refreshTokenData || {}
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '토큰 갱신에 실패했습니다.')
    }
    
    return response.data
  },

  // 사용자 인증
  async authenticateUser(credentials: LoginRequest): Promise<UserResponse> {
    const { $api } = useNuxtApp()
    const response = await $api<AuthenticateResponse>('/users/authenticate', {
      method: 'POST',
      body: credentials
    })
    
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '인증에 실패했습니다.')
    }
    
    return response.data
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

  // 사용자 생성 뮤테이션
  const useCreateUser = (
    options?: UseMutationOptions<UserResponse, APIError, UserCreateRequest>
  ) => {
    return useMutation({
      mutationFn: userApi.createUser,
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

  // 토큰 갱신 뮤테이션
  const useRefreshToken = (
    options?: UseMutationOptions<TokenResponse, APIError, RefreshTokenRequest | undefined>
  ) => {
    return useMutation({
      mutationFn: userApi.refreshToken,
      onSuccess: (data) => {
        // 토큰 갱신 성공 시 사용자 관련 쿼리들 무효화 (최신 정보 로드)
        queryClient.invalidateQueries({ queryKey: ['user'] })
      },
      ...options
    })
  }

  return {
    // Queries
    useUserById,
    useUserByEmail, 
    useUserList,

    // Availability Checks (실시간 검증용)
    useEmailAvailability,
    useUserIdAvailability,
    usePhoneAvailability,
    useNicknameAvailability,

    // Mutations
    useCreateUser,
    useUpdateUser,
    useDeleteUser,
    useLogin,
    useLogout,
    useAuthenticateUser,
    useRefreshToken
  }
}