/**
 * API Request Types
 * API 요청 타입 정의
 */

/**
 * 로그인 요청
 */
export interface LoginRequest {
  user_id: string
  password: string
}

/**
 * 회원가입 요청
 */
export interface SignupRequest {
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
 * 소셜 회원가입 요청
 */
export interface SocialSignupRequest {
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
 * 상담사 로그인 요청
 */
export interface CounselorLoginRequest {
  email: string
  password: string
}

/**
 * 프로필 업데이트 요청
 */
export interface UpdateProfileRequest {
  nickname?: string
  phone?: string
  gender?: 'M' | 'F'
  birth_date?: string
  profile_image_url?: string
}

/**
 * 포인트 사용 요청
 */
export interface UsePointsRequest {
  amount: number
  description: string
}

/**
 * 설정 업데이트 요청
 */
export interface UpdateSettingsRequest {
  notification_enabled?: boolean
  marketing_enabled?: boolean
  theme?: 'light' | 'dark' | 'system'
  language?: 'ko' | 'en'
}

/**
 * 상담사 상태 업데이트 요청
 */
export interface UpdateCounselorStatusRequest {
  counselor_status: number
}