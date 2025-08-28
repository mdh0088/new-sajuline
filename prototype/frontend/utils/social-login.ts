/**
 * 소셜 로그인 유틸리티
 * 카카오, 네이버 OAuth 인증 처리
 */

import { authAPI } from '~/api/services/auth'
import { useAuthToken } from './auth-token'
import { useUserStore } from '~/stores/user'

interface SocialLoginResult {
  success: boolean
  is_new_user: boolean
  tokens?: {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
  }
  user?: {
    id: string
    email: string
    name: string
    is_active: boolean
    email_verified: boolean
    created_at: string
  }
  social_user_info?: {
    provider: string
    social_id: string
    email?: string
    name?: string
    nickname?: string
    profile_image?: string
    raw_data: any
  }
  missing_fields?: string[]  // 추가 정보 필요 시 부족한 필드 목록
  message: string
}

/**
 * 소셜 로그인 팝업 창 처리
 */
export async function processSocialLoginPopup(provider: 'kakao' | 'naver'): Promise<SocialLoginResult> {
  return new Promise(async (resolve, reject) => {
    try {
      // 1. OAuth URL 생성
      const urlData = await authAPI.getSocialLoginUrl(provider)
      
      if (!urlData || !urlData.auth_url) {
        throw new Error(`${provider} OAuth URL 생성에 실패했습니다`)
      }

      // 2. 팝업 창 열기
      const popup = window.open(
        urlData.auth_url,
        `${provider}_login`,
        'width=500,height=600,scrollbars=yes,resizable=yes'
      )

      if (!popup) {
        throw new Error('팝업 창을 열 수 없습니다. 팝업 차단을 해제해주세요.')
      }

      // 3. 팝업 상태 모니터링
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed)
          reject(new Error('소셜 로그인이 취소되었습니다.'))
        }
      }, 1000)

      // 4. 메시지 리스너 등록 (OAuth 콜백 처리)
      const messageListener = async (event: MessageEvent) => {
        // 보안: origin 체크
        if (event.origin !== window.location.origin) {
          return
        }

        if (event.data?.type === 'SOCIAL_LOGIN_SUCCESS') {
          clearInterval(checkClosed)
          window.removeEventListener('message', messageListener)
          popup.close()

          try {
            // 백엔드로 콜백 처리 요청
            const result = await authAPI.processSocialCallback(
              provider,
              event.data.code,
              event.data.state
            )
            resolve(result)
          } catch (error) {
            reject(error)
          }
        } else if (event.data?.type === 'SOCIAL_LOGIN_ERROR') {
          clearInterval(checkClosed)
          window.removeEventListener('message', messageListener)
          popup.close()
          reject(new Error(event.data.message || '소셜 로그인 중 오류가 발생했습니다.'))
        }
      }

      window.addEventListener('message', messageListener)

    } catch (error) {
      reject(error)
    }
  })
}

/**
 * 소셜 로그인 처리 (리다이렉트 방식)
 */
export async function processSocialLoginRedirect(provider: 'kakao' | 'naver') {
  try {
    // OAuth URL 생성
    const urlData = await authAPI.getSocialLoginUrl(provider)
    
    if (!urlData || !urlData.auth_url) {
      throw new Error(`${provider} OAuth URL 생성에 실패했습니다`)
    }

    // 현재 페이지 정보를 세션 스토리지에 저장 (콜백 후 돌아올 페이지)
    sessionStorage.setItem('social_login_return_url', window.location.pathname)
    sessionStorage.setItem('social_login_provider', provider)
    
    if (urlData.state) {
      sessionStorage.setItem('social_login_state', urlData.state)
    }

    // OAuth 페이지로 리다이렉트
    window.location.href = urlData.auth_url

  } catch (error) {
    console.error(`${provider} 소셜 로그인 오류:`, error)
    throw error
  }
}

/**
 * 모바일 여부 확인
 */
export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
         window.innerWidth <= 768
}

/**
 * 소셜 로그인 실행 (모바일/데스크톱 자동 선택)
 */
export async function executeSocialLogin(provider: 'kakao' | 'naver'): Promise<SocialLoginResult> {
  if (isMobile()) {
    // 모바일: 리다이렉트 방식
    await processSocialLoginRedirect(provider)
    // 리다이렉트되므로 이 코드는 실행되지 않음
    throw new Error('Redirecting to OAuth provider')
  } else {
    // 데스크톱: 팝업 방식
    return await processSocialLoginPopup(provider)
  }
}

/**
 * 소셜 로그인 결과 처리
 */
export function handleSocialLoginResult(result: SocialLoginResult) {
  // 1) 기존 사용자: 토큰 존재 시 즉시 로그인 완료
  if (result.tokens?.access_token) {
    const { setAccessToken } = useAuthToken()
    setAccessToken(result.tokens.access_token, result.tokens.expires_in || 1800)

    const userStore = useUserStore()
    if (result.user) {
      userStore.setUser(result.user)
    }

    sessionStorage.removeItem('social_user_info')
    sessionStorage.removeItem('missing_fields')

    console.log(`[DEBUG] 소셜 로그인 완료 - is_new_user: ${result.is_new_user}, user_id: ${result.user?.id}`)

    return {
      success: true,
      action: 'login_complete',
      user: result.user,
      message: result.message
    }
  }

  // 2) 신규 사용자: 추가 정보 필요 → 회원가입 단계로 전환
  const socialInfo = (result as any).social_user_info || (result as any).user_info
  if (result.is_new_user && socialInfo) {
    return {
      success: true,
      action: 'redirect_to_signup',
      social_user_info: socialInfo,
      missing_fields: result.missing_fields,
      message: result.message
    } as any
  }

  // 3) 그 외: 오류 처리
  return {
    success: false,
    action: 'error',
    message: result.message || '소셜 로그인에 실패했습니다.'
  }
}

/**
 * 에러 메시지 한국어 변환
 */
export function getSocialLoginErrorMessage(error: any): string {
  const message = error?.message || error?.detail || String(error)
  
  if (message.includes('팝업')) return '팝업 차단이 활성화되어 있습니다. 팝업 차단을 해제해주세요.'
  if (message.includes('취소')) return '소셜 로그인이 취소되었습니다.'
  if (message.includes('token')) return '소셜 로그인 인증에 실패했습니다. 다시 시도해주세요.'
  if (message.includes('network') || message.includes('fetch')) return '네트워크 연결을 확인해주세요.'
  if (message.includes('timeout')) return '요청 시간이 초과되었습니다. 다시 시도해주세요.'
  
  return '소셜 로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
} 