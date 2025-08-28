<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 페이지 헤더 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">KCP 핸드폰 인증 테스트</h1>
        <p class="text-gray-600">Docker 환경에서 KCP 핸드폰 인증 API 테스트</p>
      </div>

      <!-- 시스템 상태 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">🔧 시스템 상태</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex items-center space-x-2">
            <div :class="systemStatus.backend ? 'w-3 h-3 bg-green-500 rounded-full' : 'w-3 h-3 bg-red-500 rounded-full'"></div>
            <span class="text-sm">백엔드 API: {{ systemStatus.backend ? '연결됨' : '연결 실패' }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="systemStatus.kcp ? 'w-3 h-3 bg-green-500 rounded-full' : 'w-3 h-3 bg-yellow-500 rounded-full'"></div>
            <span class="text-sm">KCP 바이너리: {{ systemStatus.kcp ? '사용 가능' : '테스트 모드' }}</span>
          </div>
        </div>
      </div>

      <!-- 테스트 폼 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">📱 인증 정보 입력</h2>
        
        <form @submit.prevent="startVerification" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
              <input
                v-model="formData.user_name"
                type="text"
                placeholder="홍길동"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">생년월일</label>
              <input
                v-model="formData.birth_date"
                type="text"
                placeholder="19900101"
                maxlength="8"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">휴대폰번호</label>
              <input
                v-model="formData.phone_number"
                type="tel"
                placeholder="01012345678"
                maxlength="11"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">통신사</label>
              <select
                v-model="formData.carrier"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">통신사 선택</option>
                <option value="SKT">SKT</option>
                <option value="KTF">KT</option>
                <option value="LGT">LG U+</option>
                <option value="MVNO">알뜰폰</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">성별</label>
              <select
                v-model="formData.gender"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">성별 선택</option>
                <option value="M">남성</option>
                <option value="F">여성</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">인증방법</label>
              <select
                v-model="formData.verification_method"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="01">SMS 인증</option>
                <option value="02">PASS 인증</option>
                <option value="03">신용카드 인증</option>
              </select>
            </div>
          </div>

          <!-- 테스트 버튼들 -->
          <div class="pt-4 space-y-3">
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-md transition-colors"
              data-testid="start-verification-btn"
            >
              {{ loading ? '처리 중...' : '🚀 KCP 핸드폰 인증 시작' }}
            </button>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                type="button"
                @click="checkSystemStatus"
                :disabled="loading"
                class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
                data-testid="check-status-btn"
              >
                ✅ 시스템 상태 확인
              </button>

              <button
                type="button"
                @click="testKcpConfig"
                :disabled="loading"
                class="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
                data-testid="test-kcp-config-btn"
              >
                ⚙️ KCP 설정 테스트
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- 결과 표시 영역 -->
      <div v-if="lastResponse" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">📊 테스트 결과</h2>
        
        <div class="mb-4">
          <div class="flex items-center space-x-2 mb-2">
            <div :class="lastResponse.success ? 'w-3 h-3 bg-green-500 rounded-full' : 'w-3 h-3 bg-red-500 rounded-full'"></div>
            <span class="font-medium">{{ lastResponse.success ? '성공' : '실패' }}</span>
            <span class="text-sm text-gray-500">{{ lastResponse.timestamp }}</span>
          </div>
          
          <!-- 세션 정보 (성공 시) -->
          <div v-if="lastResponse.success && lastResponse.data.session_id" class="bg-green-50 border border-green-200 rounded p-3 mb-4">
            <h3 class="font-medium text-green-800 mb-2">인증 세션 생성됨</h3>
            <div class="text-sm text-green-700 space-y-1">
              <p><strong>세션 ID:</strong> {{ lastResponse.data.session_id }}</p>
              <p><strong>만료 시간:</strong> {{ formatDate(lastResponse.data.expires_at) }}</p>
              <p v-if="lastResponse.data.gateway_url"><strong>KCP URL:</strong> <a :href="lastResponse.data.gateway_url" target="_blank" class="underline">인증창 열기</a></p>
            </div>
          </div>
        </div>

        <!-- 응답 데이터 -->
        <div class="bg-gray-50 border rounded p-4">
          <h3 class="font-medium text-gray-700 mb-2">Raw Response:</h3>
          <pre class="text-xs text-gray-600 overflow-auto max-h-64" data-testid="response-data">{{ JSON.stringify(lastResponse.data, null, 2) }}</pre>
        </div>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
        <div class="flex items-center space-x-2">
          <div class="w-5 h-5 text-red-500">⚠️</div>
          <div>
            <h3 class="font-medium text-red-800">오류 발생</h3>
            <p class="text-red-700 text-sm mt-1" data-testid="error-message">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 메타 설정
useHead({
  title: 'KCP 핸드폰 인증 테스트 - 사주라인',
  meta: [
    { name: 'description', content: 'KCP 핸드폰 인증 API 테스트 페이지' }
  ]
})

// 리액티브 데이터
const loading = ref(false)
const error = ref('')
const lastResponse = ref(null)

const systemStatus = ref({
  backend: false,
  kcp: false
})

const formData = ref({
  user_name: '홍길동',
  birth_date: '19900101',
  phone_number: '01012345678',
  carrier: 'SKT',
  gender: 'M',
  verification_method: '01',
  local_code: '01'
})

// API 호출 함수
const { $api } = useNuxtApp()

const checkSystemStatus = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 백엔드 헬스체크
    const healthResponse = await $api.get('/health')
    systemStatus.value.backend = healthResponse.status === 'healthy'
    
    // KCP 설정 확인 (추가 API 엔드포인트 필요)
    try {
      const kcpResponse = await $api.get('/phone-verification/config-test')
      systemStatus.value.kcp = kcpResponse.kcp_available || false
    } catch {
      systemStatus.value.kcp = false
    }
    
    lastResponse.value = {
      success: true,
      timestamp: new Date().toLocaleString(),
      data: {
        backend_status: healthResponse,
        system_info: {
          environment: healthResponse.environment,
          debug: healthResponse.debug,
          timestamp: healthResponse.timestamp
        }
      }
    }
  } catch (err) {
    systemStatus.value.backend = false
    error.value = `시스템 상태 확인 실패: ${err.message}`
  } finally {
    loading.value = false
  }
}

