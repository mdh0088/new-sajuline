/**
 * Auth API Service
 * 인증 관련 API 서비스
 */

import { ApiClient } from '../client'
import { useAuthToken } from '~/utils/auth-token'
import type { 
  LoginRequest, 
  SignupRequest, 
  SocialSignupRequest 
} from '~/types/api/requests'
import type { 
  LoginResponse, 
  SignupResponse, 
  SocialLoginResponse,
  RefreshTokenResponse,
  AvailabilityCheckResponse 
} from '~/types/api/responses'
import type { AuthenticatedUser } from '~/types/models/auth'

export class AuthAPI {
  constructor(private client: ApiClient) {}

  /**
   * 사용자 로그인
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    return this.client.post('/api/v1/auth/login', request)
  }

  /**
   * 회원가입
   */
  async signup(request: SignupRequest): Promise<SignupResponse> {
    return this.client.post('/api/v1/auth/signup', request)
  }

  /**
   * 로그아웃
   */
  async logout(): Promise<void> {
    const token = useAuthToken().getAccessToken()
    if (!token) return
    
    return this.client.post('/api/v1/auth/logout', null, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 토큰 갱신
   */
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    return this.client.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken
    })
  }

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser(): Promise<AuthenticatedUser> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      throw new Error('No access token available')
    }
    
    return this.client.get('/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }

  /**
   * 소셜 로그인 OAuth URL 생성
   */
  async getSocialLoginUrl(provider: 'kakao' | 'naver'): Promise<{ auth_url: string; provider: string; state?: string }> {
    return this.client.get(`/api/v1/auth/social/${provider}/url`)
  }

  /**
   * 소셜 로그인 콜백 처리
   */
  async processSocialCallback(provider: 'kakao' | 'naver', code: string, state?: string): Promise<SocialLoginResponse> {
    const params = new URLSearchParams({ code })
    if (state) params.append('state', state)

    return this.client.get(`/api/v1/auth/social/${provider}/callback?${params}`)
  }

  /**
   * 소셜 회원가입
   */
  async socialSignup(request: SocialSignupRequest): Promise<SignupResponse> {
    return this.client.post('/api/v1/auth/social/signup', request)
  }

  /**
   * 이메일 중복 확인
   */
  async checkEmail(email: string): Promise<AvailabilityCheckResponse> {
    return this.client.post('/api/v1/auth/check-email', { email })
  }

  /**
   * 전화번호 중복 확인
   */
  async checkPhone(phone: string): Promise<AvailabilityCheckResponse> {
    return this.client.post('/api/v1/auth/check-phone', { phone })
  }

  /**
   * 닉네임 중복 확인
   */
  async checkNickname(nickname: string): Promise<AvailabilityCheckResponse> {
    return this.client.post('/api/v1/auth/check-nickname', { nickname })
  }

  /**
   * 토큰 유효성 검증
   */
  async validateToken(): Promise<{ valid: boolean; user_id: string }> {
    const token = useAuthToken().getAccessToken()
    if (!token) {
      return { valid: false, user_id: '' }
    }
    
    return this.client.get('/api/v1/auth/validate', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }
}

// Lazy singleton pattern for safer initialization
let _authAPI: AuthAPI | null = null

export function getAuthAPI(): AuthAPI {
  if (!_authAPI) {
    _authAPI = new AuthAPI(new ApiClient())
  }
  return _authAPI
}

// Default export with getter for backward compatibility
export const authAPI = new Proxy({} as AuthAPI, {
  get(target, prop) {
    return getAuthAPI()[prop as keyof AuthAPI]
  }
})