/**
 * Element Plus 기반 모달 관리 컴포저블
 * - 사주라인 다크 테마에 최적화된 모달 시스템
 * - Element Plus Dialog 컴포넌트 활용
 * - 전역 모달 상태 관리 및 중첩 모달 지원
 */
import { ref, computed, nextTick } from 'vue'
import { ElMessageBox, ElNotification, ElLoading } from 'element-plus'
import type { ElMessageBoxOptions, MessageBoxData } from 'element-plus'

// 모달 상태 인터페이스
interface ModalState {
  id: string
  isOpen: boolean
  title?: string
  component?: any
  props?: Record<string, any>
  onClose?: () => void
  onConfirm?: () => void
  width?: string | number
}

// 전역 모달 상태
const modals = ref<ModalState[]>([])
const activeModalId = ref<string | null>(null)

let modalIdCounter = 0

/**
 * 사주라인 다크 테마 모달 스타일
 */
const MODAL_THEME = {
  // 다크 테마 색상
  background: '#1a1a1f',
  headerBg: '#2d2d35',
  textColor: '#ffffff',
  borderColor: '#404040',
  primaryColor: '#6366f1',
  successColor: '#10b981',
  warningColor: '#f59e0b',
  errorColor: '#ef4444',
  
  // 그림자 및 보더
  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.8), 0 10px 10px -5px rgba(0, 0, 0, 0.6)',
  borderRadius: '12px'
}

/**
 * Element Plus 모달 관리 컴포저블
 */
export const useModal = () => {
  
  /**
   * 커스텀 다이얼로그 열기
   */
  const openDialog = async (options: {
    id?: string
    title: string
    component?: any
    props?: Record<string, any>
    width?: string | number
    showClose?: boolean
    closeOnClickModal?: boolean
    closeOnPressEscape?: boolean
    onClose?: () => void
    onConfirm?: () => void
  }) => {
    const modalId = options.id || `modal-${++modalIdCounter}`
    
    // 기존 같은 ID 모달이 있다면 제거
    closeDialog(modalId)
    
    const modalState: ModalState = {
      id: modalId,
      isOpen: true,
      title: options.title,
      component: options.component,
      props: options.props || {},
      width: options.width || '500px',
      onClose: options.onClose,
      onConfirm: options.onConfirm
    }
    
    modals.value.push(modalState)
    activeModalId.value = modalId
    
    await nextTick()
    return modalId
  }
  
  /**
   * 다이얼로그 닫기
   */
  const closeDialog = (modalId?: string) => {
    const targetId = modalId || activeModalId.value
    if (!targetId) return
    
    const modalIndex = modals.value.findIndex(m => m.id === targetId)
    if (modalIndex === -1) return
    
    const modal = modals.value[modalIndex]
    
    // onClose 콜백 실행
    if (modal && modal.onClose) {
      modal.onClose()
    }
    
    // 모달 제거
    modals.value.splice(modalIndex, 1)
    
    // 활성 모달 ID 업데이트
    if (activeModalId.value === targetId) {
      const lastModal = modals.value[modals.value.length - 1]
      activeModalId.value = modals.value.length > 0 && lastModal ? lastModal.id : null
    }
  }
  
  /**
   * 확인 모달 (Element Plus MessageBox 사용)
   */
  const confirm = async (options: {
    title: string
    message: string
    type?: 'warning' | 'error' | 'success' | 'info'
    confirmButtonText?: string
    cancelButtonText?: string
    showCancelButton?: boolean
  }): Promise<boolean> => {
    try {
      const messageBoxOptions: ElMessageBoxOptions = {
        title: options.title,
        message: options.message,
        type: options.type || 'warning',
        confirmButtonText: options.confirmButtonText || '확인',
        cancelButtonText: options.cancelButtonText || '취소',
        showCancelButton: options.showCancelButton !== false,
        customClass: 'sajuline-confirm-modal',
        buttonSize: 'default',
        
        // 다크 테마 스타일링
        customStyle: {
          '--el-messagebox-width': '420px',
          '--el-messagebox-border-radius': MODAL_THEME.borderRadius,
          '--el-bg-color': MODAL_THEME.background,
          '--el-text-color-primary': MODAL_THEME.textColor,
          '--el-border-color-light': MODAL_THEME.borderColor,
          '--el-color-primary': MODAL_THEME.primaryColor,
        }
      }
      
      const result: MessageBoxData = await ElMessageBox(messageBoxOptions)
      return result === 'confirm'
    } catch (error) {
      // 사용자가 취소하거나 ESC를 누른 경우
      return false
    }
  }
  
  /**
   * 알림 모달
   */
  const alert = async (options: {
    title: string
    message: string
    type?: 'warning' | 'error' | 'success' | 'info'
    confirmButtonText?: string
  }): Promise<void> => {
    try {
      await ElMessageBox.alert(options.message, options.title, {
        type: options.type || 'info',
        confirmButtonText: options.confirmButtonText || '확인',
        customClass: 'sajuline-alert-modal',
        
        // 다크 테마 스타일링
        customStyle: {
          '--el-messagebox-width': '400px',
          '--el-messagebox-border-radius': MODAL_THEME.borderRadius,
          '--el-bg-color': MODAL_THEME.background,
          '--el-text-color-primary': MODAL_THEME.textColor,
          '--el-border-color-light': MODAL_THEME.borderColor,
          '--el-color-primary': MODAL_THEME.primaryColor,
        }
      })
    } catch (error) {
      // 사용자가 ESC를 누르거나 취소한 경우
    }
  }
  
  /**
   * 프롬프트 모달 (입력받기)
   */
  const prompt = async (options: {
    title: string
    message: string
    inputValue?: string
    inputPlaceholder?: string
    inputType?: string
    confirmButtonText?: string
    cancelButtonText?: string
    inputValidator?: (value: string) => boolean | string
  }): Promise<string | null> => {
    try {
      const { value } = await ElMessageBox.prompt(options.message, options.title, {
        inputValue: options.inputValue || '',
        inputPlaceholder: options.inputPlaceholder || '값을 입력하세요',
        inputType: options.inputType || 'text',
        confirmButtonText: options.confirmButtonText || '확인',
        cancelButtonText: options.cancelButtonText || '취소',
        inputValidator: options.inputValidator,
        customClass: 'sajuline-prompt-modal',
        
        // 다크 테마 스타일링
        customStyle: {
          '--el-messagebox-width': '450px',
          '--el-messagebox-border-radius': MODAL_THEME.borderRadius,
          '--el-bg-color': MODAL_THEME.background,
          '--el-text-color-primary': MODAL_THEME.textColor,
          '--el-border-color-light': MODAL_THEME.borderColor,
          '--el-color-primary': MODAL_THEME.primaryColor,
        }
      })
      
      return value as string
    } catch (error) {
      return null
    }
  }
  
  /**
   * 로딩 모달
   */
  const showLoading = (options: {
    text?: string
    background?: string
    customClass?: string
  } = {}) => {
    return ElLoading.service({
      lock: true,
      text: options.text || '처리 중...',
      background: options.background || 'rgba(0, 0, 0, 0.8)',
      customClass: `sajuline-loading ${options.customClass || ''}`,
      
      // 다크 테마 스타일
      spinner: 'el-loading-spinner',
      svgViewBox: '0 0 50 50'
    })
  }
  
  /**
   * 모든 모달 닫기
   */
  const closeAllDialogs = () => {
    // 커스텀 다이얼로그 모두 닫기
    for (let i = modals.value.length - 1; i >= 0; i--) {
      const modal = modals.value[i]
      if (modal && modal.onClose) {
        modal.onClose()
      }
    }
    
    modals.value = []
    activeModalId.value = null
    
    // Element Plus 모달들 닫기
    ElMessageBox.close()
  }
  
  return {
    // 상태
    modals: computed(() => modals.value),
    activeModalId: computed(() => activeModalId.value),
    hasOpenModal: computed(() => modals.value.length > 0),
    
    // 커스텀 다이얼로그
    openDialog,
    closeDialog,
    closeAllDialogs,
    
    // Element Plus 기본 모달들
    confirm,
    alert,
    prompt,
    showLoading
  }
}

