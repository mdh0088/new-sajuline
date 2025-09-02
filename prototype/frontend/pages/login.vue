<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
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
    <main class="pt-16 pb-8 px-5 overflow-y-auto">
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
        <div v-if="successMessage" class="mb-6">
          <div class="bg-green-500/20 border border-green-500/50 text-green-200 px-4 py-3 rounded-xl">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ successMessage }}
              </div>
              <button 
                @click="successMessage = ''"
                class="text-green-200 hover:text-green-100 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 일반 에러 메시지 -->
        <div v-if="errors.general" class="mb-6">
          <div class="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-xl">
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ errors.general }}
            </div>
          </div>
        </div>

        <!-- 소셜 로그인 -->
        <div class="space-y-3 mb-8">
          <button
            @click="handleKakaoLogin"
            class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 active:scale-[0.98] border"
            style="background-color: #FEE500; color: #000000; border-color: #FEE500;"
            @mouseenter="(e) => (e.target as HTMLElement).style.backgroundColor = '#FDD835'"
            @mouseleave="(e) => (e.target as HTMLElement).style.backgroundColor = '#FEE500'"
            aria-label="카카오로 로그인"
          >
            <span class="text-xl">💬</span>
            <span>카카오로 로그인</span>
          </button>
          
            <button
              @click="handleNaverLogin"
            class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 active:scale-[0.98] border text-white"
            style="background-color: #03C75A; border-color: #03C75A;"
            @mouseenter="(e) => (e.target as HTMLElement).style.backgroundColor = '#02B351'"
            @mouseleave="(e) => (e.target as HTMLElement).style.backgroundColor = '#03C75A'"
              aria-label="네이버로 로그인"
            >
            <span class="text-xl font-bold">N</span>
            <span>네이버로 로그인</span>
            </button>

            <button
              @click="handleGoogleLogin"
            class="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-medium transition-all duration-300 active:scale-[0.98] border border-white/10 bg-white/5 text-white hover:bg-white/8"
              aria-label="구글로 로그인"
            >
            <span class="text-xl">G</span>
            <span>구글로 로그인</span>
            </button>
        </div>

        <!-- 구분선 -->
        <div class="flex items-center gap-4 my-8">
          <div class="flex-1 h-px bg-white/10"></div>
          <span class="text-white/50 text-sm">또는 사용자 ID로 로그인</span>
          <div class="flex-1 h-px bg-white/10"></div>
        </div>

        <!-- 로그인 폼 -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- 사용자 ID -->
          <div>
            <label for="user_id" class="block text-sm font-medium text-white/80 mb-2">
              사용자 ID
            </label>
            <input
              id="user_id"
              v-model="formData.user_id"
              @blur="validateField('user_id')"
              @input="validateField('user_id')"
              type="text"
              placeholder="사용자 ID를 입력해주세요"
              autocomplete="username"
              :class="[
                'w-full bg-white/5 border rounded-xl px-4 py-4 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                errors.user_id ? 'border-red-500' : 'border-white/10'
              ]"
              :aria-invalid="!!errors.user_id"
              :aria-describedby="errors.user_id ? 'user_id-error' : undefined"
            />
            <p v-if="errors.user_id" id="user_id-error" class="text-red-400 text-sm mt-1" role="alert">
              {{ errors.user_id }}
            </p>
          </div>

          <!-- 비밀번호 -->
          <div>
            <label for="password" class="block text-sm font-medium text-white/80 mb-2">
              비밀번호
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="formData.password"
                @blur="validateField('password')"
                @input="validateField('password')"
                :type="showPassword ? 'text' : 'password'"
                placeholder="비밀번호를 입력해주세요"
                autocomplete="current-password"
                :class="[
                  'w-full bg-white/5 border rounded-xl px-4 py-4 pr-12 text-base text-white placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/8 transition-all duration-300',
                  errors.password ? 'border-red-500' : 'border-white/10'
                ]"
                :aria-invalid="!!errors.password"
                :aria-describedby="errors.password ? 'password-error' : undefined"
              />
              <button
                type="button"
                @click="togglePasswordVisibility"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-white/50 hover:text-white/70 transition-colors duration-300"
                :aria-label="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" id="password-error" class="text-red-400 text-sm mt-1" role="alert">
              {{ errors.password }}
            </p>
          </div>

          <!-- 옵션 -->
          <div class="flex items-center justify-between py-2">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                id="remember-me"
                v-model="formData.rememberMe"
                type="checkbox"
                class="w-5 h-5 rounded border-2 border-white/30 bg-transparent text-purple-600 focus:ring-purple-500 focus:ring-2 focus:ring-offset-0"
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
            :disabled="!isFormValid || isLoading"
            :class="[
              'w-full py-4 font-bold rounded-xl transition-all duration-300 active:scale-98 flex items-center justify-center gap-2',
              isFormValid && !isLoading
                ? 'bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white shadow-lg shadow-purple-500/25' 
                : 'bg-white/10 text-white/50 cursor-not-allowed'
            ]"
          >
            <svg v-if="isLoading" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ isLoading ? '로그인 중...' : '로그인' }}
          </button>
        </form>

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
            to="/ai-fortune" 
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
// SEO 및 메타 데이터 설정
useHead({
  title: '로그인 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
    { property: 'og:title', content: '로그인 - 사주라인' },
    { property: 'og:description', content: '사주라인 로그인. 사용자 ID와 비밀번호로 로그인하여 AI 운세와 전문 상담사 서비스를 이용하세요.' },
  ],
})

