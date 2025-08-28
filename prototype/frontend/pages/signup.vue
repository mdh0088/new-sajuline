<script setup lang="ts">
import KcpDirectAuth from '~/components/KcpDirectAuth.vue'
import { useAuthToken } from '~/utils/auth-token'

// SEO 및 메타 데이터 설정
useHead({
  title: '회원가입 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 회원가입. 이메일과 비밀번호로 간편하게 가입하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
    { property: 'og:title', content: '회원가입 - 사주라인' },
    { property: 'og:description', content: '사주라인 회원가입. 이메일과 비밀번호로 간편하게 가입하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
  ],
})

// 반응형 상태 관리
const formData = reactive({
  user_id: '',
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  phone: '',
  birthDate: '',
  phoneVerified: false,
  phoneVerificationToken: '',
  ci: '',  // KCP CI value
  di: '',  // KCP DI value
  gender: '',
  agreeTerms: false,
  agreePrivacy: false,
  agreeMarketing: false
})

const errors = reactive({
  user_id: '',
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  phone: '',
  birthDate: '',
  gender: '',
  terms: ''
})

const isLoading = ref(false)
const currentStep = ref(1)
const totalSteps = 3

// Phone verification state
const isVerifying = ref(false)
const kcpAuthRef = ref<InstanceType<typeof KcpDirectAuth> | null>(null)

// SNS 로그인 정보 상태 관리
const socialUserInfo = ref<any>(null)
const isSocialSignup = ref(false)
const route = useRoute()

// 토큰 관리 (보안)
const { setAccessToken } = useAuthToken()

// 페이지 로드 시 SNS 로그인 정보 확인
onMounted(async () => {
  // URL 쿼리 파라미터에서 SNS 로그인 여부 확인
  if (route.query.social === 'true') {
    isSocialSignup.value = true
    
    // 세션에서 SNS 사용자 정보 불러오기
    const savedSocialInfo = sessionStorage.getItem('social_user_info')
    const savedMissingFields = sessionStorage.getItem('missing_fields')
    
    if (savedSocialInfo) {
      const parsedSocialInfo = JSON.parse(savedSocialInfo)
      socialUserInfo.value = parsedSocialInfo
      
      // SNS 로그인 정보로 필드 미리 채우기
      if (parsedSocialInfo.email) {
        formData.email = parsedSocialInfo.email
      }
      if (parsedSocialInfo.name || parsedSocialInfo.nickname) {
        formData.name = parsedSocialInfo.name || parsedSocialInfo.nickname
      }
      
      // SNS 로그인일 때는 2단계부터 시작 (계정 정보는 이미 있음)
      currentStep.value = 2
      
      // user_id는 백엔드에서 자동 생성되므로 임시값 설정
      formData.user_id = 'social_auto_generated'
    } else {
      // SNS 정보가 없으면 일반 회원가입으로 전환
      isSocialSignup.value = false
      // URL에서 social 파라미터 제거
      await navigateTo('/signup', { replace: true })
    }
  }
})

// 유효성 검사 함수들
const validateUserId = (userId: string): string => {
  if (!userId) return '사용자 ID를 입력해주세요'
  if (userId.length < 4) return '사용자 ID는 4자 이상이어야 합니다'
  if (userId.length > 20) return '사용자 ID는 20자 이하여야 합니다'
  if (!/^[a-zA-Z0-9_-]+$/.test(userId)) return '사용자 ID는 영문, 숫자, _, -만 사용 가능합니다'
  return ''
}

const validateEmail = (email: string): string => {
  if (!email) return '이메일을 입력해주세요'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) return '올바른 이메일 형식이 아닙니다'
  return ''
}

const validatePassword = (password: string): string => {
  if (!password) return '비밀번호를 입력해주세요'
  if (password.length < 8) return '비밀번호는 8자 이상이어야 합니다'
  if (password.length > 128) return '비밀번호는 128자 이하여야 합니다'
  
  // 소문자 검증
  if (!/[a-z]/.test(password)) {
    return '소문자를 포함해야 합니다'
  }
  
  // 대문자 검증
  if (!/[A-Z]/.test(password)) {
    return '대문자를 포함해야 합니다'
  }
  
  // 숫자 검증
  if (!/\d/.test(password)) {
    return '숫자를 포함해야 합니다'
  }
  
  // 특수문자 검증 (백엔드와 동일한 특수문자 세트)
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    return '특수문자를 포함해야 합니다'
  }
  
  return ''
}

const validateConfirmPassword = (password: string, confirmPassword: string): string => {
  if (!confirmPassword) return '비밀번호 확인을 입력해주세요'
  if (password !== confirmPassword) return '비밀번호가 일치하지 않습니다'
  return ''
}

const validateName = (name: string): string => {
  if (!name) return '닉네임을 입력해주세요'
  if (name.length < 2) return '닉네임은 2글자 이상이어야 합니다'
  return ''
}

const validatePhone = (phone: string): string => {
  if (!phone) return '전화번호를 입력해주세요'  // 필수 항목으로 변경
  if (!/^01[0-9]{8,9}$/.test(phone)) return '올바른 전화번호 형식이 아닙니다 (01012345678)'
  return ''
}

const validateBirthDate = (birthDate: string): string => {
  if (!birthDate) return '생년월일을 입력해주세요'
  if (!/^\d{8}$/.test(birthDate)) return '생년월일은 8자리 숫자로 입력해주세요 (예: 19900101)'
  
  // 기본적인 날짜 유효성 검사
  const year = parseInt(birthDate.substring(0, 4))
  const month = parseInt(birthDate.substring(4, 6))
  const day = parseInt(birthDate.substring(6, 8))
  
  const currentYear = new Date().getFullYear()
  if (year < 1900 || year > currentYear) return '올바른 연도가 아닙니다'
  if (month < 1 || month > 12) return '올바른 월이 아닙니다'
  if (day < 1 || day > 31) return '올바른 일이 아닙니다'
  
  return ''
}

