<template>
  <div class="signup-container">
    <!-- 진행 표시 (완료 단계에서는 숨김) -->
    <div class="progress-bar" v-if="currentStep < 5">
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

      <form class="signup-form" @submit.prevent>
        <!-- Step 1: 계정 정보 -->
        <SignupStep1
          v-if="currentStep === 1"
          v-model:signupFormData="signupFormData"
        />

        <!-- Step 2: 기본 정보 -->
        <SignupStep2
          v-if="currentStep === 2"
          v-model:signupFormData="signupFormData"
        />

        <!-- Step 3: 생년월일시 -->
        <SignupStep3
          v-if="currentStep === 3"
          v-model:signupFormData="signupFormData"
        />

        <!-- Step 4: 약관 동의 -->
        <SignupStep4
          v-if="currentStep === 4"
          v-model:signupFormData="signupFormData"
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
import { useUserQueries } from '~/composables/api/useUserQueries'
import { JoinType, Gender } from '~/types/user/models'
import type { UserCreateRequest } from '~/types/user/models'
import type { SignupFormData } from '~/types/auth/signup'
// CSS 파일 import
import '~/assets/css/common/signup-common.css'

definePageMeta({
  layout: false
})

const router = useRouter()
const toast = useToast()

// Vue Query 훅을 setup 컨텍스트에서 초기화
const { useSignupUser } = useUserQueries()
const signupUserMutation = useSignupUser()

// 반응형 데이터
const currentStep = ref(1)
const totalSteps = ref(4)
const showTermsModal = ref(false)
const termsContent = ref('')

// 회원가입 폼 데이터
const signupFormData = reactive<SignupFormData>({
  user_id: '',
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  nickname: '',
  phone: '',
  gender: Gender.MALE,
  birth_date: '',
  join_type: JoinType.COMMON,
  is_marketing_agreed: false,
  // 약관 동의 (필수 약관은 프론트엔드에서만 검증)
  agreeService: false,
  agreePrivacy: false
})


// 각 Step에서 자체 검증하므로 단순화
const isCurrentStepValid = computed(() => {
  return true // Step 컴포넌트에서 개별 검증
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
    
    toast.success('회원가입이 완료되었습니다.')
    currentStep.value = 5
  } catch (error: any) {
    toast.error(error?.message || '회원가입에 실패했습니다.')
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

