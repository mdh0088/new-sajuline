/**
 * 소셜 로그인 API 컴포저블 (Vue Query)
 * - Kakao, Naver OAuth 2.0 인증
 */
import { useQuery, useMutation, type UseQueryOptions, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 소셜 로그인 URL 응답
 */
export interface SocialAuthURLResponse {
  authorization_url: string
  state: string
}

/**
 * 소셜 회원가입 필요 응답
 */
export interface SocialSignupRequired {
  requires_signup: true
  provider: 'kakao' | 'naver'
  social_id: string
  email?: string
  name?: string
  profile_image?: string
}

/**
 * 소셜 로그인 성공 응답 (기존 LoginResponse)
 */
export interface SocialLoginSuccess {
  user_id: string
  email: string
  nickname: string
  access_token_expires_in: number
  refresh_token_expires_in: number
}

/**
 * 소셜 로그인 콜백 응답 (Union 타입)
 */
export type SocialLoginCallbackResponse = SocialLoginSuccess | SocialSignupRequired

/**
 * 소셜 회원가입 요청
 */
export interface SocialSignupRequest {
  user_id: string // Kakao: kko{social_id}, Naver: email
  social_provider: 'kakao' | 'naver'
  social_id: string
  email?: string
  nickname: string
  phone: string
  phone_chk: boolean // 휴대폰 인증 완료 여부 (필수)
  gender?: 'MALE' | 'FEMALE' // 백엔드 Gender enum
  birth_date?: string
  is_marketing_agreed?: boolean
}

const socialAuthApi = {
  /**
   * OAuth 인증 URL 생성
   */
  async getSocialAuthURL(provider: 'kakao' | 'naver'): Promise<SocialAuthURLResponse> {
    const response = await $fetch<APIResponse<SocialAuthURLResponse>>(
      `/api/v1/auth/social/${provider}/url`,
      {
        method: 'GET',
        credentials: 'include'
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '소셜 로그인 URL 생성 실패')
    }

    return response.data
  },

  /**
   * OAuth 콜백 처리 (쿼리 파라미터로 code, state 전달)
   *
   * @returns SocialLoginSuccess (기존 사용자) 또는 SocialSignupRequired (신규 사용자)
   */
  async handleSocialCallback(
    provider: 'kakao' | 'naver',
    code: string,
    state?: string
  ): Promise<SocialLoginCallbackResponse> {
    const params = new URLSearchParams({ code })
    if (state) {
      params.append('state', state)
    }

    const response = await $fetch<APIResponse<SocialLoginCallbackResponse>>(
      `/api/v1/auth/social/${provider}/callback?${params.toString()}`,
      {
        method: 'GET',
        credentials: 'include'
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '소셜 로그인 처리 실패')
    }

    return response.data
  },

  /**
   * 소셜 회원가입 (기존 /users/social/signup 엔드포인트 사용)
   */
  async socialSignup(signupData: SocialSignupRequest): Promise<SocialLoginSuccess> {
    const response = await $fetch<APIResponse<SocialLoginSuccess>>(
      '/api/v1/users/social/signup',
      {
        method: 'POST',
        credentials: 'include',
        body: signupData
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '소셜 회원가입 실패')
    }

    return response.data
  }
}

export const useSocialAuthQueries = () => {
  /**
   * 소셜 로그인 URL 생성 쿼리
   */
  const useGetSocialAuthURL = (
    provider: ComputedRef<'kakao' | 'naver'> | Ref<'kakao' | 'naver'>,
    options?: Partial<UseQueryOptions<SocialAuthURLResponse, APIError>>
  ) => {
    return useQuery({
      queryKey: ['social-auth', 'url', provider],
      queryFn: () => socialAuthApi.getSocialAuthURL(unref(provider)),
      enabled: false, // 수동 호출
      staleTime: 0, // 항상 최신 state 생성
      ...options
    })
  }

  /**
   * 소셜 로그인 콜백 처리 뮤테이션
   */
  const useHandleSocialCallback = (
    options?: UseMutationOptions<
      SocialLoginCallbackResponse,
      APIError,
      { provider: 'kakao' | 'naver'; code: string; state?: string }
    >
  ) => {
    return useMutation({
      mutationFn: ({ provider, code, state }) =>
        socialAuthApi.handleSocialCallback(provider, code, state),
      ...options
    })
  }

  /**
   * 소셜 회원가입 뮤테이션
   */
  const useSocialSignup = (
    options?: UseMutationOptions<SocialLoginSuccess, APIError, SocialSignupRequest>
  ) => {
    return useMutation({
      mutationFn: socialAuthApi.socialSignup,
      ...options
    })
  }

  return {
    useGetSocialAuthURL,
    useHandleSocialCallback,
    useSocialSignup
  }
}
