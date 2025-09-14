<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <!-- 탭 메뉴 -->
    <div class="tab-menu">
      <div class="tab-list">
        <div
          class="tab-item"
          :class="{ active: activeTab === 'completed' }"
          @click="activeTab = 'completed'"
        >
          작성한 후기
          <span class="tab-badge">{{ completedReviews.length }}</span>
        </div>
        <div
          class="tab-item"
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          작성 대기
          <span class="tab-badge">{{ pendingReviews.length }}</span>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 리뷰 통계 -->
      <section class="review-stats">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ averageRating }}</div>
            <div class="stat-label">평균 평점</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalReviews }}</div>
            <div class="stat-label">작성한 후기</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ earnedPoints }}P</div>
            <div class="stat-label">받은 포인트</div>
          </div>
        </div>
      </section>

      <!-- 리뷰 리스트 -->
      <div class="review-list">
        <!-- 작성 대기 탭 -->
        <template v-if="activeTab === 'pending'">
          <div v-if="pendingReviews.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <div class="empty-title">작성 대기 중인 후기가 없습니다</div>
            <div class="empty-desc">상담 후 후기를 작성하고 포인트를 받아보세요!</div>
          </div>
          <div
            v-for="review in pendingReviews"
            :key="review.id"
            class="review-card pending"
          >
            <div class="review-header">
              <div class="counselor-info">
                <div class="counselor-avatar">{{ review.counselor.emoji }}</div>
                <div class="counselor-details">
                  <div class="counselor-name">{{ review.counselor.name }}</div>
                  <div class="consultation-date">{{ formatDate(review.consultationDate) }} 상담</div>
                </div>
              </div>
              <div class="review-status pending">작성 대기</div>
            </div>
            <div class="review-content">
              <p class="review-placeholder">아직 후기를 작성하지 않으셨습니다. 후기를 작성하고 100P를 받아보세요!</p>
            </div>
            <div class="review-actions">
              <button class="review-button write-button" @click="openWriteModal(review)">후기 작성하기</button>
            </div>
          </div>
        </template>

        <!-- 작성한 후기 탭 -->
        <template v-if="activeTab === 'completed'">
          <div v-if="completedReviews.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <div class="empty-title">작성한 후기가 없습니다</div>
            <div class="empty-desc">첫 상담 후기를 작성해보세요!</div>
            <NuxtLink to="/chat" class="empty-button">상담 받러 가기</NuxtLink>
          </div>
          <div
            v-for="review in completedReviews"
            :key="review.id"
            class="review-card"
          >
            <div class="review-header">
              <div class="counselor-info">
                <div class="counselor-avatar">{{ review.counselor.emoji }}</div>
                <div class="counselor-details">
                  <div class="counselor-name">{{ review.counselor.name }}</div>
                  <div class="consultation-date">{{ formatDate(review.consultationDate) }} 상담</div>
                </div>
              </div>
              <div class="review-status">작성 완료</div>
            </div>
            <div class="rating-section">
              <div class="rating-stars">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="star"
                  :class="{ filled: i <= review.rating }"
                >⭐</span>
              </div>
            </div>
            <div v-if="review.tags && review.tags.length > 0" class="review-tags">
              <span v-for="tag in review.tags" :key="tag" class="review-tag">{{ tag }}</span>
            </div>
            <div class="review-content">
              {{ review.content }}
            </div>
            <div class="review-actions">
              <button class="review-button edit-button" @click="openEditModal(review)">수정</button>
              <button class="review-button delete-button" @click="deleteReview(review.id)">삭제</button>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- 리뷰 작성/수정 모달 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
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
                :class="{ filled: i <= (hoverRating || modalRating) }"
                @click="modalRating = i"
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
                :class="{ selected: modalTags.includes(tag) }"
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
              v-model="modalContent"
              class="textarea"
              placeholder="다른 회원님들께 도움이 될 수 있도록 솔직한 후기를 남겨주세요. (최소 20자)"
              maxlength="500"
            ></textarea>
            <div class="char-count">{{ modalContent.length }} / 500</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-button modal-cancel" @click="closeModal">취소</button>
          <button
            class="modal-button modal-submit"
            @click="submitReview"
            :disabled="!isValidReview"
          >
            {{ isEditing ? '수정완료' : '작성완료' }}
          </button>
        </div>
      </div>
    </div>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// 반응형 데이터
const activeTab = ref<'completed' | 'pending'>('completed')
const showModal = ref(false)
const isEditing = ref(false)
const editingReview = ref<any>(null)
const currentPendingReview = ref<any>(null)

