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
            :class="{ checked: localForm.agreeService }"
            @click="localForm.agreeService = !localForm.agreeService"
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
            :class="{ checked: localForm.agreePrivacy }"
            @click="localForm.agreePrivacy = !localForm.agreePrivacy"
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
            :class="{ checked: localForm.agreeMarketing }"
            @click="localForm.agreeMarketing = !localForm.agreeMarketing"
          ></div>
          <div class="terms-text">
            마케팅 정보 수신 동의
            <span style="font-size: 12px; color: rgba(255,255,255,0.5);">(선택)</span>
          </div>
          <a href="#" class="terms-link" @click.prevent="openTermsModal('marketing')">보기</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupStepProps, SignupStep4Emits } from '~/types/auth/signup'

const props = defineProps<SignupStepProps>()
const emit = defineEmits<SignupStep4Emits>()

// 로컬 폼 데이터 (양방향 바인딩)
const localForm = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value)
})

// 전체 약관 동의 여부
const allTermsAgreed = computed(() => {
  return localForm.value.agreeService && localForm.value.agreePrivacy && localForm.value.agreeMarketing
})

const toggleAllTerms = () => {
  const newValue = !allTermsAgreed.value
  const updatedForm = {
    ...localForm.value,
    agreeService: newValue,
    agreePrivacy: newValue,
    agreeMarketing: newValue
  }
  emit('update:form', updatedForm)
}

const openTermsModal = (type: string) => {
  emit('open-terms', type)
}
</script>