const testKcpConfig = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await $api.get('/phone-verification/config-test')
    
    lastResponse.value = {
      success: true,
      timestamp: new Date().toLocaleString(),
      data: response
    }
  } catch (err) {
    error.value = `KCP 설정 테스트 실패: ${err.message}`
    lastResponse.value = {
      success: false,
      timestamp: new Date().toLocaleString(),
      data: { error: err.message }
    }
  } finally {
    loading.value = false
  }
}

const startVerification = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // API 요청 데이터 변환
    const requestData = {
      name: formData.value.user_name,
      birth_date: formData.value.birth_date,
      phone_number: formData.value.phone_number,
      carrier: formData.value.carrier === 'LG U+' ? 'LGT' : formData.value.carrier,
      gender: formData.value.gender,
      method: formData.value.verification_method
    }
    
    const response = await $api.post('/phone-verification/initiate', requestData)
    
    lastResponse.value = {
      success: true,
      timestamp: new Date().toLocaleString(),
      data: response
    }
    
    // 성공 시 KCP 인증창을 새 탭에서 열기 (선택적)
    if (response.gateway_url) {
      // window.open(response.gateway_url, '_blank', 'width=600,height=700')
    }
  } catch (err) {
    error.value = `인증 시작 실패: ${err.message}`
    lastResponse.value = {
      success: false,
      timestamp: new Date().toLocaleString(),
      data: { error: err.message }
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('ko-KR')
}

// 페이지 로드 시 시스템 상태 확인
onMounted(() => {
  checkSystemStatus()
})
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>