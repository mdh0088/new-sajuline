<template>
  <div class="phone-verification">
    <!-- 휴대폰 번호 입력 -->
    <div class="input-group">
      <label class="input-label">휴대폰 번호</label>
      <div class="input-with-button">
        <input
          v-model="phoneNumber"
          type="tel"
          class="input-field"
          placeholder="01012345678"
          maxlength="11"
          :disabled="isVerified"
          @input="handlePhoneInput"
          :class="{
            error: !isPhoneValid && phoneNumber,
            success: isVerified
          }"
        >
        <button
          type="button"
          class="verify-button"
          :disabled="!canStartVerification || isVerifying"
          @click="startVerification"
        >
          {{ isVerified ? '인증완료' : isVerifying ? '인증 중...' : '인증하기' }}
        </button>
      </div>
      <p v-if="errorMessage" class="validation-text error-text">
        {{ errorMessage }}
      </p>
      <p v-else-if="isVerified" class="validation-text success-text">
        휴대폰 인증이 완료되었습니다
      </p>
      <p v-else-if="phoneNumber && !isPhoneValid" class="validation-text error-text">
        010으로 시작하는 11자리 번호를 입력해주세요
      </p>
      <p v-else-if="phoneNumber && isPhoneValid && phoneAvailabilityQuery.isFetching.value" class="validation-text">
        확인 중...
      </p>
      <p v-else-if="phoneNumber && isPhoneValid && !isPhoneAvailable" class="validation-text error-text">
        이미 사용 중인 휴대폰 번호입니다
      </p>
      <p v-else-if="phoneNumber && isPhoneValid && isPhoneAvailable" class="validation-text success-text">
        사용 가능한 휴대폰 번호입니다
      </p>
    </div>

    <!-- 인증 모달 (PC 팝업 대체용 - 선택사항) -->
    <teleport to="body">
      <div v-if="showVerificationModal" class="verification-modal-overlay" @click="closeVerificationModal">
        <div class="verification-modal" @click.stop>
          <div class="modal-header">
            <h3>휴대폰 본인인증</h3>
            <button class="close-button" @click="closeVerificationModal">×</button>
          </div>
          <iframe
            name="kcp_cert_iframe"
            class="verification-iframe"
            frameborder="0"
          ></iframe>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '~/composables/ui/useToast'
import { useUserQueries } from '~/composables/api/useUserQueries'
import {
  usePhoneVerification,
  type PhoneVerificationResult
} from '~/composables/api/usePhoneVerification'

// Props & Emits
interface Props {
  modelValue?: string // v-model: phone
  phoneChk?: boolean // v-model:phoneChk (휴대폰 인증 완료 여부)
  verifiedPhone?: string // v-model:verifiedPhone (KCP 인증한 번호)
  useModal?: boolean // true: 모달 사용, false: 팝업 사용 (기본값)
  returnUrl?: string // Mobile Fallback 리다이렉트 URL (기본값: /signup)
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  phoneChk: false,
  verifiedPhone: '',
  useModal: false,
  returnUrl: '/signup'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:phoneChk': [value: boolean]
  'update:verifiedPhone': [value: string]  // KCP 인증 번호 emit
  'verified': [result: PhoneVerificationResult]
}>()

// Composables
const toast = useToast()
const { useInitiateVerification, setupPostMessageListener, openVerificationWindow } = usePhoneVerification()
const { usePhoneAvailability } = useUserQueries()

// State
const phoneNumber = ref(props.modelValue)
const verifiedPhoneNumber = ref('') // 인증 완료된 전화번호 저장
const errorMessage = ref('')
const isVerifying = ref(false)
const isVerified = ref(false)
const showVerificationModal = ref(false)
const gatewayUrl = ref('')
let closePopup: (() => void) | null = null
let cleanupListener: (() => void) | null = null

// 휴대폰 중복 검사
const phoneAvailabilityQuery = usePhoneAvailability(computed(() => phoneNumber.value || ''), {
  enabled: computed(() => !!phoneNumber.value && /^010\d{8}$/.test(phoneNumber.value))
})

// Computed
const isPhoneValid = computed(() => {
  return /^010\d{8}$/.test(phoneNumber.value)
})

const isPhoneAvailable = computed(() => {
  if (!isPhoneValid.value) return false
  if (phoneAvailabilityQuery.data.value === undefined) return false
  return phoneAvailabilityQuery.data.value === true
})

const canStartVerification = computed(() => {
  return isPhoneValid.value && isPhoneAvailable.value && !isVerified.value
})

// Watch modelValue 변경
watch(() => props.modelValue, (newVal) => {
  phoneNumber.value = newVal
})

// Watch phoneNumber 변경 - 전화번호 변경 시 인증 상태 초기화
watch(phoneNumber, (newVal, oldVal) => {
  emit('update:modelValue', newVal)

  // 인증 완료 상태에서 전화번호가 변경되면 인증 초기화
  if (isVerified.value && verifiedPhoneNumber.value && newVal !== verifiedPhoneNumber.value) {
    isVerified.value = false
    emit('update:phoneChk', false)
    errorMessage.value = '전화번호가 변경되었습니다. 다시 인증해주세요.'
  }
})

