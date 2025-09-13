/**
 * API 클라이언트 플러그인 (HttpOnly 쿠키 환경)
 * - 전역 $fetch 인스턴스 설정
 * - HttpOnly 쿠키 자동 전송 처리
 * - 요청/응답 인터셉터 구성
 * - 에러 핸들링
 */
import { defineNuxtPlugin, useRuntimeConfig, createError } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase ?? '/api') as string
  const { notifyError } = useNotify()

  // 동시성 제어: 간단한 Promise 공유
  let refreshPromise: Promise<any> | null = null

  // refresh token 요청 함수 (중복 요청 방지)
  const refreshToken = async (): Promise<any> => {
    // 이미 진행 중인 refresh가 있으면 그것을 기다림
    if (refreshPromise) {
      return await refreshPromise
    }

    // 새로운 refresh 시작
    refreshPromise = $fetch('/api/v1/auth/refresh', {
      baseURL: apiBase,
      method: 'POST' as const,
      credentials: 'include',
      body: {}
    }).finally(() => {
      refreshPromise = null // 완료 후 초기화
    })

    return await refreshPromise
  }

  // 커스텀 $fetch 인스턴스 생성 (HttpOnly 쿠키 환경)
  const api: typeof $fetch = $fetch.create({
    baseURL: apiBase,
    credentials: 'include', // HttpOnly 쿠키 자동 전송 (중요!)
    
    // 요청 전 인터셉터
    async onRequest({ request, options }) {
      // HttpOnly 쿠키는 브라우저가 자동으로 전송
      // Authorization 헤더 설정 불필요
      
      // 공통 헤더 설정 (Headers 안전 처리)
      const headers = new Headers(options.headers as HeadersInit)
      headers.set('Content-Type', 'application/json')
      headers.set('Accept', 'application/json')
      headers.set('X-Requested-With', 'XMLHttpRequest')

      // CSRF 토큰 처리 (서버에서 제공하는 경우)
      if (process.client) {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null
        const token = csrfMeta?.getAttribute('content')
        if (token) {
          headers.set('X-CSRF-Token', token)
        }
      }

      options.headers = headers

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
      if (process.client) {
        const token = response.headers.get('x-csrf-token')
        if (token) {
          const csrfMeta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null
          if (csrfMeta) {
            csrfMeta.setAttribute('content', token)
          }
        }
      }
    },

    // 응답 에러 인터셉터
    async onResponseError({ response, request, options }): Promise<any> {
      // 에러 로깅
      console.error('❌ API Error:', {
        status: response.status,
        url: request,
        data: response._data,
        timestamp: new Date().toISOString()
      })

      // 인증 에러 처리 (401) - 토큰 만료 또는 유효하지 않음 (자동 리프레시/리디렉션 금지)
      if (response.status === 401) {
        const isLoginRequest = request.toString().includes('/login')
        // 로그인 API 호출인 경우 토큰 갱신 시도하지 않고 바로 에러 메시지 반환
        if (isLoginRequest) {
          const errorData = response._data
          const errorMessage = errorData?.message || errorData?.error?.message || '아이디 또는 비밀번호가 올바르지 않습니다.'
          
          throw createError({
            statusCode: response.status,
            statusMessage: errorMessage,
            data: errorData
          })
        }
        
        // 정책: 자동 리프레시/리디렉션은 하지 않고 에러만 전달 (페이지 이동 시 미들웨어에서 처리)
        
        // 토큰 갱신 실패 시에도 적절한 에러 메시지 반환
        const errorData = response._data
        const errorMessage = errorData?.message || errorData?.error?.message || '인증이 필요합니다.'
        
        throw createError({
          statusCode: response.status,
          statusMessage: errorMessage,
          data: errorData
        })
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