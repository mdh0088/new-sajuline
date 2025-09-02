<template>
  <div class="form-section">
    <h2 class="section-title">계정 정보 입력</h2>
    <p class="section-subtitle">로그인에 사용할 정보를 입력해주세요</p>

    <div class="input-group">
      <label class="input-label">이메일</label>
      <div class="input-wrapper">
        <input 
          v-model="localForm.email"
          type="email" 
          class="input-field" 
          placeholder="example@email.com"
          :class="{ 
            error: !validator.emailValidator.result.value.isValid && localForm.email,
            success: validator.emailValidator.result.value.isValid && localForm.email
          }"
          @input="validator.emailValidator.update"
        >
        <span v-if="validator.emailValidator.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.emailValidator.result.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.emailValidator.result.value.isValid,
           'success-text': validator.emailValidator.result.value.isValid && localForm.email
         }">
        {{ validator.emailValidator.result.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">비밀번호</label>
      <div class="input-wrapper">
        <input 
          v-model="localForm.password"
          type="password" 
          class="input-field" 
          placeholder="8자 이상 영문, 숫자, 특수문자 포함"
          :class="{ 
            error: !validator.passwordValidator.passwordResult.value.isValid && localForm.password,
            success: validator.passwordValidator.passwordResult.value.isValid && localForm.password
          }"
          @input="validator.passwordValidator.updatePassword"
        >
      </div>
      
      <!-- 비밀번호 강도 표시 -->
      <div v-if="localForm.password" class="password-strength">
        <div class="strength-bar">
          <div 
            class="strength-fill" 
            :class="`strength-${validator.passwordValidator.passwordStrength.value.score}`"
            :style="`width: ${(validator.passwordValidator.passwordStrength.value.score / 4) * 100}%`"
          ></div>
        </div>
        <p class="strength-text">
          강도: 
          <span :class="`strength-${validator.passwordValidator.passwordStrength.value.score}`">
            {{ ['매우 약함', '약함', '보통', '강함', '매우 강함'][validator.passwordValidator.passwordStrength.value.score] }}
          </span>
        </p>
      </div>
      
      <p class="help-text">영문, 숫자, 특수문자를 포함해 8자 이상 입력해주세요</p>
      <p v-if="validator.passwordValidator.passwordResult.value.message" 
         class="validation-text"
         :class="{ 
           'error-text': !validator.passwordValidator.passwordResult.value.isValid,
           'success-text': validator.passwordValidator.passwordResult.value.isValid && localForm.password
         }">
        {{ validator.passwordValidator.passwordResult.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">비밀번호 확인</label>
      <div class="input-wrapper">
        <input 
          v-model="localForm.confirmPassword"
          type="password" 
          class="input-field" 
          placeholder="비밀번호를 다시 입력해주세요"
          :class="{ 
            error: !validator.passwordValidator.confirmResult.value.isValid && localForm.confirmPassword,
            success: validator.passwordValidator.confirmResult.value.isValid && localForm.confirmPassword
          }"
          @input="validator.passwordValidator.updateConfirmPassword"
        >
      </div>
      <p v-if="validator.passwordValidator.confirmResult.value.message" 
         class="validation-text"
         :class="{ 
           'error-text': !validator.passwordValidator.confirmResult.value.isValid,
           'success-text': validator.passwordValidator.confirmResult.value.isValid && localForm.confirmPassword
         }">
        {{ validator.passwordValidator.confirmResult.value.message }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupStepProps, SignupStep1Emits } from '~/types/auth/signup'

const props = defineProps<SignupStepProps>()
const emit = defineEmits<SignupStep1Emits>()

// 로컬 폼 데이터 (양방향 바인딩)
const localForm = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value)
})
</script>