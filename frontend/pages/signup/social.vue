<template>
  <div class="signup-container">
    <!-- KCP 리다이렉트 후 데이터 복원 중 로딩 오버레이 -->
    <div v-if="isRestoringData" class="restoration-overlay">
      <div class="restoration-spinner">
        <div class="spinner"></div>
        <p class="restoration-message">인증 정보를 불러오는 중...</p>
      </div>
    </div>

    <!-- 진행 표시 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="`width: ${(Math.min(currentStep, totalSteps) / totalSteps) * 100}%`"></div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="main-content" :class="{ 'is-loading': isRestoringData }">
      <!-- 단계 표시 -->
      <div class="step-indicator">
        <div
          v-for="(step, index) in totalSteps"
          :key="index"
          class="step-dot"
          :class="{ active: index < currentStep }"
        ></div>
      </div>

      <!-- 소셜 로그인 안내 -->
      <div v-if="currentStep === 1" class="text-center mb-8">
        <div class="text-6xl mb-4">
          {{ socialInfo?.provider === 'kakao' ? '💬' : 'N' }}
        </div>
        <h2 class="text-3xl font-bold mb-3">
          {{ socialInfo?.provider === 'kakao' ? '카카오' : '네이버' }} 회원가입
        </h2>
        <p class="text-white/70">
          추가 정보를 입력하여 회원가입을 완료해주세요
        </p>
      </div>

      <form class="signup-form" @submit.prevent>
        <!-- Step 1: 기본 정보 (이메일 + Step2 내용) -->
        <SocialSignupStep2
          v-if="currentStep === 1"
          v-model:signupFormData="signupFormData"
        />

        <!-- Step 2: 생년월일시 -->
        <SignupStep3
          v-if="currentStep === 2"
          v-model:signupFormData="signupFormData"
        />

        <!-- Step 3: 약관 동의 -->
        <SignupStep4
          v-if="currentStep === 3"
          v-model:signupFormData="signupFormData"
          @open-terms="openTermsModal"
        />

        <!-- 완료 화면 -->
        <SignupCompletion
          v-if="currentStep === 4"
          @go-to-login="goToHome"
        />

        <!-- 버튼 그룹 (완료 화면 제외) -->
        <div v-if="currentStep < 4" class="button-group">
          <button
            v-if="currentStep > 1"
            type="button"
            class="prev-button"
            @click="prevStep"
          >이전</button>
          <button
            v-if="currentStep < 3"
            type="button"
            class="next-button"
            :disabled="!isCurrentStepValid"
            @click="nextStep"
          >
            다음
          </button>
          <button
            v-if="currentStep === 3"
            type="button"
            class="next-button"
            :disabled="!isCurrentStepValid || isSigningUp"
            @click="completeSignup"
          >
            {{ isSigningUp ? '가입 중...' : '가입완료' }}
          </button>
        </div>
      </form>
    </main>

    <!-- 약관 모달 -->
    <SignupTermsModal
      :show="showTermsModal"
      :content="termsContent"
      @close="closeTermsModal"
    />
  </div>
</template>

<script setup lang="ts">
import { useToast } from '~/composables/ui/useToast'
import { useSocialAuthQueries, type SocialSignupRequest } from '~/composables/api/useSocialAuthQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { usePhoneVerification, type PhoneVerificationResult } from '~/composables/api/usePhoneVerification'
import { JoinType, Gender } from '~/types/user/models'
import type { SignupFormData } from '~/types/auth/signup'
import '~/assets/css/common/signup-common.css'

definePageMeta({
  layout: 'default'
})

