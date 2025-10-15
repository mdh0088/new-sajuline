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
            아이디와 휴대폰 번호를 입력하시면<br />
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
              required
            />
          </div>

          <!-- 휴대폰 번호 입력 -->
          <div>
            <label class="block text-sm font-medium text-white/80 mb-2">
              휴대폰 번호
            </label>
            <input
              v-model="phoneNumber"
              type="tel"
              placeholder="010-0000-0000"
              class="auth-input"
              required
            />
            <p class="mt-2 text-xs text-white/50">
              가입 시 등록한 휴대폰 번호를 입력해주세요
            </p>
          </div>

          <!-- 안내 메시지 -->
          <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
            <div class="flex items-start gap-3">
              <div class="text-xl">💡</div>
              <div class="text-sm text-white/70 leading-relaxed">
                <p class="font-semibold mb-1">임시 비밀번호 안내</p>
                <ul class="space-y-1 text-xs">
                  <li>• 임시 비밀번호는 SMS로 발송됩니다</li>
                  <li>• 로그인 후 반드시 비밀번호를 변경해주세요</li>
                  <li>• 임시 비밀번호는 24시간 동안 유효합니다</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 제출 버튼 -->
          <button
            type="submit"
            :disabled="!isFormValid || isLoading"
            class="w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-98 shadow-lg shadow-purple-500/25 disabled:shadow-none"
          >
            <span v-if="!isLoading">임시 비밀번호 발송</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              처리중...
            </span>
          </button>
        </form>

        <!-- 성공 메시지 (발송 완료 후 표시) -->
        <div v-if="isSuccess" class="mt-6 p-6 bg-green-500/10 border border-green-500/30 rounded-xl">
          <div class="text-center">
            <div class="text-3xl mb-3">✅</div>
            <h3 class="text-lg font-semibold mb-2">임시 비밀번호 발송 완료</h3>
            <p class="text-white/70 text-sm leading-relaxed">
              입력하신 휴대폰 번호로<br />
              임시 비밀번호가 발송되었습니다<br />
              <span class="text-purple-400 font-medium">{{ maskedPhoneNumber }}</span>
            </p>
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
// 인증 도메인 CSS 로드
import '~/assets/css/common/auth-common.css'

definePageMeta({
  layout: 'default'
})

// SEO 및 메타 데이터 설정
useHead({
  title: '비밀번호 찾기 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 비밀번호 찾기. 아이디와 휴대폰 번호로 임시 비밀번호를 받으실 수 있습니다.' },
    { property: 'og:title', content: '비밀번호 찾기 - 사주라인' },
    { property: 'og:description', content: '사주라인 비밀번호 찾기. 아이디와 휴대폰 번호로 임시 비밀번호를 받으실 수 있습니다.' },
  ],
})

// 상태 관리
const userId = ref('')
const phoneNumber = ref('')
const isLoading = ref(false)
const isSuccess = ref(false)

// 폼 유효성 검사
const isFormValid = computed(() => {
  return userId.value.trim().length > 0 && phoneNumber.value.trim().length > 0
})

// 마스킹된 휴대폰 번호
const maskedPhoneNumber = computed(() => {
  if (!phoneNumber.value) return ''
  const cleaned = phoneNumber.value.replace(/[^0-9]/g, '')
  if (cleaned.length < 8) return phoneNumber.value
  return cleaned.slice(0, 3) + '****' + cleaned.slice(-4)
})

// 폼 제출 처리 (추후 구현 예정)
const handleSubmit = async () => {
  if (!isFormValid.value || isLoading.value) return

  isLoading.value = true

  try {
    console.log('임시 비밀번호 발송 요청:', {
      userId: userId.value,
      phoneNumber: phoneNumber.value
    })

    // TODO: API 연동
    // await sendTemporaryPassword({ user_id: userId.value, phone: phoneNumber.value })

    // 임시 성공 처리 (실제로는 API 응답 후)
    await new Promise(resolve => setTimeout(resolve, 1500))
    isSuccess.value = true
  } catch (error) {
    console.error('임시 비밀번호 발송 실패:', error)
    // TODO: 에러 처리
  } finally {
    isLoading.value = false
  }
}
</script>
