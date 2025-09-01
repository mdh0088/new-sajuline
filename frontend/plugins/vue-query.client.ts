/**
 * Vue Query (TanStack Query) 플러그인
 * - 전역 캐싱 및 상태 관리
 * - HTTP Only 쿠키 환경에 최적화
 * - 사주라인 프로젝트 특화 설정
 */
import { QueryClient, VueQueryPlugin, type MutationCache, type QueryCache } from '@tanstack/vue-query'

export default defineNuxtPlugin((nuxtApp) => {
  const { $router } = nuxtApp

  // Query 에러 핸들링
  const queryCache = new QueryCache({
    onError: (error: any, query) => {
      console.error(`Query failed [${query.queryKey}]:`, error)
      
      // 401 에러 처리 (인증 실패)
      if (error.statusCode === 401) {
        // 로그인 페이지로 리다이렉트
        $router.push('/login')
      }
    }
  })

  // Mutation 에러 핸들링
  const mutationCache = new MutationCache({
    onError: (error: any, variables, context, mutation) => {
      console.error(`Mutation failed:`, error)
      
      // 401 에러 처리
      if (error.statusCode === 401) {
        $router.push('/login')
      }
    }
  })

  // QueryClient 설정
  const queryClient = new QueryClient({
    queryCache,
    mutationCache,
    defaultOptions: {
      queries: {
        // 사주라인 프로젝트 특화 설정
        staleTime: 5 * 60 * 1000,        // 5분 - 운세 데이터 등은 자주 변하지 않음
        gcTime: 30 * 60 * 1000,         // 30분 - 메모리 효율성 고려
        refetchOnWindowFocus: false,     // 윈도우 포커스 시 자동 리페칭 비활성화
        refetchOnMount: true,            // 컴포넌트 마운트 시 리페칭
        refetchOnReconnect: true,        // 네트워크 재연결 시 리페칭
        retry: (failureCount, error: any) => {
          // 401, 403, 404는 재시도 안함
          if (error.statusCode && [401, 403, 404].includes(error.statusCode)) {
            return false
          }
          // 3회까지 재시도
          return failureCount < 3
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
      },
      mutations: {
        // Mutation 기본 설정
        retry: (failureCount, error: any) => {
          // 클라이언트 에러는 재시도 안함
          if (error.statusCode && error.statusCode < 500) {
            return false
          }
          return failureCount < 2
        }
      }
    }
  })

  // Vue Query 플러그인 등록
  nuxtApp.vueApp.use(VueQueryPlugin, {
    queryClient
  })

  // QueryClient를 전역에서 사용할 수 있도록 제공
  return {
    provide: {
      queryClient
    }
  }
})