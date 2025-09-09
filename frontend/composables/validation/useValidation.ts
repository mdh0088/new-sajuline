/**
 * 실시간 유효성 검증 컴포저블
 * - 사주라인 프로젝트 특화 검증 로직
 * - Backend API 실시간 중복 검사 연동
 * - Vue Query 기반 캐싱으로 성능 최적화
 */
import { ref, computed, watch } from 'vue'
import { debounce } from 'lodash-es'
import type { JoinType } from '~/types/user/models'
import type { UseQueryReturnType } from '@tanstack/vue-query'

/**
 * 비밀번호 강도 측정
 */
interface PasswordStrength {
  score: number // 0-4 점수
  feedback: string[]
  warning?: string
  crack_times_display: {
    offline_slow_hashing_1e4_per_second?: string
    offline_fast_hashing_1e10_per_second?: string
  }
}

/**
 * 검증 결과 인터페이스
 */
interface ValidationResult {
  isValid: boolean
  message: string
  isChecking?: boolean
}

/**
 * 실시간 유효성 검증 훅
 */
export const useValidation = () => {

  /**
   * 이메일 검증 (Vue Query 결과를 외부에서 받아옴)
   */
  const validateEmail = (email: string, availabilityQuery?: any) => {
    const emailRef = ref(email)
    
    // 기본 이메일 형식 검증
    const basicValidation = computed((): ValidationResult => {
      if (!emailRef.value) {
        return { isValid: false, message: '이메일을 입력해주세요.' }
      }
      
      const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      if (!emailPattern.test(emailRef.value)) {
        return { isValid: false, message: '올바른 이메일 형식을 입력해주세요.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    // 최종 검증 결과 (외부 Vue Query 결과 활용)
    const result = computed((): ValidationResult => {
      if (!basicValidation.value.isValid) {
        return basicValidation.value
      }
      
      if (availabilityQuery?.isLoading?.value) {
        return { isValid: true, message: '', isChecking: true }
      }
      
      if (availabilityQuery?.error?.value) {
        return { isValid: false, message: '이메일 중복 검사 중 오류가 발생했습니다.' }
      }
      
      if (availabilityQuery?.data?.value === false) {
        return { isValid: false, message: '이미 사용 중인 이메일입니다.' }
      }
      
      if (availabilityQuery?.data?.value === true) {
        return { isValid: true, message: '사용 가능한 이메일입니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    return {
      update: (value: string) => { emailRef.value = value },
      result
    }
  }

  /**
   * 사용자 ID 검증 (Vue Query 결과를 외부에서 받아옴)
   */
  const validateUserId = (userId: string, availabilityQuery?: any) => {
    const userIdRef = ref(userId)
    
    // 기본 형식 검증
    const basicValidation = computed((): ValidationResult => {
      if (!userIdRef.value) {
        return { isValid: false, message: '사용자 ID를 입력해주세요.' }
      }
      
      if (userIdRef.value.length < 4 || userIdRef.value.length > 20) {
        return { isValid: false, message: '사용자 ID는 4-20자 사이로 입력해주세요.' }
      }
      
      // 이메일 형식 금지 검사
      const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      if (emailPattern.test(userIdRef.value)) {
        return { isValid: false, message: '사용자 ID에는 이메일 형식을 사용할 수 없습니다.' }
      }
      
      const userIdPattern = /^[a-zA-Z0-9_]+$/
      if (!userIdPattern.test(userIdRef.value)) {
        return { isValid: false, message: '영문, 숫자, 밑줄(_)만 사용 가능합니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    // 최종 검증 결과
    const result = computed((): ValidationResult => {
      if (!basicValidation.value.isValid) {
        return basicValidation.value
      }
      
      if (availabilityQuery?.isLoading?.value) {
        return { isValid: true, message: '', isChecking: true }
      }
      
      if (availabilityQuery?.error?.value) {
        return { isValid: false, message: '사용자 ID 중복 검사 중 오류가 발생했습니다.' }
      }
      
      if (availabilityQuery?.data?.value === false) {
        return { isValid: false, message: '이미 사용 중인 사용자 ID입니다.' }
      }
      
      if (availabilityQuery?.data?.value === true) {
        return { isValid: true, message: '사용 가능한 사용자 ID입니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    return {
      update: (value: string) => { userIdRef.value = value },
      result
    }
  }

  /**
   * 전화번호 검증 (01012345678 형식)
   */
  const validatePhone = (phone: string, availabilityQuery?: any) => {
    const phoneRef = ref(phone)
    
    // 기본 형식 검증
    const basicValidation = computed((): ValidationResult => {
      if (!phoneRef.value) {
        return { isValid: false, message: '전화번호를 입력해주세요.' }
      }
      
      const phonePattern = /^010\d{8}$/
      if (!phonePattern.test(phoneRef.value)) {
        return { isValid: false, message: '올바른 전화번호 형식을 입력해주세요. (01012345678)' }
      }
      
      return { isValid: true, message: '' }
    })
    
    // 최종 검증 결과
    const result = computed((): ValidationResult => {
      if (!basicValidation.value.isValid) {
        return basicValidation.value
      }
      
      if (availabilityQuery?.isLoading?.value) {
        return { isValid: true, message: '', isChecking: true }
      }
      
      if (availabilityQuery?.error?.value) {
        return { isValid: false, message: '전화번호 중복 검사 중 오류가 발생했습니다.' }
      }
      
      if (availabilityQuery?.data?.value === false) {
        return { isValid: false, message: '이미 사용 중인 전화번호입니다.' }
      }
      
      if (availabilityQuery?.data?.value === true) {
        return { isValid: true, message: '사용 가능한 전화번호입니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    return {
      update: (value: string) => { phoneRef.value = value },
      result
    }
  }

  /**
   * 닉네임 검증
   */
  const validateNickname = (nickname: string, availabilityQuery?: any) => {
    const nicknameRef = ref(nickname)
    
    // 기본 형식 검증
    const basicValidation = computed((): ValidationResult => {
      if (!nicknameRef.value) {
        return { isValid: false, message: '닉네임을 입력해주세요.' }
      }
      
      if (nicknameRef.value.length < 2 || nicknameRef.value.length > 10) {
        return { isValid: false, message: '닉네임은 2-10자 사이로 입력해주세요.' }
      }
      
      const nicknamePattern = /^[a-zA-Z0-9가-힣_]+$/
      if (!nicknamePattern.test(nicknameRef.value)) {
        return { isValid: false, message: '한글, 영문, 숫자, 밑줄(_)만 사용 가능합니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    // 최종 검증 결과
    const result = computed((): ValidationResult => {
      if (!basicValidation.value.isValid) {
        return basicValidation.value
      }
      
      if (availabilityQuery?.isLoading?.value) {
        return { isValid: true, message: '', isChecking: true }
      }
      
      if (availabilityQuery?.error?.value) {
        return { isValid: false, message: '닉네임 중복 검사 중 오류가 발생했습니다.' }
      }
      
      if (availabilityQuery?.data?.value === false) {
        return { isValid: false, message: '이미 사용 중인 닉네임입니다.' }
      }
      
      if (availabilityQuery?.data?.value === true) {
        return { isValid: true, message: '사용 가능한 닉네임입니다.' }
      }
      
      return { isValid: true, message: '' }
    })
    
    return {
      update: (value: string) => { nicknameRef.value = value },
      result
    }
  }

  /**
   * 비밀번호 강도 측정 (zxcvbn 스타일)
   */
  const calculatePasswordStrength = (password: string): PasswordStrength => {
    if (!password) {
      return {
        score: 0,
        feedback: ['비밀번호를 입력해주세요.'],
        crack_times_display: {}
      }
    }

    let score = 0
    const feedback: string[] = []

    // 길이 검사
    if (password.length >= 8) score++
    else feedback.push('최소 8자 이상 입력해주세요.')

    // 대소문자 포함
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
    else feedback.push('대문자와 소문자를 포함해주세요.')

    // 숫자 포함
    if (/\d/.test(password)) score++
    else feedback.push('숫자를 포함해주세요.')

    // 특수문자 포함
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++
    else feedback.push('특수문자를 포함해주세요.')

    // 연속된 문자나 반복 패턴 체크
    if (!/(.)\1{2,}/.test(password) && !/123|abc|qwe/i.test(password)) {
      score = Math.min(score + 1, 4)
    } else {
      feedback.push('연속된 문자나 반복 패턴을 피해주세요.')
    }

    return {
      score: Math.max(0, Math.min(score, 4)),
      feedback: feedback.length > 0 ? feedback : ['강력한 비밀번호입니다.'],
      crack_times_display: {
        offline_slow_hashing_1e4_per_second: score >= 3 ? '수세기' : '몇 시간',
        offline_fast_hashing_1e10_per_second: score >= 3 ? '수년' : '몇 분'
      }
    }
  }

  /**
   * 비밀번호 검증
   */
  const validatePassword = (password: string, confirmPassword?: string) => {
    const passwordRef = ref(password)
    const confirmPasswordRef = ref(confirmPassword || '')
    
    // 비밀번호 강도 측정
    const passwordStrength = computed(() => calculatePasswordStrength(passwordRef.value))
    
    // 기본 검증
    const basicValidation = computed((): ValidationResult => {
      if (!passwordRef.value) {
        return { isValid: false, message: '비밀번호를 입력해주세요.' }
      }
      
      if (passwordStrength.value.score < 3) {
        return { 
          isValid: false, 
          message: passwordStrength.value.feedback[0] || '더 강력한 비밀번호를 사용해주세요.' 
        }
      }
      
      return { isValid: true, message: '사용 가능한 비밀번호입니다.' }
    })
    
    // 비밀번호 확인 검증
    const confirmValidation = computed((): ValidationResult => {
      if (!confirmPasswordRef.value) {
        return { isValid: false, message: '비밀번호 확인을 입력해주세요.' }
      }
      
      if (passwordRef.value !== confirmPasswordRef.value) {
        return { isValid: false, message: '비밀번호가 일치하지 않습니다.' }
      }
      
      return { isValid: true, message: '비밀번호가 일치합니다.' }
    })
    
    return {
      updatePassword: (value: string) => { passwordRef.value = value },
      updateConfirmPassword: (value: string) => { confirmPasswordRef.value = value },
      passwordResult: basicValidation,
      confirmResult: confirmValidation,
      passwordStrength
    }
  }

  /**
   * 생년월일 검증 (YYYY-MM-DD)
   */
  const validateBirthDate = (birthDate: string): ValidationResult => {
    if (!birthDate) {
      return { isValid: false, message: '생년월일을 입력해주세요.' }
    }
    
    const datePattern = /^\d{4}-\d{2}-\d{2}$/
    if (!datePattern.test(birthDate)) {
      return { isValid: false, message: '올바른 날짜 형식을 입력해주세요. (YYYY-MM-DD)' }
    }
    
    const date = new Date(birthDate)
    const today = new Date()
    
    // 유효한 날짜인지 확인
    if (isNaN(date.getTime())) {
      return { isValid: false, message: '존재하지 않는 날짜입니다.' }
    }
    
    // 미래 날짜 확인
    if (date > today) {
      return { isValid: false, message: '미래 날짜는 입력할 수 없습니다.' }
    }
    
    // 너무 과거 날짜 확인 (100년 전)
    const hundredYearsAgo = new Date()
    hundredYearsAgo.setFullYear(today.getFullYear() - 100)
    if (date < hundredYearsAgo) {
      return { isValid: false, message: '올바른 생년월일을 입력해주세요.' }
    }
    
    return { isValid: true, message: '올바른 생년월일입니다.' }
  }

  /**
   * 전체 회원가입 폼 검증
   */
  const validateSignupForm = (formData: {
    user_id: string
    email: string
    password: string
    confirmPassword: string
    nickname: string
    phone: string
    birth_date?: string
    join_type: JoinType
    is_marketing_agreed: boolean
  }, availabilityQueries?: {
    email?: any
    userId?: any
    phone?: any
    nickname?: any
  }) => {
    const emailValidator = validateEmail(formData.email, availabilityQueries?.email)
    const userIdValidator = validateUserId(formData.user_id, availabilityQueries?.userId)
    const phoneValidator = validatePhone(formData.phone, availabilityQueries?.phone)
    const nicknameValidator = validateNickname(formData.nickname, availabilityQueries?.nickname)
    const passwordValidator = validatePassword(formData.password, formData.confirmPassword)
    
    const birthDateValidation = computed(() => 
      formData.birth_date ? validateBirthDate(formData.birth_date) : { isValid: true, message: '' }
    )
    
    // 전체 폼 유효성
    const isFormValid = computed(() => {
      return emailValidator.result.value.isValid &&
             userIdValidator.result.value.isValid &&
             phoneValidator.result.value.isValid &&
             nicknameValidator.result.value.isValid &&
             passwordValidator.passwordResult.value.isValid &&
             passwordValidator.confirmResult.value.isValid &&
             birthDateValidation.value.isValid &&
             formData.is_marketing_agreed
    })
    
    // 폼 검사 중 여부
    const isChecking = computed(() => {
      return emailValidator.result.value.isChecking ||
             userIdValidator.result.value.isChecking ||
             phoneValidator.result.value.isChecking ||
             nicknameValidator.result.value.isChecking
    })
    
    return {
      emailValidator,
      userIdValidator,
      phoneValidator,
      nicknameValidator,
      passwordValidator,
      birthDateValidation,
      isFormValid,
      isChecking
    }
  }

  /**
   * 간단한 필수 값 검증
   */
  const validateRequired = (value: string): boolean => {
    return !!(value && value.trim())
  }

  /**
   * 최소 길이 검증
   */
  const validateMinLength = (value: string, minLength: number): boolean => {
    return !!(value && value.length >= minLength)
  }

  /**
   * 이메일 형식 검증 (간단한 버전)
   */
  const validateEmailFormat = (email: string): boolean => {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return emailPattern.test(email)
  }

  return {
    // 개별 검증 함수들
    validateEmail,
    validateUserId,
    validatePhone,
    validateNickname,
    validatePassword,
    validateBirthDate,
    
    // 통합 검증
    validateSignupForm,
    
    // 유틸리티
    calculatePasswordStrength,
    
    // 간단한 헬퍼 함수들 (로그인 폼 등에서 사용)
    validateRequired,
    validateMinLength,
    validateEmailFormat
  }
}