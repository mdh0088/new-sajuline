<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">{{ isEditing ? '후기 수정' : '후기 작성' }}</h3>
      </div>
      <div class="modal-body">
        <!-- 별점 -->
        <div class="form-group">
          <label class="form-label">만족도를 평가해주세요</label>
          <div class="rating-stars">
            <span
              v-for="i in 5"
              :key="i"
              class="star"
              :class="{ filled: i <= (hoverRating || rating) }"
              @click="updateRating(i)"
              @mouseenter="hoverRating = i"
              @mouseleave="hoverRating = 0"
            >⭐</span>
          </div>
        </div>

        <!-- 태그 선택 -->
        <div class="form-group">
          <label class="form-label">어떤 점이 좋았나요? (최대 3개)</label>
          <div class="tag-select">
            <div
              v-for="tag in availableTags"
              :key="tag"
              class="tag-option"
              :class="{ selected: tags.includes(tag) }"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </div>
          </div>
        </div>

        <!-- 리뷰 내용 -->
        <div class="form-group">
          <label class="form-label">상담은 어떠셨나요?</label>
          <textarea
            v-model="content"
            class="textarea"
            placeholder="다른 회원님들께 도움이 될 수 있도록 솔직한 후기를 남겨주세요. (최소 20자)"
            maxlength="500"
          ></textarea>
          <div class="char-count">{{ content.length }} / 500</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-button modal-cancel" @click="handleClose">취소</button>
        <button
          class="modal-button modal-submit"
          @click="handleSubmit"
          :disabled="!isValidReview || submitting"
        >
          {{ submitting ? '처리중...' : (isEditing ? '수정완료' : '작성완료') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ReviewData {
  rating: number
  tags: string[]
  content: string
}

interface Props {
  isVisible: boolean
  isEditing?: boolean
  initialData?: ReviewData
  submitting?: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'submit', data: ReviewData): void
}

const props = withDefaults(defineProps<Props>(), {
  isEditing: false,
  initialData: () => ({ rating: 0, tags: [], content: '' }),
  submitting: false
})

const emit = defineEmits<Emits>()

// 반응형 데이터
const rating = ref(props.initialData.rating)
const tags = ref<string[]>([...props.initialData.tags])
const content = ref(props.initialData.content)
const hoverRating = ref(0)

// 사용 가능한 태그
const availableTags = [
  '정확해요', '친절해요', '속시원해요',
  '위로가 돼요', '공감력 좋아요', '해결책 제시'
]

// computed
const isValidReview = computed(() => {
  return rating.value > 0 && content.value.length >= 20
})

// 초기 데이터 감시
watch(() => props.initialData, (newData) => {
  rating.value = newData.rating
  tags.value = [...newData.tags]
  content.value = newData.content
}, { deep: true })

watch(() => props.isVisible, (visible) => {
  if (!visible) {
    // 모달이 닫힐 때 호버 상태 초기화
    hoverRating.value = 0
  }
})

// 메서드
const updateRating = (value: number) => {
  rating.value = value
}

const toggleTag = (tag: string) => {
  const index = tags.value.indexOf(tag)
  if (index > -1) {
    tags.value.splice(index, 1)
  } else if (tags.value.length < 3) {
    tags.value.push(tag)
  }
}

const handleOverlayClick = () => {
  emit('close')
}

const handleClose = () => {
  emit('close')
}

const handleSubmit = () => {
  if (!isValidReview.value) return

  const reviewData: ReviewData = {
    rating: rating.value,
    tags: [...tags.value],
    content: content.value
  }

  emit('submit', reviewData)
}

// 리셋 메서드 (외부에서 호출 가능하도록)
const resetForm = () => {
  rating.value = 0
  tags.value = []
  content.value = ''
  hoverRating.value = 0
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

/* 별점 스타일 */
.rating-stars {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.star {
  font-size: 32px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  /* 기본 회색 별 - 필터로 더 확실하게 구분 */
  filter: grayscale(1) opacity(0.3);
}

.star.filled {
  /* 선택된 황금색 별 */
  filter: none;
  color: #FFD700;
}

.star:hover {
  filter: none;
  color: #FFD700;
}

/* 태그 선택 스타일 */
.tag-select {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-option {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.tag-option:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.tag-option.selected {
  background: linear-gradient(135deg, #9333EA 0%, #7C3AED 100%);
  color: #ffffff;
  border-color: #9333EA;
}

/* 텍스트영역 스타일 */
.textarea {
  width: 100%;
  min-height: 120px;
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

  .star {
    font-size: 28px;
  }

  .tag-option {
    padding: 6px 12px;
    font-size: 13px;
  }

  .textarea {
    min-height: 100px;
    padding: 12px;
  }
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  .modal-button,
  .tag-option,
  .star,
  .textarea {
    transition: none;
  }
}
</style>