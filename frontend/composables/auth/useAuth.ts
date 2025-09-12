/**
 * 인증 관련 컴포저블
 * - 로그인/로그아웃 상태 관리
 * - HttpOnly 쿠키 기반 인증 시스템
 * - 토큰 자동 갱신 및 세션 관리
 */
import { ref, computed, onMounted, watch, readonly } from 'vue'
import { useRouter } from 'vue-router'
import { useState } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { useAuthQueries } from '~/composables/api/useAuthQueries'
import { isEmailFormat } from '~/composables/utils/validation'
import type { LoginRequest, LoginData, UserSession, TokenResponse } from '~/types/user/models'
import type { APIError } from '~/types/common/api'

/**
 * 인증 상태 관리 컴포저블
 */
export const useAuth = () => {
  const router = useRouter()
  const { notifySuccess } = useNotify()
  const { useLogin: useUserLogin, useLogout: useUserLogout } = useUserQueries()
  const { useLogin: useCounselorLogin, useLogout: useCounselorLogout } = useCounselorQueries()
  const { useRefreshToken } = useAuthQueries()
  
  // 사용자 세션 상태
  const userSession = ref<UserSession | null>(null)
  const isAuthChecking = ref(true)
  
  // 컴퓨티드 속성들
  const isAuthenticated = computed(() => !!userSession.value?.isAuthenticated)
  const role = computed<('user' | 'counselor') | null>(() => userSession.value?.role ?? null)
  const isUser = computed(() => role.value === 'user')
  const isCounselor = computed(() => role.value === 'counselor')
  const currentUser = computed(() => userSession.value)
  
  /**
   * 세션 정보를 로컬스토리지에서 복원
   */
  const restoreSession = async () => {
    try {
      // SSR: 서버에서 프리로드된 세션(useState)에 우선 의존
      if (process.server) {
        const ssrSession = useState<UserSession | null>('user_session')
        if (ssrSession.value?.isAuthenticated) {
          userSession.value = ssrSession.value
          return
        }
      }

      // CSR: 하이드레이션된 세션이 있으면 우선 사용 → 없으면 localStorage → 필요 시 refresh
      if (process.client) {
        const hydrated = useState<UserSession | null>('user_session')
        if (hydrated.value?.isAuthenticated) {
          userSession.value = hydrated.value
          // 로컬 저장소 동기화(초기 로드 시 공백 방지)
          localStorage.setItem('user_session', JSON.stringify(hydrated.value))
          return
        }

        const stored = localStorage.getItem('user_session')
        if (stored) {
          const session = JSON.parse(stored) as UserSession

          // 토큰 만료 시간 확인
          const now = Date.now()
          if (session.access_token_expires_at && session.access_token_expires_at > now) {
            userSession.value = session
          } else {
            // 액세스 토큰이 만료된 경우 리프레시 토큰으로 갱신 시도 (대기)
            await attemptTokenRefresh()
          }
        }
      }
    } catch (error) {
      console.error('Failed to restore session:', error)
      clearSession()
    } finally {
      isAuthChecking.value = false
    }
  }
  
  /**
   * 세션 정보를 로컬스토리지에 저장
   */
  const saveSession = (session: UserSession) => {
    if (process.client) {
      localStorage.setItem('user_session', JSON.stringify(session))
    }
    userSession.value = session
  }
  
  /**
   * 세션 정보 클리어
   */
  const clearSession = () => {
    if (process.client) {
      localStorage.removeItem('user_session')
    }
    userSession.value = null
  }
  
  /**
   * 세션 저장 성공 핸들러
   */
  const handleLoginSuccessWithRole = (data: LoginData, sessionRole: 'user' | 'counselor') => {
    const now = Date.now()
    const session: UserSession = {
      user_id: data.user_id,
      email: data.email,
      nickname: data.nickname,
      isAuthenticated: true,
      loginAt: new Date().toISOString(),
      access_token_expires_at: now + (data.access_token_expires_in * 1000),
      refresh_token_expires_at: now + (data.refresh_token_expires_in * 1000),
      role: sessionRole
    }
    
    saveSession(session)
    
    // 성공 메시지 (옵션)
    if (process.client) {
      // 유틸리티 함수로 간편하게 환영 알림 표시
      notifySuccess(`🎉 ${data.nickname}님, 환영합니다!`)
    }
  }

  /**
   * 로그인 실패 핸들러
   */
  const handleLoginError = (error: any) => {
    console.error('Login failed:', error)
    clearSession()
  }

  /**
   * 사용자 로그인 뮤테이션
   */
  const userLoginMutation = useUserLogin({
    onSuccess: (data) => handleLoginSuccessWithRole(data, 'user'),
    onError: handleLoginError
  })

  /**
   * 상담사 로그인 뮤테이션
   */
  const counselorLoginMutation = useCounselorLogin({
    onSuccess: (data) => handleLoginSuccessWithRole(data, 'counselor'),
    onError: handleLoginError
  })
  
  /**
   * 사용자 로그아웃 뮤테이션
   */
  const userLogoutMutation = useUserLogout({
    onSuccess: () => {
      clearSession()
      router.push('/login')
    },
    onError: (error) => {
      console.error('User logout failed:', error)
      // 로그아웃 실패해도 로컬 세션은 클리어
      clearSession()
      router.push('/login')
    }
  })

  /**
   * 상담사 로그아웃 뮤테이션
   */
  const counselorLogoutMutation = useCounselorLogout({
    onSuccess: () => {
      clearSession()
      router.push('/login')
    },
    onError: (error) => {
      console.error('Counselor logout failed:', error)
      // 로그아웃 실패해도 로컬 세션은 클리어
      clearSession()
      router.push('/login')
    }
  })
  
  /**
   * 토큰 갱신 뮤테이션 설정
   */
  const refreshMutation = useRefreshToken({
    onSuccess: (data: TokenResponse) => {
      if (userSession.value) {
        const now = Date.now()
        const updatedSession: UserSession = {
          ...userSession.value,
          access_token_expires_at: now + (data.access_token_expires_in * 1000),
          refresh_token_expires_at: now + (data.refresh_token_expires_in * 1000)
        }
        saveSession(updatedSession)
      }
    },
    onError: (error: APIError) => {
      console.error('Token refresh failed:', error)
      clearSession()
      router.push('/login')
    }
  })
  
  /**
   * 로그인 실행 (이메일 형식에 따른 API 분기)
   */
  const login = async (credentials: LoginRequest) => {
    try {
      // 이메일 형식 체크하여 적절한 API 호출
      if (isEmailFormat(credentials.user_id)) {
        // 이메일 형식이면 상담사 로그인 API 사용
        await counselorLoginMutation.mutateAsync(credentials)
      } else {
        // 이메일 형식이 아니면 사용자 로그인 API 사용
        await userLoginMutation.mutateAsync(credentials)
      }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '로그인에 실패했습니다.' 
      }
    }
  }
  
  /**
   * 로그아웃 실행
   */
  const logout = async () => {
    try {
      if (userSession.value?.role === 'counselor') {
        await counselorLogoutMutation.mutateAsync()
      } else {
        await userLogoutMutation.mutateAsync()
      }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '로그아웃에 실패했습니다.' 
      }
    }
  }
  
  /**
   * 토큰 갱신 시도
   */
  const attemptTokenRefresh = async () => {
    try {
      // HttpOnly 쿠키 환경에서는 Refresh 토큰의 클라이언트 만료 추적 대신 서버에 위임
      await refreshMutation.mutateAsync({})
      return true
    } catch (error) {
      clearSession()
      return false
    }
  }
  
  /**
   * 토큰 만료 확인 및 자동 갱신
   */
  const checkTokenExpiry = async () => {
    if (!userSession.value?.access_token_expires_at) {
      return false
    }
    
    const now = Date.now()
    const expiresAt = userSession.value.access_token_expires_at
    const timeUntilExpiry = expiresAt - now
    
    // 토큰이 5분 이내에 만료되는 경우 갱신 시도
    if (timeUntilExpiry <= 5 * 60 * 1000) {
      return await attemptTokenRefresh()
    }
    
    return true
  }
  
  /**
   * 인증이 필요한 페이지 가드
   */
  const requireAuth = async () => {
    if (isAuthChecking.value) {
      await restoreSession()
    }
    if (!isAuthenticated.value) {
      router.push('/login')
      return false
    }
    return true
  }
  
  /**
   * 인증된 사용자는 접근할 수 없는 페이지 가드 (로그인 페이지 등)
   */
  const requireGuest = () => {
    if (isAuthenticated.value) {
      router.push('/')
      return false
    }
    return true
  }
  
  /**
   * 정기적인 토큰 만료 체크 설정
   */
  let tokenCheckInterval: NodeJS.Timeout | null = null
  
  const startTokenCheck = () => {
    if (tokenCheckInterval) {
      clearInterval(tokenCheckInterval)
    }
    
    // 1분마다 토큰 만료 체크
    tokenCheckInterval = setInterval(() => {
      if (isAuthenticated.value) {
        checkTokenExpiry()
      }
    }, 60 * 1000)
  }
  
  const stopTokenCheck = () => {
    if (tokenCheckInterval) {
      clearInterval(tokenCheckInterval)
      tokenCheckInterval = null
    }
  }
  
  /**
   * 컴포넌트 마운트 시 초기화
   */
  if (process.client) {
    onMounted(() => {
      // 세션 복원은 비동기 수행 (중복 호출 방지)
      restoreSession()
      if (isAuthenticated.value) {
        startTokenCheck()
      }
    })
  }

  /** 세션 역할 설정 (API 호출 없이 세션만 갱신) */
  const setRole = (newRole: 'user' | 'counselor') => {
    if (userSession.value) {
      const updated: UserSession = { ...userSession.value, role: newRole }
      saveSession(updated)
    }
  }

  /** 간단 권한 체크 유틸 */
  const hasRole = (required: 'user' | 'counselor') => role.value === required
  const getCurrentRole = () => role.value
  
  /**
   * 사용자 정보 업데이트 (프로필 수정 후 등)
   */
  const updateUserInfo = (updates: Partial<Pick<UserSession, 'nickname' | 'email'>>) => {
    if (userSession.value) {
      const updatedSession = { ...userSession.value, ...updates }
      saveSession(updatedSession)
    }
  }
  
  /**
   * 로그인 상태 변경 감지
   */
  watch(isAuthenticated, (newValue) => {
    if (newValue) {
      startTokenCheck()
    } else {
      stopTokenCheck()
    }
  })
  
  return {
    // 상태
    userSession: readonly(userSession),
    isAuthenticated,
    currentUser,
    isAuthChecking,
    role,
    isUser,
    isCounselor,
    
    // 로딩 상태
    isLoginLoading: computed(() => userLoginMutation.isPending.value || counselorLoginMutation.isPending.value),
    isLogoutLoading: computed(() => userLogoutMutation.isPending.value || counselorLogoutMutation.isPending.value),
    isRefreshLoading: computed(() => refreshMutation.isPending.value),
    
    // 메서드
    login,
    logout,
    attemptTokenRefresh,
    checkTokenExpiry,
    updateUserInfo,
    setRole,
    hasRole,
    getCurrentRole,
    
    // 가드 함수들
    requireAuth,
    requireGuest,
    
    // 유틸리티
    restoreSession,
    clearSession
  }
}