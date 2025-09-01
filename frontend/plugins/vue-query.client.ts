/**
 * Vue Query (TanStack Query) 플러그인
 * - 전역 캐싱 및 상태 관리 (최소 구성)
 */
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { defineNuxtPlugin } from 'nuxt/app'

export default defineNuxtPlugin((nuxtApp) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,
        gcTime: 30 * 60 * 1000,
        refetchOnWindowFocus: false,
        refetchOnMount: true,
        refetchOnReconnect: true,
        retry: (failureCount, error: any) => {
          if (error?.statusCode && [401, 403, 404].includes(error.statusCode)) return false
          return failureCount < 3
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
      },
      mutations: {
        retry: (failureCount, error: any) => {
          if (error?.statusCode && error.statusCode < 500) return false
          return failureCount < 2
        }
      }
    }
  })

  nuxtApp.vueApp.use(VueQueryPlugin, { queryClient })

  return { provide: { queryClient } }
})