/**
 * 알림 메시지 컴포저블 (토스트)
 */
export const useNotification = () => {
  
  /**
   * 성공 알림
   */
  const success = (options: {
    title?: string
    message: string
    duration?: number
    showClose?: boolean
  }) => {
    ElNotification.success({
      title: options.title || '성공',
      message: options.message,
      duration: options.duration || 4500,
      showClose: options.showClose !== false,
      customClass: 'sajuline-notification-success',
      
      // 포지션 및 오프셋
      position: 'top-right',
      offset: 20
    })
  }
  
  /**
   * 에러 알림
   */
  const error = (options: {
    title?: string
    message: string
    duration?: number
    showClose?: boolean
  }) => {
    ElNotification.error({
      title: options.title || '오류',
      message: options.message,
      duration: options.duration || 6000,
      showClose: options.showClose !== false,
      customClass: 'sajuline-notification-error',
      
      // 포지션 및 오프셋
      position: 'top-right',
      offset: 20
    })
  }
  
  /**
   * 경고 알림
   */
  const warning = (options: {
    title?: string
    message: string
    duration?: number
    showClose?: boolean
  }) => {
    ElNotification.warning({
      title: options.title || '경고',
      message: options.message,
      duration: options.duration || 5000,
      showClose: options.showClose !== false,
      customClass: 'sajuline-notification-warning',
      
      // 포지션 및 오프셋
      position: 'top-right',
      offset: 20
    })
  }
  
  /**
   * 정보 알림
   */
  const info = (options: {
    title?: string
    message: string
    duration?: number
    showClose?: boolean
  }) => {
    ElNotification.info({
      title: options.title || '알림',
      message: options.message,
      duration: options.duration || 4500,
      showClose: options.showClose !== false,
      customClass: 'sajuline-notification-info',
      
      // 포지션 및 오프셋
      position: 'top-right',
      offset: 20
    })
  }
  
  return {
    success,
    error,
    warning,
    info
  }
}