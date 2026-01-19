/**
 * API Response Types
 * API 응답 타입 정의
 */

import type { User } from '../models/user'
import type { Counselor } from '../models/counselor'
import type { TokenPair } from '../models/auth'

/**
 * 기본 API 응답
 */
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: {
    code: string
    message: string
    details?: any
  }
}

/**
 * 페이지네이션 응답
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Auth 응답 타입들

/**
 * 로그인 응답
 */
export interface LoginResponse {
  tokens: TokenPair
  user: {
    id: string
    email: string
    name: string
    is_active: boolean
    email_verified: boolean
    created_at: string
  }
}

/**
 * 회원가입 응답
 */
export interface SignupResponse {
  user: {
    id: string
    email: string
    name: string
    is_active: boolean
    email_verified: boolean
    created_at: string
  }
  tokens?: TokenPair  // 자동 로그인 시에만 제공
}

/**
 * 소셜 로그인 응답
 */
export interface SocialLoginResponse {
  success: boolean
  is_new_user: boolean
  user?: User
  tokens?: TokenPair
  social_info?: {
    provider: string
    social_id: string
    email?: string
    name?: string
  }
}

/**
 * 토큰 갱신 응답
 */
export interface RefreshTokenResponse {
  access_token: string
  expires_in: number
}

// User 응답 타입들

/**
 * 사용자 프로필 응답
 */
export interface UserProfileResponse {
  user: User
}

/**
 * 포인트 거래 내역 응답
 */
export interface PointTransactionsResponse {
  transactions: Array<{
    transaction_id: string
    amount: number
    type: string
    description: string
    balance_after: number
    created_at: string
  }>
  current_balance: number
}

// Counselor 응답 타입들

/**
 * 상담사 로그인 응답
 */
export interface CounselorLoginResponse {
  tokens: TokenPair
  counselor: Counselor
}

/**
 * 상담사 목록 응답
 */
export interface CounselorListResponse {
  counselors: Counselor[]
  total: number
}

// Check 응답 타입들

/**
 * 중복 확인 응답
 */
export interface AvailabilityCheckResponse {
  available: boolean
  message: string
}