// 반응형 상태 관리
const formData = reactive({
  user_id: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  user_id: '',
  password: '',
  general: ''
})

const isLoading = ref(false)
const showPassword = ref(false)

// URL 쿼리 파라미터에서 메시지 확인
const route = useRoute()
const successMessage = ref('')

// 페이지 로드 시 쿼리 파라미터 확인
onMounted(() => {
  if (route.query.message === 'signup_success') {
    successMessage.value = '회원가입이 완료되었습니다! 로그인해주세요.'
    if (route.query.user_id) {
      formData.user_id = route.query.user_id as string
    }
  } else if (route.query.message === 'social_signup_success') {
    successMessage.value = '소셜 회원가입이 완료되었습니다! 로그인해주세요.'
  }
  
  // 성공 메시지가 있으면 7초 후 자동 숨김
  if (successMessage.value) {
    setTimeout(() => {
      successMessage.value = ''
    }, 7000)
  }
})

// 유효성 검사 함수들
const validateUserIdLocal = (userId: string): string => {
  if (!userId.trim()) return '사용자 ID를 입력해주세요'
  if (userId.trim().length < 4) return '사용자 ID는 4자 이상 입력해주세요'
  if (userId.trim().length > 20) return '사용자 ID는 20자 이하로 입력해주세요'
  const userIdRegex = /^[a-zA-Z0-9_-]+$/
  if (!userIdRegex.test(userId.trim())) return '사용자 ID는 영문, 숫자, 언더스코어(_), 하이픈(-)만 사용할 수 있습니다'
  if (!/^[a-zA-Z]/.test(userId.trim())) return '사용자 ID는 영문으로 시작해야 합니다'
  return ''
}

const validatePassword = (password: string): string => {
  if (!password) return '비밀번호를 입력해주세요'
  if (password.length < 8) return '비밀번호는 8자 이상이어야 합니다'
  return ''
}

// 실시간 유효성 검사
const validateField = (field: keyof typeof formData) => {
  switch (field) {
    case 'user_id':
      errors.user_id = validateUserIdLocal(formData.user_id)
      break
    case 'password':
      errors.password = validatePassword(formData.password)
      break
  }
  // 일반 에러 클리어
  if (errors.general) errors.general = ''
}

// 폼 유효성 검사
const isFormValid = computed(() => {
  return formData.user_id && 
         !errors.user_id && 
         formData.password && 
         !errors.password
})

// 뒤로가기
const goBack = () => {
  navigateTo('/')
}

// 로그인 처리
const handleLogin = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  errors.general = ''
  
  try {
    // 환경 변수에서 API Base URL 가져오기
    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase
    console.log('[Login] Using baseURL:', baseURL)
    const response = await $fetch(`${baseURL}/api/v1/auth/login`, {
      method: 'POST',
      credentials: 'include',
      body: {
        user_id: formData.user_id,
        password: formData.password,
        remember_me: formData.rememberMe
      }
    })
    
    // 공통 래퍼 해제
    const payload = response?.data || response
    
    // 토큰을 안전하게 저장
    const { setAccessToken } = useAuthToken()
    setAccessToken(payload.tokens.access_token, payload.tokens.expires_in || 1800)
    
    // 사용자 정보는 Pinia store에 저장
    const userStore = useUserStore()
    userStore.setUser(payload.user)
    
    // 성공 시 성공 메시지와 함께 메인 페이지로 이동
    await navigateTo('/?message=login_success')
    
  } catch (error: any) {
    console.error('로그인 실패:', error)
    
    // 에러 메시지 처리
    if (error.data?.detail) {
      errors.general = error.data.detail
    } else if (error.status === 401) {
      errors.general = '사용자 ID 또는 비밀번호가 올바르지 않습니다'
    } else if (error.status === 403) {
      errors.general = '비활성화된 계정입니다. 고객센터에 문의해주세요'
    } else if (error.status >= 500) {
      errors.general = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요'
    } else {
      errors.general = '로그인 중 문제가 발생했습니다. 다시 시도해주세요'
    }
  } finally {
    isLoading.value = false
  }
}

