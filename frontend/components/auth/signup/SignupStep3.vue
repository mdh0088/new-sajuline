<template>
  <div class="form-section">
    <h2 class="section-title">생년월일시 입력</h2>
    <p class="section-subtitle">정확한 운세 분석을 위해 필요합니다</p>

    <div class="input-group">
      <label class="input-label">생년월일</label>
      <div class="date-picker-container">
        <el-date-picker
          v-model="birthDate"
          type="date"
          placeholder="생년월일을 선택해주세요"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledDate"
          :clearable="false"
          class="birth-date-picker custom-date-input"
          size="large"
          @change="handleBirthDateChange"
        />
      </div>
      <p v-if="validator.birthValidator.value.message" 
         class="validation-text" 
         :class="{ 
           'error-text': !validator.birthValidator.value.isValid,
           'success-text': validator.birthValidator.value.isValid && birthDate
         }">
        {{ validator.birthValidator.value.message }}
      </p>
    </div>

    <div class="input-group">
      <label class="input-label">태어난 시간 (선택)</label>
      <div class="time-input-container">
        <el-time-picker
          v-model="birthTime"
          placeholder="태어난 시간을 선택해주세요"
          format="HH:mm"
          value-format="HH:mm"
          class="birth-time-picker custom-date-input"
          size="large"
          @change="handleBirthTimeChange"
        />
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
const isStepValid = defineModel<boolean>('isStepValid', { default: false })

// Step3 자체 검증 로직
const { validateBirthDate } = useValidation()

// Element Plus DatePicker를 위한 로컬 상태
const birthDate = ref<string>('')
const birthTime = ref<string>('')

// birth_date 통합 처리 함수
const updateBirthDate = () => {
  if (birthDate.value) {
    // 날짜만 있는 경우: YYYY-MM-DD 00:00
    let dateTimeString = `${birthDate.value} 00:00`

    // 시간도 있는 경우: YYYY-MM-DD HH:MM
    if (birthTime.value) {
      dateTimeString = `${birthDate.value} ${birthTime.value}`
    }

    signupFormData.value.birth_date = dateTimeString
  } else {
    signupFormData.value.birth_date = ''
  }
}

// 초기값 설정 (기존 birth_date에서 날짜/시간 분리)
onMounted(() => {
  const existingBirthDate = signupFormData.value.birth_date
  if (existingBirthDate) {
    const parts = existingBirthDate.split(' ')
    if (parts.length >= 1 && parts[0]) {
      birthDate.value = parts[0] // YYYY-MM-DD 부분
    }
    if (parts.length >= 2 && parts[1] && parts[1] !== '00:00') {
      birthTime.value = parts[1] // HH:MM 부분 (00:00이 아닌 경우에만)
    }
  }
})

// 날짜 선택 핸들러
const handleBirthDateChange = (value: string) => {
  birthDate.value = value || ''
  updateBirthDate()
}

// 시간 선택 핸들러
const handleBirthTimeChange = (value: string) => {
  birthTime.value = value || ''
  updateBirthDate()
}

// 날짜 비활성화 함수 (1900년 이전, 미래 날짜 비활성화)
const disabledDate = (time: Date) => {
  const currentDate = new Date()
  const minDate = new Date('1900-01-01')
  return time.getTime() > currentDate.getTime() || time.getTime() < minDate.getTime()
}

// 생년월일 유효성 검증
const birthValidator = computed(() => {
  const birthDateValue = signupFormData.value.birth_date

  // 필수 필드 체크
  if (!birthDateValue || !birthDate.value) {
    return {
      isValid: false,
      message: '생년월일을 선택해주세요.'
    }
  }

  // 날짜 유효성 검증 (날짜 부분만 검증)
  return validateBirthDate(birthDate.value)
})

// Step3 종합 검증 결과
const validator = computed(() => ({
  birthValidator,
  isValid: birthValidator.value.isValid
}))

// 검증 상태를 부모로 전달
watch(() => validator.value.isValid, (valid) => {
  isStepValid.value = valid
}, { immediate: true })
</script>

<style>
@import '~/assets/css/common/signup-common.css';
@import '~/assets/css/signup/signup_step3.css';
</style>