/**
 * Counselor Domain Models
 * 상담사 관련 도메인 모델 타입 정의
 */

/**
 * 상담사 정보
 */
export interface Counselor {
  counselor_id: string
  email: string
  name: string
  counselor_code: string
  phone?: string
  profile_image_url?: string
  introduction?: string
  specialties: string[]
  counselor_status: number  // 0: 오프라인, 1: 온라인, 2: 상담중, 3: 휴식
  is_online: boolean
  is_authorized: boolean
  rating: number
  total_consultations: number
  created_at: string
  updated_at?: string
}

/**
 * 상담사 로그인 인증 정보
 */
export interface CounselorLoginCredentials {
  email: string
  password: string
}

/**
 * 상담사 상태
 */
export enum CounselorStatus {
  OFFLINE = 0,
  ONLINE = 1,
  IN_CONSULTATION = 2,
  BREAK = 3
}

/**
 * 상담사 전문 분야
 */
export interface CounselorSpecialty {
  specialty_id: string
  name: string
  category: string
  description?: string
}