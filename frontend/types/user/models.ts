/**
 * 사용자 도메인 타입 정의
 * - 사용자 관련 API 전용 타입
 * - Backend User 스키마 기반
 */
import type { APIResponse } from '../common/api'

// =============================================================================
// 사용자 열거형 타입 (Backend enum과 동일)
// =============================================================================

/**
 * 사용자 상태 열거형
 * Backend: UserStatus enum
 */
export enum UserStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE', 
  SUSPENDED = 'SUSPENDED',
  DELETED = 'DELETED'
}

/**
 * 가입 유형 열거형
 * Backend: JoinType enum
 */
export enum JoinType {
  COMMON = 'COMMON',
  KAKAO = 'KAKAO',
  NAVER = 'NAVER'
}

/**
 * 성별 열거형
 * Backend: Gender enum
 */
export enum Gender {
  MALE = 'MALE',
  FEMALE = 'FEMALE',
  OTHER = 'OTHER'
}

// =============================================================================
// 사용자 모델 타입 (Backend 스키마 기반)
// =============================================================================

/**
 * 사용자 기본 정보
 * Backend: UserBase 스키마
 */
export interface UserBase {
  email: string
  nickname: string
  phone: string
  join_type: JoinType
  profile_image_url?: string
  birth_date?: string              // YYYY-MM-DD 형식
  gender?: Gender
  is_marketing_agreed: boolean
}

/**
 * 사용자 생성 요청
 * Backend: UserCreate 스키마
 */
export interface UserCreateRequest extends UserBase {
  user_id: string
  password?: string               // 소셜로그인 시 불필요
  social_provider?: string
  social_id?: string
}

/**
 * 사용자 정보 수정 요청
 * Backend: UserUpdate 스키마
 */
export interface UserUpdateRequest {
  nickname?: string
  phone?: string
  profile_image_url?: string
  birth_date?: string
  gender?: Gender
  is_marketing_agreed?: boolean
}

/**
 * 사용자 정보 응답
 * Backend: UserResponse 스키마
 */
export interface UserResponse extends UserBase {
  user_id: string
  user_status: UserStatus
  grade_code: string
  social_provider?: string
  failed_login_count: number
  locked_until?: string            // ISO datetime string
  created_at: string               // ISO datetime string
  updated_at?: string              // ISO datetime string  
  last_login_at?: string           // ISO datetime string
}

/**
 * 사용자 목록 응답 데이터 (페이지네이션)
 * Backend: UserListResponse 스키마
 */
export interface UserListData {
  users: UserResponse[]
  total: number
  page: number
  size: number
}

/**
 * 비밀번호 변경 요청
 * Backend: PasswordChange 스키마
 */
export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

// =============================================================================
// 인증 관련 타입 (auth 도메인 포함)
// =============================================================================

/**
 * 로그인 요청
 * Backend: LoginRequest 스키마 (auth_schema.py)
 */
export interface LoginRequest {
  user_id: string                  // 사용자 ID 또는 이메일
  password: string
}

/**
 * 로그인 응답 데이터 (HttpOnly 쿠키 환경)
 * Backend: LoginData 스키마 (auth_schema.py)
 */
export interface LoginData {
  user_id: string
  email: string
  nickname: string
  // 주의: access_token은 HttpOnly 쿠키로 전송되어 여기에 포함되지 않음
}

/**
 * 사용자 세션 정보 (클라이언트 상태 관리용)
 */
export interface UserSession {
  user_id: string
  email: string
  nickname: string
  isAuthenticated: boolean
  loginAt: string                  // 로그인 시간
}

// =============================================================================
// API 응답 타입 (실제 엔드포인트별)
// =============================================================================

export type UserCreateResponse = APIResponse<UserResponse>
export type UserDetailResponse = APIResponse<UserResponse>  
export type UserUpdateResponse = APIResponse<UserResponse>
export type UserListResponse = APIResponse<UserListData>
export type AuthenticateResponse = APIResponse<UserResponse>
export type LoginResponse = APIResponse<LoginData>
export type LogoutResponse = APIResponse<null>