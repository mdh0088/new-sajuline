<template>
  <div class="auth-container">
    <!-- 메인 콘텐츠 -->
    <main class="auth-main">
      <div class="max-w-md mx-auto">
        <!-- 히어로 섹션 -->
        <div class="text-center mb-10">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-3xl font-bold mb-3">아이디 찾기</h2>
          <p class="text-white/70 text-base">
            본인인증을 통해<br />
            가입하신 아이디를 찾아드립니다
          </p>
        </div>

        <!-- 본인인증 안내 -->
        <div class="mb-8 p-6 bg-white/5 border border-white/10 rounded-xl">
          <div class="flex items-start gap-3 mb-4">
            <div class="text-2xl">📱</div>
            <div>
              <h3 class="text-lg font-semibold mb-2">휴대폰 본인인증</h3>
              <p class="text-white/60 text-sm leading-relaxed">
                휴대폰 본인인증을 진행하시면<br />
                해당 번호로 가입된 아이디를 확인하실 수 있습니다
              </p>
            </div>
          </div>

          <!-- 본인인증 버튼 -->
          <button
            type="button"
            class="w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-98 shadow-lg shadow-purple-500/25"
            :disabled="isVerifying"
            @click="startVerification"
          >
            <span v-if="!isVerifying">휴대폰 본인인증 하기</span>
            <span v-else>인증 진행 중...</span>
          </button>
        </div>

        <!-- 결과 표시 영역 (본인인증 후 표시) -->
        <div v-if="foundUserId" class="mb-8 p-6 bg-green-500/10 border border-green-500/30 rounded-xl">
          <div class="text-center">
            <div class="text-3xl mb-3">✅</div>
            <h3 class="text-lg font-semibold mb-3">아이디를 찾았습니다</h3>
            <div class="p-4 bg-white/5 rounded-lg mb-4">
              <p class="text-2xl font-bold text-purple-400">{{ foundUserId }}</p>
            </div>
            <p class="text-white/60 text-sm">
              가입일: {{ foundUserDate }}
            </p>
          </div>
        </div>

        <!-- 에러 메시지 표시 -->
        <div v-if="errorMessage" class="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <div class="flex items-center gap-2 text-red-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- 하단 링크 -->
        <div class="space-y-4">
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

          <!-- 비밀번호 찾기 링크 -->
          <div class="text-center pt-4 border-t border-white/10">
            <p class="text-white/60 text-sm">
              비밀번호를 잊으셨나요?
              <NuxtLink to="/user/find-password" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
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
onMounted(() => {
  const fromKcp = route.query.from_kcp
  const phone = route.query.phone as string

  if (fromKcp === 'true' && phone) {
    // 모바일에서 본인인증 완료 후 리다이렉트된 경우
    console.log('[Find-ID] KCP redirect received', phone)
    findUserId(phone)
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
