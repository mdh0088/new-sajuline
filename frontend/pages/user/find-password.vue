<template>
  <div class="auth-container">
    <!-- 메인 콘텐츠 -->
    <main class="auth-main">
      <div class="max-w-md mx-auto">
        <!-- 히어로 섹션 -->
        <div class="text-center mb-10">
          <div class="text-6xl mb-4">🔑</div>
          <h2 class="text-3xl font-bold mb-3">비밀번호 찾기</h2>
          <p class="text-white/70 text-base">
            아이디와 본인인증을 통해<br />
            임시 비밀번호를 발송해드립니다
          </p>
        </div>

        <!-- 비밀번호 찾기 폼 -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- 아이디 입력 -->
          <div>
            <label class="block text-sm font-medium text-white/80 mb-2">
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
          <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
            <div class="flex items-start gap-3">
              <div class="text-xl">💡</div>
              <div class="text-sm text-white/70 leading-relaxed">
                <p class="font-semibold mb-1">임시 비밀번호 안내</p>
                <ul class="space-y-1 text-xs">
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
            class="w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-98 shadow-lg shadow-purple-500/25 disabled:shadow-none"
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
        <div v-if="successMessage" class="mt-6 p-6 bg-green-500/10 border border-green-500/30 rounded-xl">
          <div class="text-center">
            <div class="text-3xl mb-3">✅</div>
            <h3 class="text-lg font-semibold mb-3">임시 비밀번호 발송 완료</h3>
            <p class="text-white/70 text-sm leading-relaxed mb-2">
              가입하신 이메일로 임시 비밀번호가 발송되었습니다
            </p>
            <div class="p-3 bg-white/5 rounded-lg mb-2">
              <p class="text-purple-400 font-medium">{{ maskedEmail }}</p>
            </div>
            <p class="text-white/50 text-xs">
              {{ successMessage }}
            </p>
          </div>
        </div>

        <!-- 에러 메시지 표시 -->
        <div v-if="errorMessage" class="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <div class="flex items-center gap-2 text-red-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- 하단 링크 -->
        <div class="space-y-4 mt-8">
          <!-- 로그인 링크 -->
          <div class="text-center">
            <NuxtLink
              to="/login"
              class="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
              </svg>
              로그인하기
            </NuxtLink>
          </div>

          <!-- 아이디 찾기 링크 -->
          <div class="text-center pt-4 border-t border-white/10">
            <p class="text-white/60 text-sm">
              아이디를 잊으셨나요?
              <NuxtLink to="/user/find-id" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
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

// 팝업 및 리스너 관리
let closePopup: (() => void) | null = null
let cleanupListener: (() => void) | null = null

// 비밀번호 찾기 mutation hook
const { mutate: findPassword } = useFindPassword({
  onSuccess: (data) => {
    maskedEmail.value = data.email
    successMessage.value = data.message
    isVerifying.value = false
    toast.success('임시 비밀번호가 발송되었습니다')
  },
  onError: (error: any) => {
    console.error('Find password error:', error)
    errorMessage.value = error.message || '비밀번호 찾기 중 오류가 발생했습니다. 다시 시도해주세요.'
    isVerifying.value = false
    toast.error(errorMessage.value)
  }
})

// 모바일 리다이렉트 처리 (query parameter에서 user_id와 전화번호 받기)
onMounted(() => {
  const fromKcp = route.query.from_kcp
  const phone = route.query.phone as string
  const userIdParam = route.query.user_id as string

  if (fromKcp === 'true' && phone && userIdParam) {
    // 모바일에서 본인인증 완료 후 리다이렉트된 경우
    console.log('[Find-Password] KCP redirect received', { user_id: userIdParam, phone })
    userId.value = userIdParam
    findPassword({ user_id: userIdParam, phone })
  }
})

// 폼 제출 처리 (본인인증 시작)
const handleSubmit = async () => {
  if (!userId.value.trim() || isVerifying.value) return

  isVerifying.value = true
  errorMessage.value = ''
  successMessage.value = ''
  maskedEmail.value = ''

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
  console.log('[KCP] handleVerificationComplete called', result)

  // 팝업 닫기
  if (closePopup) {
    closePopup()
    closePopup = null
  }

  if (result.success && result.phone) {
    // 인증된 전화번호로 비밀번호 찾기 API 호출
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
