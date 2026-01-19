/**
 * 토큰 관리 유틸리티
 * HttpOnly 쿠키와 메모리를 사용한 안전한 토큰 관리
 */

interface TokenStore {
  accessToken: string | null
  expiresAt: number | null
}

// 메모리에 액세스 토큰 저장 (XSS 방어)
let tokenStore: TokenStore = {
  accessToken: null,
  expiresAt: null
}

export const useAuthToken = () => {
  /**
   * 액세스 토큰을 메모리에 저장
   */
  const setAccessToken = (token: string, expiresIn: number) => {
    tokenStore.accessToken = token
    tokenStore.expiresAt = Date.now() + (expiresIn * 1000)
  }

  /**
   * 메모리에서 액세스 토큰 가져오기
   */
  const getAccessToken = (): string | null => {
    // 토큰이 만료되었는지 확인
    if (tokenStore.expiresAt && Date.now() > tokenStore.expiresAt) {
      clearTokens()
      return null
    }
    return tokenStore.accessToken
  }

  /**
   * 리프레시 토큰을 HttpOnly 쿠키에 저장 (서버 사이드)
   * 이 함수는 서버 API 응답에서 Set-Cookie 헤더로 처리되어야 함
   */
  const setRefreshTokenCookie = () => {
    // 서버에서 HttpOnly 쿠키로 설정
    // 클라이언트에서는 직접 설정할 수 없음
    console.info('Refresh token은 서버에서 HttpOnly 쿠키로 설정됩니다.')
  }

  /**
   * 토큰 새로고침
   */
  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      // Native fetch를 사용하여 401 에러 시 콘솔 출력 방지
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include', // 쿠키 포함
        headers: {
          'Content-Type': 'application/json',
        }
      })

      // 401 응답은 정상적인 로그아웃 상태
      if (response.status === 401) {
        return false // 조용히 실패 처리
      }

      // 다른 에러 상태
      if (!response.ok) {
        console.error('Token refresh failed with status:', response.status)
        return false
      }

      // 성공 응답 처리
      const data = await response.json()
      if (data.access_token) {
        setAccessToken(data.access_token, data.expires_in || 1800)
        return true
      }
      
      return false
    } catch (error: any) {
      // 네트워크 오류 등
      console.error('Token refresh network error:', error)
      return false
    }
  }

  /**
   * 모든 토큰 제거
   */
  const clearTokens = () => {
    tokenStore.accessToken = null
    tokenStore.expiresAt = null
    
    // 로그아웃 API 호출 시 서버가 HttpOnly 쿠키를 제거함
  }

  /**
   * 인증된 API 요청 헬퍼
   */
  const authenticatedFetch = async <T>(url: string, options: any = {}): Promise<T> => {
    // 액세스 토큰 확인
    let accessToken = getAccessToken()
    
    // 토큰이 없거나 만료된 경우 새로고침 시도
    if (!accessToken) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        accessToken = getAccessToken()
      } else {
        // 새로고침 실패 시 로그인 페이지로 리다이렉트
        await navigateTo('/login')
        throw new Error('인증이 필요합니다.')
      }
    }

    // 요청 헤더에 액세스 토큰 추가
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`
    }

    try {
      return await $fetch<T>(url, {
        ...options,
        headers,
        credentials: 'include' // 쿠키 포함
      })
    } catch (error: any) {
      // 401 에러인 경우 토큰 새로고침 시도
      if (error.status === 401) {
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          // 새로운 토큰으로 재시도
          const newAccessToken = getAccessToken()
          headers.Authorization = `Bearer ${newAccessToken}`
          return await $fetch<T>(url, {
            ...options,
            headers,
            credentials: 'include'
          })
        } else {
          // 새로고침 실패 시 로그인 페이지로
          await navigateTo('/login')
          throw new Error('인증이 필요합니다.')
        }
      }
      throw error
    }
  }

  /**
   * 초기화 - 페이지 로드 시 토큰 복구
   */
  const initializeAuth = async () => {
    // 1. 메모리에 유효한 액세스 토큰이 있으면 그대로 사용
    if (tokenStore.accessToken && tokenStore.expiresAt && Date.now() < tokenStore.expiresAt) {
      return
    }
    
    // 2. 브라우저 환경이 아니면 종료 (SSR 호환성)
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return
    }
    
    // 3. refresh_token 쿠키가 있는지 확인
    const hasRefreshToken = document.cookie
      .split(';')
      .some(cookie => cookie.trim().startsWith('refresh_token='))
    
    // 4. 리프레시 토큰이 없으면 인증 초기화 불가
    if (!hasRefreshToken) {
      return
    }
    
    // 5. 리프레시 토큰이 있을 때만 새로운 액세스 토큰 발급 시도
    await refreshAccessToken()
  }

  return {
    setAccessToken,
    getAccessToken,
    refreshAccessToken,
    clearTokens,
    authenticatedFetch,
    initializeAuth
  }
}