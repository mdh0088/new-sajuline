<template>
  <div class="form-section">
    <h2 class="section-title">기본 정보 입력</h2>
    <p class="section-subtitle">서비스 이용에 필요한 정보를 입력해주세요</p>

    <!-- 이메일 입력 (SignupStep1에서 가져옴) -->
    <div class="input-group">
      <label class="input-label">이메일</label>
      <div class="input-wrapper">
        <input
          v-model="signupFormData.email"
          type="email"
          class="input-field"
          placeholder="example@email.com"
          :class="{
            error: !validator.emailValidator.value.result.value.isValid && signupFormData.email,
            success: validator.emailValidator.value.result.value.isValid && signupFormData.email
          }"
        >
        <span v-if="validator.emailValidator.value.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.emailValidator.value.result.value.message"
         class="validation-text"
         :class="{
           'error-text': !validator.emailValidator.value.result.value.isValid,
           'success-text': validator.emailValidator.value.result.value.isValid && signupFormData.email
         }">
        {{ validator.emailValidator.value.result.value.message }}
      </p>
    </div>

    <!-- 닉네임 입력 -->
    <div class="input-group">
      <label class="input-label">닉네임</label>
      <div class="input-wrapper">
        <input
          v-model="signupFormData.nickname"
          type="text"
          class="input-field"
          placeholder="닉네임을 입력해주세요"
          :class="{
            error: !validator.nicknameValidator.value.result.value.isValid && signupFormData.nickname,
            success: validator.nicknameValidator.value.result.value.isValid && signupFormData.nickname
          }"
        >
        <span v-if="validator.nicknameValidator.value.result.value.isChecking" class="checking-indicator">확인 중...</span>
      </div>
      <p v-if="validator.nicknameValidator.value.result.value.message"
         class="validation-text"
         :class="{
           'error-text': !validator.nicknameValidator.value.result.value.isValid,
           'success-text': validator.nicknameValidator.value.result.value.isValid && signupFormData.nickname
         }">
        {{ validator.nicknameValidator.value.result.value.message }}
      </p>
    </div>

    <!-- 휴대폰 본인인증 -->
    <PhoneVerification
      v-model="signupFormData.phone"
      v-model:phoneChk="signupFormData.phone_chk"
      :name="signupFormData.name"
      :birthDate="signupFormData.birth_date"
      :gender="convertGenderForKCP(signupFormData.gender)"
      @verified="handlePhoneVerified"
    />

    <!-- 성별 선택 -->
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
import type { PhoneVerificationResult } from '~/composables/api/usePhoneVerification'
import { Gender } from '~/types/user/models'
import { useValidation } from '~/composables/validation/useValidation'
import { useUserQueries } from '~/composables/api/useUserQueries'
import PhoneVerification from '~/components/auth/PhoneVerification.vue'

// defineModel로 간단하게 처리
const signupFormData = defineModel<SignupFormData>('signupFormData', { required: true })

// 검증 로직 (이메일 + 닉네임)
const { validateEmail, validateNickname } = useValidation()
const { useEmailAvailability, useNicknameAvailability } = useUserQueries()

// 이메일 중복 검사
const emailAvailabilityQuery = useEmailAvailability(computed(() => signupFormData.value.email || ''), {
  enabled: computed(() => !!signupFormData.value.email && signupFormData.value.email.includes('@'))
})

// 닉네임 중복 검사
const nicknameAvailabilityQuery = useNicknameAvailability(computed(() => signupFormData.value.nickname || ''), {
  enabled: computed(() => !!signupFormData.value.nickname && signupFormData.value.nickname.length >= 2)
})

// 개별 필드 검증
const emailValidator = computed(() => validateEmail(signupFormData.value.email, emailAvailabilityQuery))
const nicknameValidator = computed(() => validateNickname(signupFormData.value.nickname, nicknameAvailabilityQuery))

// 종합 검증 결과
const validator = computed(() => ({
  emailValidator,
  nicknameValidator,
  isValid: emailValidator.value.result.value.isValid &&
           nicknameValidator.value.result.value.isValid &&
           !!signupFormData.value.phone_chk
}))

// Gender enum을 KCP 형식으로 변환
const convertGenderForKCP = (gender: Gender): 'M' | 'F' => {
  return gender === Gender.MALE ? 'M' : 'F'
}

// 휴대폰 인증 완료 핸들러
const handlePhoneVerified = (result: PhoneVerificationResult) => {
  // v-model:phoneChk가 자동으로 업데이트되므로 추가 처리 불필요
  // 필요한 경우 추가 로직 작성 가능
}
</script>

<style>
@import '~/assets/css/common/signup-common.css';
@import '~/assets/css/signup/signup_step2.css';
</style>
