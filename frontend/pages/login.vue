<template>
  <div class="auth-container">
    <!-- 메인 콘텐츠 -->
    <main class="auth-main">
      <div class="max-w-md mx-auto">
        <!-- 히어로 섹션 -->
        <div class="text-center mb-10">
          <div class="text-6xl mb-4">🔮</div>
          <h2 class="text-3xl font-bold mb-3">다시 만나서 반가워요!</h2>
          <p class="text-white/70 text-base">
            로그인하여 개인화된 운세와<br />
            전문 상담사 서비스를 이용하세요
          </p>
        </div>

        <!-- 성공 메시지 -->
        <div class="mb-6" style="display: none;">
          <div class="auth-success-message">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                성공 메시지
              </div>
              <button class="text-green-200 hover:text-green-100 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 일반 에러 메시지 -->
        <div class="mb-6" style="display: none;">
          <div class="auth-error-message">
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              에러 메시지
            </div>
          </div>
        </div>

        <!-- 소셜 로그인 컴포넌트 -->
        <div class="mb-8">
          <LoginForm
            @success="handleLoginSuccess"
            @forgot-password="handleForgotPassword"
          />
        </div>

        <!-- 구분선 -->
        <div class="flex items-center gap-4 my-8">
          <div class="flex-1 h-px bg-white/10"></div>
          <span class="text-white/50 text-sm">또는 간편 로그인</span>
          <div class="flex-1 h-px bg-white/10"></div>
        </div>

        <!-- 소셜 로그인 버튼 -->
        <SocialLogin />

        <!-- 아이디/비밀번호 찾기 링크 -->
        <div class="flex items-center justify-center gap-4 mt-6">
          <NuxtLink
            to="/user/find-id"
            class="text-white/60 hover:text-white/90 text-sm transition-colors"
          >
            아이디 찾기
          </NuxtLink>
          <div class="w-px h-3 bg-white/20"></div>
          <NuxtLink
            to="/user/find-password"
            class="text-white/60 hover:text-white/90 text-sm transition-colors"
          >
            비밀번호 찾기
          </NuxtLink>
        </div>

        <!-- 회원가입 링크 -->
        <div class="text-center mt-6">
          <p class="text-white/60 text-sm">
            아직 계정이 없으신가요?
            <NuxtLink to="/signup" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
              회원가입하기
            </NuxtLink>
          </p>
        </div>

        <!-- 게스트 모드 -->
        <div class="text-center mt-6 pt-6 border-t border-white/10">
          <div class="inline-flex items-center gap-2 text-white/40 text-sm">
            <span>✨</span>
            회원가입 없이 AI 운세 체험하기 (준비중)
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
// 인증 도메인 CSS 로드
import '~/assets/css/common/auth-common.css'
import { useAuth } from '~/composables/auth/useAuth'

// SEO 및 메타 데이터 설정
useHead({
  title: '로그인 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
    { property: 'og:title', content: '로그인 - 사주라인' },
    { property: 'og:description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
    { name: 'robots', content: 'noindex,nofollow' }
  ],
})

// 뒤로가기
const goBack = () => {
  navigateTo('/')
}

// 로그인 성공 처리 (역할 기반 라우팅)
const route = useRoute()
const { isAuthenticated, role } = useAuth()

// 이미 로그인된 사용자가 접근하면 자동 리다이렉트
onMounted(() => {
  if (isAuthenticated.value) {
    console.log('🔐 [login.vue] Already logged in, redirecting...')

    // redirect 쿼리가 있으면 우선 사용
    const redirectQuery = route.query.redirect as string
    if (redirectQuery) {
      console.log('🎯 [login.vue] Redirecting to query redirect:', redirectQuery)
      // ✅ 강제 새로고침으로 페이지 이동
      window.location.href = redirectQuery
      return
    }

    // 역할에 따라 자동 라우팅
    const currentRole = role.value
    if (currentRole === 'counselor') {
      console.log('👨‍💼 [login.vue] Redirecting logged-in counselor to mypage')
      // ✅ 강제 새로고침으로 페이지 이동
      window.location.href = '/counselor/mypage'
    } else {
      console.log('👤 [login.vue] Redirecting logged-in user to mypage')
      // ✅ 강제 새로고침으로 페이지 이동
      window.location.href = '/user/mypage'
    }
  }
})

const handleLoginSuccess = () => {
  console.log('🎉 [login.vue] handleLoginSuccess called - LOGIN SUCCESS!')

  // redirect 쿼리가 있으면 우선 사용
  const redirectQuery = route.query.redirect as string

  if (redirectQuery) {
    console.log('🎯 [login.vue] Redirecting to query redirect:', redirectQuery)
    // ✅ 강제 새로고침으로 페이지 이동
    window.location.href = redirectQuery
    return
  }

  // redirect 쿼리가 없으면 역할(role)에 따라 자동 라우팅
  const currentRole = role.value
  console.log('🔍 [login.vue] Current role:', currentRole)

  if (currentRole === 'counselor') {
    console.log('👨‍💼 [login.vue] Redirecting to counselor mypage with page reload')
    // ✅ 강제 새로고침으로 페이지 이동
    window.location.href = '/counselor/mypage'
  } else {
    console.log('👤 [login.vue] Redirecting to user mypage with page reload')
    // ✅ 강제 새로고침으로 페이지 이동
    window.location.href = '/user/mypage'
  }
}

// 비밀번호 찾기
const handleForgotPassword = () => {
  console.log('비밀번호 찾기')
}
</script>