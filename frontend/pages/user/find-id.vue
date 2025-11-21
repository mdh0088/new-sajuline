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
          <div class="auth-hero-emoji">🔍</div>
          <h2 class="auth-page-title">아이디 찾기</h2>
          <p class="auth-subtitle">
            본인인증을 통해<br />
            가입하신 아이디를 찾아드립니다
          </p>
        </div>

        <!-- 본인인증 안내 -->
        <div class="auth-info-box">
          <div class="auth-info-header">
            <div class="auth-info-icon">📱</div>
            <div>
              <h3 class="auth-info-title">휴대폰 본인인증</h3>
              <p class="auth-info-desc">
                휴대폰 본인인증을 진행하시면<br />
                해당 번호로 가입된 아이디를 확인하실 수 있습니다
              </p>
            </div>
          </div>

          <!-- 본인인증 버튼 -->
          <button
            type="button"
            class="auth-btn-verify"
            :disabled="isVerifying"
            @click="startVerification"
          >
            <span v-if="!isVerifying">휴대폰 본인인증 하기</span>
            <span v-else>인증 진행 중...</span>
          </button>
        </div>

        <!-- 결과 표시 영역 (본인인증 후 표시) -->
        <div v-if="foundUserId" class="auth-result-box success">
          <div class="auth-result-icon">✅</div>
          <h3 class="auth-result-title">아이디를 찾았습니다</h3>
          <div class="auth-result-content">
            <p class="auth-result-value">{{ foundUserId }}</p>
          </div>
          <p class="auth-result-meta">
            가입일: {{ foundUserDate }}
          </p>
        </div>

        <!-- 에러 메시지 표시 -->
        <div v-if="errorMessage" class="auth-error-message">
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

          <!-- 비밀번호 찾기 링크 -->
          <div class="text-center auth-divider">
            <p class="auth-secondary-text">
              비밀번호를 잊으셨나요?
              <NuxtLink to="/user/find-password" class="auth-link-primary">
                비밀번호 찾기
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
  title: '아이디 찾기 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 아이디 찾기. 휴대폰 본인인증으로 가입하신 아이디를 찾으실 수 있습니다.' },
    { property: 'og:title', content: '아이디 찾기 - 사주라인' },
    { property: 'og:description', content: '사주라인 아이디 찾기. 휴대폰 본인인증으로 가입하신 아이디를 찾으실 수 있습니다.' },
    { name: 'robots', content: 'noindex,nofollow' }
  ],
})

// Composables
const toast = useToast()
const { setupPostMessageListener, openVerificationWindow } = usePhoneVerification()
const { useFindUserId } = useUserQueries()
const route = useRoute()

// 상태 관리
const foundUserId = ref('')
const foundUserDate = ref('')
const errorMessage = ref('')
const isVerifying = ref(false)
// ✅ KCP Fallback 리다이렉트 시 페이지 진입부터 로딩 표시
const isRestoringData = ref(route.query.from_kcp === 'true')

// 팝업 및 리스너 관리
let closePopup: (() => void) | null = null
let cleanupListener: (() => void) | null = null

// ID 찾기 mutation hook
const { mutate: findUserId } = useFindUserId({
  onSuccess: (data) => {
    foundUserId.value = data.user_id
    foundUserDate.value = new Date(data.created_at).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
    isVerifying.value = false
    toast.success('아이디를 찾았습니다')
  },
  onError: (error: any) => {
    console.error('Find ID error:', error)
    errorMessage.value = error.message || '아이디 찾기 중 오류가 발생했습니다. 다시 시도해주세요.'
    isVerifying.value = false
    toast.error(errorMessage.value)
  }
})

// 모바일 리다이렉트 처리 (query parameter에서 전화번호 받기)
onMounted(async () => {
  const fromKcp = route.query.from_kcp
  const phone = route.query.phone as string

  if (fromKcp === 'true' && phone) {
    // ✅ 로딩 상태는 이미 초기화 시점에 true로 설정됨 (페이지 진입부터 표시)

    // ✅ DOM 업데이트 대기 - 로딩 오버레이가 실제로 렌더링될 때까지 대기
    await nextTick()

    // ✅ 최소 표시 시간 보장 (300ms) - UX 개선 및 깜빡임 방지
    const startTime = Date.now()

    try {
      // 모바일에서 본인인증 완료 후 리다이렉트된 경우
      console.log('[Find-ID] KCP redirect received', phone)
      findUserId(phone)

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
})

// 본인인증 시작
const startVerification = async () => {
  isVerifying.value = true
  errorMessage.value = ''
  foundUserId.value = ''
  foundUserDate.value = ''

  // ID 찾기 전용 API 호출
  try {
    const { $api } = useNuxtApp()
    const response = await $api<any>('/api/v1/phone-verification/initiate-for-find-id', {
      method: 'POST',
      body: {
        return_url: '/user/find-id'
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
  console.log('[KCP] handleVerificationComplete called', result)

  // 팝업 닫기
  if (closePopup) {
    closePopup()
    closePopup = null
  }

  if (result.success && result.phone) {
    // 인증된 전화번호로 ID 찾기 API 호출
    findUserId(result.phone)
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
