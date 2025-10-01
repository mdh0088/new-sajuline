<template>
  <div class="space-y-3">
    <button
      @click="handleKakaoLogin"
      class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 auth-scale-98 border social-btn-kakao"
      aria-label="카카오로 로그인"
    >
      <span class="text-xl">💬</span>
      <span>카카오로 로그인</span>
    </button>
    
    <button
      @click="handleNaverLogin"
      class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 auth-scale-98 border social-btn-naver"
      aria-label="네이버로 로그인"
    >
      <span class="text-xl font-bold">N</span>
      <span>네이버로 로그인</span>
    </button>

    <button
      @click="handleGoogleLogin"
      class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 auth-scale-98 border border-white/10 bg-white/5 text-white hover:bg-white/8"
      aria-label="구글로 로그인"
    >
      <span class="text-xl">G</span>
      <span>구글로 로그인</span>
    </button>
  </div>
</template>

<script setup lang="ts">
// Emits 정의
const emit = defineEmits<{
  kakaoLogin: []
  naverLogin: []
  googleLogin: []
}>()

// 이벤트 핸들러
const handleKakaoLogin = () => {
  console.log('카카오 로그인')
  emit('kakaoLogin')
}

const handleNaverLogin = () => {
  console.log('네이버 로그인')
  emit('naverLogin')
}

const handleGoogleLogin = () => {
  console.log('구글 로그인')
  emit('googleLogin')
}
</script>

<style>
@import '~/assets/css/common/auth-common.css';
</style>