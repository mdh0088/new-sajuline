<template>
  <div class="auth-container">
    <main class="auth-main">
      <div class="max-w-md mx-auto text-center">
        <div class="text-6xl mb-4">💬</div>
        <h2 class="text-2xl font-bold mb-4">카카오 로그인 중...</h2>
        <p class="text-white/60">잠시만 기다려주세요</p>

        <div v-if="error" class="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p class="text-red-400">{{ error }}</p>
          <button
            @click="goToLogin"
            class="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            로그인 페이지로 돌아가기
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useSocialAuthQueries, type SocialSignupRequired, type SocialLoginSuccess } from '~/composables/api/useSocialAuthQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { useToast } from '~/composables/ui/useToast'
import '~/assets/css/common/auth-common.css'

definePageMeta({
  layout: false
})

// SEO 메타 데이터 설정
useHead({
  title: '카카오 로그인 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { handleLoginSuccessWithRole } = useAuth()
const { useHandleSocialCallback } = useSocialAuthQueries()

const error = ref<string>('')

// OAuth 콜백 처리
const callbackMutation = useHandleSocialCallback({
  onSuccess: (data) => {
    // 타입 가드: SocialSignupRequired 체크
    if ('requires_signup' in data && data.requires_signup) {
      // 신규 사용자: 회원가입 페이지로 이동
      const signupData = data as SocialSignupRequired
      router.push({
        path: '/signup/social',
        query: {
          provider: signupData.provider,
          social_id: signupData.social_id,
          email: signupData.email || '',
          name: signupData.name || ''
        }
      })
    } else {
      // 기존 사용자: 자동 로그인 (쿠키 이미 설정됨)
      const loginData = data as SocialLoginSuccess
      handleLoginSuccessWithRole(loginData, 'user')
      toast.success('카카오 로그인 성공!')
      // 소셜 로그인은 현재 user만 지원하므로 user/mypage로 라우팅
      router.push('/user/mypage')
    }
  },
  onError: (err: any) => {
    error.value = err?.message || '카카오 로그인에 실패했습니다.'
    toast.error(error.value)
  }
})

// 컴포넌트 마운트 시 콜백 처리
onMounted(async () => {
  const code = route.query.code as string
  const state = route.query.state as string

  if (!code) {
    error.value = '인증 코드가 없습니다.'
    return
  }

  // 백엔드로 콜백 처리 요청
  await callbackMutation.mutateAsync({
    provider: 'kakao',
    code,
    state
  })
})

const goToLogin = () => {
  router.push('/login')
}
</script>
