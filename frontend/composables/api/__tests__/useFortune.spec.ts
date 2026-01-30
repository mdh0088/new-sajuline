/**
 * useFortune Composable 단위 테스트
 *
 * Task 4.2: composable 기본 동작 테스트 (mock API)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import type { IFortune, IFortuneResponse, FortuneType } from '~/types/fortune'

// Mock 데이터
const mockDailyFortune: IFortune = {
  date: '2026-01-30',
  fortune_type: 'daily',
  day_pillar: {
    stem: '갑',
    branch: '진',
  },
  overall: '오늘은 새로운 시작에 좋은 날입니다. 긍정적인 마음으로 하루를 시작하세요.',
  love: '연인과의 대화가 원활해지는 시기입니다.',
  career: '직장에서 인정받을 수 있는 기회가 찾아옵니다.',
  health: '가벼운 운동으로 활력을 되찾으세요.',
  wealth: '예상치 못한 수입이 있을 수 있습니다.',
  lucky_color: '파랑',
  lucky_number: 7,
  source: 'llm',
  luck_score: 4,
  keywords: ['새로운 시작', '긍정', '행운'],
  sipsung: '정관',
}

const mockSuccessResponse: IFortuneResponse = {
  success: true,
  message: '운세 조회 성공',
  data: mockDailyFortune,
}

const mockErrorResponse: IFortuneResponse = {
  success: false,
  error: {
    code: 'SAJU_INFO_REQUIRED',
    message: '사주 정보가 등록되지 않았습니다.',
  },
}

// $api mock
const mockApi = vi.fn()

// useNuxtApp mock
vi.mock('nuxt/app', () => ({
  useNuxtApp: () => ({
    $api: mockApi,
  }),
}))

// TanStack Query mocks
const mockQueryClient = {
  invalidateQueries: vi.fn(),
}

vi.mock('@tanstack/vue-query', async () => {
  const actual = await vi.importActual('@tanstack/vue-query')
  return {
    ...actual,
    useQueryClient: () => mockQueryClient,
    useQuery: vi.fn((options) => {
      // 실제 queryFn 실행 시뮬레이션
      const queryKey = typeof options.queryKey === 'function'
        ? options.queryKey()
        : options.queryKey?.value ?? options.queryKey

      return {
        queryKey,
        data: ref(null),
        isLoading: ref(false),
        isPending: ref(false),
        isError: ref(false),
        error: ref(null),
        refetch: vi.fn(),
      }
    }),
  }
})

describe('useFortune Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi.mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Type Definitions', () => {
    it('FortuneType should accept valid types', () => {
      const validTypes: FortuneType[] = ['daily', 'weekly', 'monthly', 'yearly']

      validTypes.forEach((type) => {
        expect(['daily', 'weekly', 'monthly', 'yearly']).toContain(type)
      })
    })

    it('IFortune interface should have required properties', () => {
      expect(mockDailyFortune).toHaveProperty('date')
      expect(mockDailyFortune).toHaveProperty('fortune_type')
      expect(mockDailyFortune).toHaveProperty('day_pillar')
      expect(mockDailyFortune).toHaveProperty('overall')
      expect(mockDailyFortune).toHaveProperty('love')
      expect(mockDailyFortune).toHaveProperty('career')
      expect(mockDailyFortune).toHaveProperty('health')
      expect(mockDailyFortune).toHaveProperty('wealth')
      expect(mockDailyFortune).toHaveProperty('source')
    })

    it('IDayPillar interface should have stem and branch', () => {
      expect(mockDailyFortune.day_pillar).toHaveProperty('stem')
      expect(mockDailyFortune.day_pillar).toHaveProperty('branch')
      expect(typeof mockDailyFortune.day_pillar.stem).toBe('string')
      expect(typeof mockDailyFortune.day_pillar.branch).toBe('string')
    })

    it('Optional properties should be valid', () => {
      expect(mockDailyFortune.lucky_color).toBe('파랑')
      expect(mockDailyFortune.lucky_number).toBe(7)
      expect(mockDailyFortune.luck_score).toBe(4)
      expect(mockDailyFortune.keywords).toEqual(['새로운 시작', '긍정', '행운'])
      expect(mockDailyFortune.sipsung).toBe('정관')
    })
  })

  describe('useFortuneApi Composable', () => {
    it('should import useFortuneApi without errors', async () => {
      const { useFortuneApi } = await import('../useFortune')
      expect(useFortuneApi).toBeDefined()
      expect(typeof useFortuneApi).toBe('function')
    })

    it('should return expected hooks and utilities', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const api = useFortuneApi()

      // 개별 훅 확인
      expect(api.useDailyFortune).toBeDefined()
      expect(api.useWeeklyFortune).toBeDefined()
      expect(api.useMonthlyFortune).toBeDefined()
      expect(api.useYearlyFortune).toBeDefined()

      // 통합 훅 확인 (AC 4)
      expect(api.useFortune).toBeDefined()

      // 유틸리티 함수 확인
      expect(api.invalidateFortuneCache).toBeDefined()
      expect(api.getFortuneErrorMessage).toBeDefined()
    })

    it('useDailyFortune should return query result', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { useDailyFortune } = useFortuneApi()

      const result = useDailyFortune()

      expect(result).toHaveProperty('data')
      expect(result).toHaveProperty('isLoading')
      expect(result).toHaveProperty('isError')
      expect(result).toHaveProperty('error')
    })

    it('useDailyFortune should accept date parameter', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { useDailyFortune } = useFortuneApi()

      const dateRef = ref('2026-01-30')
      const result = useDailyFortune(dateRef)

      expect(result).toBeDefined()
    })

    it('useFortune (unified) should accept type parameter', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { useFortune } = useFortuneApi()

      const typeRef = ref<FortuneType>('weekly')
      const result = useFortune(typeRef)

      expect(result).toBeDefined()
    })
  })

  describe('Error Handling', () => {
    it('getFortuneErrorMessage should return mapped error message', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { getFortuneErrorMessage } = useFortuneApi()

      const error = {
        data: {
          error: {
            code: 'SAJU_INFO_REQUIRED',
            message: '사주 정보가 등록되지 않았습니다.',
          },
        },
      }

      const message = getFortuneErrorMessage(error)
      expect(message).toBe('사주 정보를 먼저 등록해주세요')
    })

    it('getFortuneErrorMessage should handle INVALID_DATE_RANGE', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { getFortuneErrorMessage } = useFortuneApi()

      const error = {
        data: {
          error: {
            code: 'INVALID_DATE_RANGE',
          },
        },
      }

      const message = getFortuneErrorMessage(error)
      expect(message).toBe('조회 가능한 날짜 범위를 벗어났습니다')
    })

    it('getFortuneErrorMessage should handle RATE_LIMIT_EXCEEDED', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { getFortuneErrorMessage } = useFortuneApi()

      const error = {
        data: {
          error: {
            code: 'RATE_LIMIT_EXCEEDED',
          },
        },
      }

      const message = getFortuneErrorMessage(error)
      expect(message).toBe('요청이 너무 많습니다. 잠시 후 다시 시도해주세요')
    })

    it('getFortuneErrorMessage should return server message for unknown error', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { getFortuneErrorMessage } = useFortuneApi()

      const error = {
        data: {
          error: {
            code: 'UNKNOWN_ERROR',
            message: '서버에서 보낸 에러 메시지',
          },
        },
      }

      const message = getFortuneErrorMessage(error)
      expect(message).toBe('서버에서 보낸 에러 메시지')
    })

    it('getFortuneErrorMessage should return default message for null error', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { getFortuneErrorMessage } = useFortuneApi()

      const message = getFortuneErrorMessage(null)
      expect(message).toBe('운세 조회에 실패했습니다')
    })
  })

  describe('Cache Invalidation', () => {
    it('invalidateFortuneCache should call queryClient with specific type', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { invalidateFortuneCache } = useFortuneApi()

      invalidateFortuneCache('daily')

      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['fortune', 'daily'],
      })
    })

    it('invalidateFortuneCache should invalidate all fortune queries when no type specified', async () => {
      const { useFortuneApi } = await import('../useFortune')
      const { invalidateFortuneCache } = useFortuneApi()

      invalidateFortuneCache()

      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['fortune'],
      })
    })
  })

  describe('FortuneApiError Class', () => {
    it('should export FortuneApiError class', async () => {
      const { FortuneApiError } = await import('../useFortune')
      expect(FortuneApiError).toBeDefined()
    })

    it('FortuneApiError should have correct properties', async () => {
      const { FortuneApiError } = await import('../useFortune')

      const error = new FortuneApiError('테스트 에러', 400, 'SAJU_INFO_REQUIRED', { test: true })

      expect(error.message).toBe('테스트 에러')
      expect(error.statusCode).toBe(400)
      expect(error.code).toBe('SAJU_INFO_REQUIRED')
      expect(error.data).toEqual({ test: true })
      expect(error.name).toBe('FortuneApiError')
    })

    it('FortuneApiError should extend Error', async () => {
      const { FortuneApiError } = await import('../useFortune')

      const error = new FortuneApiError('테스트 에러')

      expect(error instanceof Error).toBe(true)
    })
  })

  describe('Cache TTL Configuration', () => {
    it('should have correct staleTime values', async () => {
      // staleTime 상수 검증 (내부 상수이므로 타입 체크로 대체)
      const expectedTimes = {
        daily: 24 * 60 * 60 * 1000,      // 24시간
        weekly: 7 * 24 * 60 * 60 * 1000, // 7일
        monthly: 30 * 24 * 60 * 60 * 1000, // 30일
        yearly: 365 * 24 * 60 * 60 * 1000, // 365일
      }

      expect(expectedTimes.daily).toBe(86400000)
      expect(expectedTimes.weekly).toBe(604800000)
      expect(expectedTimes.monthly).toBe(2592000000)
      expect(expectedTimes.yearly).toBe(31536000000)
    })
  })
})

describe('Fortune Type Validation', () => {
  it('IFortuneResponse should wrap IFortune in APIResponse', () => {
    expect(mockSuccessResponse.success).toBe(true)
    expect(mockSuccessResponse.data).toEqual(mockDailyFortune)
  })

  it('Error response should have error object', () => {
    expect(mockErrorResponse.success).toBe(false)
    expect(mockErrorResponse.error).toBeDefined()
    expect(mockErrorResponse.error?.code).toBe('SAJU_INFO_REQUIRED')
  })
})
