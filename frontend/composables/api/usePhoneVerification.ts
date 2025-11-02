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

    if (isMobile) {
      // 모바일: 현재 창에서 Form POST
      submitKcpForm('_self')
      return () => {} // 모바일은 페이지 이동이므로 닫기 불필요
    } else {
      // PC: 팝업 창 이름 (고정)
      const windowName = 'auth_popup'

      // 기존 팝업이 있으면 재사용, 없으면 새로 생성
      let popup = window.open('', windowName)

      if (!popup || popup.closed) {
        // 팝업 차단 - 새로 열기 시도
        popup = window.open(
          'about:blank',
          windowName,
          'width=600,height=700,scrollbars=yes,resizable=yes'
        )

        if (!popup || popup.closed) {
          throw new Error('팝업이 차단되었습니다. 팝업 차단을 해제해주세요.')
        }
      }

      // Form을 팝업으로 제출
      submitKcpForm(windowName, popup)

      // 팝업 닫기 함수 반환
      return () => {
        if (popup && !popup.closed) {
          popup.close()
        }
        // Form 정리
        const form = document.getElementById('kcp_cert_form')
        if (form) {
          form.remove()
        }
      }
    }
  }

  return {
    useInitiateVerification,
    setupPostMessageListener,
    openVerificationWindow
  }
}
