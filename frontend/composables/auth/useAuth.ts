/**
 * 인증 관련 컴포저블
 * - 로그인/로그아웃 상태 관리
 * - HttpOnly 쿠키 기반 인증 시스템
 * - 토큰 자동 갱신 및 세션 관리
 */
import { ref, computed, onMounted, watch, readonly } from 'vue'
import { useRouter } from 'vue-router'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { isEmailFormat } from '~/composables/utils/validation'
import type { LoginRequest, LoginData, UserSession } from '~/types/user/models'

/**
 * 인증 상태 관리 컴포저블
 */
export const useAuth = () => {
  const router = useRouter()
  const { useLogin: useUserLogin, useLogout: useUserLogout, useRefreshToken } = useUserQueries()
  const { useLogin: useCounselorLogin, useLogout: useCounselorLogout } = useCounselorQueries()
  
  // 사용자 세션 상태
  const userSession = ref<UserSession | null>(null)
  const isAuthChecking = ref(true)
  
  // 컴퓨티드 속성들
  const isAuthenticated = computed(() => !!userSession.value?.isAuthenticated)
  const currentUser = computed(() => userSession.value)
  
  /**
   * 세션 정보를 로컬스토리지에서 복원
   */
  const restoreSession = () => {
    if (process.client) {
      try {
        const stored = localStorage.getItem('user_session')
        if (stored) {
          const session = JSON.parse(stored) as UserSession
          
          // 토큰 만료 시간 확인
          const now = Date.now()
          if (session.access_token_expires_at && session.access_token_expires_at > now) {
            userSession.value = session
          } else {
            // 액세스 토큰이 만료된 경우 리프레시 토큰으로 갱신 시도
            attemptTokenRefresh()
          }
        }
      } catch (error) {
        console.error('Failed to restore session:', error)
        clearSession()
      }
    }
    isAuthChecking.value = false
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
  const handleLoginSuccess = (data: LoginData) => {
    const now = Date.now()
    const session: UserSession = {
      user_id: data.user_id,
      email: data.email,
      nickname: data.nickname,
      isAuthenticated: true,
      loginAt: new Date().toISOString(),
      access_token_expires_at: now + (data.access_token_expires_in * 1000),
      refresh_token_expires_at: now + (data.refresh_token_expires_in * 1000)
    }
    
    saveSession(session)
    
    // 성공 메시지 (옵션)
    if (process.client) {
      // toast나 다른 알림 시스템이 있다면 여기서 사용
      console.log(`${data.nickname}님, 환영합니다!`)
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
    onSuccess: handleLoginSuccess,
    onError: handleLoginError
  })

  /**
   * 상담사 로그인 뮤테이션
   */
  const counselorLoginMutation = useCounselorLogin({
    onSuccess: handleLoginSuccess,
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
    onSuccess: (data) => {
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
    onError: (error) => {
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
      // 현재 세션이 상담사인지 사용자인지에 따라 적절한 API 호출
      // 일반적으로는 토큰에서 role을 확인하거나, 현재 세션 타입을 판단
      // 현재는 사용자 로그아웃을 기본으로 사용 (추후 role 기반 분기 가능)
      await userLogoutMutation.mutateAsync()
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
    if (!userSession.value?.refresh_token_expires_at) {
      clearSession()
      return false
    }
    
    const now = Date.now()
    if (userSession.value.refresh_token_expires_at <= now) {
      clearSession()
      return false
    }
    
    try {
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
  const requireAuth = () => {
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
  onMounted(() => {
    restoreSession()
    if (isAuthenticated.value) {
      startTokenCheck()
    }
  })
  
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
    
    // 가드 함수들
    requireAuth,
    requireGuest,
    
    // 유틸리티
    restoreSession,
    clearSession
  }
}