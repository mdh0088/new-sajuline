<template>
  <div class="kcp-auth-container">
    <!-- KCP 인증 폼 (PHP 패턴과 동일) -->
    <form 
      ref="kcpForm"
      name="form_auth"
      method="post" 
      :action="baseURL + '/api/v1/sms/kcp-redirect'"
      target="auth_popup"
      accept-charset="UTF-8"
      style="display: none;"
    >
      <input type="hidden" name="ordr_idxx" :value="sessionId" />
      <input type="hidden" name="req_tx" value="cert" />
      <input type="hidden" name="cert_method" value="01" />
      <input type="hidden" name="web_siteid" value="J23022409076" />
      <input type="hidden" name="site_cd" value="S6186" />
      <input type="hidden" name="Ret_URL" value="http://localhost:8000/api/v1/sms/kcp-callback" />
      <input type="hidden" name="cert_otp_use" value="Y" />
      <input type="hidden" name="cert_enc_use_ext" value="Y" />
      <input type="hidden" name="cert_able_yn" value="Y" />
      <input type="hidden" name="web_siteid_hashYN" value="Y" />
      <input type="hidden" name="param_opt_1" value="" />
      <input type="hidden" name="param_opt_2" value="" />
      <input type="hidden" name="param_opt_3" value="" />
      <input type="hidden" name="user_name" value="" />
      <input type="hidden" name="year" value="00" />
      <input type="hidden" name="month" value="00" />
      <input type="hidden" name="day" value="00" />
      <input type="hidden" name="sex_code" value="" />
      <input type="hidden" name="local_code" value="" />
      <input type="hidden" name="fix_commid" value="" />
      <!-- veri_up_hash for verification (PHP 패턴) -->
      <input type="hidden" name="veri_up_hash" value="" />
    </form>
    
    <!-- 로딩 상태 (필요시 표시) -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>인증 준비 중...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface Props {
  name: string
  birthDate: string  // YYYYMMDD format
  phone: string
  gender?: string    // M or F
}