const validateGender = (gender: string): string => {
  if (!gender) return '성별을 선택해주세요'  // 필수 항목으로 변경
  if (!['M', 'F'].includes(gender)) return '올바른 성별을 선택해주세요'
  return ''
}

// 실시간 중복 체크 함수들
const checkEmailDuplicate = async (email: string): Promise<string> => {
  if (!email) return ''
  
  try {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase
    const response = await $fetch<any>(`${baseURL}/api/v1/auth/check-email`, {
      method: 'POST',
      body: { email }
    })
    
    const payload = response?.data || response
    if (!payload.available) {
      return payload.message || '이미 사용 중인 이메일입니다'
    }
    return ''
  } catch (error: any) {
    console.error('이메일 중복 체크 실패:', error)
    return ''  // 네트워크 오류 시 일단 넘어감
  }
}

const checkPhoneDuplicate = async (phone: string): Promise<string> => {
  if (!phone) return ''
  
  try {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase
    const response = await $fetch<any>(`${baseURL}/api/v1/auth/check-phone`, {
      method: 'POST',
      body: { phone }
    })
    
    const payload = response?.data || response
    if (!payload.available) {
      return payload.message || '이미 사용 중인 전화번호입니다'
    }
    return ''
  } catch (error: any) {
    console.error('전화번호 중복 체크 실패:', error)
    return ''  // 네트워크 오류 시 일단 넘어감
  }
}

const checkNicknameDuplicate = async (nickname: string): Promise<string> => {
  if (!nickname) return ''
  
  try {
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase
    const response = await $fetch<any>(`${baseURL}/api/v1/auth/check-nickname`, {
      method: 'POST',
      body: { nickname }
    })
    
    const payload = response?.data || response
    if (!payload.available) {
      return payload.message || '이미 사용 중인 닉네임입니다'
    }
    return ''
  } catch (error: any) {
    console.error('닉네임 중복 체크 실패:', error)
    return ''  // 네트워크 오류 시 일단 넘어감
  }
}

const checkUserIdDuplicate = async (userId: string): Promise<string> => {
  if (!userId || validateUserId(userId)) return ''
  
  // 사용자 ID 중복 체크 API가 없으므로 임시로 기본 검증만 수행
  // 실제 중복 체크는 회원가입 시점에서 처리됨
  return ''
}

// 실시간 유효성 검사
const validateField = async (field: keyof typeof formData) => {
  switch (field) {
    case 'user_id':
      errors.user_id = validateUserId(formData.user_id)
      if (!errors.user_id) {
        // 기본 유효성 검사 통과 시 중복 체크
        errors.user_id = await checkUserIdDuplicate(formData.user_id)
      }
      break
    case 'email':
      errors.email = validateEmail(formData.email)
      if (!errors.email) {
        // 기본 유효성 검사 통과 시 중복 체크
        errors.email = await checkEmailDuplicate(formData.email)
      }
      break
    case 'password':
      errors.password = validatePassword(formData.password)
      if (formData.confirmPassword) {
        errors.confirmPassword = validateConfirmPassword(formData.password, formData.confirmPassword)
      }
      break
    case 'confirmPassword':
      errors.confirmPassword = validateConfirmPassword(formData.password, formData.confirmPassword)
      break
    case 'name':
      errors.name = validateName(formData.name)
      if (!errors.name) {
        // 기본 유효성 검사 통과 시 중복 체크
        errors.name = await checkNicknameDuplicate(formData.name)
      }
      break
    case 'phone':
      errors.phone = validatePhone(formData.phone)
      if (!errors.phone) {
        // 기본 유효성 검사 통과 시 중복 체크
        errors.phone = await checkPhoneDuplicate(formData.phone)
      }
      break
    case 'birthDate':
      errors.birthDate = validateBirthDate(formData.birthDate)
      break
    case 'gender':
      errors.gender = validateGender(formData.gender)
      break
  }
}

// 비동기 중복 체크 함수들
const validateUserIdAsync = async () => {
  if (!formData.user_id) return
  
  // 먼저 기본 유효성 검사
  const basicError = validateUserId(formData.user_id)
  if (basicError) {
    errors.user_id = basicError
    return
  }
  
  // 중복 체크
  const duplicateError = await checkUserIdDuplicate(formData.user_id)
  errors.user_id = duplicateError
}

const validateEmailAsync = async () => {
  if (!formData.email) return
  
  // 먼저 기본 유효성 검사
  const basicError = validateEmail(formData.email)
  if (basicError) {
    errors.email = basicError
    return
  }
  
  // 중복 체크
  const duplicateError = await checkEmailDuplicate(formData.email)
  errors.email = duplicateError
}

const validatePhoneAsync = async () => {
  if (!formData.phone) return
  
  // 먼저 기본 유효성 검사
  const basicError = validatePhone(formData.phone)
  if (basicError) {
    errors.phone = basicError
    return
  }
  
  // 중복 체크
  const duplicateError = await checkPhoneDuplicate(formData.phone)
  errors.phone = duplicateError
}

const validateNameAsync = async () => {
  if (!formData.name) return
  
  // 먼저 기본 유효성 검사
  const basicError = validateName(formData.name)
  if (basicError) {
    errors.name = basicError
    return
  }
  
  // 중복 체크
  const duplicateError = await checkNicknameDuplicate(formData.name)
  errors.name = duplicateError
}

