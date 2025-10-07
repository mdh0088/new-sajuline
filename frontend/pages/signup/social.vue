<template>
  <div class="signup-container">
    <!-- 진행 표시 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="`width: ${(Math.min(currentStep, totalSteps) / totalSteps) * 100}%`"></div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
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
          {{ socialProvider === 'kakao' ? '💬' : 'N' }}
        </div>
        <h2 class="text-3xl font-bold mb-3">
          {{ socialProvider === 'kakao' ? '카카오' : '네이버' }} 회원가입
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
import { JoinType, Gender } from '~/types/user/models'
import type { SignupFormData } from '~/types/auth/signup'
import '~/assets/css/common/signup-common.css'

definePageMeta({
  layout: false
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

// 유효성 검사
if (!socialProvider.value || !socialId.value) {
  toast.error('잘못된 접근입니다.')
  router.push('/login')
}

// 반응형 데이터
const currentStep = ref(1)
const totalSteps = ref(3) // Step1 스킵으로 총 3단계
const showTermsModal = ref(false)
const termsContent = ref('')
const isSigningUp = ref(false)

// 회원가입 폼 데이터 (Step1 필드 제외, 소셜 정보로 채움)
const signupFormData = reactive<SignupFormData>({
  user_id: '', // 소셜 로그인은 user_id 불필요
  email: socialEmail.value || '',
  password: '', // 소셜 로그인은 password 불필요
  confirmPassword: '',
  name: socialName.value || '',
  nickname: '',
  phone: '',
  phone_chk: false,
  gender: Gender.MALE,
  birth_date: '',
  join_type: socialProvider.value === 'kakao' ? JoinType.KAKAO : JoinType.NAVER,
  is_marketing_agreed: false,
  agreeService: false,
  agreePrivacy: false
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

  isSigningUp.value = true

  // Provider별 user_id 생성
  const userId = socialProvider.value === 'kakao'
    ? `kko${socialId.value}`  // Kakao: kko + 카카오ID
    : socialId.value           // Naver: 이메일 (social_id가 email)

  // Gender enum을 백엔드 형식으로 변환
  const convertGender = (gender: Gender): 'MALE' | 'FEMALE' => {
    return gender === Gender.MALE ? 'MALE' : 'FEMALE'
  }

  // 소셜 회원가입 데이터 생성
  const signupData: SocialSignupRequest = {
    user_id: userId,
    social_provider: socialProvider.value,
    social_id: socialId.value,
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
  } catch (error) {
    // 에러는 mutation onError에서 처리됨
  }
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
