<template>
  <div class="form-section">
    <h2 class="section-title">생년월일시 입력</h2>
    <p class="section-subtitle">정확한 운세 분석을 위해 필요합니다</p>

    <div class="input-group">
      <label class="input-label">생년월일</label>
      <div class="birth-input">
        <input 
          v-model.number="localForm.birthYear"
          type="number" 
          class="input-field birth-field" 
          placeholder="1990" 
          min="1900" 
          max="2025"
        >
        <span class="birth-unit">년</span>
        <input 
          v-model.number="localForm.birthMonth"
          type="number" 
          class="input-field birth-field" 
          placeholder="1" 
          min="1" 
          max="12"
        >
        <span class="birth-unit">월</span>
        <input 
          v-model.number="localForm.birthDay"
          type="number" 
          class="input-field birth-field" 
          placeholder="1" 
          min="1" 
          max="31"
        >
        <span class="birth-unit">일</span>
      </div>
    </div>

    <div class="input-group">
      <label class="input-label">태어난 시간 (선택)</label>
      <div class="birth-input">
        <input 
          v-model.number="localForm.birthHour"
          type="number" 
          class="input-field birth-field" 
          placeholder="14" 
          min="0" 
          max="23"
        >
        <span class="birth-unit">시</span>
        <input 
          v-model.number="localForm.birthMinute"
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
import type { SignupStepProps, SignupStep3Emits } from '~/types/auth/signup'

const props = defineProps<SignupStepProps>()
const emit = defineEmits<SignupStep3Emits>()

// 로컬 폼 데이터 (양방향 바인딩)
const localForm = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value)
})
</script>