// 단계별 유효성 검사
const isStepValid = computed(() => {
  switch (currentStep.value) {
    case 1:
      // SNS 로그인인 경우 1단계는 항상 통과 (계정 정보는 이미 있음)
      if (isSocialSignup.value) {
        return true
      }
      return formData.user_id && !errors.user_id && formData.email && !errors.email && formData.password && !errors.password && formData.confirmPassword && !errors.confirmPassword
    case 2:
      // SNS 회원가입에서 필수 필드만 검사 + 이메일 유효성/중복 검사 포함
      if (isSocialSignup.value) {
        // missing_fields 기반으로 검사
        const savedMissingFields = sessionStorage.getItem('missing_fields')
        const missingFields = savedMissingFields ? JSON.parse(savedMissingFields) : ['name', 'phone', 'gender']
        
        const emailValid = !!formData.email && !errors.email
        const nameValid = missingFields.includes('name') ? (formData.name && !errors.name) : true
        const phoneValid = missingFields.includes('phone') ? (formData.phone && !errors.phone && formData.phoneVerified) : true
        const genderValid = missingFields.includes('gender') ? !!formData.gender : true
        
        return emailValid && nameValid && phoneValid && genderValid
      }
      // Regular signup - require phone verification, birth date and gender
      return formData.name && !errors.name && formData.birthDate && !errors.birthDate && formData.phone && !errors.phone && formData.phoneVerified && formData.gender
    case 3:
      return formData.agreeTerms && formData.agreePrivacy
    default:
      return false
  }
})

// 진행률 계산
const progressPercentage = computed(() => (currentStep.value / totalSteps) * 100)

