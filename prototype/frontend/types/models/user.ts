/**
 * User Domain Models
 * 사용자 관련 도메인 모델 타입 정의
 */

/**
 * 사용자 기본 정보
 */
export interface User {
  user_id: string
  email: string
  name: string
  nickname: string
  phone?: string
  gender?: 'M' | 'F'
  birth_date?: string
  profile_image_url?: string
  point_balance: number
  is_active: boolean
  is_premium: boolean
  join_type: 'COMMON' | 'KAKAO' | 'NAVER'
  created_at: string
  updated_at?: string
}

/**
 * 사용자 프로필 업데이트 데이터
 */
export interface UserProfileUpdate {
  nickname?: string
  phone?: string
  gender?: 'M' | 'F'
  birth_date?: string
  profile_image_url?: string
}

/**
 * 사용자 설정
 */
export interface UserSettings {
  user_id: string
  notification_enabled: boolean
  marketing_enabled: boolean
  theme: 'light' | 'dark' | 'system'
  language: 'ko' | 'en'
}

/**
 * 포인트 거래
 */
export interface PointTransaction {
  transaction_id: string
  user_id: string
  amount: number
  type: 'ADD' | 'USE' | 'REFUND' | 'EXPIRE'
  description: string
  balance_after: number
  created_at: string
}

/**
 * 사용자 통계
 */
export interface UserStats {
  total_consultations: number
  total_points_used: number
  total_points_purchased: number
  member_since_days: number
  favorite_counselors: number
}