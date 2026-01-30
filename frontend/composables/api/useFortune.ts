/**
 * 운세 API 컴포저블 (인증 필수)
 *
 * TanStack Query 기반 운세 데이터 조회 및 캐싱
 * - 일/주/월/연 운세 조회
 * - 캐시 TTL: 각 기간별 매칭 (daily: 24h, weekly: 7d, monthly: 30d, yearly: 365d)
 *
 * Backend: backend/src/api/v1/fortune_api.py
 */
import { computed, unref, type Ref } from 'vue'
import { useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/vue-query'
import { useNuxtApp } from 'nuxt/app'
import type { IFortune, IFortuneResponse, FortuneType, FortuneErrorCode } from '~/types/fortune'
import type { APIError } from '~/types/common/api'

// =============================================================================
// 캐시 TTL 상수 (밀리초)
// =============================================================================

const FORTUNE_STALE_TIME = {
  daily: 24 * 60 * 60 * 1000,      // 24시간
  weekly: 7 * 24 * 60 * 60 * 1000, // 7일
  monthly: 30 * 24 * 60 * 60 * 1000, // 30일
  yearly: 365 * 24 * 60 * 60 * 1000, // 365일
} as const

// gcTime은 staleTime과 동일하게 설정하여 캐시 불일치 방지
const FORTUNE_GC_TIME = {
  daily: 24 * 60 * 60 * 1000,
  weekly: 7 * 24 * 60 * 60 * 1000,
  monthly: 30 * 24 * 60 * 60 * 1000,
  yearly: 365 * 24 * 60 * 60 * 1000,
} as const

// =============================================================================
// 에러 메시지 매핑 (Task 3.1 + H2 수정)
// =============================================================================

const FORTUNE_ERROR_MESSAGES: Record<FortuneErrorCode, string> = {
  SAJU_INFO_REQUIRED: '사주 정보를 먼저 등록해주세요',
  INVALID_DATE_RANGE: '조회 가능한 날짜 범위를 벗어났습니다',
  USER_NOT_FOUND: '사용자 정보를 찾을 수 없습니다',
  RATE_LIMIT_EXCEEDED: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요',
}

// =============================================================================
// 에러 클래스 (H3 수정 - 타입 안전성)
// =============================================================================

/**
 * Fortune API 에러 클래스
 */
class FortuneApiError extends Error {
  readonly statusCode: number
  readonly code?: FortuneErrorCode
  readonly data?: unknown

  constructor(message: string, statusCode: number = 400, code?: FortuneErrorCode, data?: unknown) {
    super(message)
    this.name = 'FortuneApiError'
    this.statusCode = statusCode
    this.code = code
    this.data = data
  }
}

/**
 * API 에러 코드에서 사용자 친화적 메시지 반환
 */
const getFortuneErrorMessage = (error: unknown): string => {
  if (!error || typeof error !== 'object') {
    return '운세 조회에 실패했습니다'
  }

  const errorObj = error as Record<string, unknown>

  // 서버에서 반환한 에러 코드 추출
  const errorData = errorObj.data as Record<string, unknown> | undefined
  const errorCode = (errorData?.error as Record<string, unknown>)?.code ||
                    (errorData?.detail as Record<string, unknown>)?.code

  if (errorCode && typeof errorCode === 'string' && errorCode in FORTUNE_ERROR_MESSAGES) {
    return FORTUNE_ERROR_MESSAGES[errorCode as FortuneErrorCode]
  }

  // 서버 에러 메시지 사용
  const serverMessage = (errorData?.error as Record<string, unknown>)?.message ||
                        (errorData?.detail as Record<string, unknown>)?.message ||
                        errorObj.message

  if (typeof serverMessage === 'string' && serverMessage) {
    return serverMessage
  }

  return '운세 조회에 실패했습니다'
}

/**
 * 에러 코드 추출
 */
const extractErrorCode = (error: unknown): FortuneErrorCode | undefined => {
  if (!error || typeof error !== 'object') return undefined

  const errorObj = error as Record<string, unknown>
  const errorData = errorObj.data as Record<string, unknown> | undefined
  const code = (errorData?.error as Record<string, unknown>)?.code ||
               (errorData?.detail as Record<string, unknown>)?.code

  if (typeof code === 'string' && code in FORTUNE_ERROR_MESSAGES) {
    return code as FortuneErrorCode
  }
  return undefined
}

// =============================================================================
// 내부 API 함수 (Task 2.2)
// =============================================================================

const fortuneApi = {
  /**
   * 일일 운세 조회
   * GET /api/v1/fortune/daily?date=YYYY-MM-DD
   */
  async getDailyFortune(date?: string): Promise<IFortune> {
    const { $api } = useNuxtApp()
    // M3 수정: URL 인코딩 적용
    const url = date
      ? `/api/v1/fortune/daily?date=${encodeURIComponent(date)}`
      : '/api/v1/fortune/daily'
    const res = await $api<IFortuneResponse>(url, { method: 'GET' })

    if (!res.success || !res.data) {
      const errorCode = extractErrorCode(res)
      throw new FortuneApiError(
        getFortuneErrorMessage(res),
        res.error ? 400 : 500,
        errorCode,
        res
      )
    }

    return res.data
  },

  /**
   * 주간 운세 조회
   * GET /api/v1/fortune/weekly
   */
  async getWeeklyFortune(): Promise<IFortune> {
    const { $api } = useNuxtApp()
    const res = await $api<IFortuneResponse>('/api/v1/fortune/weekly', { method: 'GET' })

    if (!res.success || !res.data) {
      const errorCode = extractErrorCode(res)
      throw new FortuneApiError(
        getFortuneErrorMessage(res),
        res.error ? 400 : 500,
        errorCode,
        res
      )
    }

    return res.data
  },

  /**
   * 월간 운세 조회
   * GET /api/v1/fortune/monthly
   */
  async getMonthlyFortune(): Promise<IFortune> {
    const { $api } = useNuxtApp()
    const res = await $api<IFortuneResponse>('/api/v1/fortune/monthly', { method: 'GET' })

    if (!res.success || !res.data) {
      const errorCode = extractErrorCode(res)
      throw new FortuneApiError(
        getFortuneErrorMessage(res),
        res.error ? 400 : 500,
        errorCode,
        res
      )
    }

    return res.data
  },

  /**
   * 연간 운세 조회
   * GET /api/v1/fortune/yearly
   */
  async getYearlyFortune(): Promise<IFortune> {
    const { $api } = useNuxtApp()
    const res = await $api<IFortuneResponse>('/api/v1/fortune/yearly', { method: 'GET' })

    if (!res.success || !res.data) {
      const errorCode = extractErrorCode(res)
      throw new FortuneApiError(
        getFortuneErrorMessage(res),
        res.error ? 400 : 500,
        errorCode,
        res
      )
    }

    return res.data
  },

  /**
   * 기간별 운세 조회 (AC 4 - 통합 함수)
   * H1 수정: AC 요구사항에 맞는 통합 함수 추가
   */
  async getFortune(type: FortuneType, date?: string): Promise<IFortune> {
    switch (type) {
      case 'daily':
        return this.getDailyFortune(date)
      case 'weekly':
        return this.getWeeklyFortune()
      case 'monthly':
        return this.getMonthlyFortune()
      case 'yearly':
        return this.getYearlyFortune()
      default:
        throw new FortuneApiError(`지원하지 않는 운세 유형: ${type}`, 400)
    }
  },
}

// =============================================================================
// Composable 함수 (Task 2.3)
// =============================================================================

/**
 * 운세 API Composable
 *
 * @example
 * ```ts
 * const { useDailyFortune, useWeeklyFortune, useFortune } = useFortuneApi()
 *
 * // 오늘 일운 조회
 * const { data: fortune, isLoading, error } = useDailyFortune()
 *
 * // 특정 날짜 일운 조회
 * const dateRef = ref('2026-01-28')
 * const { data } = useDailyFortune(dateRef)
 *
 * // AC 4: 기간별 운세 조회 (통합 함수)
 * const { data } = useFortune('weekly')
 * ```
 */
export const useFortuneApi = () => {
  const qc = useQueryClient()

  // M4 수정: 함수 내부에 타입 정의 (기존 패턴과 일치)
  type FortuneQueryOpts = Omit<UseQueryOptions<IFortune, APIError, IFortune, any>, 'queryKey' | 'queryFn'>

  /**
   * 일일 운세 조회 훅 (AC 1, 2, 3, 4)
   *
   * @param date - 조회할 날짜 (YYYY-MM-DD, 선택적, 기본: 오늘)
   * @param options - TanStack Query 옵션
   *
   * 캐시 키: ['fortune', 'daily', date] (Task 2.4)
   * staleTime: 24시간 (Task 2.5)
   */
  const useDailyFortune = (
    date?: Ref<string | undefined> | string,
    options?: FortuneQueryOpts
  ) => {
    const dateValue = computed(() => unref(date))

    return useQuery({
      // Task 2.4: 캐시 키 패턴
      queryKey: computed(() => ['fortune', 'daily', dateValue.value] as const),
      queryFn: () => fortuneApi.getDailyFortune(dateValue.value),
      // Task 2.5: staleTime 24시간
      staleTime: FORTUNE_STALE_TIME.daily,
      // M2 수정: gcTime을 staleTime과 일치시켜 캐시 불일치 방지
      gcTime: FORTUNE_GC_TIME.daily,
      ...options,
    })
  }

  /**
   * 주간 운세 조회 훅 (AC 4)
   *
   * @param options - TanStack Query 옵션
   *
   * 캐시 키: ['fortune', 'weekly'] (Task 2.4)
   * staleTime: 7일 (Task 2.5)
   */
  const useWeeklyFortune = (options?: FortuneQueryOpts) => {
    return useQuery({
      queryKey: ['fortune', 'weekly'] as const,
      queryFn: () => fortuneApi.getWeeklyFortune(),
      staleTime: FORTUNE_STALE_TIME.weekly,
      gcTime: FORTUNE_GC_TIME.weekly,
      ...options,
    })
  }

  /**
   * 월간 운세 조회 훅 (AC 4)
   *
   * @param options - TanStack Query 옵션
   *
   * 캐시 키: ['fortune', 'monthly'] (Task 2.4)
   * staleTime: 30일 (Task 2.5)
   */
  const useMonthlyFortune = (options?: FortuneQueryOpts) => {
    return useQuery({
      queryKey: ['fortune', 'monthly'] as const,
      queryFn: () => fortuneApi.getMonthlyFortune(),
      staleTime: FORTUNE_STALE_TIME.monthly,
      gcTime: FORTUNE_GC_TIME.monthly,
      ...options,
    })
  }

  /**
   * 연간 운세 조회 훅 (AC 4)
   *
   * @param options - TanStack Query 옵션
   *
   * 캐시 키: ['fortune', 'yearly'] (Task 2.4)
   * staleTime: 365일 (Task 2.5)
   */
  const useYearlyFortune = (options?: FortuneQueryOpts) => {
    return useQuery({
      queryKey: ['fortune', 'yearly'] as const,
      queryFn: () => fortuneApi.getYearlyFortune(),
      staleTime: FORTUNE_STALE_TIME.yearly,
      gcTime: FORTUNE_GC_TIME.yearly,
      ...options,
    })
  }

  /**
   * 기간별 운세 조회 훅 (AC 4 - 통합 함수)
   * H1 수정: AC 요구사항 "fetchFortune(type: ...)" 구현
   *
   * @param type - 운세 유형 ('daily' | 'weekly' | 'monthly' | 'yearly')
   * @param date - 일일 운세의 경우 조회할 날짜 (선택적)
   * @param options - TanStack Query 옵션
   *
   * @example
   * ```ts
   * const typeRef = ref<FortuneType>('daily')
   * const { data, isLoading, error } = useFortune(typeRef)
   * ```
   */
  const useFortune = (
    type: Ref<FortuneType> | FortuneType,
    date?: Ref<string | undefined> | string,
    options?: FortuneQueryOpts
  ) => {
    const typeValue = computed(() => unref(type))
    const dateValue = computed(() => unref(date))

    return useQuery({
      queryKey: computed(() => {
        if (typeValue.value === 'daily') {
          return ['fortune', 'daily', dateValue.value] as const
        }
        return ['fortune', typeValue.value] as const
      }),
      queryFn: () => fortuneApi.getFortune(typeValue.value, dateValue.value),
      staleTime: computed(() => FORTUNE_STALE_TIME[typeValue.value]),
      gcTime: computed(() => FORTUNE_GC_TIME[typeValue.value]),
      ...options,
    })
  }

  /**
   * 운세 캐시 무효화
   *
   * @param type - 운세 유형 (선택적, 미지정 시 전체 무효화)
   */
  const invalidateFortuneCache = (type?: FortuneType) => {
    if (type) {
      qc.invalidateQueries({ queryKey: ['fortune', type] })
    } else {
      qc.invalidateQueries({ queryKey: ['fortune'] })
    }
  }

  return {
    // Query hooks (개별)
    useDailyFortune,
    useWeeklyFortune,
    useMonthlyFortune,
    useYearlyFortune,
    // Query hook (통합 - AC 4)
    useFortune,
    // Utilities
    invalidateFortuneCache,
    // Error utilities
    getFortuneErrorMessage,
  }
}

// 에러 클래스 export (테스트 등에서 사용)
export { FortuneApiError }
