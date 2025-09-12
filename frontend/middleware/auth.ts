import { defineNuxtRouteMiddleware, navigateTo } from 'nuxt/app'
import { useAuth } from '~/composables/auth/useAuth'

/**
 * 전역 인증/역할 기반 미들웨어
 * - 페이지 메타에서 requiresAuth, requireRole을 읽어 가드 처리
 * - 세션 복원 비동기 처리 후 판단
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const { isAuthenticated, isAuthChecking, restoreSession, getCurrentRole } = useAuth()

  // 페이지 메타 선언으로 제어
  const requiresAuth = to.meta?.requiresAuth as boolean | undefined
  const requireRole = to.meta?.requireRole as ('user' | 'counselor') | undefined

  // 인증이 필요 없는 페이지는 통과
  if (!requiresAuth && !requireRole) return

  // 세션 복원 대기 (SSR에서도 session.server.ts가 프리로드하므로 빠르게 완료)
  if (isAuthChecking.value) {
    await restoreSession()
  }

  // 인증 필요 체크: SSR 단계에서는 리다이렉트를 최소화하고, 클라이언트에서 최종 판단
  if ((requiresAuth || requireRole) && !isAuthenticated.value) {
    if (process.server) return
    return navigateTo('/login')
  }

  // 역할 필요 체크
  if (requireRole) {
    const role = getCurrentRole()
    if (role !== requireRole) {
      // 역할 불일치 시 각 역할 기본 마이페이지로 라우팅
      return navigateTo(role === 'counselor' ? '/counselor/mypage' : '/mypage')
    }
  }
})