// 단계 이동
const nextStep = () => {
  if (isStepValid.value && currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 뒤로가기
const goBack = () => {
  if (currentStep.value > 1) {
    prevStep()
  } else {
    navigateTo('/')
  }
}

// 약관 전체 동의
const toggleAllTerms = () => {
  const allChecked = formData.agreeTerms && formData.agreePrivacy && formData.agreeMarketing
  formData.agreeTerms = !allChecked
  formData.agreePrivacy = !allChecked
  formData.agreeMarketing = !allChecked
}

// Phone verification methods
const startPhoneVerification = async () => {
  // Validate phone number first
  const phoneError = validatePhone(formData.phone)
  if (phoneError) {
    errors.phone = phoneError
    return
  }
  
  // Validate name and birth date as well
  const nameError = validateName(formData.name)
  if (nameError) {
    errors.name = nameError
    return
  }
  
  const birthError = validateBirthDate(formData.birthDate)
  if (birthError) {
    errors.birthDate = birthError
    return
  }
  
  // TEST MODE: 자동 인증 완료 (개발 환경에서만)
  if (formData.phone === '01012345678') {
    console.log('TEST MODE: Auto-completing phone verification')
    formData.phoneVerified = true
    formData.phoneVerificationToken = 'test-token-123'
    isVerifying.value = false
    
    // 상태 업데이트 강제 반영
    await nextTick()
    return
  }
  
  // Open KCP authentication popup directly
  isVerifying.value = true
  
  // Wait for next tick to ensure the component is mounted
  await nextTick()
  
  // Small delay to ensure component is fully initialized
  setTimeout(() => {
    if (kcpAuthRef.value) {
      kcpAuthRef.value.startAuth()
    }
  }, 100)
}

const handleVerificationSuccess = (result: any) => {
  console.log('Signup - handleVerificationSuccess called with:', result)
  
  // Update user info if provided (do this first)
  if (result.phone) {
    formData.phone = result.phone
  }
  if (result.name) {
    formData.name = result.name
  }
  if (result.birth_day) {
    // Keep as YYYYMMDD to align with validateBirthDate()
    const birthStr = result.birth_day
    if (birthStr && birthStr.length === 8) {
      formData.birthDate = birthStr
    }
  }
  
  // Store verification data (CI/DI or token)
  if (result.ci && result.di) {
    // KCP verification with CI/DI
    formData.phoneVerificationToken = result.ci // Use CI as verification token
    formData.ci = result.ci
    formData.di = result.di
  } else if (result.token) {
    // Regular SMS verification
    formData.phoneVerificationToken = result.token
  }
  
  // Set verification status - MUST be after all other updates
  formData.phoneVerified = true
  
  // Clear any errors
  errors.phone = ''
  errors.birthDate = ''
  errors.name = ''
  // Don't clear gender error - it's optional and clearing it causes "Next" button to activate
  
  // Reset verification state
  isVerifying.value = false
  
  // Log the final state for debugging
  console.log('Signup - After verification update:', {
    phoneVerified: formData.phoneVerified,
    name: formData.name,
    birthDate: formData.birthDate,
    phone: formData.phone,
    gender: formData.gender,
    ci: formData.ci,
    di: formData.di
  })
  
  // Check if step is valid now
  const stepValid = formData.name && !errors.name && 
                   formData.birthDate && !errors.birthDate && 
                   formData.phone && !errors.phone && 
                   formData.phoneVerified && !errors.gender
  
  console.log('Signup - Step 2 valid after verification?', stepValid)
  
  // Show success message
  if (process.client) {
    alert('휴대폰 인증이 완료되었습니다!')
  }
}

const handleVerificationError = (error: string) => {
  errors.phone = error
  isVerifying.value = false
  
  // Show error message
  if (process.client) {
    alert('인증에 실패했습니다. 다시 시도해주세요.')
  }
}

const resetPhoneVerification = () => {
  formData.phoneVerified = false
  formData.phoneVerificationToken = ''
  formData.phone = ''
  errors.phone = ''
}

const closeVerificationModal = () => {
  isVerifying.value = false
  if (kcpAuthRef.value) {
    kcpAuthRef.value.closePopup()
  }
}

// Watch for phone number changes
watch(() => formData.phone, (newPhone, oldPhone) => {
  if (oldPhone && newPhone !== oldPhone && formData.phoneVerified) {
    // Reset verification if phone number changes after verification
    formData.phoneVerified = false
    formData.phoneVerificationToken = ''
  }
})

// 회원가입 처리
const handleSignup = async () => {
  if (!isStepValid.value) return
  
  // 마지막 단계 유효성 재검증
  if (!formData.agreeTerms || !formData.agreePrivacy) {
    errors.terms = '필수 약관에 동의해주세요'
    return
  }
  
  isLoading.value = true
  errors.terms = ''
  
  try {
    let response
    
    if (isSocialSignup.value && socialUserInfo.value) {
      // SNS 회원가입 API 호출
      const config = useRuntimeConfig()
      const baseURL = config.public.apiBase
      response = await $fetch(`${baseURL}/api/v1/auth/social/signup`, {
        method: 'POST',
        body: {
          provider: socialUserInfo.value.provider,
          social_id: socialUserInfo.value.social_id,
          email: formData.email,
          name: formData.name || socialUserInfo.value.name,
          nickname: socialUserInfo.value.nickname,
          phone: formData.phone,
          phone_verification_token: formData.phoneVerificationToken,
          gender: formData.gender,
          agree_terms: formData.agreeTerms,
          agree_privacy: formData.agreePrivacy,
          agree_marketing: formData.agreeMarketing
        }
      }) as any
      // 공통 래퍼 해제
      const payload = (response && 'data' in response) ? (response as any).data : response
      
      // SNS 회원가입 성공 시 처리
      if (payload) {
        console.log('SNS 회원가입 성공:', response)
        
        // 세션에서 SNS 정보 삭제
        sessionStorage.removeItem('social_user_info')
        sessionStorage.removeItem('missing_fields')
        
        // 로딩 종료
        isLoading.value = false
        
        // 토큰이 함께 반환된 경우 (즉시 로그인)
        if (payload.tokens) {
          // 토큰 저장(보안): HttpOnly 쿠키 기반(백엔드가 세팅) 또는 안전한 토큰 스토리지 사용
          setAccessToken(payload.tokens.access_token, payload.tokens.expires_in || 1800)
          // 리프레시 토큰은 서버에서 HttpOnly 쿠키로 처리됨
          
          // 사용자 정보 저장 (보안상 localStorage 대신 메모리/상태 관리 고려)
          if (payload.user) {
            // TODO: 보안을 위해 localStorage 대신 안전한 저장 방식 적용 필요
            localStorage.setItem('user_info', JSON.stringify(payload.user))
          }
          
          // 메인 페이지로 리다이렉트 (로그인 상태로)
          await navigateTo('/?message=social_signup_success', { replace: true })
          return
        } else {
          // 토큰이 없는 경우 로그인 페이지로 이동
          console.log('토큰이 없어 로그인 페이지로 이동')
          await navigateTo('/login?message=social_signup_success', { replace: true })
          return
        }
      } else {
        // SNS 회원가입 실패
        console.error('SNS 회원가입 실패:', response)
        throw new Error(response.message || 'SNS 회원가입 처리 중 오류가 발생했습니다.')
      }
    } else {
      // 일반 회원가입 API 호출
      const config = useRuntimeConfig()
      const baseURL = config.public.apiBase
      // Build request body - gender is now required
      const requestBody: any = {
        user_id: formData.user_id,
        email: formData.email,
        password: formData.password,
        name: formData.name,
        phone: formData.phone,
        gender: formData.gender,  // Required field
        agree_terms: formData.agreeTerms,
        agree_privacy: formData.agreePrivacy,
        agree_marketing: formData.agreeMarketing
      }
      
      response = await $fetch(`${baseURL}/api/v1/auth/signup`, {
        method: 'POST',
        body: requestBody
      })
      const payload = (response && 'data' in (response as any)) ? (response as any).data : response
      
      // 성공 시 성공 메시지와 함께 로그인 페이지로 이동
      isLoading.value = false
      await navigateTo('/login?message=signup_success&email=' + encodeURIComponent(formData.email), { replace: true })
    }
    
  } catch (error: any) {
    console.error('회원가입 실패:', error)
    
    // 에러 메시지 처리 개선 (공통 래퍼 적용 케이스 포함)
    const errorMessage = error?.data?.error?.message || error?.data?.message || error?.data?.detail || error?.message || ''
    if (errorMessage) {
      const errorDetail = errorMessage
      console.log('백엔드 에러 상세:', errorDetail)
      
      // 백엔드에서 온 구체적인 에러 메시지
      if (errorDetail.includes('이미 사용 중인 사용자 ID')) {
        currentStep.value = 1
        errors.user_id = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('이미 사용 중인 이메일')) {
        // 소셜 가입이면 2단계에서, 일반 가입이면 1단계에서 표시
        currentStep.value = isSocialSignup.value ? 2 : 1
        errors.email = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('이미 사용 중인 전화번호')) {
        currentStep.value = 2
        errors.phone = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('이미 사용 중인 닉네임')) {
        currentStep.value = 2
        errors.name = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('비밀번호가 요구사항을 충족하지 않습니다')) {
        currentStep.value = 1
        errors.password = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('전화번호 형식')) {
        currentStep.value = 2
        errors.phone = errorDetail
        errors.terms = ''
      } else if (errorDetail.includes('약관')) {
        currentStep.value = 3
        errors.terms = errorDetail
      } else {
        errors.terms = errorDetail
      }
    } else if (error.status === 400) {
      errors.terms = error.data?.message || '입력하신 정보를 다시 확인해주세요'
    } else if (error.status === 409) {
      currentStep.value = isSocialSignup.value ? 2 : 1
      errors.terms = '이미 사용 중인 사용자 ID 또는 이메일입니다'
    } else if (error.status === 422) {
      errors.terms = '입력 정보의 형식이 올바르지 않습니다'
    } else if (error.status >= 500) {
      errors.terms = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요'
    } else {
      errors.terms = error.message || '회원가입 중 문제가 발생했습니다. 다시 시도해주세요'
    }
  } finally {
    isLoading.value = false
  }
}

// 소셜 로그인 핸들러들
const handleKakaoSignup = async () => {
  try {
    isLoading.value = true
    
    // 소셜 로그인 실행 (모바일/데스크톱 자동 선택)
    const { executeSocialLogin, handleSocialLoginResult, getSocialLoginErrorMessage } = await import('~/utils/social-login')
    
    const result = await executeSocialLogin('kakao')
    const processedResult = handleSocialLoginResult(result)
    
    if (processedResult.action === 'login_complete') {
      // 기존 사용자 로그인 완료 → 홈으로 이동
      await navigateTo('/?message=social_login_success')
    } else if (processedResult.action === 'redirect_to_signup') {
      
      // 신규 사용자 → SNS 회원가입 플로우 시작
      const socialInfo = processedResult.social_user_info
      if (socialInfo) {
        // sessionStorage에 SNS 정보 저장
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        // 소셜 회원가입 모드 활성화
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        // 수정: formData는 reactive 객체이므로 .value 제거
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        
        // 2단계(추가 정보 입력)로 이동
        currentStep.value = 2
      }
    } else if (processedResult.action === 'additional_info_required') {
      // 레거시 액션 처리 → SNS 회원가입 플로우로 변경
      const socialInfo = processedResult.social_user_info
      if (socialInfo) {
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        // 수정: formData 올바른 참조  
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        currentStep.value = 2
      }
    } else if (processedResult.action === 'signup_required') {
      // 레거시 액션 처리 → SNS 회원가입 플로우로 변경
      const socialInfo = processedResult.social_user_info || processedResult.user_info
      if (socialInfo) {
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        // 수정: formData 올바른 참조
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        currentStep.value = 2
      }
    } else {
      throw new Error(processedResult.message)
    }
    
  } catch (error: any) {
    console.error('카카오 회원가입 오류:', error)
    
    if (!error.message.includes('Redirecting')) {
      const { getSocialLoginErrorMessage } = await import('~/utils/social-login')
      const errorMessage = getSocialLoginErrorMessage(error)
      errors.terms = errorMessage
    }
  } finally {
    isLoading.value = false
  }
}

const handleNaverSignup = async () => {
  try {
    isLoading.value = true
    
    // 소셜 로그인 실행 (모바일/데스크톱 자동 선택)
    const { executeSocialLogin, handleSocialLoginResult, getSocialLoginErrorMessage } = await import('~/utils/social-login')
    
    const result = await executeSocialLogin('naver')
    const processedResult = handleSocialLoginResult(result)
    
    if (processedResult.action === 'login_complete') {
      // 기존 사용자 로그인 완료 → 홈으로 이동
      await navigateTo('/?message=social_login_success')
    } else if (processedResult.action === 'redirect_to_signup') {
      // 수정: 페이지 새로고침 대신 직접 처리
      const socialInfo = processedResult.social_user_info
      if (socialInfo) {
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        currentStep.value = 2
      }
    } else if (processedResult.action === 'additional_info_required') {
      // 수정: 페이지 새로고침 대신 직접 처리
      const socialInfo = processedResult.social_user_info
      if (socialInfo) {
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        currentStep.value = 2
      }
    } else if (processedResult.action === 'signup_required') {
      // 수정: 페이지 새로고침 대신 직접 처리
      const socialInfo = processedResult.social_user_info
      if (socialInfo) {
        sessionStorage.setItem('social_user_info', JSON.stringify(socialInfo))
        if (processedResult.missing_fields) {
          sessionStorage.setItem('missing_fields', JSON.stringify(processedResult.missing_fields))
        }
        
        isSocialSignup.value = true
        socialUserInfo.value = socialInfo
        
        formData.email = socialInfo.email || ''
        formData.name = socialInfo.name || socialInfo.nickname || ''
        currentStep.value = 2
      }
    } else {
      throw new Error(processedResult.message)
    }
    
  } catch (error: any) {
    console.error('네이버 회원가입 오류:', error)
    
    if (!error.message.includes('Redirecting')) {
      const { getSocialLoginErrorMessage } = await import('~/utils/social-login')
      const errorMessage = getSocialLoginErrorMessage(error)
      errors.terms = errorMessage
    }
  } finally {
    isLoading.value = false
  }
}

</script>

<template>
  <div class="min-h-screen bg-slate-950 text-white">
    
    <!-- 헤더 -->
    <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
      <div class="flex justify-between items-center px-5 py-4 h-15">
        <button 
          @click="goBack"
          class="w-9 h-9 bg-transparent hover:bg-white/10 rounded-xl flex items-center justify-center text-xl transition-all duration-300 active:scale-95"
          aria-label="뒤로가기"
        >
          ←
        </button>
        
        <h1 class="absolute left-1/2 transform -translate-x-1/2 text-lg font-semibold">
          회원가입
        </h1>
        
        <div class="w-9"></div> <!-- 헤더 균형 맞추기 -->
      </div>
      
      <!-- 진행 표시 바 -->
      <div class="h-1 bg-white/10">
        <div 
          class="h-full bg-gradient-to-r from-purple-600 to-purple-400 transition-all duration-500 ease-out"
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="pt-16 pb-8 px-5 overflow-y-auto">
      <div class="max-w-md mx-auto">
        <!-- 단계 표시 -->
        <div class="flex justify-center gap-2 mb-8">
          <div 
            v-for="step in totalSteps" 
            :key="step"
            :class="[
              'w-2 h-2 rounded-full transition-all duration-300',
              step === currentStep ? 'bg-purple-400 w-6' : step < currentStep ? 'bg-purple-600' : 'bg-white/20'
            ]"
          ></div>
        </div>

        <!-- Step 1: 이메일/비밀번호 -->
        <div v-if="currentStep === 1" class="space-y-6">
          <!-- 히어로 섹션 -->
          <div class="text-center mb-8">
            <div class="text-5xl mb-4">✨</div>
            <h2 class="text-2xl font-bold mb-2">사주라인에 오신 것을 환영합니다</h2>
            <p class="text-white/70 text-sm">
              이메일과 비밀번호로 간편하게 가입하세요
            </p>
          </div>

          <!-- 소셜 로그인 (일반 회원가입에서만 표시) -->
          <div v-if="!isSocialSignup" class="space-y-3 mb-6">
            <button
              @click="handleKakaoSignup"
              class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 active:scale-[0.98] border"
              style="background-color: #FEE500; color: #000000; border-color: #FEE500;"
              @mouseenter="(e) => (e.target as HTMLElement).style.backgroundColor = '#FDD835'"
              @mouseleave="(e) => (e.target as HTMLElement).style.backgroundColor = '#FEE500'"
              aria-label="카카오로 회원가입"
            >
              <span class="text-xl">💬</span>
              <span>카카오로 시작하기</span>
            </button>
            
            <button
              @click="handleNaverSignup"
              class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 active:scale-[0.98] border text-white"
              style="background-color: #03C75A; border-color: #03C75A;"
              @mouseenter="(e) => (e.target as HTMLElement).style.backgroundColor = '#02B351'"
              @mouseleave="(e) => (e.target as HTMLElement).style.backgroundColor = '#03C75A'"
              aria-label="네이버로 회원가입"
            >
              <span class="text-xl font-bold">N</span>
              <span>네이버로 시작하기</span>
            </button>

          </div>

          <!-- 구분선 (일반 회원가입에서만 표시) -->
          <div v-if="!isSocialSignup" class="flex items-center gap-4 my-6">
            <div class="flex-1 h-px bg-white/10"></div>
            <span class="text-white/50 text-sm">또는 이메일로 계속</span>
            <div class="flex-1 h-px bg-white/10"></div>
          </div>

          <!-- SNS 로그인 안내 (SNS 회원가입에서만 표시) -->
          <div v-if="isSocialSignup" class="bg-blue-500/20 border border-blue-500/30 rounded-xl p-4 mb-6">
            <div class="flex items-center gap-3">
              <div class="text-2xl">
                {{ socialUserInfo?.provider === 'kakao' ? '💬' : 'N' }}
              </div>
              <div>
                <p class="text-sm font-medium text-blue-200">
                  {{ socialUserInfo?.provider === 'kakao' ? '카카오' : '네이버' }} 로그인 진행 중
                </p>
                <p class="text-xs text-blue-200/70">
                  회원가입 완료를 위해 추가 정보를 입력해주세요
                </p>
              </div>
            </div>
          </div>

          <!-- 이메일/비밀번호 폼 (일반 회원가입에서만 표시) -->
          <div v-if="!isSocialSignup" class="space-y-4">
            <!-- 사용자 ID -->
            <div>
              <label for="user_id" class="block text-sm font-medium text-white/80 mb-2">
                사용자 ID <span class="text-red-400">*</span>
              </label>
              <input
                id="user_id"
                v-model="formData.user_id"
                @blur="validateUserIdAsync"
                @input="validateField('user_id')"
                type="text"
                placeholder="사용자 ID를 입력해주세요"
                autocomplete="username"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.user_id ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.user_id"
                :aria-describedby="errors.user_id ? 'user_id-error' : undefined"
              />
              <p v-if="errors.user_id" id="user_id-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.user_id }}
              </p>
            </div>

            <!-- 이메일 -->
            <div>
              <label for="email" class="block text-sm font-medium text-white/80 mb-2">
                이메일 <span class="text-red-400">*</span>
              </label>
              <input
                id="email"
                v-model="formData.email"
                @blur="validateEmailAsync"
                @input="validateField('email')"
                type="email"
                placeholder="이메일을 입력해주세요"
                autocomplete="email"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.email ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.email"
                :aria-describedby="errors.email ? 'email-error' : undefined"
              />
              <p v-if="errors.email" id="email-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.email }}
              </p>
            </div>

            <!-- 비밀번호 -->
            <div>
              <label for="password" class="block text-sm font-medium text-white/80 mb-2">
                비밀번호 <span class="text-red-400">*</span>
              </label>
              <input
                id="password"
                v-model="formData.password"
                @blur="validateField('password')"
                @input="validateField('password')"
                type="password"
                placeholder="8자 이상, 대소문자+숫자 포함"
                autocomplete="new-password"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.password ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.password"
                :aria-describedby="errors.password ? 'password-error' : undefined"
              />
              <p v-if="errors.password" id="password-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.password }}
              </p>
            </div>

            <!-- 비밀번호 확인 -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-white/80 mb-2">
                비밀번호 확인 <span class="text-red-400">*</span>
              </label>
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                @blur="validateField('confirmPassword')"
                @input="validateField('confirmPassword')"
                type="password"
                placeholder="비밀번호를 다시 입력해주세요"
                autocomplete="new-password"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.confirmPassword ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.confirmPassword"
                :aria-describedby="errors.confirmPassword ? 'confirm-password-error' : undefined"
              />
              <p v-if="errors.confirmPassword" id="confirm-password-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.confirmPassword }}
              </p>
            </div>
          </div>
        </div>

        <!-- Step 2: 개인정보 입력 -->
        <div v-if="currentStep === 2" class="space-y-6">
          <div class="text-center mb-8">
            <div class="text-5xl mb-4">👋</div>
            <h2 class="text-2xl font-bold mb-2">개인정보를 입력해주세요</h2>
            <p class="text-white/70 text-sm">
              {{ isSocialSignup ? '추가 정보를 입력하여 회원가입을 완료하세요' : '상담 서비스 이용을 위한 기본 정보입니다' }}
            </p>
          </div>

          <!-- SNS 로그인 시 이메일 정보 표시 -->
          <div v-if="isSocialSignup && socialUserInfo" class="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
            <div class="flex items-center gap-3">
              <div class="text-2xl">
                {{ socialUserInfo.provider === 'kakao' ? '💬' : 'N' }}
              </div>
              <div>
                <p class="text-sm font-medium text-white">
                  {{ socialUserInfo.provider === 'kakao' ? '카카오' : '네이버' }} 계정
                </p>
                <p class="text-xs text-white/70">
                  {{ socialUserInfo.email }}
                </p>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <!-- 이메일 (SNS 가입에서도 입력/검증) -->
            <div v-if="isSocialSignup">
              <label for="email_social" class="block text-sm font-medium text-white/80 mb-2">
                이메일 <span class="text-red-400">*</span>
              </label>
              <input
                id="email_social"
                v-model="formData.email"
                @blur="validateEmailAsync"
                @input="validateField('email')"
                type="email"
                placeholder="이메일을 입력해주세요"
                autocomplete="email"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.email ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.email"
                :aria-describedby="errors.email ? 'email-error' : undefined"
              />
              <p v-if="errors.email" id="email-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.email }}
              </p>
            </div>
            <!-- 이름 -->
            <div>
              <label for="name" class="block text-sm font-medium text-white/80 mb-2">
                닉네임 <span class="text-red-400">*</span>
              </label>
              <input
                id="name"
                v-model="formData.name"
                @blur="validateNameAsync"
                @input="validateField('name')"
                type="text"
                placeholder="닉네임을 입력해주세요"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.name ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.name"
                :aria-describedby="errors.name ? 'name-error' : undefined"
              />
              <p v-if="errors.name" id="name-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.name }}
              </p>
            </div>

            <!-- 생년월일 -->
            <div>
              <label for="birthDate" class="block text-sm font-medium text-white/80 mb-2">
                생년월일 <span class="text-red-400">*</span>
              </label>
              <input
                id="birthDate"
                v-model="formData.birthDate"
                @input="validateField('birthDate')"
                type="text"
                placeholder="19900101 (8자리)"
                maxlength="8"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.birthDate ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.birthDate"
                :aria-describedby="errors.birthDate ? 'birthDate-error' : undefined"
              />
              <p v-if="errors.birthDate" id="birthDate-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.birthDate }}
              </p>
            </div>

            <!-- 전화번호 with Verification -->
            <div>
              <label for="phone" class="block text-sm font-medium text-white/80 mb-2">
                전화번호 <span class="text-red-400">*</span>
              </label>
              
              <!-- If not verified, show input with verify button -->
              <div v-if="!formData.phoneVerified" class="space-y-3">
                <div class="flex gap-2">
                  <input
                    id="phone"
                    v-model="formData.phone"
                    @blur="validatePhoneAsync"
                    @input="validateField('phone')"
                    type="tel"
                    placeholder="01012345678"
                    :disabled="isVerifying"
                    :class="[
                      'flex-1 bg-white/5 border rounded-xl px-4 py-3.5 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                      errors.phone ? 'border-red-500' : 'border-white/10'
                    ]"
                    :aria-invalid="!!errors.phone"
                    :aria-describedby="errors.phone ? 'phone-error' : undefined"
                  />
                  <button
                    type="button"
                    @click="startPhoneVerification"
                    :disabled="!formData.phone || errors.phone || isVerifying"
                    class="px-4 py-3.5 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/40 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all duration-300 whitespace-nowrap"
                  >
                    {{ isVerifying ? '인증 중...' : '인증하기' }}
                  </button>
                </div>
                <div class="flex items-center justify-between">
                  <p class="text-xs text-white/50">'-' 없이 숫자만 입력해주세요</p>
                  <p class="text-xs" :class="formData.phoneVerified ? 'text-green-400' : 'text-red-400'">
                    {{ formData.phoneVerified ? '인증 완료' : '인증 안됨' }}
                  </p>
                </div>
              </div>
              
              <!-- If verified, show success message -->
              <div v-else class="space-y-2">
                <div class="flex items-center gap-2 p-3 bg-green-500/10 border border-green-500/30 rounded-xl">
                  <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span class="text-green-400">인증 완료: {{ formData.phone }}</span>
                </div>
                <button
                  type="button"
                  @click="resetPhoneVerification"
                  class="text-xs text-white/50 hover:text-white/70 transition-colors"
                >
                  다른 번호로 인증하기
                </button>
              </div>
              
              <p v-if="errors.phone" id="phone-error" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.phone }}
              </p>
            </div>

            <!-- 성별 -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                성별 <span class="text-white/50">(선택)</span>
              </label>
              <div class="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  @click="formData.gender = 'M'; validateField('gender')"
                  :class="[
                    'px-4 py-3 rounded-xl border transition-all duration-300',
                    formData.gender === 'M'
                      ? 'bg-purple-600 text-white border-purple-600'
                      : 'bg-white/5 text-white border-white/10 hover:border-purple-500/50 hover:bg-white/8'
                  ]"
                >
                  남성
                </button>
                <button
                  type="button"
                  @click="formData.gender = 'F'; validateField('gender')"
                  :class="[
                    'px-4 py-3 rounded-xl border transition-all duration-300',
                    formData.gender === 'F'
                      ? 'bg-purple-600 text-white border-purple-600'
                      : 'bg-white/5 text-white border-white/10 hover:border-purple-500/50 hover:bg-white/8'
                  ]"
                >
                  여성
                </button>
              </div>
              <p v-if="errors.gender" class="text-red-400 text-sm mt-1" role="alert">
                {{ errors.gender }}
              </p>
            </div>
          </div>
        </div>

        <!-- Step 3: 약관 동의 -->
        <div v-if="currentStep === 3" class="space-y-6">
          <div class="text-center mb-8">
            <div class="text-5xl mb-4">📝</div>
            <h2 class="text-2xl font-bold mb-2">약관에 동의해주세요</h2>
            <p class="text-white/70 text-sm">
              서비스 이용을 위해 약관 동의가 필요합니다
            </p>
          </div>

          <div class="space-y-4">
            <!-- 전체 동의 -->
            <div 
              @click="toggleAllTerms"
              class="flex items-center gap-3 p-4 bg-purple-600/20 border border-purple-600/30 rounded-xl cursor-pointer hover:bg-purple-600/25 transition-all duration-300"
            >
              <div class="flex-shrink-0">
                <div 
                  :class="[
                    'w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-300',
                    (formData.agreeTerms && formData.agreePrivacy && formData.agreeMarketing) 
                      ? 'bg-purple-600 border-purple-600' 
                      : 'border-white/30'
                  ]"
                >
                  <svg v-if="formData.agreeTerms && formData.agreePrivacy && formData.agreeMarketing" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
              <span class="font-medium text-purple-300">전체 동의</span>
            </div>

            <!-- 개별 약관 -->
            <div class="space-y-3">
              <!-- 이용약관 -->
              <div class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl">
                <div class="flex-shrink-0">
                  <input
                    id="agree-terms"
                    v-model="formData.agreeTerms"
                    type="checkbox"
                    class="w-5 h-5 rounded border-2 border-white/30 bg-transparent text-purple-600 focus:ring-purple-500 focus:ring-2 focus:ring-offset-0"
                  />
                </div>
                <label for="agree-terms" class="flex-1 flex items-center justify-between cursor-pointer">
                  <span class="text-sm">
                    이용약관 동의 <span class="text-red-400">*</span>
                  </span>
                  <button type="button" class="text-purple-400 text-sm hover:underline">
                    보기
                  </button>
                </label>
              </div>

              <!-- 개인정보처리방침 -->
              <div class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl">
                <div class="flex-shrink-0">
                  <input
                    id="agree-privacy"
                    v-model="formData.agreePrivacy"
                    type="checkbox"
                    class="w-5 h-5 rounded border-2 border-white/30 bg-transparent text-purple-600 focus:ring-purple-500 focus:ring-2 focus:ring-offset-0"
                  />
                </div>
                <label for="agree-privacy" class="flex-1 flex items-center justify-between cursor-pointer">
                  <span class="text-sm">
                    개인정보처리방침 동의 <span class="text-red-400">*</span>
                  </span>
                  <button type="button" class="text-purple-400 text-sm hover:underline">
                    보기
                  </button>
                </label>
              </div>

              <!-- 마케팅 정보 수신 -->
              <div class="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl">
                <div class="flex-shrink-0">
                  <input
                    id="agree-marketing"
                    v-model="formData.agreeMarketing"
                    type="checkbox"
                    class="w-5 h-5 rounded border-2 border-white/30 bg-transparent text-purple-600 focus:ring-purple-500 focus:ring-2 focus:ring-offset-0"
                  />
                </div>
                <label for="agree-marketing" class="flex-1 cursor-pointer">
                  <span class="text-sm text-white/80">
                    마케팅 정보 수신 동의 (선택)
                  </span>
                </label>
              </div>
            </div>

            <p v-if="errors.terms" class="text-red-400 text-sm" role="alert">
              {{ errors.terms }}
            </p>
          </div>
        </div>

        <!-- 버튼 그룹 -->
        <div class="flex gap-3 mt-8">
          <button
            v-if="currentStep > 1"
            @click="prevStep"
            class="flex-1 py-4 bg-white/10 hover:bg-white/15 border border-white/20 text-white font-medium rounded-xl transition-all duration-300 active:scale-98"
          >
            이전
          </button>
          
          <button
            v-if="currentStep < totalSteps"
            @click="nextStep"
            :disabled="!isStepValid"
            :class="[
              'py-4 font-bold rounded-xl transition-all duration-300 active:scale-98',
              currentStep === 1 ? 'w-full' : 'flex-1',
              isStepValid 
                ? 'bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white shadow-lg shadow-purple-500/25' 
                : 'bg-white/10 text-white/50 cursor-not-allowed'
            ]"
          >
            다음
          </button>
          
          <button
            v-if="currentStep === totalSteps"
            @click="handleSignup"
            :disabled="!isStepValid || isLoading"
            :class="[
              'flex-1 py-4 font-bold rounded-xl transition-all duration-300 active:scale-98 flex items-center justify-center gap-2',
              isStepValid && !isLoading
                ? 'bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white shadow-lg shadow-purple-500/25' 
                : 'bg-white/10 text-white/50 cursor-not-allowed'
            ]"
          >
            <svg v-if="isLoading" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ isLoading ? '가입 중...' : '회원가입 완료' }}
          </button>
        </div>

        <!-- 로그인 링크 -->
        <div class="text-center mt-6">
          <p class="text-white/60 text-sm">
            이미 계정이 있으신가요?
            <NuxtLink to="/login" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
              로그인하기
            </NuxtLink>
          </p>
        </div>
      </div>
    </main>
  </div>

  <!-- KCP Direct Authentication (Hidden Component for Popup) -->
  <div v-if="isVerifying" style="display: none;">
    <KcpDirectAuth
      ref="kcpAuthRef"
      :name="formData.name"
      :birth-date="formData.birthDate"
      :phone="formData.phone"
      :gender="formData.gender"
      @success="handleVerificationSuccess"
      @error="handleVerificationError"
      @close="closeVerificationModal"
    />
  </div>
</template>

<style scoped>
/* 커스텀 체크박스 스타일 */
input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  background-color: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

input[type="checkbox"]:checked {
  background-color: rgb(147, 51, 234);
  border-color: rgb(147, 51, 234);
}

input[type="checkbox"]:checked::after {
  content: '✓';
  color: white;
  font-size: 14px;
  font-weight: bold;
}

input[type="checkbox"]:focus {
  box-shadow: 0 0 0 2px rgba(147, 51, 234, 0.5);
}

/* 애니메이션 */
.active\:scale-98:active {
  transform: scale(0.98);
}
</style> 