<template>
  <div class="auth-container">
    <!-- KCP 리다이렉트 후 데이터 복원 중 로딩 오버레이 -->
    <div v-if="isRestoringData" class="restoration-overlay">
      <div class="restoration-spinner">
        <div class="spinner"></div>
        <p class="restoration-message">인증 정보를 처리하는 중...</p>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="auth-main" :class="{ 'is-loading': isRestoringData }">
      <div class="max-w-md mx-auto">
        <!-- 히어로 섹션 -->
        <div class="text-center mb-10">
          <div class="auth-hero-emoji">🔑</div>
          <h2 class="auth-page-title">비밀번호 찾기</h2>
          <p class="auth-subtitle">
            아이디와 본인인증을 통해<br />
            임시 비밀번호를 발송해드립니다
          </p>
        </div>

        <!-- 비밀번호 찾기 폼 -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- 아이디 입력 -->
          <div>
            <label class="auth-label">
              아이디
            </label>
            <input
              v-model="userId"
              type="text"
              placeholder="아이디를 입력하세요"
              class="auth-input"
              :disabled="isVerifying"
              required
            />
          </div>

          <!-- 안내 메시지 -->
          <div class="auth-result-box info">
            <div class="flex items-start gap-3">
              <div class="auth-info-icon">💡</div>
              <div>
                <p class="auth-info-title">임시 비밀번호 안내</p>
                <ul class="auth-notice-list">
                  <li>• 임시 비밀번호는 가입하신 이메일로 발송됩니다</li>
                  <li>• 로그인 후 반드시 비밀번호를 변경해주세요</li>
                  <li>• 보안을 위해 정기적으로 비밀번호를 변경하세요</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 휴대폰 본인인증 버튼 -->
          <button
            type="submit"
            :disabled="!userId.trim() || isVerifying"
            class="auth-btn-verify"
          >
            <span v-if="!isVerifying">휴대폰 본인인증 하기</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              인증 진행 중...
            </span>
          </button>
        </form>

        <!-- 성공 메시지 (발송 완료 후 표시) -->
        <div v-if="successMessage" class="mt-6 auth-result-box success">
          <div class="auth-result-icon">✅</div>
          <h3 class="auth-result-title">임시 비밀번호 발송 완료</h3>
          <p class="auth-info-desc mb-2">
            가입하신 이메일로 임시 비밀번호가 발송되었습니다
          </p>
          <div class="auth-result-content">
            <p class="auth-result-value">{{ maskedEmail }}</p>
          </div>
          <p class="auth-result-meta">
            {{ successMessage }}
          </p>
        </div>

        <!-- 에러 메시지 표시 -->
        <div v-if="errorMessage" class="mt-6 auth-error-message">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>{{ errorMessage }}</p>
          </div>
        </div>

        <!-- 하단 링크 -->
        <div class="auth-footer-links">
          <!-- 로그인 링크 -->
          <div class="text-center">
            <NuxtLink to="/login" class="auth-footer-link">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
              </svg>
              로그인하기
            </NuxtLink>
          </div>

          <!-- 아이디 찾기 링크 -->
          <div class="text-center auth-divider">
            <p class="auth-secondary-text">
              아이디를 잊으셨나요?
              <NuxtLink to="/user/find-id" class="auth-link-primary">
                아이디 찾기
              </NuxtLink>
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { usePhoneVerification, type PhoneVerificationResult } from '~/composables/api/usePhoneVerification'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useToast } from '~/composables/ui/useToast'

// 인증 도메인 CSS 로드
import '~/assets/css/common/auth-common.css'

definePageMeta({
  layout: 'default'
})

// SEO 및 메타 데이터 설정
useHead({
  title: '비밀번호 찾기 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 비밀번호 찾기. 아이디와 본인인증으로 임시 비밀번호를 받으실 수 있습니다.' },
    { property: 'og:title', content: '비밀번호 찾기 - 사주라인' },
    { property: 'og:description', content: '사주라인 비밀번호 찾기. 아이디와 본인인증으로 임시 비밀번호를 받으실 수 있습니다.' },
    { name: 'robots', content: 'noindex,nofollow' }
  ],
})

// Composables
const toast = useToast()
const { setupPostMessageListener, openVerificationWindow } = usePhoneVerification()
const { useFindPassword } = useUserQueries()
const route = useRoute()

