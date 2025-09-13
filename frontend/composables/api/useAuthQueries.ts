/**
 * 인증 API 컴포저블 (Vue Query)
 * - 인증/권한 관련 호출 전용
 */
import { useQuery, useMutation, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import { useRequestHeaders } from 'nuxt/app'
import type { APIResponse, APIError } from '~/types/common/api'
import type { RefreshTokenRequest, TokenResponse, RefreshTokenResponse } from '~/types/user/models'

export interface AuthMePayload {
  sub: string
  email: string
  role: 'user' | 'counselor'
  exp: number
  iat: number
  jti: string
}

const authApi = {
  async whoAmI(): Promise<AuthMePayload> {
    const init: any = { credentials: 'include' }
    if (process.server) {
      const headers = useRequestHeaders(['cookie'])
      init.headers = { cookie: headers.cookie || '' }
    }
    const response = await $fetch<APIResponse<AuthMePayload>>('/api/v1/auth/me', init)
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '권한 정보를 가져오지 못했습니다.')
    }
    return response.data
  },
  async refreshToken(refreshTokenData?: RefreshTokenRequest): Promise<TokenResponse> {
    const init: any = { method: 'POST', credentials: 'include', body: refreshTokenData || {} }
    if (process.server) {
      const headers = useRequestHeaders(['cookie'])
      init.headers = { cookie: headers.cookie || '' }
    }
    const response = await $fetch<RefreshTokenResponse>('/api/v1/auth/refresh', init)
    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '토큰 갱신에 실패했습니다.')
    }
    return response.data
  }
}

export const useAuthQueries = () => {
  const useWhoAmI = (
    options?: Partial<UseQueryOptions<AuthMePayload, APIError>>
  ) => {
    return useQuery({
      queryKey: ['auth', 'me'],
      queryFn: authApi.whoAmI,
      enabled: false,
      retry: 0,
      staleTime: 0,
      ...options
    })
  }

  const useRefreshToken = (
    options?: UseMutationOptions<TokenResponse, APIError, RefreshTokenRequest | undefined>
  ) => {
    return useMutation({
      mutationFn: authApi.refreshToken,
      ...options
    })
  }

  return {
    useWhoAmI,
    useRefreshToken
  }
}


