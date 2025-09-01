/**
 * API 클라이언트 플러그인 (HttpOnly 쿠키 환경)
 * - 전역 $fetch 인스턴스 설정
 * - HttpOnly 쿠키 자동 전송 처리
 * - 요청/응답 인터셉터 구성
 * - 에러 핸들링
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  // 커스텀 $fetch 인스턴스 생성 (HttpOnly 쿠키 환경)
  const api = $fetch.create({
    baseURL: config.public.apiBase,
    credentials: 'include', // HttpOnly 쿠키 자동 전송 (중요!)
    
    // 요청 전 인터셉터
    async onRequest({ request, options }) {
      // HttpOnly 쿠키는 브라우저가 자동으로 전송
      // Authorization 헤더 설정 불필요
      
      // 공통 헤더 설정
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }

      // CSRF 토큰 처리 (서버에서 제공하는 경우)
      if (process.client) {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]')
        if (csrfMeta) {
          options.headers['X-CSRF-Token'] = csrfMeta.getAttribute('content')
        }
      }

      // 요청 로깅 (개발 환경)
      if (process.dev) {
        console.log('🚀 API Request:', {
          url: request,
          method: options.method || 'GET',
          headers: options.headers,
          body: options.body
        })
      }
    },

    // 응답 성공 인터셉터
    onResponse({ response }) {
      // 응답 로깅 (개발 환경)
      if (process.dev) {
        console.log('✅ API Response:', {
          status: response.status,
          url: response.url,
          data: response._data
        })
      }

      // 새로운 CSRF 토큰 업데이트 (헤더에서 제공하는 경우)
      if (process.client && response.headers.get('x-csrf-token')) {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]')
        if (csrfMeta) {
          csrfMeta.setAttribute('content', response.headers.get('x-csrf-token'))
        }
      }
    },

    // 응답 에러 인터셉터
    async onResponseError({ response, request }) {
      // 에러 로깅
      console.error('❌ API Error:', {
        status: response.status,
        url: request,
        data: response._data,
        timestamp: new Date().toISOString()
      })

      // 인증 에러 처리 (401)
      if (response.status === 401) {
        // HttpOnly 쿠키는 서버에서 자동 삭제됨
        // 클라이언트에서 별도 처리 불필요
        
        // 로그인 페이지로 리다이렉트
        if (process.client) {
          await navigateTo('/login', { replace: true })
        }
        return
      }

      // 권한 에러 (403)
      if (response.status === 403) {
        throw createError({
          statusCode: 403,
          statusMessage: '접근 권한이 없습니다.'
        })
      }

      // 서버 에러 (5xx)
      if (response.status >= 500) {
        throw createError({
          statusCode: response.status,
          statusMessage: '서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
        })
      }

      // 클라이언트 에러 (4xx)
      if (response.status >= 400) {
        const errorData = response._data
        const errorMessage = errorData?.message || errorData?.detail || '요청 처리 중 오류가 발생했습니다.'
        
        throw createError({
          statusCode: response.status,
          statusMessage: errorMessage,
          data: errorData
        })
      }

      // 기타 에러
      throw createError({
        statusCode: response.status || 500,
        statusMessage: '알 수 없는 오류가 발생했습니다.'
      })
    }
  })

  return {
    provide: {
      api
    }
  }
})