// 모달 폼 데이터
const modalRating = ref(0)
const modalTags = ref<string[]>([])
const modalContent = ref('')
const hoverRating = ref(0)

// 사용 가능한 태그
const availableTags = [
  '정확해요', '친절해요', '속시원해요',
  '위로가 돼요', '공감력 좋아요', '해결책 제시'
]

// 임시 데이터 (실제로는 API에서 가져올 데이터)
const completedReviews = ref([
  {
    id: 1,
    counselor: { name: '천기누설 선생님', emoji: '🔥' },
    consultationDate: new Date('2025-05-25'),
    rating: 5,
    tags: ['정확해요', '친절해요', '속시원해요'],
    content: '취업 관련해서 고민이 많았는데 선생님께서 정말 정확하게 봐주셨어요. 말씀하신 시기에 정말로 면접 연락이 왔고, 덕분에 좋은 회사에 합격했습니다. 앞으로도 중요한 결정할 때마다 찾아뵙고 싶어요. 감사합니다!'
  },
  {
    id: 2,
    counselor: { name: '별빛 선생님', emoji: '💫' },
    consultationDate: new Date('2025-05-20'),
    rating: 4,
    tags: ['위로가 돼요', '공감력 좋아요'],
    content: '힘든 시기에 큰 위로가 되었습니다. 선생님의 따뜻한 말씀 덕분에 마음이 많이 편안해졌어요. 앞으로의 방향도 잘 제시해주셔서 희망을 갖고 나아갈 수 있을 것 같습니다.'
  }
])

const pendingReviews = ref([
  {
    id: 3,
    counselor: { name: '명월 선생님', emoji: '🌙' },
    consultationDate: new Date('2025-05-30')
  }
])

// 계산된 값들
const totalReviews = computed(() => completedReviews.value.length)
const averageRating = computed(() => {
  if (completedReviews.value.length === 0) return '0.0'
  const sum = completedReviews.value.reduce((acc, review) => acc + review.rating, 0)
  return (sum / completedReviews.value.length).toFixed(1)
})
const earnedPoints = computed(() => totalReviews.value * 100)

const isValidReview = computed(() => {
  return modalRating.value > 0 && modalContent.value.length >= 20
})

// 유틸리티 함수
const formatDate = (date: Date) => {
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

// 모달 관련 함수
const openWriteModal = (review: any) => {
  isEditing.value = false
  currentPendingReview.value = review
  resetModalForm()
  showModal.value = true
}

const openEditModal = (review: any) => {
  isEditing.value = true
  editingReview.value = review
  modalRating.value = review.rating
  modalTags.value = [...review.tags]
  modalContent.value = review.content
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  resetModalForm()
}

const resetModalForm = () => {
  modalRating.value = 0
  modalTags.value = []
  modalContent.value = ''
  hoverRating.value = 0
  editingReview.value = null
  currentPendingReview.value = null
}

const toggleTag = (tag: string) => {
  const index = modalTags.value.indexOf(tag)
  if (index > -1) {
    modalTags.value.splice(index, 1)
  } else if (modalTags.value.length < 3) {
    modalTags.value.push(tag)
  }
}

const submitReview = async () => {
  if (!isValidReview.value) return

  // 여기에 실제 API 호출 로직 추가
  if (isEditing.value && editingReview.value) {
    // 수정 로직
    const index = completedReviews.value.findIndex(r => r.id === editingReview.value!.id)
    if (index > -1) {
      completedReviews.value[index]!.rating = modalRating.value
      completedReviews.value[index]!.tags = [...modalTags.value]
      completedReviews.value[index]!.content = modalContent.value
    }
  } else if (currentPendingReview.value) {
    // 새 작성 로직
    const newReview = {
      id: Date.now(),
      counselor: currentPendingReview.value.counselor,
      consultationDate: currentPendingReview.value.consultationDate,
      rating: modalRating.value,
      tags: [...modalTags.value],
      content: modalContent.value
    }

    completedReviews.value.unshift(newReview)

    // 대기 목록에서 제거
    const pendingIndex = pendingReviews.value.findIndex(r => r.id === currentPendingReview.value.id)
    if (pendingIndex > -1) {
      pendingReviews.value.splice(pendingIndex, 1)
    }
  }

  closeModal()
}

const deleteReview = async (reviewId: number) => {
  if (!confirm('정말로 이 후기를 삭제하시겠습니까?')) return

  // 여기에 실제 API 호출 로직 추가
  const index = completedReviews.value.findIndex(r => r.id === reviewId)
  if (index > -1) {
    completedReviews.value.splice(index, 1)
  }
}
</script>

<style src="~/assets/css/user/reviews.css" scoped></style>