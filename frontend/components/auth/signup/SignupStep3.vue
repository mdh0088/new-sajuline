<template>
  <div class="form-section">
    <h2 class="section-title">생년월일시 입력</h2>
    <p class="section-subtitle">정확한 운세 분석을 위해 필요합니다</p>

    <div class="input-group">
      <label class="input-label">생년월일</label>
      <div class="birth-input">
        <input 
          v-model.number="signupFormData.birthYear"
          type="number" 
          class="input-field birth-field" 
          placeholder="1990" 
          min="1900" 
          max="2025"
        >
        <span class="birth-unit">년</span>
        <input 
          v-model.number="signupFormData.birthMonth"
          type="number" 
          class="input-field birth-field" 
          placeholder="1" 
          min="1" 
          max="12"
        >
        <span class="birth-unit">월</span>
        <input 
          v-model.number="signupFormData.birthDay"
          type="number" 
          class="input-field birth-field" 
          placeholder="1" 
          min="1" 
          max="31"
        >
        <span class="birth-unit">일</span>
      </div>
      <p v-if="validator.birthValidator.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.birthValidator.value.isValid,
           'success-text': validator.birthValidator.value.isValid && birthDateString
         }">
        {{ validator.birthValidator.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">태어난 시간 (선택)</label>
      <div class="birth-input">
        <input 
          v-model.number="signupFormData.birthHour"
          type="number" 
          class="input-field birth-field" 
          placeholder="14" 
          min="0" 
          max="23"
        >
        <span class="birth-unit">시</span>
        <input 
          v-model.number="signupFormData.birthMinute"
          type="number" 
          class="input-field birth-field" 
          placeholder="30" 
          min="0" 
          max="59"
        >
        <span class="birth-unit">분</span>
      </div>
      <p class="help-text">모르시는 경우 입력하지 않으셔도 됩니다</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupFormData } from '~/types/auth/signup'
import { useValidation } from '~/composables/validation/useValidation'

// defineModel로 간단하게 처리
const signupFormData = defineModel<SignupFormData>('signupFormData', { required: true })

// Step3 자체 검증 로직
const { validateBirthDate } = useValidation()

// 생년월일 조합 및 검증
const birthDateString = computed(() => {
  const { birthYear, birthMonth, birthDay } = signupFormData.value
  if (birthYear && birthMonth && birthDay) {
    const year = birthYear.toString().padStart(4, '0')
    const month = birthMonth.toString().padStart(2, '0')
    const day = birthDay.toString().padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  return ''
})

// 생년월일 유효성 검증
const birthValidator = computed(() => {
  const { birthYear, birthMonth, birthDay } = signupFormData.value
  
  // 필수 필드 체크
  if (!birthYear || !birthMonth || !birthDay) {
    return {
      isValid: false,
      message: '생년월일을 모두 입력해주세요.'
    }
  }
  
  // 날짜 유효성 검증
  return validateBirthDate(birthDateString.value)
})

// Step3 종합 검증 결과
const validator = computed(() => ({
  birthValidator,
  isValid: birthValidator.value.isValid
}))
</script>