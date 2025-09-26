<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">문의하기</h3>
      </div>
      <div class="modal-body">
        <!-- 문의 내용 -->
        <div class="form-group">
          <label class="form-label">문의 내용</label>
          <textarea
            v-model="inquiryContent"
            class="textarea"
            placeholder="문의하실 내용을 입력해주세요. (최소 10자)"
            maxlength="500"
          ></textarea>
          <div class="char-count">{{ inquiryContent.length }} / 500</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-button modal-cancel" @click="handleClose">취소</button>
        <button
          class="modal-button modal-submit"
          @click="handleSubmit"
          :disabled="!isValidInquiry || submitting"
        >
          {{ submitting ? '처리중...' : '등록' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface InquiryData {
  content: string
}

interface Props {
  isVisible: boolean
  submitting?: boolean
  initialContent?: string
}

interface Emits {
  (e: 'close'): void
  (e: 'submit', data: InquiryData): void
}

const props = withDefaults(defineProps<Props>(), {
  submitting: false,
  initialContent: ''
})

const emit = defineEmits<Emits>()

// 반응형 데이터
const inquiryContent = ref(props.initialContent)

// computed
const isValidInquiry = computed(() => {
  return inquiryContent.value.length >= 10
})

// 초기 데이터 감시
watch(() => props.initialContent, (newContent) => {
  inquiryContent.value = newContent
})

// 모달이 열릴 때 내용 초기화
watch(() => props.isVisible, (visible) => {
  if (visible && !props.initialContent) {
    inquiryContent.value = ''
  }
})

// 메서드
const handleOverlayClick = () => {
  emit('close')
}

const handleClose = () => {
  emit('close')
}

const handleSubmit = () => {
  if (!isValidInquiry.value) return

  const inquiryData: InquiryData = {
    content: inquiryContent.value
  }

  emit('submit', inquiryData)
}

// 리셋 메서드 (외부에서 호출 가능하도록)
const resetForm = () => {
  inquiryContent.value = ''
}

// 외부에서 접근 가능하도록 expose
defineExpose({
  resetForm
})
</script>

<style scoped>
/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 24px 24px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 24px;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  padding-bottom: 16px;
}

.modal-body {
  padding: 0 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 12px;
}

/* 텍스트영역 스타일 */
.textarea {
  width: 100%;
  min-height: 150px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.textarea:focus {
  outline: none;
  border-color: #9333EA;
  box-shadow: 0 0 0 2px rgba(147, 51, 234, 0.2);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
}

/* 모달 푸터 */
.modal-footer {
  padding: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-button {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.modal-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.modal-submit {
  background: linear-gradient(135deg, #9333EA 0%, #7C3AED 100%);
  color: #ffffff;
}

.modal-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(147, 51, 234, 0.4);
}

.modal-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-submit:active:not(:disabled) {
  transform: translateY(0);
}

/* 모바일 반응형 */
@media (max-width: 480px) {
  .modal-overlay {
    padding: 12px;
  }

  .modal-header {
    padding: 20px 20px 0;
  }

  .modal-title {
    font-size: 18px;
  }

  .modal-body {
    padding: 0 20px;
  }

  .modal-footer {
    padding: 20px;
  }

  .textarea {
    min-height: 120px;
    padding: 12px;
  }
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  .modal-button,
  .textarea {
    transition: none;
  }
}
</style>