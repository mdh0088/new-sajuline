import { defineNuxtRouteMiddleware, navigateTo } from 'nuxt/app'
import type { RouteLocationNormalized } from 'vue-router'
import { useAuth } from '~/composables/auth/useAuth'

/**
 * 전역 인증/역할 기반 미들웨어
 * - 페이지 메타에서 requiresAuth, requireRole을 읽어 가드 처리
 * - 세션 복원 비동기 처리 후 판단
 */
// 정책 헬퍼: 메타 판독 로직을 중앙화
const requireAuth = (to: RouteLocationNormalized): boolean => {
  const requiresAuth = to.meta?.requiresAuth as boolean | undefined
  const requireRole = to.meta?.requireRole as ('user' | 'counselor') | undefined
  return !!requiresAuth || !!requireRole
}

const requireGuest = (to: RouteLocationNormalized): boolean => {
  const guestOnly = to.meta?.guestOnly as boolean | undefined
  return !!guestOnly
}

const getRequiredRole = (to: RouteLocationNormalized): ('user' | 'counselor') | undefined => {
  return to.meta?.requireRole as ('user' | 'counselor') | undefined
}

// 중복 리다이렉트 헬퍼
const goLogin = (to: RouteLocationNormalized) => {
  const redirect = to.fullPath || '/'
  return navigateTo({ path: '/login', query: { redirect } }, { redirectCode: 302 })
}

export default defineNuxtRouteMiddleware(async (to) => {
  const { isAuthenticated, isAuthChecking, restoreSession, getCurrentRole, checkTokenExpiry, attemptTokenRefresh, clearSession } = useAuth()

  const needsAuth = requireAuth(to)
  const requiredRole = getRequiredRole(to)

  // 인증이 필요 없는 페이지는 통과
  if (!needsAuth && !requiredRole && !requireGuest(to)) return

  // 세션 복원 대기 (SSR에서도 session.server.ts가 프리로드하므로 빠르게 완료)
  if (isAuthChecking.value) {
    await restoreSession()
  }

  // 게스트 전용 페이지 보호 (로그인 상태면 접근 차단)
  if (requireGuest(to) && isAuthenticated.value) {
    return navigateTo('/user/mypage')
  }

  // 인증 필요 체크: SSR/CSR 모두에서 즉시 리다이렉트하여 초기 렌더 노출 방지
  if (needsAuth && !isAuthenticated.value) {
    return goLogin(to)
  }

  // 내비게이션 시 토큰 상태 점검 정책 (게스트 제외, 클라이언트 전용 refresh 실행)
  if (needsAuth && isAuthenticated.value) {
    // 만료 여부 확인
    const valid = await checkTokenExpiry()
    if (!valid) {
      // 만료됨 → 로그아웃 처리 후 로그인 페이지로 (SSR/CSR 공통)
      clearSession()
      return goLogin(to)
    } else if (process.client) {
      // 아직 만료는 아니면 즉시 refresh 호출로 수명 연장 (실패 시 로그아웃)
      try {
        await attemptTokenRefresh()
      } catch {
        clearSession()
        return goLogin(to)
      }
    }
  }

  // 역할 필요 체크
  if (requiredRole) {
    const role = getCurrentRole()
    if (role !== requiredRole) {
      // 역할 불일치 시 각 역할 기본 마이페이지로 라우팅
      return navigateTo(role === 'counselor' ? '/counselor/mypage' : '/user/mypage')
    }
  }
})


