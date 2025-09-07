/**
 * 간단한 검증 유틸리티 함수들
 */

/**
 * 이메일 형식 검증
 * @param input 검증할 문자열
 * @returns 이메일 형식 여부
 */
export const isEmailFormat = (input: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)
}