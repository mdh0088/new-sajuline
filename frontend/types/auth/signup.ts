/**
 * 회원가입 폼 타입 정의
 * - 회원가입 단계별 폼 데이터 타입
 * - 각 컴포넌트에서 공통으로 사용
 */
import type { Gender, JoinType } from '~/types/user/models'

/**
 * 전체 회원가입 폼 데이터
 */
export interface SignupFormData {
  user_id: string
  email: string
  password: string
  confirmPassword: string
  name: string
  nickname: string
  phone: string
  phone_chk: boolean  // 휴대폰 인증 완료 여부 (true: 인증 완료, false: 미인증)
  verified_phone?: string  // KCP에서 실제 인증한 번호 (디버깅용)
  gender: Gender
  birth_date: string  // YYYY-MM-DD HH:MM 형식 (예: "1993-06-19 14:30")
  join_type: JoinType
  is_marketing_agreed: boolean
  // 약관 동의 (필수 약관은 프론트엔드에서만 검증)
  agreeService: boolean
  agreePrivacy: boolean
}

/**
 * 각 단계별 컴포넌트 Props 인터페이스
 */
export interface SignupStepProps {
  form: SignupFormData
  validator?: any
}

/**
 * 단계별 emit 이벤트 (각 컴포넌트별로 필요한 것만 사용)
 */
export interface SignupStep1Emits {
  'update:form': [form: SignupFormData]
}

export interface SignupStep2Emits {
  'update:form': [form: SignupFormData]
  'send-verification': []
}

export interface SignupStep3Emits {
  'update:form': [form: SignupFormData]
}

export interface SignupStep4Emits {
  'update:form': [form: SignupFormData]
  'open-terms': [type: string]
}