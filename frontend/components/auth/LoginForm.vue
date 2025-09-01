<template>
  <form @submit.prevent="handleSubmit" class="space-y-5">
    <!-- 사용자 ID -->
    <div>
      <label for="user_id" class="block text-sm font-medium text-white/80 mb-2">
        사용자 ID
      </label>
      <input
        id="user_id"
        type="text"
        placeholder="사용자 ID를 입력해주세요"
        autocomplete="username"
        class="auth-input"
      />
    </div>

    <!-- 비밀번호 -->
    <div>
      <label for="password" class="block text-sm font-medium text-white/80 mb-2">
        비밀번호
      </label>
      <div class="relative">
        <input
          id="password"
          type="password"
          placeholder="비밀번호를 입력해주세요"
          autocomplete="current-password"
          class="auth-input pr-12"
        />
        <button
          type="button"
          @click="togglePasswordVisibility"
          class="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-white/50 hover:text-white/70 transition-colors duration-300"
          aria-label="비밀번호 보기"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- 옵션 -->
    <div class="flex items-center justify-between py-2">
      <label class="flex items-center gap-3 cursor-pointer">
        <input
          id="remember-me"
          type="checkbox"
          class="auth-checkbox"
        />
        <span class="text-sm text-white/80">로그인 상태 유지</span>
      </label>
      
      <button
        type="button"
        @click="handleForgotPassword"
        class="text-sm text-purple-400 hover:text-purple-300 hover:underline transition-colors duration-300"
      >
        비밀번호 찾기
      </button>
    </div>

    <!-- 로그인 버튼 -->
    <button
      type="submit"
      class="w-full py-4 font-bold rounded-xl transition-all duration-300 auth-scale-98 flex items-center justify-center gap-2 auth-btn-primary"
    >
      로그인
    </button>
  </form>
</template>

<script setup lang="ts">
// Emits 정의
const emit = defineEmits<{
  submit: []
  forgotPassword: []
}>()

// 이벤트 핸들러
const handleSubmit = () => {
  console.log('로그인 폼 제출')
  emit('submit')
}

const handleForgotPassword = () => {
  console.log('비밀번호 찾기')
  emit('forgotPassword')
}

const togglePasswordVisibility = () => {
  console.log('비밀번호 표시/숨김')
}
</script>