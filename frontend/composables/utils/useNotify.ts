/**
 * Notivue 기반 알림 유틸리티
 * - 간편한 알림 표시를 위한 래퍼 함수들
 * - 기본 설정이 적용된 알림 시스템
 */
import { push } from 'notivue'

export interface NotifyOptions {
  title?: string
  message?: string
  duration?: number
}

/**
 * 편리한 알림 함수들을 제공하는 컴포저블
 */
export const useNotify = () => {
  
  /**
   * 성공 알림 (headless - 타이틀 없음)
   */
  const notifySuccess = (message: string) => {
    push.success(message)
  }

  /**
   * 에러 알림 (headless - 타이틀 없음)
   */
  const notifyError = (message: string) => {
    push.error(message)
  }

  /**
   * 경고 알림 (headless - 타이틀 없음)
   */
  const notifyWarning = (message: string) => {
    push.warning(message)
  }

  /**
   * 정보 알림 (headless - 타이틀 없음)
   */
  const notifyInfo = (message: string) => {
    push.info(message)
  }

  return {
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo
  }
}