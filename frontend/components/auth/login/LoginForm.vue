<template>
  <form @submit.prevent="handleSubmit" class="space-y-5">
    <!-- 사용자 ID -->
    <div>
      <label for="user_id" class="block text-sm font-medium text-white/80 mb-2">
        사용자 ID
      </label>
      <el-input
        id="user_id"
        v-model="formData.user_id"
        type="text"
        placeholder="사용자 ID 또는 이메일을 입력해주세요"
        autocomplete="username"
        class="auth-input-wrapper"
        :class="{ 'error': errors.user_id }"
        @input="clearError('user_id')"
      />
      <p v-if="errors.user_id" class="text-red-400 text-sm mt-1">{{ errors.user_id }}</p>
    </div>

    <!-- 비밀번호 -->
    <div>
      <label for="password" class="block text-sm font-medium text-white/80 mb-2">
        비밀번호
      </label>
      <el-input
        id="password"
        v-model="formData.password"
        type="password"
        placeholder="비밀번호를 입력해주세요"
        autocomplete="current-password"
        show-password
        class="auth-input-wrapper"
        :class="{ 'error': errors.password }"
        @input="clearError('password')"
      />
      <p v-if="errors.password" class="text-red-400 text-sm mt-1">{{ errors.password }}</p>
    </div>

    <!-- 일반 에러 메시지 -->
    <div v-if="errors.general" class="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
      <p class="text-red-400 text-sm">{{ errors.general }}</p>
    </div>

    <!-- 옵션 -->
    <div class="flex items-center justify-between py-2">
      <el-checkbox v-model="formData.rememberMe" class="auth-checkbox-wrapper">
        로그인 상태 유지
      </el-checkbox>
      
      <button
        type="button"
        @click="handleForgotPassword"
        class="text-sm text-purple-400 hover:text-purple-300 hover:underline transition-colors duration-300"
      >
        비밀번호 찾기
      </button>
    </div>

    <!-- 로그인 버튼 -->
    <el-button
      type="primary"
      :loading="isLoading"
      native-type="submit"
      class="w-full py-4 font-bold rounded-xl auth-btn-primary"
    >
      <Icon v-if="!isLoading" name="mdi:login" class="w-5 h-5" />
      {{ isLoading ? '로그인 중...' : '로그인' }}
    </el-button>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useValidation } from '~/composables/validation/useValidation'
import type { LoginRequest } from '~/types/user/models'

// Emits 정의
const emit = defineEmits<{
  success: []
  forgotPassword: []
}>()

// 컴포저블
const { login, isLoginLoading } = useAuth()
const { validateRequired, validateMinLength, validateEmailFormat } = useValidation()

// 반응형 데이터
const formData = reactive<LoginRequest & { rememberMe: boolean }>({
  user_id: '',
  password: '',
  rememberMe: false
})

const errors = reactive<Record<string, string>>({
  user_id: '',
  password: '',
  general: ''
})

const isLoading = computed(() => isLoginLoading.value)

// 유효성 검증
const validateForm = (): boolean => {
  // 에러 초기화
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  let isValid = true

  // 사용자 ID 검증
  if (!validateRequired(formData.user_id)) {
    errors.user_id = '사용자 ID 또는 이메일을 입력해주세요.'
    isValid = false
  } else if (formData.user_id.includes('@')) {
    // 이메일 형식 검증
    if (!validateEmailFormat(formData.user_id)) {
      errors.user_id = '올바른 이메일 형식을 입력해주세요.'
      isValid = false
    }
  } else {
    // 사용자 ID 검증
    if (!validateMinLength(formData.user_id, 4)) {
      errors.user_id = '사용자 ID는 4자 이상 입력해주세요.'
      isValid = false
    }
  }

  // 비밀번호 검증
  if (!validateRequired(formData.password)) {
    errors.password = '비밀번호를 입력해주세요.'
    isValid = false
  } else if (!validateMinLength(formData.password, 6)) {
    errors.password = '비밀번호는 6자 이상 입력해주세요.'
    isValid = false
  }

  return isValid
}

// 에러 클리어
const clearError = (field: string) => {
  if (errors[field]) {
    errors[field] = ''
  }
  if (errors.general) {
    errors.general = ''
  }
}

// 로그인 제출
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    const result = await login({
      user_id: formData.user_id,
      password: formData.password
    })

    if (result.success) {
      // 로그인 성공
      emit('success')
    } else {
      // 로그인 실패
      errors.general = result.error || '로그인에 실패했습니다.'
    }
  } catch (error: any) {
    errors.general = error?.message || '로그인 중 오류가 발생했습니다.'
  }
}

// 비밀번호 찾기
const handleForgotPassword = () => {
  emit('forgotPassword')
}
</script>

<style>
@import '~/assets/css/common/auth-common.css';
</style>