interface Emits {
  (e: 'success', data: any): void
  (e: 'error', error: string): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Refs
const kcpForm = ref<HTMLFormElement>()

// State
const loading = ref(false)
const kcpPopup = ref<Window | null>(null)
const popupMonitor = ref<number | null>(null)
const sessionId = ref('')

// Track if authentication is in progress
const authInProgress = ref(false)

// Base URL for API calls
const baseURL = computed(() => {
  return process.client ? 'http://localhost:8000' : 'http://backend:8000'
})

// Start authentication - PHP 패턴과 정확히 동일
const startAuth = async () => {
  // Prevent multiple simultaneous authentications
  if (authInProgress.value) {
    console.log('Authentication already in progress')
    return
  }
  
  authInProgress.value = true
  loading.value = true
  
  try {
    // Close any existing popup first
    if (kcpPopup.value && !kcpPopup.value.closed) {
      kcpPopup.value.close()
    }
    
    // Development mode: Mock success for testing
    if (process.env.NODE_ENV === 'development' && window.location.search.includes('mock=true')) {
      console.log('KCP Mock Mode: Simulating successful authentication')
      setTimeout(() => {
        emit('success', {
          phone: props.phone,
          name: props.name,
          birth_day: props.birthDate,
          ci: 'mock-ci-' + Date.now(),
          di: 'mock-di-' + Date.now(),
          session_id: 'mock-session',
          verified: true
        })
        loading.value = false
        authInProgress.value = false
      }, 1000)
      return
    }
    
    // 1. Get session ID from prepare-kcp-auth API
    console.log('Preparing KCP authentication session')
    
    const response = await $fetch(`${baseURL.value}/api/v1/sms/prepare-kcp-auth`, {
      method: 'POST',
      body: {
        name: props.name,
        birth_date: props.birthDate,
        phone: props.phone,
        gender: props.gender
      }
    })
    
    console.log('KCP prepare response:', response)
    
    if (!response?.success) {
      throw new Error(response?.message || 'KCP 인증 준비에 실패했습니다')
    }
    
    const responseData = response.data
    if (!responseData || !responseData.session_id) {
      throw new Error('세션 ID를 가져오지 못했습니다')
    }
    
    // 2. Set session ID in form (PHP 패턴)
    sessionId.value = responseData.session_id
    
    // 3. Create popup window FIRST (PHP auth_type_check 함수와 동일)
    console.log('Creating KCP popup window (PHP pattern)')
    const width = 410
    const height = 500
    const leftpos = screen.width / 2 - (width / 2)
    const toppos = screen.height / 2 - (height / 2)
    const winopts = `width=${width}, height=${height}, toolbar=no,status=no,statusbar=no,menubar=no,scrollbars=no,resizable=no`
    const position = `,left=${leftpos}, top=${toppos}`
    
    // PHP 패턴: var AUTH_POP = window.open('','auth_popup', winopts + position);
    kcpPopup.value = window.open('', 'auth_popup', winopts + position)
    
    if (!kcpPopup.value || kcpPopup.value.closed) {
      throw new Error('팝업 차단으로 인해 인증창을 열 수 없습니다. 팝업 차단을 해제해주세요.')
    }
    
    // 4. Setup form (PHP 패턴)
    // auth_form.method = "post";
    // auth_form.target = "auth_popup"; (이미 설정됨)
    // auth_form.action = "./kcpcert_proc_req.php"; (이미 설정됨)
    
    await nextTick()
    
    if (kcpForm.value) {
      console.log('Submitting form to kcp-redirect (PHP pattern)')
      console.log('Session ID:', sessionId.value)
      
      // 5. Submit form - 같은 팝업창에서 처리됨 (PHP 패턴)
      kcpForm.value.submit()
      
      // 6. Start monitoring the popup
      startPopupMonitor()
      
    } else {
      throw new Error('KCP 폼을 찾을 수 없습니다.')
    }
    
  } catch (error: any) {
    console.error('KCP auth preparation failed:', error)
    emit('error', error.data?.message || error.message || 'KCP 인증 준비 중 오류가 발생했습니다')
  } finally {
    loading.value = false
    authInProgress.value = false
  }
}

// Monitor popup window
const startPopupMonitor = () => {
  // Clear any existing monitor
  if (popupMonitor.value) {
    clearInterval(popupMonitor.value)
  }
  
  popupMonitor.value = window.setInterval(() => {
    if (kcpPopup.value && kcpPopup.value.closed) {
      console.log('KCP popup window was closed')
      stopPopupMonitor()
      emit('close')
    }
  }, 500)
}

// Stop monitoring popup
const stopPopupMonitor = () => {
  if (popupMonitor.value) {
    clearInterval(popupMonitor.value)
    popupMonitor.value = null
  }
  authInProgress.value = false
}

// Close popup if still open
const closePopup = () => {
  if (kcpPopup.value && !kcpPopup.value.closed) {
    kcpPopup.value.close()
  }
  stopPopupMonitor()
}

// Handle messages from popup/iframe
const handleMessage = (event: MessageEvent) => {
  console.log('KcpDirectAuth - Received message from:', event.origin)
  console.log('KcpDirectAuth - Message data:', event.data)
  
  // Check if message is from our callback or KCP
  if (event.data && event.data.type === 'kcp_verification_complete') {
    console.log('KcpDirectAuth - Processing KCP verification message')
    // Message from our callback endpoint
    if (event.data.success) {
      console.log('KCP verification successful:', event.data)
      
      // Emit success event with verified data
      const successData = {
        phone: event.data.phone || props.phone,
        name: event.data.name || event.data.user_name || '',
        birth_day: event.data.birth_day || '',
        ci: event.data.ci || '',
        di: event.data.di || '',
        phone_chk: event.data.phone_chk || '',
        session_id: sessionId.value,
        verified: true
      }
      
      console.log('KcpDirectAuth - Emitting success with:', successData)
      emit('success', successData)
      authInProgress.value = false
      closePopup()
    } else {
      console.error('KCP verification failed:', event.data.message)
      emit('error', event.data.message || '인증에 실패했습니다')
      authInProgress.value = false
      closePopup()
    }
  } else if (event.origin && event.origin.includes('kcp.co.kr')) {
    console.log('KcpDirectAuth - Direct message from KCP')
    // Direct message from KCP (fallback)
    if (event.data && event.data.success) {
      emit('success', event.data)
      authInProgress.value = false
      closePopup()
    } else if (event.data && event.data.error) {
      emit('error', event.data.message || '인증에 실패했습니다')
      authInProgress.value = false
      closePopup()
    }
  }
}

// KCP callback handler (global function)
const setupKcpCallback = () => {
  if (process.client) {
    // Set up global auth_data function for KCP callback
    (window as any).auth_data = (frm: HTMLFormElement) => {
      console.log('KCP auth_data called', frm)
      
      const result: Record<string, string> = {}
      for (let i = 0; i < frm.elements.length; i++) {
        const element = frm.elements[i] as HTMLInputElement
        if (element.value) {
          result[element.name] = element.value
        }
      }
      
      // Check if authentication was successful
      if (result.res_cd === '0000') {
        emit('success', {
          phone: result.phone_no || props.phone,
          name: result.user_name || '',  // Use empty name if not provided by KCP
          ci: result.ci_url,
          di: result.di_url,
          session_id: sessionId.value
        })
      } else {
        emit('error', result.res_msg || '인증에 실패했습니다')
      }
      
      closePopup()
    }
  }
}

// Lifecycle
onMounted(() => {
  if (process.client) {
    window.addEventListener('message', handleMessage)
    setupKcpCallback()
    // Don't auto-start - wait for parent to call startAuth()
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('message', handleMessage)
    // Clean up
    stopPopupMonitor()
    closePopup()
    // Clean up global function
    if ((window as any).auth_data) {
      delete (window as any).auth_data
    }
  }
})

// Expose methods for parent component
defineExpose({
  startAuth,
  closePopup
})
</script>

<style scoped>
.kcp-auth-container {
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  color: white;
  margin-top: 16px;
  font-size: 16px;
}
</style>