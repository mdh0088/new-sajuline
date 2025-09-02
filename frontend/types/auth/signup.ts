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
  gender: Gender
  birth_date: string
  join_type: JoinType
  is_marketing_agreed: boolean
  // 단계별 데이터
  birthYear: number | null
  birthMonth: number | null
  birthDay: number | null
  birthHour: number | null
  birthMinute: number | null
  // 약관 동의
  agreeService: boolean
  agreePrivacy: boolean
  agreeMarketing: boolean
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