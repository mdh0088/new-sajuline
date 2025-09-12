import { defineNuxtPlugin, useRuntimeConfig, useRequestHeaders, useState } from 'nuxt/app'
import type { APIResponse } from '~/types/common/api'
import type { UserSession } from '~/types/user/models'

interface TokenPayload {
  sub: string
  email: string
  role: 'user' | 'counselor'
  exp?: number
  iat?: number
  jti?: string
  token_type?: 'access' | 'refresh'
}

export default defineNuxtPlugin(async () => {
  if (!process.server) return

  const headers = useRequestHeaders(['cookie'])
  const cookie = headers.cookie || ''
  if (!cookie) return

  const config = useRuntimeConfig()

  try {
    const me = await $fetch<APIResponse<TokenPayload>>('/api/v1/auth/me', {
      baseURL: (config.public.apiBase ?? '/api') as string,
      credentials: 'include',
      headers: { cookie }
    })

    if (me?.success && me.data) {
      const session: UserSession = {
        user_id: me.data.sub,
        email: me.data.email,
        nickname: '', // SSR 프리로드 단계에서는 상세 정보 미확정
        isAuthenticated: true,
        loginAt: new Date().toISOString(),
        access_token_expires_at: me.data.exp ? me.data.exp * 1000 : undefined,
        refresh_token_expires_at: undefined,
        role: me.data.role
      }

      const ssrSession = useState<UserSession | null>('user_session', () => null)
      ssrSession.value = session
    }
  } catch (_err) {
    // 인증되지 않은 요청이거나 토큰 만료 등: SSR 프리로드는 조용히 패스
  }
})
