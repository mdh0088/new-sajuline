<template>
  <div class="form-section">
    <h2 class="section-title">기본 정보 입력</h2>
    <p class="section-subtitle">서비스 이용에 필요한 정보를 입력해주세요</p>

    <div class="input-group">
      <label class="input-label">이름</label>
      <div class="input-wrapper">
        <input 
          v-model="localForm.name"
          type="text" 
          class="input-field" 
          placeholder="실명을 입력해주세요"
          :class="{ 
            error: !props.validator?.nicknameValidator?.result?.value?.isValid && localForm.name,
            success: props.validator?.nicknameValidator?.result?.value?.isValid && localForm.name
          }"
        >
      </div>
      <p v-if="props.validator?.nicknameValidator?.result?.value?.message" 
         class="validation-text"
         :class="{ 
           'error-text': !props.validator?.nicknameValidator?.result?.value?.isValid,
           'success-text': props.validator?.nicknameValidator?.result?.value?.isValid && localForm.name
         }">
        {{ props.validator?.nicknameValidator?.result?.value?.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">휴대폰 번호</label>
      <div class="input-with-button">
        <input 
          v-model="localForm.phone"
          type="tel" 
          class="input-field" 
          placeholder="010-0000-0000"
          maxlength="13" 
          @input="handlePhoneInput"
          :class="{ 
            error: !props.validator?.phoneValidator?.result?.value?.isValid && localForm.phone,
            success: props.validator?.phoneValidator?.result?.value?.isValid && localForm.phone
          }"
        >
        <button type="button" class="verify-button" @click="sendVerificationCode">인증하기</button>
      </div>
      <p v-if="props.validator?.phoneValidator?.result?.value?.message" 
         class="validation-text"
         :class="{ 
           'error-text': !props.validator?.phoneValidator?.result?.value?.isValid,
           'success-text': props.validator?.phoneValidator?.result?.value?.isValid && localForm.phone
         }">
        {{ props.validator?.phoneValidator?.result?.value?.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">성별</label>
      <div class="gender-select">
        <div 
          class="gender-option"
          :class="{ selected: localForm.gender === Gender.MALE }"
          @click="localForm.gender = Gender.MALE"
        >
          <div class="gender-icon">👨</div>
          <div class="gender-label">남성</div>
        </div>
        <div 
          class="gender-option"
          :class="{ selected: localForm.gender === Gender.FEMALE }"
          @click="localForm.gender = Gender.FEMALE"
        >
          <div class="gender-icon">👩</div>
          <div class="gender-label">여성</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SignupStepProps, SignupStep2Emits } from '~/types/auth/signup'
import { Gender } from '~/types/user/models'

const props = defineProps<SignupStepProps>()
const emit = defineEmits<SignupStep2Emits>()

// 로컬 폼 데이터 (양방향 바인딩)
const localForm = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value)
})

// 휴대폰 번호 입력 처리
const handlePhoneInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  // 숫자만 허용하고 11자리로 제한
  let value = target.value.replace(/[^0-9]/g, '')
  if (value.length > 11) {
    value = value.slice(0, 11)
  }
  const updatedForm = { ...localForm.value, phone: value }
  emit('update:form', updatedForm)
}

// 인증번호 전송
const sendVerificationCode = () => {
  emit('send-verification')
}

</script>