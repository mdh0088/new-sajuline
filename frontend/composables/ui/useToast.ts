/**
 * 토스트 메시지 관리 컴포저블
 * - Element Plus Message 컴포넌트 활용
 * - 사주라인 다크 테마 최적화
 * - 간단한 알림 메시지 시스템
 */
import { ElMessage } from 'element-plus'
import type { MessageOptions } from 'element-plus'

/**
 * 사주라인 토스트 테마 설정
 */
const TOAST_THEME = {
  duration: 3000, // 기본 3초
  showClose: false, // 기본적으로 닫기 버튼 숨김
  offset: 20, // 상단에서 20px
  
  // 다크 테마 색상
  customClass: 'sajuline-toast'
}

/**
 * 토스트 메시지 컴포저블
 */
export const useToast = () => {
  
  /**
   * 성공 메시지
   */
  const success = (message: string, options: Partial<MessageOptions> = {}) => {
    ElMessage.success({
      message,
      duration: TOAST_THEME.duration,
      showClose: TOAST_THEME.showClose,
      offset: TOAST_THEME.offset,
      customClass: `${TOAST_THEME.customClass} ${TOAST_THEME.customClass}-success`,
      ...options
    })
  }
  
  /**
   * 에러 메시지
   */
  const error = (message: string, options: Partial<MessageOptions> = {}) => {
    ElMessage.error({
      message,
      duration: 5000, // 에러는 5초간 표시
      showClose: true, // 에러는 닫기 버튼 표시
      offset: TOAST_THEME.offset,
      customClass: `${TOAST_THEME.customClass} ${TOAST_THEME.customClass}-error`,
      ...options
    })
  }
  
  /**
   * 경고 메시지
   */
  const warning = (message: string, options: Partial<MessageOptions> = {}) => {
    ElMessage.warning({
      message,
      duration: 4000, // 경고는 4초간 표시
      showClose: TOAST_THEME.showClose,
      offset: TOAST_THEME.offset,
      customClass: `${TOAST_THEME.customClass} ${TOAST_THEME.customClass}-warning`,
      ...options
    })
  }
  
  /**
   * 정보 메시지
   */
  const info = (message: string, options: Partial<MessageOptions> = {}) => {
    ElMessage.info({
      message,
      duration: TOAST_THEME.duration,
      showClose: TOAST_THEME.showClose,
      offset: TOAST_THEME.offset,
      customClass: `${TOAST_THEME.customClass} ${TOAST_THEME.customClass}-info`,
      ...options
    })
  }
  
  /**
   * 일반 메시지 (기본 스타일)
   */
  const message = (text: string, options: Partial<MessageOptions> = {}) => {
    ElMessage({
      message: text,
      duration: TOAST_THEME.duration,
      showClose: TOAST_THEME.showClose,
      offset: TOAST_THEME.offset,
      customClass: TOAST_THEME.customClass,
      ...options
    })
  }
  
  /**
   * 로딩 메시지 (수동으로 닫아야 함)
   */
  const loading = (message: string = '처리 중...', options: Partial<MessageOptions> = {}) => {
    return ElMessage({
      message,
      duration: 0, // 수동으로 닫을 때까지 표시
      showClose: false,
      offset: TOAST_THEME.offset,
      customClass: `${TOAST_THEME.customClass} ${TOAST_THEME.customClass}-loading`,
      icon: 'Loading',
      ...options
    })
  }
  
  /**
   * 모든 토스트 메시지 닫기
   */
  const closeAll = () => {
    ElMessage.closeAll()
  }
  
  return {
    success,
    error,
    warning,
    info,
    message,
    loading,
    closeAll
  }
}

/**
 * 토스트 유틸리티 함수들
 */
export const toast = {
  success: (message: string) => ElMessage.success({
    message,
    duration: 3000,
    customClass: 'sajuline-toast sajuline-toast-success'
  }),
  
  error: (message: string) => ElMessage.error({
    message,
    duration: 5000,
    showClose: true,
    customClass: 'sajuline-toast sajuline-toast-error'
  }),
  
  warning: (message: string) => ElMessage.warning({
    message,
    duration: 4000,
    customClass: 'sajuline-toast sajuline-toast-warning'
  }),
  
  info: (message: string) => ElMessage.info({
    message,
    duration: 3000,
    customClass: 'sajuline-toast sajuline-toast-info'
  })
}