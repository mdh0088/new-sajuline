<template>
  <div class="form-section">
    <h2 class="section-title">계정 정보 입력</h2>
    <p class="section-subtitle">로그인에 사용할 정보를 입력해주세요</p>

    <div class="input-group">
      <label class="input-label">사용자 ID</label>
      <div class="input-wrapper">
        <input 
          v-model="signupFormData.user_id"
          type="text" 
          class="input-field" 
          placeholder="4-20자 영문, 숫자, 밑줄(_) 조합 (이메일 형식 불가)"
        >
        <span v-if="validator.userIdValidator.value.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p class="help-text">영문, 숫자, 밑줄(_)만 사용 가능하며, 이메일 형식은 사용할 수 없습니다</p>
      <p v-if="validator.userIdValidator.value.result.value.message && signupFormData.user_id"
         class="validation-text"
         :class="{
           'error-text': !validator.userIdValidator.value.result.value.isValid,
           'success-text': validator.userIdValidator.value.result.value.isValid && signupFormData.user_id
         }">
        {{ validator.userIdValidator.value.result.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">이메일</label>
      <div class="input-wrapper">
        <input 
          v-model="signupFormData.email"
          type="email" 
          class="input-field" 
          placeholder="example@email.com"
        >
        <span v-if="validator.emailValidator.value.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.emailValidator.value.result.value.message && signupFormData.email"
         class="validation-text"
         :class="{
           'error-text': !validator.emailValidator.value.result.value.isValid,
           'success-text': validator.emailValidator.value.result.value.isValid && signupFormData.email
         }">
        {{ validator.emailValidator.value.result.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">비밀번호</label>
      <div class="input-wrapper">
        <input 
          v-model="signupFormData.password"
          type="password" 
          class="input-field" 
          placeholder="8자 이상 영문, 숫자, 특수문자 포함"
        >
      </div>
      
      <!-- 비밀번호 강도 표시 -->
      <div v-if="signupFormData.password" class="password-strength">
        <div class="strength-bar">
          <div 
            class="strength-fill" 
            :class="`strength-${validator.passwordValidator.value.passwordStrength.value.score}`"
            :style="`width: ${(validator.passwordValidator.value.passwordStrength.value.score / 4) * 100}%`"
          ></div>
        </div>
        <p class="strength-text">
          강도: 
          <span :class="`strength-${validator.passwordValidator.value.passwordStrength.value.score}`">
            {{ ['매우 약함', '약함', '보통', '강함', '매우 강함'][validator.passwordValidator.value.passwordStrength.value.score] }}
          </span>
        </p>
      </div>
      
      <p class="help-text">영문, 숫자, 특수문자를 포함해 8자 이상 입력해주세요</p>
      <p v-if="validator.passwordValidator.value.passwordResult.value.message && signupFormData.password"
         class="validation-text"
         :class="{
           'error-text': !validator.passwordValidator.value.passwordResult.value.isValid,
           'success-text': validator.passwordValidator.value.passwordResult.value.isValid && signupFormData.password
         }">
        {{ validator.passwordValidator.value.passwordResult.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">비밀번호 확인</label>
      <div class="input-wrapper">
        <input 
          v-model="signupFormData.confirmPassword"
          type="password" 
          class="input-field" 
          placeholder="비밀번호를 다시 입력해주세요"
        >
      </div>
      <p v-if="validator.passwordValidator.value.confirmResult.value.message && signupFormData.confirmPassword"
         class="validation-text"
         :class="{
           'error-text': !validator.passwordValidator.value.confirmResult.value.isValid,
           'success-text': validator.passwordValidator.value.confirmResult.value.isValid && signupFormData.confirmPassword
         }">
        {{ validator.passwordValidator.value.confirmResult.value.message }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupFormData } from '~/types/auth/signup'
import { useValidation } from '~/composables/validation/useValidation'
import { useUserQueries } from '~/composables/api/useUserQueries'

// defineModel로 간단하게 처리
const signupFormData = defineModel<SignupFormData>('signupFormData', { required: true })
const isStepValid = defineModel<boolean>('isStepValid', { default: false })

// Step1 자체 검증 로직
const { validateEmail, validateUserId, validatePassword } = useValidation()
const { useEmailAvailability, useUserIdAvailability } = useUserQueries()

// 중복 검사 쿼리들
const emailAvailabilityQuery = useEmailAvailability(computed(() => signupFormData.value.email || ''), {
  enabled: computed(() => !!signupFormData.value.email && signupFormData.value.email.includes('@'))
})

const userIdAvailabilityQuery = useUserIdAvailability(computed(() => signupFormData.value.user_id || ''), {
  enabled: computed(() => !!signupFormData.value.user_id && signupFormData.value.user_id.length >= 4)
})

// 개별 필드 검증
const userIdValidator = computed(() => validateUserId(signupFormData.value.user_id, userIdAvailabilityQuery))
const emailValidator = computed(() => validateEmail(signupFormData.value.email, emailAvailabilityQuery))
const passwordValidator = computed(() => validatePassword(signupFormData.value.password, signupFormData.value.confirmPassword))

// Step1 종합 검증 결과
const validator = computed(() => ({
  userIdValidator,
  emailValidator,
  passwordValidator,
  isValid: userIdValidator.value.result.value.isValid &&
           emailValidator.value.result.value.isValid &&
           passwordValidator.value.passwordResult.value.isValid &&
           passwordValidator.value.confirmResult.value.isValid
}))

// 검증 상태를 부모로 전달
watch(() => validator.value.isValid, (valid) => {
  isStepValid.value = valid
}, { immediate: true })
</script>

<style>
@import '~/assets/css/common/signup-common.css';
@import '~/assets/css/signup/signup_step1.css';
</style>