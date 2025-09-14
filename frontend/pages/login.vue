<template>
  <div class="auth-container">
    <!-- 헤더 -->
    <header class="auth-header">
      <div class="flex justify-between items-center px-5 py-4 h-15">
        <button 
          @click="goBack"
          class="w-9 h-9 bg-transparent hover:bg-white/10 rounded-xl flex items-center justify-center text-xl transition-all duration-300 active:scale-95"
          aria-label="뒤로가기"
        >
          ←
        </button>
        
        <h1 class="absolute left-1/2 transform -translate-x-1/2 text-lg font-semibold">
          로그인
        </h1>
        
        <div class="w-9"></div> <!-- 헤더 균형 맞추기 -->
      </div>
    </header>

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
          <SocialLogin 
            @kakao-login="handleKakaoLogin"
            @naver-login="handleNaverLogin" 
            @google-login="handleGoogleLogin"
          />
        </div>

        <!-- 구분선 -->
        <div class="flex items-center gap-4 my-8">
          <div class="flex-1 h-px bg-white/10"></div>
          <span class="text-white/50 text-sm">또는 사용자 ID로 로그인</span>
          <div class="flex-1 h-px bg-white/10"></div>
        </div>

        <!-- 로그인 폼 컴포넌트 -->
        <LoginForm 
          @success="handleLoginSuccess"
          @forgot-password="handleForgotPassword"
        />

        <!-- 회원가입 링크 -->
        <div class="text-center mt-8">
          <p class="text-white/60 text-sm">
            아직 계정이 없으신가요?
            <NuxtLink to="/signup" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
              회원가입하기
            </NuxtLink>
          </p>
        </div>

        <!-- 게스트 모드 -->
        <div class="text-center mt-6 pt-6 border-t border-white/10">
          <NuxtLink 
            to="/fortune" 
            class="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm hover:underline transition-colors duration-300"
          >
            <span>✨</span>
            회원가입 없이 AI 운세 체험하기
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// 인증 도메인 CSS 로드
import '~/assets/css/login/common.css'

// SEO 및 메타 데이터 설정
useHead({
  title: '로그인 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
    { property: 'og:title', content: '로그인 - 사주라인' },
    { property: 'og:description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
  ],
})

// 뒤로가기
const goBack = () => {
  navigateTo('/')
}

// 로그인 성공 처리 (redirect 쿼리 지원)
const route = useRoute()
const handleLoginSuccess = () => {
  const redirect = (route.query.redirect as string) || '/'
  navigateTo(redirect)
}

// 소셜 로그인 핸들러들
const handleKakaoLogin = async () => {
  console.log('카카오 로그인')
}

const handleNaverLogin = async () => {
  console.log('네이버 로그인')
}

const handleGoogleLogin = async () => {
  console.log('구글 로그인')
}

// 비밀번호 찾기
const handleForgotPassword = () => {
  console.log('비밀번호 찾기')
}
</script>