// Mutation
const verificationMutation = useInitiateVerification({
  onSuccess: (data) => {
    gatewayUrl.value = data.gateway_url

    // postMessage 리스너 설정
    cleanupListener = setupPostMessageListener(handleVerificationComplete)

    // 인증창 열기
    if (props.useModal) {
      // 모달 사용 (Form POST 방식)
      showVerificationModal.value = true
      // 모달이 열린 후 Form 제출 (nextTick 사용)
      nextTick(() => {
        submitFormToModal(data.gateway_url, data.form_data)
      })
    } else {
      // 팝업 사용 (Form POST 방식)
      try {
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
        closePopup = openVerificationWindow(data.gateway_url, data.form_data, isMobile)
      } catch (error: any) {
        toast.error(error.message || '인증창을 열 수 없습니다')
        isVerifying.value = false
      }
    }
  },
  onError: (error: any) => {
    isVerifying.value = false
    errorMessage.value = error?.message || '인증 시작에 실패했습니다'
    toast.error(errorMessage.value)
  }
})

// Methods
const submitFormToModal = (gatewayUrl: string, formData: Record<string, string>) => {
  console.log('[KCP] submitFormToModal called', { gatewayUrl, formData })

  // 기존 form 제거 (중복 방지)
  const existingForm = document.getElementById('kcp_modal_form')
  if (existingForm) {
    console.log('[KCP] Removing existing form')
    existingForm.remove()
  }

  // Form 요소 생성
  const form = document.createElement('form')
  form.id = 'kcp_modal_form'
  form.method = 'POST'
  form.action = gatewayUrl
  form.target = 'kcp_cert_iframe' // iframe name과 일치
  form.style.display = 'none'

  // Form 데이터 추가
  Object.entries(formData).forEach(([key, value]) => {
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = key
    input.value = value
    form.appendChild(input)
  })

  // Form을 body에 추가하고 제출
  document.body.appendChild(form)
  console.log('[KCP] Form submitted to iframe')
  form.submit()
}

const handlePhoneInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value = target.value.replace(/[^0-9]/g, '')
  if (value.length > 11) {
    value = value.slice(0, 11)
  }
  phoneNumber.value = value
  errorMessage.value = ''
}

const startVerification = async () => {
  if (!canStartVerification.value) {
    return
  }

  isVerifying.value = true
  errorMessage.value = ''

  // step2에서 입력한 번호로 세션 생성 (return_url 포함 - Fallback 리다이렉트용)
  await verificationMutation.mutateAsync({
    phone_number: phoneNumber.value,
    return_url: props.returnUrl  // Fallback 시 props.returnUrl로 리다이렉트 (기본값: /signup)
  })
}

const handleVerificationComplete = (result: PhoneVerificationResult) => {
  console.log('[KCP] handleVerificationComplete called', result)
  isVerifying.value = false

  // 팝업/모달 닫기
  closeVerificationModal()

  if (result.success) {
    // Backend에서 전화번호 일치 여부 확인
    const isPhoneMatched = result.is_phone_matched !== undefined ? result.is_phone_matched : true
    const verifiedPhone = result.phone || ''
    const inputPhone = phoneNumber.value

    // KCP 인증 번호를 항상 emit (디버깅용)
    emit('update:verifiedPhone', verifiedPhone)

    // AND 조건: KCP 인증 성공 AND 전화번호 일치
    if (!isPhoneMatched) {
      errorMessage.value = `입력한 번호(${inputPhone})와 인증한 번호(${verifiedPhone})가 다릅니다. 동일한 번호로 다시 인증해주세요.`
      toast.error(errorMessage.value)
      isVerified.value = false
      emit('update:phoneChk', false) // 인증 실패 - boolean false 전달
      return
    }

    // 인증 성공 - KCP 인증 통과 AND 전화번호 일치 확인됨
    isVerified.value = true
    verifiedPhoneNumber.value = verifiedPhone // 인증된 전화번호 저장
    phoneNumber.value = verifiedPhone
    emit('update:modelValue', phoneNumber.value)
    emit('update:phoneChk', true) // 인증 성공 - boolean true 전달
    emit('verified', result)
    toast.success('휴대폰 인증이 완료되었습니다')
  } else {
    errorMessage.value = result.error || '인증에 실패했습니다'
    toast.error(errorMessage.value)
    emit('update:phoneChk', false) // 인증 실패 - boolean false 전달
  }
}

const closeVerificationModal = () => {
  showVerificationModal.value = false
  gatewayUrl.value = ''

  // 팝업 닫기
  if (closePopup) {
    closePopup()
    closePopup = null
  }

  // Form 정리
  const modalForm = document.getElementById('kcp_modal_form')
  if (modalForm) {
    modalForm.remove()
  }
}

// Cleanup
onUnmounted(() => {
  if (cleanupListener) {
    cleanupListener()
  }
  if (closePopup) {
    closePopup()
  }
  // Form 정리
  const popupForm = document.getElementById('kcp_cert_form')
  if (popupForm) {
    popupForm.remove()
  }
  const modalForm = document.getElementById('kcp_modal_form')
  if (modalForm) {
    modalForm.remove()
  }
})
</script>

<style scoped>
.phone-verification {
  width: 100%;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  position: relative;
}

.input-field {
  flex: 1;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  transition: all 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: rgba(124, 58, 237, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-field.error {
  border-color: rgba(239, 68, 68, 0.5);
}

.input-field.success {
  border-color: rgba(34, 197, 94, 0.5);
}

.verify-button {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-width: 100px;
}

.verify-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.verify-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.validation-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.error-text {
  color: #ef4444;
}

.success-text {
  color: #22c55e;
}

/* 인증 모달 */
.verification-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.verification-modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-button:hover {
  color: #1f2937;
}

.verification-iframe {
  flex: 1;
  width: 100%;
  min-height: 500px;
  border: none;
}

@media (max-width: 640px) {
  .verification-modal {
    max-height: 90vh;
  }

  .verification-iframe {
    min-height: 400px;
  }
}
</style>
