<template>
  <div class="signup-container">
    <!-- KCP 리다이렉트 후 데이터 복원 중 로딩 오버레이 -->
    <div v-if="isRestoringData" class="restoration-overlay">
      <div class="restoration-spinner">
        <div class="spinner"></div>
        <p class="restoration-message">인증 정보를 불러오는 중...</p>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="main-content" :class="{ 'is-loading': isRestoringData }">
      <!-- 진행 표시 (완료 단계에서는 숨김) -->
      <div v-if="currentStep < 5" class="progress-bar-wrapper">
        <div class="progress-bar-inline">
          <div class="progress-fill" :style="`width: ${(Math.min(currentStep, totalSteps) / totalSteps) * 100}%`"></div>
        </div>
      </div>
      <!-- 단계 표시 -->
      <div class="step-indicator">
        <div 
          v-for="(step, index) in totalSteps" 
          :key="index"
          class="step-dot"
          :class="{ active: index < currentStep }"
        ></div>
      </div>

      <form class="signup-form" @submit.prevent>
        <!-- Step 1: 계정 정보 -->
        <SignupStep1
          v-if="currentStep === 1"
          v-model:signupFormData="signupFormData"
          v-model:isStepValid="step1Valid"
        />

        <!-- Step 2: 기본 정보 -->
        <SignupStep2
          v-if="currentStep === 2"
          v-model:signupFormData="signupFormData"
          v-model:isStepValid="step2Valid"
        />

        <!-- Step 3: 생년월일시 -->
        <SignupStep3
          v-if="currentStep === 3"
          v-model:signupFormData="signupFormData"
          v-model:isStepValid="step3Valid"
        />

        <!-- Step 4: 약관 동의 -->
        <SignupStep4
          v-if="currentStep === 4"
          v-model:signupFormData="signupFormData"
          v-model:isStepValid="step4Valid"
          @open-terms="openTermsModal"
        />

        <!-- 완료 화면 -->
        <SignupCompletion
          v-if="currentStep === 5"
          @go-to-login="goToLogin"
        />

        <!-- 버튼 그룹 (완료 화면 제외) -->
        <div v-if="currentStep < 5" class="button-group">
          <button 
            v-if="currentStep > 1" 
            type="button" 
            class="prev-button" 
            @click="prevStep"
          >이전</button>
          <button 
            v-if="currentStep < 4" 
            type="button" 
            class="next-button" 
            :disabled="!isCurrentStepValid"
            @click="nextStep"
          >
            다음
          </button>
          <button 
            v-if="currentStep === 4" 
            type="button" 
            class="next-button" 
            :disabled="!isCurrentStepValid"
            @click="completeSignup"
          >
            가입완료
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
import { useNotify } from '~/composables/utils/useNotify'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { JoinType, Gender } from '~/types/user/models'
import type { UserCreateRequest } from '~/types/user/models'
import type { SignupFormData } from '~/types/auth/signup'
// CSS 파일 import
import '~/assets/css/common/signup-common.css'

definePageMeta({
  layout: 'default'
})

// SEO 메타 데이터 설정
useHead({
  title: '회원가입 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const router = useRouter()
const route = useRoute()
const toast = useToast()
const { notifyConfirm } = useNotify()

// Vue Query 훅을 setup 컨텍스트에서 초기화
const { useSignupUser } = useUserQueries()
const signupUserMutation = useSignupUser()

// 반응형 데이터
const currentStep = ref(1)
const totalSteps = ref(4)
const showTermsModal = ref(false)
const termsContent = ref('')
// ✅ KCP Fallback 리다이렉트 시 페이지 진입부터 로딩 표시
const isRestoringData = ref(route.query.from_kcp === 'true')

// 회원가입 폼 데이터
const signupFormData = reactive<SignupFormData>({
  user_id: '',
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  nickname: '',
  phone: '',
  phone_chk: false,
  gender: Gender.MALE,
  birth_date: '',
  join_type: JoinType.COMMON,
  is_marketing_agreed: false,
  // 약관 동의 (필수 약관은 프론트엔드에서만 검증)
  agreeService: false,
  agreePrivacy: false
})

// 각 Step별 검증 상태
const step1Valid = ref(false)
const step2Valid = ref(false)
const step3Valid = ref(false)
const step4Valid = ref(false)

// localStorage에 폼 데이터 저장 (KCP redirect 후 복원용)
const STORAGE_KEY = 'signup_form_data'
const STEP_KEY = 'signup_current_step'

watch(signupFormData, (newData) => {
  if (process.client) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newData))
  }
}, { deep: true })

watch(currentStep, (step) => {
  if (process.client) {
    localStorage.setItem(STEP_KEY, step.toString())
  }
})

