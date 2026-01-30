/**
 * 운세 관련 타입 정의
 *
 * Backend 스키마 참조: backend/src/schemas/fortune_schema.py
 */
import type { APIResponse } from '~/types/common/api'

// =============================================================================
// 기본 타입 (Task 1.2)
// =============================================================================

/**
 * 운세 유형
 * - daily: 일일 운세
 * - weekly: 주간 운세
 * - monthly: 월간 운세
 * - yearly: 연간 운세
 */
export type FortuneType = 'daily' | 'weekly' | 'monthly' | 'yearly'

// =============================================================================
// 일주 정보 (Task 1.3)
// =============================================================================

/**
 * 일주 정보 (천간 + 지지)
 * Backend: DayPillar
 */
export interface IDayPillar {
  /** 천간 (갑, 을, 병, 정, 무, 기, 경, 신, 임, 계) */
  stem: string
  /** 지지 (자, 축, 인, 묘, 진, 사, 오, 미, 신, 유, 술, 해) */
  branch: string
}

// =============================================================================
// 운세 응답 인터페이스 (Task 1.4)
// =============================================================================

/**
 * 운세 데이터 인터페이스
 * Backend: FortuneResponse
 */
export interface IFortune {
  /** 운세 대상 날짜 (YYYY-MM-DD) */
  date: string
  /** 운세 유형 */
  fortune_type: FortuneType
  /** 일주 정보 */
  day_pillar: IDayPillar
  /** 총운 (50~150자) */
  overall: string
  /** 애정운 */
  love: string
  /** 직장운/사업운 */
  career: string
  /** 건강운 */
  health: string
  /** 재물운 */
  wealth: string
  /** 행운의 색상 */
  lucky_color?: string
  /** 행운의 숫자 (1~99) */
  lucky_number?: number
  /** 운세 출처 (llm: LLM 생성, fallback: 폴백, cache: 캐시) */
  source: 'llm' | 'fallback' | 'cache'
  /** 운세 점수 (1~5) */
  luck_score?: number
  /** 핵심 키워드 목록 */
  keywords?: string[]
  /** 오늘의 십성 (비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인) */
  sipsung?: string
}

// =============================================================================
// API 응답 타입 (Task 1.5)
// =============================================================================

/**
 * 운세 API 응답 타입
 * Backend: APIResponse[FortuneResponse]
 */
export type IFortuneResponse = APIResponse<IFortune>

// =============================================================================
// 에러 코드
// =============================================================================

/**
 * 운세 API 에러 코드
 */
export type FortuneErrorCode =
  | 'SAJU_INFO_REQUIRED'      // 사주 정보 미등록
  | 'INVALID_DATE_RANGE'      // 날짜 범위 초과
  | 'USER_NOT_FOUND'          // 사용자 없음
  | 'RATE_LIMIT_EXCEEDED'     // Rate Limit 초과 (429)

// =============================================================================
// 공통 상수 (Story 3.3 Code Review - DRY 원칙)
// =============================================================================

/**
 * 운세 탭 정의
 * FortuneTabs 컴포넌트와 fortune 페이지에서 공통 사용
 */
export interface IFortuneTab {
  value: FortuneType
  label: string
}

export const FORTUNE_TABS: readonly IFortuneTab[] = [
  { value: 'daily', label: '일운' },
  { value: 'weekly', label: '주운' },
  { value: 'monthly', label: '월운' },
  { value: 'yearly', label: '연운' },
] as const

/**
 * 운세 타입 배열 (순서 보장)
 */
export const FORTUNE_TYPES: readonly FortuneType[] = ['daily', 'weekly', 'monthly', 'yearly'] as const
