<template>
  <div class="form-section">
    <h2 class="section-title">기본 정보 입력</h2>
    <p class="section-subtitle">서비스 이용에 필요한 정보를 입력해주세요</p>

    <div class="input-group">
      <label class="input-label">닉네임</label>
      <div class="input-wrapper">
        <input 
          v-model="signupFormData.nickname"
          type="text" 
          class="input-field" 
          placeholder="닉네임을 입력해주세요"
          :class="{ 
            error: !validator.nicknameValidator.result.value.isValid && signupFormData.name,
            success: validator.nicknameValidator.result.value.isValid && signupFormData.name
          }"
        >
        <span v-if="validator.nicknameValidator.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.nicknameValidator.result.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.nicknameValidator.result.value.isValid,
           'success-text': validator.nicknameValidator.result.value.isValid && signupFormData.nickname
         }">
        {{ validator.nicknameValidator.result.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">휴대폰 번호</label>
      <div class="input-with-button">
        <input 
          v-model="signupFormData.phone"
          type="tel" 
          class="input-field" 
          placeholder="01012345678"
          maxlength="11" 
          @input="handlePhoneInput"
          :class="{ 
            error: !validator.phoneValidator.result.value.isValid && signupFormData.phone,
            success: validator.phoneValidator.result.value.isValid && signupFormData.phone
          }"
        >
        <button type="button" class="verify-button" @click="sendVerificationCode">인증하기</button>
        <span v-if="validator.phoneValidator.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.phoneValidator.result.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.phoneValidator.result.value.isValid,
           'success-text': validator.phoneValidator.result.value.isValid && signupFormData.phone
         }">
        {{ validator.phoneValidator.result.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">성별</label>
      <div class="gender-select">
        <div 
          class="gender-option"
          :class="{ selected: signupFormData.gender === Gender.MALE }"
          @click="signupFormData.gender = Gender.MALE"
        >
          <div class="gender-icon">👨</div>
          <div class="gender-label">남성</div>
        </div>
        <div 
          class="gender-option"
          :class="{ selected: signupFormData.gender === Gender.FEMALE }"
          @click="signupFormData.gender = Gender.FEMALE"
        >
          <div class="gender-icon">👩</div>
          <div class="gender-label">여성</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupFormData } from '~/types/auth/signup'
import { Gender } from '~/types/user/models'
import { useValidation } from '~/composables/validation/useValidation'
import { useUserQueries } from '~/composables/api/useUserQueries'

// defineModel로 간단하게 처리
const signupFormData = defineModel<SignupFormData>('signupFormData', { required: true })

// Step2 자체 검증 로직
const { validateNickname, validatePhone } = useValidation()
const { useNicknameAvailability, usePhoneAvailability } = useUserQueries()

// 닉네임 중복 검사
const nicknameAvailabilityQuery = useNicknameAvailability(computed(() => signupFormData.value.nickname || ''), {
  enabled: computed(() => !!signupFormData.value.nickname && signupFormData.value.nickname.length >= 2)
})

// 휴대폰 중복 검사
const phoneAvailabilityQuery = usePhoneAvailability(computed(() => signupFormData.value.phone || ''), {
  enabled: computed(() => !!signupFormData.value.phone && /^010\d{8}$/.test(signupFormData.value.phone))
})

// 개별 필드 검증
const nicknameValidator = computed(() => validateNickname(signupFormData.value.nickname, nicknameAvailabilityQuery))
const phoneValidator = computed(() => validatePhone(signupFormData.value.phone, phoneAvailabilityQuery))

// Step2 종합 검증 결과
const validator = computed(() => ({
  nicknameValidator,
  phoneValidator,
  isValid: nicknameValidator.value.result.value.isValid && 
           phoneValidator.value.result.value.isValid
}))

// 휴대폰 번호 입력 처리
const handlePhoneInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  // 숫자만 허용하고 11자리로 제한
  let value = target.value.replace(/[^0-9]/g, '')
  if (value.length > 11) {
    value = value.slice(0, 11)
  }
  signupFormData.value.phone = value
}

// 인증번호 전송 (이 컴포넌트에서 직접 처리)
const sendVerificationCode = () => {
  // TODO: 휴대폰 인증 로직 구현
  console.log('인증번호 전송:', signupFormData.value.phone)
}

</script>