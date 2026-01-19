/**
 * 클라이언트 사이드 인증 초기화 플러그인
 * 페이지 로드 시 인증 상태를 복구 (토큰이 있을 때만)
 */
export default defineNuxtPlugin(async (nuxtApp) => {
  const { initializeAuth, getAccessToken } = useAuthToken()
  const userStore = useUserStore()

  // 인증 초기화 (토큰이 없으면 자동으로 스킵됨)
  await initializeAuth()

  // 액세스 토큰이 있으면 사용자 정보 로드
  if (getAccessToken()) {
    try {
      await userStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user on initialization:', error)
    }
  }
})