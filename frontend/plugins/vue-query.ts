/**
 * Vue Query (TanStack Query) SSR 호환 플러그인
 * - 서버사이드 렌더링과 클라이언트 하이드레이션 완벽 지원
 * - 상태 동기화 및 캐싱 최적화
 */
import type { DehydratedState } from '@tanstack/vue-query'
import { VueQueryPlugin, QueryClient, hydrate, dehydrate } from '@tanstack/vue-query'

export default defineNuxtPlugin((nuxtApp) => {
  // 서버와 클라이언트 간 Vue Query 상태 공유
  const vueQueryState = useState<DehydratedState | null>('vue-query')
  
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,        // 5분 - 사주라인 사용자 정보는 자주 변하지 않음
        gcTime: 30 * 60 * 1000,          // 30분 - 가비지 컬렉션 시간
        refetchOnWindowFocus: false,     // 포커스 시 자동 리프레시 비활성화
        refetchOnMount: 'always',        // 마운트 시 항상 리프레시
        refetchOnReconnect: true,        // 재연결 시 리프레시
        retry: (failureCount, error: any) => {
          // 클라이언트 오류(4xx)는 재시도 안함
          if (error?.statusCode && [401, 403, 404].includes(error.statusCode)) return false
          return failureCount < 3
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000) // 지수 백오프
      },
      mutations: {
        retry: (failureCount, error: any) => {
          // 서버 오류(5xx)만 재시도
          if (error?.statusCode && error.statusCode < 500) return false
          return failureCount < 2
        }
      }
    }
  })

  // Vue Query 플러그인 등록
  nuxtApp.vueApp.use(VueQueryPlugin, { queryClient })

  // 서버사이드: 렌더링 완료 후 쿼리 상태를 dehydrate하여 저장
  if (process.server) {
    nuxtApp.hooks.hook('app:rendered', () => {
      vueQueryState.value = dehydrate(queryClient)
    })
  }

  // 클라이언트사이드: 앱 생성 시 서버에서 dehydrate된 상태를 hydrate
  if (process.client) {
    nuxtApp.hooks.hook('app:created', () => {
      if (vueQueryState.value) {
        hydrate(queryClient, vueQueryState.value)
      }
    })
  }

  return { 
    provide: { 
      queryClient 
    } 
  }
})