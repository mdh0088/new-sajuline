<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- 로고 및 제목 -->
      <div class="text-center">
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          상담사 로그인
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          사주라인 상담사 전용 관리 페이지 접속
        </p>
        <div class="mt-4 flex justify-center">
          <div class="w-16 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"></div>
        </div>
      </div>

      <!-- 로그인 폼 -->
      <form @submit.prevent="handleLogin" class="mt-8 space-y-6 bg-white p-8 rounded-xl shadow-lg">
        <div class="space-y-4">
          <!-- 이메일 입력 -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              이메일 주소
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                autocomplete="email"
                :class="[
                  'pl-10 mt-1 appearance-none rounded-lg relative block w-full px-3 py-3 border',
                  'placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2',
                  'focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm transition-colors',
                  emailError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                ]"
                placeholder="예: counselor@example.com"
                @blur="validateEmail"
                @input="emailError = ''"
              />
            </div>
            <!-- 이메일 에러 메시지 -->
            <p v-if="emailError" class="mt-2 text-sm text-red-600 flex items-center">
              <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              {{ emailError }}
            </p>
          </div>

          <!-- 비밀번호 입력 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              비밀번호
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                autocomplete="current-password"
                :class="[
                  'pl-10 mt-1 appearance-none rounded-lg relative block w-full px-3 py-3 border',
                  'placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2',
                  'focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm transition-colors',
                  passwordError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                ]"
                placeholder="비밀번호를 입력하세요"
                @blur="validatePassword"
                @input="passwordError = ''"
              />
            </div>
            <!-- 비밀번호 에러 메시지 -->
            <p v-if="passwordError" class="mt-2 text-sm text-red-600 flex items-center">
              <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              {{ passwordError }}
            </p>
          </div>
        </div>

        <!-- 전체 에러 메시지 -->
        <div v-if="counselorStore.error" class="rounded-lg bg-red-50 p-4 border border-red-200">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                로그인 실패
              </h3>
              <p class="mt-1 text-sm text-red-700">
                {{ counselorStore.error }}
              </p>
            </div>
          </div>
        </div>

        <!-- 로그인 버튼 -->
        <div>
          <button
            type="submit"
            :disabled="counselorStore.loading || !isFormValid"
            :class="[
              'group relative w-full flex justify-center py-3 px-4 border border-transparent',
              'text-sm font-medium rounded-lg text-white focus:outline-none focus:ring-2',
              'focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200',
              counselorStore.loading || !isFormValid
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
            ]"
          >
            <!-- 로딩 스피너 -->
            <svg
              v-if="counselorStore.loading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            {{ counselorStore.loading ? '로그인 중...' : '로그인' }}
          </button>
        </div>

        <!-- 링크 -->
        <div class="text-center space-y-2 pt-4 border-t border-gray-100">
          <p class="text-sm text-gray-600">
            일반 사용자이신가요?
            <NuxtLink to="/login" class="font-medium text-purple-600 hover:text-purple-500 transition-colors">
              일반 로그인
            </NuxtLink>
          </p>
          <p class="text-xs text-gray-500">
            상담사 계정이 없으시다면 관리자에게 문의하세요.
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useCounselorStore } from '~/stores/counselor'

// SEO 설정
useHead({
  title: '상담사 로그인 - 사주라인',
  meta: [
    {
      name: 'description',
      content: '사주라인 상담사 전용 로그인 페이지입니다. 이메일과 비밀번호로 로그인하세요.'
    }
  ]
})

// Pinia 스토어
const counselorStore = useCounselorStore()

// 라우터
const router = useRouter()

// 폼 상태
const form = reactive({
  email: '',
  password: ''
})

// 유효성 검사 에러
const emailError = ref('')
const passwordError = ref('')

// 이메일 유효성 검사
function validateEmail() {
  emailError.value = ''
  
  if (!form.email) {
    emailError.value = '이메일을 입력해주세요.'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    emailError.value = '올바른 이메일 형식을 입력해주세요.'
    return false
  }
  
  return true
}

// 비밀번호 유효성 검사
function validatePassword() {
  passwordError.value = ''
  
  if (!form.password) {
    passwordError.value = '비밀번호를 입력해주세요.'
    return false
  }
  
  if (form.password.length < 1) {
    passwordError.value = '비밀번호를 입력해주세요.'
    return false
  }
  
  return true
}

// 폼 전체 유효성 검사
const isFormValid = computed(() => {
  return form.email && 
         form.password && 
         !emailError.value && 
         !passwordError.value
})

// 로그인 처리
async function handleLogin() {
  // 에러 초기화
  counselorStore.clearError()
  
  // 유효성 검사
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  
  if (!isEmailValid || !isPasswordValid) {
    return
  }

  try {
    const result = await counselorStore.login(form.email, form.password)
    
    if (result.success) {
      // 로그인 성공 시 상담사 마이페이지로 이동
      await router.push('/counselor/mypage')
    }
    // 실패한 경우 에러는 스토어에서 자동으로 처리됨
  } catch (error) {
    console.error('Login error:', error)
  }
}

// 컴포넌트 마운트 시 기존 세션 확인
onMounted(async () => {
  // 이미 로그인된 상태라면 마이페이지로 리다이렉트
  if (counselorStore.isAuthenticated) {
    await router.push('/counselor/mypage')
    return
  }
  
  // 저장된 토큰으로 세션 복원 시도
  const restored = await counselorStore.restoreSession()
  if (restored) {
    await router.push('/counselor/mypage')
  }
})
</script>