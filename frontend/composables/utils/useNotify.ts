/**
 * Notivue 기반 알림 유틸리티
 * - 간편한 알림 표시를 위한 래퍼 함수들
 * - 기본 설정이 적용된 알림 시스템
 */
import { push } from 'notivue'
import { ElMessageBox } from 'element-plus'

export interface NotifyOptions {
  title?: string
  message?: string
  duration?: number
}

export interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
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

  /**
   * 확인 창 (Promise 기반 Element Plus MessageBox)
   * Element Plus MessageBox를 사용한 확인 대화상자
   */
  const notifyConfirm = async (message: string, options?: Partial<ConfirmOptions>): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(
        message,
        options?.title || '확인',
        {
          confirmButtonText: options?.confirmText || '확인',
          cancelButtonText: options?.cancelText || '취소',
          type: 'warning',
          customClass: 'sajuline-confirm-modal',
          distinguishCancelAndClose: true,
          showClose: false,
          center: true,
          roundButton: true,
          buttonSize: 'default'
        }
      )
      return true
    } catch (action) {
      // 취소 버튼 클릭 또는 ESC 키 처리
      return false
    }
  }

  return {
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
    notifyConfirm
  }
}