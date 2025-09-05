<template>
  <div class="form-section">
    <h2 class="section-title">약관 동의</h2>
    <p class="section-subtitle">서비스 이용약관에 동의해주세요</p>

    <div class="terms-section">
      <div class="terms-all" @click="toggleAllTerms">
        <div class="checkbox" :class="{ checked: allTermsAgreed }"></div>
        <div class="terms-text">
          <strong>전체 동의</strong>
        </div>
      </div>

      <div class="terms-list">
        <div class="terms-item">
          <div 
            class="checkbox terms-check" 
            :class="{ checked: signupFormData.agreeService }"
            @click="signupFormData.agreeService = !signupFormData.agreeService"
          ></div>
          <div class="terms-text">
            서비스 이용약관 동의
            <span class="required-badge">(필수)</span>
          </div>
          <a href="#" class="terms-link" @click.prevent="openTermsModal('service')">보기</a>
        </div>

        <div class="terms-item">
          <div 
            class="checkbox terms-check" 
            :class="{ checked: signupFormData.agreePrivacy }"
            @click="signupFormData.agreePrivacy = !signupFormData.agreePrivacy"
          ></div>
          <div class="terms-text">
            개인정보 수집 및 이용 동의
            <span class="required-badge">(필수)</span>
          </div>
          <a href="#" class="terms-link" @click.prevent="openTermsModal('privacy')">보기</a>
        </div>

        <div class="terms-item">
          <div 
            class="checkbox terms-check" 
            :class="{ checked: signupFormData.agreeMarketing }"
            @click="signupFormData.agreeMarketing = !signupFormData.agreeMarketing"
          ></div>
          <div class="terms-text">
            마케팅 정보 수신 동의
            <span style="font-size: 12px; color: rgba(255,255,255,0.5);">(선택)</span>
          </div>
          <a href="#" class="terms-link" @click.prevent="openTermsModal('marketing')">보기</a>
        </div>
      </div>
      
      <!-- 필수 약관 동의 검증 메시지 -->
      <p v-if="validator.requiredTermsValidator.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.requiredTermsValidator.value.isValid,
           'success-text': validator.requiredTermsValidator.value.isValid
         }">
        {{ validator.requiredTermsValidator.value.message }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupFormData } from '~/types/auth/signup'

// defineModel로 간단하게 처리
const signupFormData = defineModel<SignupFormData>('signupFormData', { required: true })

// 이벤트 emit 정의
interface Emits {
  'open-terms': [type: string]
}
const emit = defineEmits<Emits>()

// 전체 약관 동의 여부
const allTermsAgreed = computed(() => {
  return signupFormData.value.agreeService && signupFormData.value.agreePrivacy && signupFormData.value.agreeMarketing
})

// 필수 약관 동의 검증
const requiredTermsValidator = computed(() => {
  const hasServiceAgree = signupFormData.value.agreeService
  const hasPrivacyAgree = signupFormData.value.agreePrivacy
  
  if (!hasServiceAgree || !hasPrivacyAgree) {
    return {
      isValid: false,
      message: '필수 약관에 동의해주세요.'
    }
  }
  
  return {
    isValid: true,
    message: '필수 약관 동의가 완료되었습니다.'
  }
})

// Step4 종합 검증 결과
const validator = computed(() => ({
  requiredTermsValidator,
  isValid: requiredTermsValidator.value.isValid
}))

const toggleAllTerms = () => {
  const newValue = !allTermsAgreed.value
  signupFormData.value.agreeService = newValue
  signupFormData.value.agreePrivacy = newValue
  signupFormData.value.agreeMarketing = newValue
}

const openTermsModal = (type: string) => {
  emit('open-terms', type)
}
</script>

<style>
@import '~/assets/css/signup/common.css';
@import '~/assets/css/signup/signup_step4.css';
</style>