// SEO 메타 데이터 설정
useHead({
  title: '소셜 회원가입 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { handleLoginSuccessWithRole } = useAuth()
const { useSocialSignup } = useSocialAuthQueries()

// 쿼리 파라미터에서 소셜 정보 추출
const socialProvider = computed(() => route.query.provider as 'kakao' | 'naver')
const socialId = computed(() => route.query.social_id as string)
const socialEmail = computed(() => route.query.email as string)
const socialName = computed(() => route.query.name as string)

// localStorage 키
const SOCIAL_SIGNUP_FORM_KEY = 'social_signup_form_data'
const SOCIAL_INFO_KEY = 'social_signup_info'  // 소셜 정보 별도 저장

// KCP Fallback 감지 (페이지 진입 시점부터)
const fromKcp = route.query.from_kcp as string
const isRestoringData = ref(fromKcp === 'true')  // KCP 복원 중 로딩 표시

// 소셜 정보 (localStorage에서 복원 가능하도록)
interface SocialInfo {
  provider: 'kakao' | 'naver'
  social_id: string
  email: string
  name: string
}

// 소셜 정보 초기화 (URL 쿼리 또는 localStorage에서)
const getSocialInfo = (): SocialInfo | null => {
  // 1. URL 쿼리 파라미터에서 먼저 확인
  if (socialProvider.value && socialId.value) {
    return {
      provider: socialProvider.value,
      social_id: socialId.value,
      email: socialEmail.value || '',
      name: socialName.value || ''
    }
  }

  // 2. localStorage에서 복원 시도 (KCP Fallback 케이스)
  if (process.client) {
    const stored = localStorage.getItem(SOCIAL_INFO_KEY)
    if (stored) {
      try {
        return JSON.parse(stored) as SocialInfo
      } catch (e) {
        console.error('[Social Signup] Failed to parse social info:', e)
      }
    }
  }

  return null
}

const socialInfo = ref<SocialInfo | null>(getSocialInfo())

// 반응형 데이터
const currentStep = ref(1)
const totalSteps = ref(3) // Step1 스킵으로 총 3단계
const showTermsModal = ref(false)
const termsContent = ref('')
const isSigningUp = ref(false)

// 회원가입 폼 데이터 (Step1 필드 제외, 소셜 정보로 채움)
const signupFormData = reactive<SignupFormData>({
  user_id: '', // 소셜 로그인은 user_id 불필요
  email: socialInfo.value?.email || '',
  password: '', // 소셜 로그인은 password 불필요
  confirmPassword: '',
  name: socialInfo.value?.name || '',
  nickname: '',
  phone: '',
  phone_chk: false,
  gender: Gender.MALE,
  birth_date: '',
  join_type: socialInfo.value?.provider === 'kakao' ? JoinType.KAKAO : JoinType.NAVER,
  is_marketing_agreed: false,
  agreeService: false,
  agreePrivacy: false
})

// KCP Fallback 처리 (Mobile에서 인증 완료 후 리다이렉트)
const { setupPostMessageListener } = usePhoneVerification()

// 소셜 정보를 localStorage에 저장 (KCP Fallback 대비)
watch(() => socialInfo.value, (info) => {
  if (process.client && info) {
    localStorage.setItem(SOCIAL_INFO_KEY, JSON.stringify(info))
  }
}, { immediate: true })

// 폼 데이터 변경 시 localStorage에 저장 (KCP Fallback 대비)
watch(signupFormData, (newData) => {
  if (process.client) {
    localStorage.setItem(SOCIAL_SIGNUP_FORM_KEY, JSON.stringify(newData))
  }
}, { deep: true })

onMounted(async () => {
  // 클라이언트 체크
  if (!process.client) return

  // 유효성 검사 (클라이언트에서만 실행)
  // KCP Fallback이 아닌데 소셜 정보가 없으면 잘못된 접근
  if (!socialInfo.value && fromKcp !== 'true') {
    // localStorage에서 복원 시도
    const storedSocialInfo = localStorage.getItem(SOCIAL_INFO_KEY)
    if (storedSocialInfo) {
      try {
        socialInfo.value = JSON.parse(storedSocialInfo)
      } catch (e) {
        console.error('[Social Signup] Failed to parse social info:', e)
      }
    }

    // 복원 후에도 없으면 리다이렉트
    if (!socialInfo.value) {
      toast.error('잘못된 접근입니다.')
      router.push('/login')
      return
    }
  }

  // KCP Fallback에서 돌아온 경우 처리
  if (fromKcp === 'true') {
    console.log('[Social Signup] KCP Fallback detected')

    // DOM 업데이트 대기 - 로딩 오버레이가 렌더링될 때까지
    await nextTick()

    // 최소 표시 시간 보장 (300ms)
    const startTime = Date.now()

    try {
      // 1. localStorage에서 소셜 정보 복원
      const storedSocialInfo = localStorage.getItem(SOCIAL_INFO_KEY)
      if (storedSocialInfo) {
        try {
          socialInfo.value = JSON.parse(storedSocialInfo)
          console.log('[Social Signup] Social info restored:', socialInfo.value)
        } catch (e) {
          console.error('[Social Signup] Failed to parse social info:', e)
        }
      }

      // 2. localStorage에서 폼 데이터 복원
      const savedFormData = localStorage.getItem(SOCIAL_SIGNUP_FORM_KEY)
      if (savedFormData) {
        try {
          const parsedData = JSON.parse(savedFormData)
          Object.assign(signupFormData, parsedData)
          console.log('[Social Signup] Form data restored from localStorage')
        } catch (e) {
          console.error('[Social Signup] Failed to parse saved form data:', e)
        }
      }

      // 3. Query parameter에서 KCP 인증 결과 세팅
      // 백엔드가 보내는 파라미터: phone, phone_chk (= is_phone_matched), verified_phone
      const phone = route.query.phone as string
      const phoneChk = route.query.phone_chk === 'true'  // 백엔드에서 is_phone_matched 값을 phone_chk로 전달
      const verifiedPhone = route.query.verified_phone as string

      if (phone) {
        signupFormData.phone = phone
        signupFormData.phone_chk = phoneChk
        signupFormData.verified_phone = verifiedPhone

        if (phoneChk) {
          toast.success('휴대폰 인증이 완료되었습니다')
          console.log('[Social Signup] KCP verification completed', {
            phone,
            phone_chk: phoneChk,
            verified_phone: verifiedPhone
          })
        } else {
          toast.error('입력한 번호와 인증한 번호가 다릅니다')
        }
      }

      // 4. URL clean up (소셜 정보 쿼리 파라미터 복원)
      const cleanParams: Record<string, string> = {}
      if (socialInfo.value) {
        cleanParams.provider = socialInfo.value.provider
        cleanParams.social_id = socialInfo.value.social_id
        if (socialInfo.value.email) cleanParams.email = socialInfo.value.email
        if (socialInfo.value.name) cleanParams.name = socialInfo.value.name
      }

      await router.replace({ path: '/signup/social', query: cleanParams })

      console.log('[Social Signup] KCP redirect - data restored')

      // 최소 표시 시간 보장 - 300ms 미만이면 남은 시간 대기
      const elapsed = Date.now() - startTime
      if (elapsed < 300) {
        await new Promise(resolve => setTimeout(resolve, 300 - elapsed))
      }
    } finally {
      // 로딩 종료
      isRestoringData.value = false
      await nextTick()
    }
  }

  // postMessage 리스너 설정 (PC 팝업 인증용)
  setupPostMessageListener((result: PhoneVerificationResult) => {
    if (result.success && result.is_phone_matched) {
      signupFormData.phone = result.phone || ''
      signupFormData.phone_chk = true
    }
  })
})

// 각 Step 검증
const isCurrentStepValid = computed(() => {
  return true // Step 컴포넌트에서 개별 검증
})

// 소셜 회원가입 뮤테이션
const socialSignupMutation = useSocialSignup({
  onSuccess: (data) => {
    // 자동 로그인 (쿠키 이미 설정됨)
    handleLoginSuccessWithRole(data, 'user')
    toast.success('회원가입이 완료되었습니다!')
    currentStep.value = 4
  },
  onError: (error: any) => {
    isSigningUp.value = false
    toast.error(error?.message || '회원가입에 실패했습니다.')
  }
})

// 메서드
const nextStep = () => {
  if (isCurrentStepValid.value && currentStep.value < totalSteps.value) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const completeSignup = async () => {
  if (!signupFormData.agreeService || !signupFormData.agreePrivacy) {
    toast.error('필수 약관에 동의해주세요.')
    return
  }

  if (!socialInfo.value) {
    toast.error('소셜 로그인 정보가 없습니다.')
    return
  }

  isSigningUp.value = true

  // Provider별 user_id 생성 (socialInfo에서 가져옴)
  const userId = socialInfo.value.provider === 'kakao'
    ? `kko${socialInfo.value.social_id}`  // Kakao: kko + 카카오ID
    : socialInfo.value.social_id           // Naver: 이메일 (social_id가 email)

  // Gender enum을 백엔드 형식으로 변환
  const convertGender = (gender: Gender): 'MALE' | 'FEMALE' => {
    return gender === Gender.MALE ? 'MALE' : 'FEMALE'
  }

  // 소셜 회원가입 데이터 생성 (socialInfo에서 가져옴)
  const signupData: SocialSignupRequest = {
    user_id: userId,
    social_provider: socialInfo.value.provider,
    social_id: socialInfo.value.social_id,
    email: signupFormData.email || undefined,
    nickname: signupFormData.nickname,
    phone: signupFormData.phone,
    phone_chk: signupFormData.phone_chk,
    gender: convertGender(signupFormData.gender),
    birth_date: signupFormData.birth_date || undefined,
    is_marketing_agreed: signupFormData.is_marketing_agreed
  }

  try {
    await socialSignupMutation.mutateAsync(signupData)
    // 성공 시 localStorage 정리
    clearStorage()
  } catch (error) {
    // 에러는 mutation onError에서 처리됨
  }
}

// localStorage 정리
const clearStorage = () => {
  localStorage.removeItem(SOCIAL_SIGNUP_FORM_KEY)
  localStorage.removeItem(SOCIAL_INFO_KEY)
}

const goToHome = () => {
  router.push('/')
}

const openTermsModal = (type: string) => {
  let content = ''

  switch(type) {
    case 'service':
      content = `
        <h4>서비스 이용약관</h4>
        <p>제1조 (목적)</p>
        <p>이 약관은 사주라인(이하 "회사")이 제공하는 서비스의 이용과 관련하여 회사와 회원 간의 권리, 의무 및 책임사항을 규정함을 목적으로 합니다.</p>
        <p>제2조 (정의)</p>
        <p>1. "서비스"란 회사가 제공하는 모든 서비스를 의미합니다.</p>
        <p>2. "회원"이란 회사와 서비스 이용계약을 체결한 자를 말합니다.</p>
      `
      break
    case 'privacy':
      content = `
        <h4>개인정보 수집 및 이용 동의</h4>
        <p>1. 수집하는 개인정보 항목</p>
        <p>- 필수항목: 이메일, 이름, 휴대폰번호, 성별</p>
        <p>- 선택항목: 생년월일시</p>
        <p>2. 개인정보의 수집 및 이용목적</p>
        <p>- 회원 관리 및 서비스 제공</p>
      `
      break
    case 'marketing':
      content = `
        <h4>마케팅 정보 수신 동의</h4>
        <p>1. 마케팅 활용 목적</p>
        <p>- 새로운 서비스 및 이벤트 정보 제공</p>
      `
      break
  }

  termsContent.value = content
  showTermsModal.value = true
}

const closeTermsModal = () => {
  showTermsModal.value = false
}
</script>

<style scoped>
/* KCP 리다이렉트 후 데이터 복원 중 로딩 오버레이 */
.restoration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.restoration-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.restoration-message {
  color: white;
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
}

/* 로딩 중 메인 콘텐츠 비활성화 */
.main-content.is-loading {
  pointer-events: none;
  opacity: 0.5;
  user-select: none;
}
</style>
