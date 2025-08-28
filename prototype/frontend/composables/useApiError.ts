/**
 * API Error Handling Composable
 * API 에러 처리를 위한 공통 컴포저블
 */

import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import type { ApiError } from '~/api/client'

export const useApiError = () => {
  const error: Ref<ApiError | null> = ref(null)
  const errorMessage = computed(() => error.value?.message || null)
  const errorCode = computed(() => error.value?.error_code || null)
  const isError = computed(() => !!error.value)
  
  /**
   * 에러 설정
   */
  const setError = (err: ApiError | Error | string | null) => {
    if (!err) {
      error.value = null
    } else if (typeof err === 'string') {
      error.value = {
        message: err,
        status_code: 500,
        error_code: 'UNKNOWN_ERROR'
      }
    } else if (err instanceof Error) {
      error.value = {
        message: err.message,
        status_code: 500,
        error_code: 'UNKNOWN_ERROR'
      }
    } else {
      error.value = err
    }
  }
  
  /**
   * 에러 초기화
   */
  const clearError = () => {
    error.value = null
  }
  
  /**
   * 에러 메시지 포맷팅
   */
  const formatErrorMessage = (err: ApiError): string => {
    // 에러 코드별 사용자 친화적 메시지 매핑
    const errorMessages: Record<string, string> = {
      'NETWORK_ERROR': '네트워크 연결을 확인해주세요.',
      'UNAUTHORIZED': '로그인이 필요합니다.',
      'FORBIDDEN': '접근 권한이 없습니다.',
      'NOT_FOUND': '요청한 리소스를 찾을 수 없습니다.',
      'VALIDATION_ERROR': '입력값을 확인해주세요.',
      'DUPLICATE_EMAIL': '이미 사용 중인 이메일입니다.',
      'DUPLICATE_PHONE': '이미 사용 중인 전화번호입니다.',
      'DUPLICATE_USER_ID': '이미 사용 중인 사용자 ID입니다.',
      'DUPLICATE_NICKNAME': '이미 사용 중인 닉네임입니다.',
      'INVALID_CREDENTIALS': '아이디 또는 비밀번호가 올바르지 않습니다.',
      'ACCOUNT_LOCKED': '계정이 잠겼습니다. 잠시 후 다시 시도해주세요.',
      'ACCOUNT_INACTIVE': '비활성화된 계정입니다.',
      'TOKEN_EXPIRED': '인증이 만료되었습니다. 다시 로그인해주세요.',
      'RATE_LIMIT_ERROR': '너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요.',
      'AI_SERVICE_ERROR': 'AI 서비스가 일시적으로 불안정합니다. 잠시 후 다시 시도해주세요.',
      'INTERNAL_SERVER_ERROR': '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }
    
    return errorMessages[err.error_code] || err.message || '알 수 없는 오류가 발생했습니다.'
  }
  
  /**
   * 에러 처리 래퍼 함수
   */
  const handleApiCall = async <T>(
    apiCall: () => Promise<T>,
    options?: {
      onError?: (error: ApiError) => void
      showNotification?: boolean
    }
  ): Promise<T | null> => {
    clearError()
    
    try {
      const result = await apiCall()
      return result
    } catch (err: any) {
      const apiError: ApiError = {
        message: err.message || '알 수 없는 오류가 발생했습니다.',
        status_code: err.status_code || 500,
        error_code: err.error_code || 'UNKNOWN_ERROR',
        details: err.details
      }
      
      setError(apiError)
      
      // 커스텀 에러 핸들러 실행
      if (options?.onError) {
        options.onError(apiError)
      }
      
      // 알림 표시 (Nuxt 플러그인이나 컴포넌트에서 처리)
      if (options?.showNotification) {
        // useNuxtData().$toast 등을 사용하여 알림 표시
        console.error('API Error:', formatErrorMessage(apiError))
      }
      
      return null
    }
  }
  
  return {
    // 상태
    error: readonly(error),
    errorMessage: readonly(errorMessage),
    errorCode: readonly(errorCode),
    isError: readonly(isError),
    
    // 메서드
    setError,
    clearError,
    formatErrorMessage,
    handleApiCall
  }
}