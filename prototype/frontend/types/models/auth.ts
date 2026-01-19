/**
 * Auth Domain Models
 * 인증 관련 도메인 모델 타입 정의
 */

/**
 * 토큰 쌍
 */
export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

/**
 * 로그인 인증 정보
 */
export interface LoginCredentials {
  user_id: string
  password: string
}

/**
 * 회원가입 데이터
 */
export interface SignupData {
  user_id: string
  email: string
  password: string
  phone: string
  name: string
  gender?: 'M' | 'F'
  agree_terms: boolean
  agree_privacy: boolean
  agree_marketing: boolean
}

/**
 * 소셜 회원가입 데이터
 */
export interface SocialSignupData {
  provider: 'kakao' | 'naver'
  social_id: string
  email?: string
  name: string
  nickname?: string
  phone?: string
  gender?: 'M' | 'F'
  agree_terms: boolean
  agree_privacy: boolean
  agree_marketing: boolean
}

/**
 * 인증된 사용자 정보
 */
export interface AuthenticatedUser {
  user_id: string
  email: string
  name: string
  is_active: boolean
  is_verified: boolean
  roles: string[]
  permissions: string[]
}