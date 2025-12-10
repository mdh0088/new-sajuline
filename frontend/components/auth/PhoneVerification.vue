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
const { useInitiateVerification, setupPostMessageListener, openVerificationWindow, checkVerificationStatus } = usePhoneVerification()
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
let preOpenedPopup: Window | null = null // 미리 열어둔 팝업 참조

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

  // 전화번호가 변경되면 localStorage 정리 및 인증 상태 초기화
  if (oldVal && newVal !== oldVal) {
    // localStorage 정리
    localStorage.removeItem('kcp_session_id')
    localStorage.removeItem('kcp_phone_number')

    // 인증 진행 중이면 중단
    isVerifying.value = false

    // 인증 완료 상태였으면 초기화
    if (isVerified.value && verifiedPhoneNumber.value && newVal !== verifiedPhoneNumber.value) {
      isVerified.value = false
      emit('update:phoneChk', false)
      errorMessage.value = '전화번호가 변경되었습니다. 다시 인증해주세요.'
    }
  }
})

// Mutation
const verificationMutation = useInitiateVerification({
  onSuccess: (data) => {
    gatewayUrl.value = data.gateway_url

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

    // 인증창에 폼 제출
    if (props.useModal) {
      // 모달 사용 (Form POST 방식)
      // postMessage 리스너 설정
      cleanupListener = setupPostMessageListener(handleVerificationComplete)
      showVerificationModal.value = true
      // 모달이 열린 후 Form 제출 (nextTick 사용)
      nextTick(() => {
        submitFormToModal(data.gateway_url, data.form_data)
      })
    } else if (isMobile) {
      // 모바일: _self 방식으로 현재 페이지에서 이동
      // 세션 ID를 localStorage에 저장 (돌아왔을 때 확인용)
      localStorage.setItem('kcp_session_id', data.session_id)
      localStorage.setItem('kcp_phone_number', phoneNumber.value)
      submitFormToSelf(data.gateway_url, data.form_data)
    } else {
      // PC: 팝업 사용 - 미리 열어둔 팝업에 폼 제출
      // postMessage 리스너 설정
      cleanupListener = setupPostMessageListener(handleVerificationComplete)
      try {
        if (preOpenedPopup && !preOpenedPopup.closed) {
          submitFormToPopup(data.gateway_url, data.form_data, preOpenedPopup)
        } else {
          // 팝업이 닫혔거나 없는 경우 에러
          throw new Error('인증창이 닫혔습니다. 다시 시도해주세요.')
        }
      } catch (error: any) {
        toast.error(error.message || '인증창을 열 수 없습니다')
        isVerifying.value = false
        // 팝업 정리
        if (preOpenedPopup && !preOpenedPopup.closed) {
          preOpenedPopup.close()
        }
        preOpenedPopup = null
      }
    }
  },
  onError: (error: any) => {
    isVerifying.value = false
    errorMessage.value = error?.message || '인증 시작에 실패했습니다'
    toast.error(errorMessage.value)
    // 팝업 정리
    if (preOpenedPopup && !preOpenedPopup.closed) {
      preOpenedPopup.close()
    }
    preOpenedPopup = null
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

const submitFormToSelf = (gatewayUrl: string, formData: Record<string, string>) => {
  console.log('[KCP] submitFormToSelf called (mobile)', { gatewayUrl, formData })

  // 기존 form 제거 (중복 방지)
  const existingForm = document.getElementById('kcp_cert_form')
  if (existingForm) {
    existingForm.remove()
  }

  // Form 요소 생성
  const form = document.createElement('form')
  form.id = 'kcp_cert_form'
  form.method = 'POST'
  form.action = gatewayUrl
  form.target = '_self' // 현재 페이지에서 이동
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
  console.log('[KCP] Submitting form to _self (mobile redirect)')
  form.submit()
}

const submitFormToPopup = (gatewayUrl: string, formData: Record<string, string>, popup: Window) => {
  console.log('[KCP] submitFormToPopup called', { gatewayUrl, formData })

  const windowName = 'kcp_auth_popup'

  // 기존 form 제거 (중복 방지)
  const existingForm = document.getElementById('kcp_cert_form')
  if (existingForm) {
    existingForm.remove()
  }

  // Form 요소 생성
  const form = document.createElement('form')
  form.id = 'kcp_cert_form'
  form.method = 'POST'
  form.action = gatewayUrl
  form.target = windowName
  form.style.display = 'none'

  // Form 데이터 추가
  Object.entries(formData).forEach(([key, value]) => {
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = key
    input.value = value
    form.appendChild(input)
  })

  // 팝업 window에 name 설정
  try {
    popup.name = windowName
  } catch (e) {
    console.warn('[KCP] Could not set window name:', e)
  }

  // Form을 body에 추가하고 제출
  document.body.appendChild(form)
  console.log('[KCP] Submitting form to popup:', windowName)
  form.submit()

  // closePopup 함수 설정
  closePopup = () => {
    if (popup && !popup.closed) {
      popup.close()
    }
    const formEl = document.getElementById('kcp_cert_form')
    if (formEl) {
      formEl.remove()
    }
    preOpenedPopup = null
  }
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

  // 이전 세션 데이터 정리 (새 인증 시작 전 항상 정리)
  localStorage.removeItem('kcp_session_id')
  localStorage.removeItem('kcp_phone_number')

  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

  // PC에서만 팝업 미리 열기 (모바일은 _self 방식 사용)
  if (!props.useModal && !isMobile) {
    const windowName = 'kcp_auth_popup'

    try {
      // PC: 팝업 창으로 열기
      preOpenedPopup = window.open('about:blank', windowName, 'width=600,height=700,scrollbars=yes,resizable=yes')

      if (!preOpenedPopup || preOpenedPopup.closed) {
        throw new Error('인증창을 열 수 없습니다. 팝업 차단을 해제해주세요.')
      }

      // 로딩 중 메시지 표시
      preOpenedPopup.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>본인인증</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 100vh;
              margin: 0;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              text-align: center;
            }
            .loader {
              border: 4px solid rgba(255,255,255,0.3);
              border-top: 4px solid white;
              border-radius: 50%;
              width: 40px;
              height: 40px;
              animation: spin 1s linear infinite;
              margin: 0 auto 20px;
            }
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          </style>
        </head>
        <body>
          <div>
            <div class="loader"></div>
            <p>인증 페이지를 불러오는 중...</p>
          </div>
        </body>
        </html>
      `)
    } catch (error: any) {
      toast.error(error.message || '인증창을 열 수 없습니다. 팝업 차단을 해제해주세요.')
      isVerifying.value = false
      return
    }
  }

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

// 모바일 _self 방식에서 돌아왔을 때 세션 확인 (폴링 방식)
onMounted(async () => {
  // localStorage에서 KCP 세션 정보 확인
  const savedSessionId = localStorage.getItem('kcp_session_id')
  const savedPhoneNumber = localStorage.getItem('kcp_phone_number')

  if (savedSessionId && savedPhoneNumber) {
    console.log('[KCP] Found saved session, checking status...', savedSessionId)

    // 세션 상태 확인
    isVerifying.value = true
    phoneNumber.value = savedPhoneNumber

    // 폴링으로 인증 완료 대기 (최대 30초, 2초 간격)
    const maxAttempts = 15
    let attempts = 0

    const pollStatus = async (): Promise<void> => {
      attempts++
      console.log(`[KCP] Polling attempt ${attempts}/${maxAttempts}`)

      const result = await checkVerificationStatus(savedSessionId)
      console.log('[KCP] Session status result:', result)

      if (result.success) {
        // 인증 완료
        localStorage.removeItem('kcp_session_id')
        localStorage.removeItem('kcp_phone_number')
        handleVerificationComplete(result)
      } else if (result.error === '인증이 아직 완료되지 않았습니다' && attempts < maxAttempts) {
        // 아직 인증 중 - 2초 후 재시도
        setTimeout(pollStatus, 2000)
      } else {
        // 최대 시도 횟수 초과 또는 다른 에러
        localStorage.removeItem('kcp_session_id')
        localStorage.removeItem('kcp_phone_number')
        isVerifying.value = false
        if (attempts >= maxAttempts) {
          errorMessage.value = '인증 시간이 초과되었습니다. 다시 시도해주세요.'
          toast.error(errorMessage.value)
        } else {
          handleVerificationComplete(result)
        }
      }
    }

    // 폴링 시작
    await pollStatus()
  }
})

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