// 페이지 로드 시 복구
onMounted(async () => {
  // 클라이언트 체크
  if (!process.client) return

  // KCP 인증 완료 후 redirect인지 확인 (URL query parameter)
  const fromKcp = route.query.from_kcp

  if (fromKcp === 'true') {
    // ✅ 로딩 상태는 이미 초기화 시점에 true로 설정됨 (페이지 진입부터 표시)
    // isRestoringData.value = true  ← 불필요 (초기값으로 이미 설정)

    // ✅ DOM 업데이트 대기 - 로딩 오버레이가 실제로 렌더링될 때까지 대기
    await nextTick()

    // ✅ 최소 표시 시간 보장 (300ms) - UX 개선 및 깜빡임 방지
    const startTime = Date.now()

    try {
      // 1. localStorage에서 기존 폼 데이터 복원 (Step1 데이터)
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        try {
          const data = JSON.parse(stored)
          Object.assign(signupFormData, data)
        } catch (e) {
          console.error('Failed to restore form data:', e)
        }
      }

      // 2. Query parameter에서 KCP 인증 결과 세팅
      const phone = route.query.phone as string
      const phoneChk = route.query.phone_chk === 'true'
      const verifiedPhone = route.query.verified_phone as string

      if (phone) {
        signupFormData.phone = phone
        signupFormData.phone_chk = phoneChk
        signupFormData.verified_phone = verifiedPhone

        if (phoneChk) {
          toast.success('휴대폰 인증이 완료되었습니다')
          console.log('[Signup] KCP verification completed', {
            phone,
            phone_chk: phoneChk,
            verified_phone: verifiedPhone
          })
        } else {
          toast.error('입력한 번호와 인증한 번호가 다릅니다')
        }
      }

      // 3. Step2로 이동 (KCP 인증 완료 상태)
      currentStep.value = 2

      // 4. URL clean up (query parameter 제거 - 새로고침 시 재실행 방지)
      await router.replace({ path: '/signup' })

      console.log('[Signup] KCP redirect - auto restored to step2')

      // ✅ 최소 표시 시간 보장 - 300ms 미만이면 남은 시간 대기
      const elapsed = Date.now() - startTime
      if (elapsed < 300) {
        await new Promise(resolve => setTimeout(resolve, 300 - elapsed))
      }
    } finally {
      // 로딩 종료 - 에러가 발생해도 반드시 로딩 해제
      isRestoringData.value = false

      // ✅ DOM 업데이트 대기 - 로딩 오버레이 제거가 반영될 때까지 대기
      await nextTick()
    }
  }

  // 일반 접근 (새로고침, 직접 접근): 아무것도 안함
})

// 회원가입 완료 시 localStorage 삭제
const clearStorage = () => {
  localStorage.removeItem(STORAGE_KEY)
  localStorage.removeItem(STEP_KEY)
}

// 현재 Step의 검증 상태
const isCurrentStepValid = computed(() => {
  switch (currentStep.value) {
    case 1: return step1Valid.value
    case 2: return step2Valid.value
    case 3: return step3Valid.value
    case 4: return step4Valid.value
    default: return false
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

  // SignupStep3에서 이미 birth_date 형식으로 통합되어 별도 처리 불필요

  // 회원가입 데이터 생성
  const userData: UserCreateRequest = {
    user_id: signupFormData.user_id,
    email: signupFormData.email,
    password: signupFormData.password,
    nickname: signupFormData.nickname,
    phone: signupFormData.phone,
    phone_chk: signupFormData.phone_chk,
    join_type: signupFormData.join_type,
    profile_image_url: undefined,
    birth_date: signupFormData.birth_date || undefined,
    gender: signupFormData.gender,
    is_marketing_agreed: signupFormData.is_marketing_agreed,
    social_provider: undefined,
    social_id: undefined
  }

  try {
    // 회원가입 실행
    await signupUserMutation.mutateAsync(userData)

    // 회원가입 완료 - localStorage 삭제
    clearStorage()

    toast.success('회원가입이 완료되었습니다.')
    currentStep.value = 5
  } catch (error: any) {
    // 에러 메시지 추출 (H3Error, API Response, 일반 Error 모두 대응)
    const errorMessage =
      error?.statusMessage ||
      error?.message ||
      error?.data?.message ||
      '회원가입에 실패했습니다.'

    // 탈퇴 후 재가입 제한 경고 - 중요 경고이므로 confirm 다이얼로그로 표시
    if (errorMessage.includes('탈퇴') && errorMessage.includes('재가입')) {
      await notifyConfirm(errorMessage, {
        title: '재가입 제한 안내',
        confirmText: '확인',
        cancelText: ''
      })
    } else {
      toast.error(errorMessage)
    }
  }
}

const goToLogin = () => {
  router.push('/login')
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
        <p>제3조 (서비스의 제공)</p>
        <p>회사는 회원에게 아래와 같은 서비스를 제공합니다.</p>
        <p>1. 사주 상담 서비스</p>
        <p>2. 운세 분석 서비스</p>
        <p>3. 기타 회사가 정하는 서비스</p>
      `
      break
    case 'privacy':
      content = `
        <h4>개인정보 수집 및 이용 동의</h4>
        <p>1. 수집하는 개인정보 항목</p>
        <p>- 필수항목: 이메일, 비밀번호, 이름, 휴대폰번호, 성별, 생년월일</p>
        <p>- 선택항목: 생년월일시</p>
        <p>2. 개인정보의 수집 및 이용목적</p>
        <p>- 회원 관리 및 서비스 제공</p>
        <p>- 상담 및 문의 응대</p>
        <p>3. 개인정보의 보유 및 이용기간</p>
        <p>- 회원 탈퇴 시까지</p>
      `
      break
    case 'marketing':
      content = `
        <h4>마케팅 정보 수신 동의</h4>
        <p>1. 마케팅 활용 목적</p>
        <p>- 새로운 서비스 및 이벤트 정보 제공</p>
        <p>- 서비스 이용에 대한 통계 분석</p>
        <p>2. 마케팅 활용 항목</p>
        <p>- 이메일, 휴대폰번호</p>
        <p>3. 보유 및 이용기간</p>
        <p>- 동의 철회 시까지</p>
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