// 소셜 로그인 핸들러들
const handleKakaoLogin = async () => {
  try {
    isLoading.value = true
    errors.general = ''
    
    // 소셜 로그인 실행 (모바일/데스크톱 자동 선택)
    const { executeSocialLogin, handleSocialLoginResult, getSocialLoginErrorMessage } = await import('~/utils/social-login')
    
    const result = await executeSocialLogin('kakao')
    const processedResult = handleSocialLoginResult(result)
    
    if (processedResult.action === 'login_complete') {
      // 기존 사용자 로그인 완료 → 홈으로 이동
      await navigateTo('/?message=social_login_success')
    } else if (processedResult.action === 'redirect_to_signup') {
      // 신규 사용자 → 일반 회원가입 페이지로 이동
      await navigateTo('/signup?social=true')
    } else if (processedResult.action === 'additional_info_required') {
      // 레거시 액션 처리 (일반 회원가입 페이지로 리다이렉트)
      await navigateTo('/signup?social=true')
    } else if (processedResult.action === 'signup_required') {
      // 레거시 액션 처리 (일반 회원가입 페이지로 리다이렉트)
      await navigateTo('/signup?social=true')
    } else {
      throw new Error(processedResult.message)
    }
    
  } catch (error: any) {
    console.error('카카오 로그인 오류:', error)
    
    if (!error.message.includes('Redirecting')) {
      const { getSocialLoginErrorMessage } = await import('~/utils/social-login')
      const errorMessage = getSocialLoginErrorMessage(error)
      errors.general = errorMessage
    }
  } finally {
    isLoading.value = false
  }
}

const handleNaverLogin = async () => {
  try {
    isLoading.value = true
    errors.general = ''
    
    // 소셜 로그인 실행 (모바일/데스크톱 자동 선택)
    const { executeSocialLogin, handleSocialLoginResult, getSocialLoginErrorMessage } = await import('~/utils/social-login')
    
    const result = await executeSocialLogin('naver')
    const processedResult = handleSocialLoginResult(result)
    
    if (processedResult.action === 'login_complete') {
      // 기존 사용자 로그인 완료 → 홈으로 이동
      await navigateTo('/?message=social_login_success')
    } else if (processedResult.action === 'redirect_to_signup') {
      // 신규 사용자 → 일반 회원가입 페이지로 이동
      await navigateTo('/signup?social=true')
    } else if (processedResult.action === 'additional_info_required') {
      // 레거시 액션 처리 (일반 회원가입 페이지로 리다이렉트)
      await navigateTo('/signup?social=true')
    } else if (processedResult.action === 'signup_required') {
      // 레거시 액션 처리 (일반 회원가입 페이지로 리다이렉트)
      await navigateTo('/signup?social=true')
    } else {
      throw new Error(processedResult.message)
    }
    
  } catch (error: any) {
    console.error('네이버 로그인 오류:', error)
    
    if (!error.message.includes('Redirecting')) {
      const { getSocialLoginErrorMessage } = await import('~/utils/social-login')
      const errorMessage = getSocialLoginErrorMessage(error)
      errors.general = errorMessage
    }
  } finally {
    isLoading.value = false
  }
}

const handleGoogleLogin = async () => {
  // Google 소셜 로그인은 추후 구현
  errors.general = '구글 로그인은 준비 중입니다. 카카오 또는 네이버를 이용해주세요.'
}

// 비밀번호 찾기
const handleForgotPassword = () => {
  console.log('비밀번호 찾기')
}

// 비밀번호 표시/숨김 토글
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}
</script>

<style scoped>
/* 커스텀 체크박스 스타일 */
input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  background-color: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

input[type="checkbox"]:checked {
  background-color: rgb(147, 51, 234);
  border-color: rgb(147, 51, 234);
}

input[type="checkbox"]:checked::after {
  content: '✓';
  color: white;
  font-size: 14px;
  font-weight: bold;
}

input[type="checkbox"]:focus {
  box-shadow: 0 0 0 2px rgba(147, 51, 234, 0.5);
}

/* 애니메이션 */
.active\:scale-98:active {
  transform: scale(0.98);
}
</style> 