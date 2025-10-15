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
  </div>
</template>

<script setup lang="ts">
import { useSocialAuthQueries } from '~/composables/api/useSocialAuthQueries'
import { useToast } from '~/composables/ui/useToast'

// Emits 정의
const emit = defineEmits<{
  kakaoLogin: []
  naverLogin: []
  googleLogin: []
}>()

const toast = useToast()
const { useGetSocialAuthURL } = useSocialAuthQueries()

// Kakao OAuth URL 쿼리
const kakaoProvider = ref<'kakao'>('kakao')
const kakaoAuthQuery = useGetSocialAuthURL(kakaoProvider, {
  enabled: false // 수동 호출
})

// Naver OAuth URL 쿼리
const naverProvider = ref<'naver'>('naver')
const naverAuthQuery = useGetSocialAuthURL(naverProvider, {
  enabled: false // 수동 호출
})

// 이벤트 핸들러
const handleKakaoLogin = async () => {
  emit('kakaoLogin')
  try {
    // OAuth URL 생성 및 리다이렉트
    const result = await kakaoAuthQuery.refetch()
    if (result.data) {
      window.location.href = result.data.authorization_url
    }
  } catch (error: any) {
    toast.error(error?.message || '카카오 로그인 URL 생성 실패')
  }
}

const handleNaverLogin = async () => {
  emit('naverLogin')
  try {
    // OAuth URL 생성 및 리다이렉트
    const result = await naverAuthQuery.refetch()
    if (result.data) {
      window.location.href = result.data.authorization_url
    }
  } catch (error: any) {
    toast.error(error?.message || '네이버 로그인 URL 생성 실패')
  }
}

const handleGoogleLogin = () => {
  console.log('구글 로그인')
  emit('googleLogin')
  toast.info('구글 로그인은 준비 중입니다.')
}
</script>

<style>
@import '~/assets/css/common/auth-common.css';
</style>