/**
 * 휴대폰 본인인증 API 컴포저블 (Vue Query)
 * - KCP 본인인증 서비스 연동
 */
import { useMutation, type UseMutationOptions } from '@tanstack/vue-query'
import type { APIResponse, APIError } from '~/types/common/api'

/**
 * 휴대폰 인증 시작 요청 - KCP 모달에서 사용자 정보 입력
 */
export interface PhoneVerificationInitiateRequest {
  phone_number: string // 01012345678 (하이픈 없이)
  return_url?: string // 인증 완료 후 리다이렉트할 URL (Fallback용, 기본값: /signup)
}

/**
 * 휴대폰 인증 시작 응답
 */
export interface PhoneVerificationInitiateResponse {
  gateway_url: string
  form_data: Record<string, string>
  session_id: string
  site_cd: string
}

/**
 * 휴대폰 인증 완료 결과 (postMessage)
 */
export interface PhoneVerificationResult {
  success: boolean
  phone?: string
  phone_chk?: string
  is_phone_matched?: boolean
  ci?: string
  di?: string
  name?: string
  birth_date?: string
  gender?: string
  error?: string
}

/**
 * 인증 상태 조회 응답
 */
export interface PhoneVerificationStatusResponse {
  status: 'initiated' | 'verified' | 'expired'
  phone?: string
  phone_chk?: string
  ci?: string
  di?: string
  verified_name?: string
  verified_birth_date?: string
  verified_gender?: string
  phone_number?: string
}

const phoneVerificationApi = {
  /**
   * 본인인증 시작
   */
  async initiateVerification(
    request: PhoneVerificationInitiateRequest
  ): Promise<PhoneVerificationInitiateResponse> {
    const response = await $fetch<APIResponse<PhoneVerificationInitiateResponse>>(
      '/api/v1/phone-verification/initiate',
      {
        method: 'POST',
        credentials: 'include',
        body: request
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '본인인증 시작 실패')
    }

    return response.data
  },

  /**
   * 인증 상태 조회 (모바일 _self 방식에서 사용)
   */
  async getVerificationStatus(
    sessionId: string
  ): Promise<PhoneVerificationStatusResponse> {
    const response = await $fetch<APIResponse<PhoneVerificationStatusResponse>>(
      `/api/v1/phone-verification/status/${sessionId}`,
      {
        method: 'GET',
        credentials: 'include'
      }
    )

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || '인증 상태 조회 실패')
    }

    return response.data
  }
}

export const usePhoneVerification = () => {
  /**
   * 본인인증 시작 뮤테이션
   */
  const useInitiateVerification = (
    options?: UseMutationOptions<
      PhoneVerificationInitiateResponse,
      APIError,
      PhoneVerificationInitiateRequest
    >
  ) => {
    return useMutation({
      mutationFn: phoneVerificationApi.initiateVerification,
      ...options
    })
  }

  /**
   * postMessage 리스너 설정
   *
   * KCP 인증창에서 postMessage로 결과를 전달받음
   */
  const setupPostMessageListener = (
    onComplete: (result: PhoneVerificationResult) => void
  ): (() => void) => {
    const handleMessage = (event: MessageEvent) => {
      console.log('[KCP] postMessage received:', event.data, 'from:', event.origin)

      // 보안: origin 검증 (개발/운영 환경 모두 허용)
      // const allowedOrigins = ['http://localhost:8000', 'https://api.sajuline.com']
      // if (!allowedOrigins.includes(event.origin)) {
      //   console.warn('Invalid postMessage origin:', event.origin)
      //   return
      // }

      // KCP 인증 완료 메시지 확인
      if (event.data && event.data.type === 'kcp_verification_complete') {
        console.log('[KCP] Verification complete message received')
        onComplete(event.data as PhoneVerificationResult)
      }
    }

    console.log('[KCP] Setting up postMessage listener')
    window.addEventListener('message', handleMessage)

    // 클린업 함수 반환
    return () => {
      console.log('[KCP] Removing postMessage listener')
      window.removeEventListener('message', handleMessage)
    }
  }

  /**
   * KCP 인증창 열기
   *
   * @param gatewayUrl KCP Gateway URL
   * @param formData KCP Form 데이터
   * @param isMobile 모바일 여부 (popup vs iframe)
   * @returns 창 닫기 함수
   */
  const openVerificationWindow = (
    gatewayUrl: string,
    formData: Record<string, string>,
    isMobile: boolean = false
  ): (() => void) => {
    // Form 생성 및 제출 헬퍼 함수
    const submitKcpForm = (windowName: string, windowRef?: Window | null) => {
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

      // 창에 name 설정 (중요!)
      if (windowRef) {
        try {
          windowRef.name = windowName
        } catch (e) {
          console.warn('[KCP] Could not set window name:', e)
        }
      }

      // Form을 body에 추가하고 제출
      document.body.appendChild(form)
      console.log('[KCP] Submitting form to window:', windowName)
      form.submit()

      return form
    }

    // 모바일/PC 모두 새 창(팝업) 방식 사용
    // 모바일에서 _self 사용 시 KCP가 POST 대신 GET으로 리다이렉트하여 인증 데이터 손실됨
    const windowName = 'kcp_auth_popup'

    // 새 창 열기 (모바일에서는 새 탭으로 열림)
    let popup: Window | null = null

    if (isMobile) {
      // 모바일: 새 탭으로 열기 (팝업 옵션 없이)
      popup = window.open('about:blank', windowName)
    } else {
      // PC: 팝업 창으로 열기
      popup = window.open('', windowName)
      if (!popup || popup.closed) {
        popup = window.open(
          'about:blank',
          windowName,
          'width=600,height=700,scrollbars=yes,resizable=yes'
        )
      }
    }

    if (!popup || popup.closed) {
      throw new Error('인증창을 열 수 없습니다. 팝업 차단을 해제해주세요.')
    }

    // Form을 새 창으로 제출
    submitKcpForm(windowName, popup)

    // 창 닫기 함수 반환
    return () => {
      if (popup && !popup.closed) {
        popup.close()
      }
      const form = document.getElementById('kcp_cert_form')
      if (form) {
        form.remove()
      }
    }
  }

  /**
   * 인증 상태 조회 (모바일 _self 방식에서 돌아왔을 때 사용)
   */
  const checkVerificationStatus = async (
    sessionId: string
  ): Promise<PhoneVerificationResult> => {
    try {
      const status = await phoneVerificationApi.getVerificationStatus(sessionId)

      if (status.status === 'verified') {
        return {
          success: true,
          phone: status.phone,
          phone_chk: status.phone_chk,
          is_phone_matched: status.phone === status.phone_number,
          ci: status.ci,
          di: status.di,
          name: status.verified_name,
          birth_date: status.verified_birth_date,
          gender: status.verified_gender
        }
      } else if (status.status === 'initiated') {
        return {
          success: false,
          error: '인증이 아직 완료되지 않았습니다'
        }
      } else {
        return {
          success: false,
          error: '인증 세션이 만료되었습니다'
        }
      }
    } catch (error: any) {
      return {
        success: false,
        error: error?.message || '인증 상태 조회 실패'
      }
    }
  }

  return {
    useInitiateVerification,
    setupPostMessageListener,
    openVerificationWindow,
    checkVerificationStatus
  }
}