// 상태 관리
const userId = ref('')
const maskedEmail = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const isVerifying = ref(false)
// ✅ KCP Fallback 리다이렉트 시 페이지 진입부터 로딩 표시
const isRestoringData = ref(route.query.from_kcp === 'true')
// ✅ 중복 호출 방지 플래그
const isProcessing = ref(false)

// 팝업 및 리스너 관리
let closePopup: (() => void) | null = null
let cleanupListener: (() => void) | null = null

// 비밀번호 찾기 mutation hook
const { mutate: findPassword } = useFindPassword({
  onSuccess: (data) => {
    maskedEmail.value = data.email
    successMessage.value = data.message
    isVerifying.value = false
    isProcessing.value = false  // ✅ 처리 완료
    toast.success('임시 비밀번호가 발송되었습니다')
  },
  onError: (error: any) => {
    console.error('Find password error:', error)
    errorMessage.value = error.message || '비밀번호 찾기 중 오류가 발생했습니다. 다시 시도해주세요.'
    isVerifying.value = false
    isProcessing.value = false  // ✅ 처리 완료 (에러 시에도)
    toast.error(errorMessage.value)
  }
})

// ✅ onMounted 처리 제거 - postMessage로만 처리
// 모바일 리다이렉트는 발생하지 않아야 함 (KCP 콜백에서 postMessage 사용)
onMounted(() => {
  if (route.query.from_kcp === 'true') {
    isRestoringData.value = false
  }
})

// 폼 제출 처리 (본인인증 시작)
const handleSubmit = async () => {
  if (!userId.value.trim() || isVerifying.value) return

  // ✅ 재인증 시작 - 이전 상태 초기화
  isVerifying.value = true
  errorMessage.value = ''
  successMessage.value = ''
  maskedEmail.value = ''
  isProcessing.value = false  // ✅ 재인증을 위해 플래그 초기화

  // ✅ 기존 리스너 완전 제거 (중복 등록 방지)
  if (cleanupListener) {
    cleanupListener()
    cleanupListener = null
  }

  // 비밀번호 찾기 전용 API 호출
  try {
    const { $api } = useNuxtApp()
    const response = await $api<any>('/api/v1/phone-verification/initiate-for-find-password', {
      method: 'POST',
      body: {
        user_id: userId.value,
        return_url: '/user/find-password'
      }
    })

    if (response.success && response.data) {
      // postMessage 리스너 설정
      cleanupListener = setupPostMessageListener(handleVerificationComplete)

      // 인증창 열기 (팝업 방식)
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
      closePopup = openVerificationWindow(response.data.gateway_url, response.data.form_data, isMobile)
    }
  } catch (error: any) {
    isVerifying.value = false
    errorMessage.value = error?.message || '인증 시작에 실패했습니다'
    toast.error(errorMessage.value)
  }
}

// 본인인증 완료 핸들러
const handleVerificationComplete = (result: PhoneVerificationResult) => {
  // ✅ 중복 호출 방지 - 이미 처리 중이면 무시
  if (isProcessing.value) {
    return
  }

  // ✅ 즉시 리스너 제거 (중복 실행 방지)
  if (cleanupListener) {
    cleanupListener()
    cleanupListener = null
  }

  // 팝업 닫기
  if (closePopup) {
    closePopup()
    closePopup = null
  }

  if (result.success && result.phone) {
    // ✅ 처리 시작 플래그 설정 (1회성 보장)
    isProcessing.value = true

    // ✅ 인증된 전화번호로 비밀번호 찾기 API 단 1회 호출
    findPassword({ user_id: userId.value, phone: result.phone })
  } else {
    isVerifying.value = false
    errorMessage.value = result.error || '인증에 실패했습니다'
    toast.error(errorMessage.value)
  }
}

// Cleanup
onUnmounted(() => {
  if (cleanupListener) {
    cleanupListener()
  }
  if (closePopup) {
    closePopup()
  }
  // Form 정리
  const popupForm = document.getElementById('kcp_cert_form')
  if (popupForm) {
    popupForm.remove()
  }
})
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
.auth-main.is-loading {
  pointer-events: none;
  opacity: 0.5;
  user-select: none;
}
</style>
