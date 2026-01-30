/**
 * 날짜 포맷팅 유틸리티
 *
 * 한국어 날짜 형식으로 포맷팅하는 함수들을 제공합니다.
 */

const KOREAN_DAYS = ['일', '월', '화', '수', '목', '금', '토'] as const

/**
 * 날짜를 한국어 형식으로 포맷팅
 * @param date - Date 객체 또는 날짜 문자열 (YYYY-MM-DD)
 * @returns "2026년 1월 30일 (목)" 형식의 문자열
 *
 * @example
 * ```ts
 * formatKoreanDate(new Date()) // "2026년 1월 30일 (목)"
 * formatKoreanDate('2026-01-30') // "2026년 1월 30일 (목)"
 * ```
 */
export const formatKoreanDate = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (isNaN(dateObj.getTime())) {
    return ''
  }

  const year = dateObj.getFullYear()
  const month = dateObj.getMonth() + 1
  const day = dateObj.getDate()
  const dayOfWeek = KOREAN_DAYS[dateObj.getDay()]

  return `${year}년 ${month}월 ${day}일 (${dayOfWeek})`
}

/**
 * 오늘 날짜를 한국어 형식으로 반환
 * @returns "2026년 1월 30일 (목)" 형식의 문자열
 */
export const getTodayKoreanDate = (): string => {
  return formatKoreanDate(new Date())
}
