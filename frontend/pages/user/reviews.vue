<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <!-- 탭 메뉴 -->
    <div class="tab-menu">
      <div class="tab-list">
        <div
          class="tab-item"
          :class="{ active: activeTab === 'completed' }"
          @click="switchTab('completed')"
        >
          작성한 후기
          <span class="tab-badge">{{ summary?.total_my_reviews || 0 }}</span>
        </div>
        <div
          class="tab-item"
          :class="{ active: activeTab === 'pending' }"
          @click="switchTab('pending')"
        >
          작성 대기
          <span class="tab-badge">{{ summary?.total_pending_reviews || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 리뷰 통계 -->
      <section class="review-stats">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ Number(summary?.average_rating ?? 0).toFixed(1) }}</div>
            <div class="stat-label">평균 평점</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ (summary?.earned_points ?? 0).toLocaleString() }}P</div>
            <div class="stat-label">받은 포인트</div>
          </div>
        </div>
      </section>

      <!-- 리뷰 리스트 -->
      <div class="review-list">
        <!-- 작성 대기 탭 -->
        <template v-if="activeTab === 'pending'">
          <div v-if="pendingItems.length === 0 && !isLoading" class="empty-state">
            <div class="empty-icon">📝</div>
            <div class="empty-title">작성 대기 중인 후기가 없습니다</div>
            <div class="empty-desc">상담 후 후기를 작성하고 포인트를 받아보세요!</div>
          </div>
          <div
            v-for="item in pendingItems"
            :key="item.session_id"
            class="review-card pending"
          >
            <div class="review-header">
              <div class="counselor-info">
                <div>
                  <img
                    v-if="getCounselorImage(item.counselor?.profile_image_url)"
                    :src="getCounselorImage(item.counselor?.profile_image_url)"
                    alt="프로필 이미지"
                    class="w-12 h-12 rounded-full object-cover border border-white/10"
                    width="48"
                    height="48"
                    loading="lazy"
                  />
                  <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
                </div>
                <div class="counselor-details">
                  <div class="counselor-name">{{ item.counselor?.nickname || '상담사' }}</div>
                  <div class="consultation-date">{{ (item.starttm || '') }} 상담</div>
                  <div class="consultation-time">{{ formatPendingMinutes(item.realchattm) }}분 상담</div>
                </div>
              </div>
              <div class="review-status pending">작성 대기</div>
            </div>
            <div class="review-content">
              <p class="review-placeholder">아직 후기를 작성하지 않으셨습니다. 후기를 작성하고 100P를 받아보세요!</p>
            </div>
            <div class="review-actions">
              <button class="review-button write-button" @click="openWriteModal(item)">후기 작성하기</button>
            </div>
          </div>
          <div ref="infiniteSentinel" class="h-8"></div>
        </template>

        <!-- 작성한 후기 탭 -->
        <template v-if="activeTab === 'completed'">
          <div v-if="reviewItems.length === 0 && !isLoading" class="empty-state">
            <div class="empty-icon">📝</div>
            <div class="empty-title">작성한 후기가 없습니다</div>
            <div class="empty-desc">첫 상담 후기를 작성해보세요!</div>
            <NuxtLink to="/chat" class="empty-button">상담 받러 가기</NuxtLink>
          </div>
          <div
            v-for="review in reviewItems"
            :key="review.review_id"
            class="review-card"
          >
            <div class="review-header">
              <div class="counselor-info">
                <div>
                  <img
                    v-if="getCounselorImage(review.counselor?.profile_image_url)"
                    :src="getCounselorImage(review.counselor?.profile_image_url)"
                    alt="프로필 이미지"
                    class="w-12 h-12 rounded-full object-cover border border-white/10"
                    width="48"
                    height="48"
                    loading="lazy"
                  />
                  <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
                </div>
                <div class="counselor-details">
                  <div class="counselor-name">{{ review.counselor?.nickname || '상담사' }}</div>
                  <div class="consultation-date">{{ new Date(review.created_at).toLocaleString() }}</div>
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
            <div v-if="review.review_tags && review.review_tags.length > 0" class="review-tags">
              <span v-for="tag in review.review_tags" :key="tag" class="review-tag">{{ tag }}</span>
            </div>
            <div class="review-content">
              {{ review.content }}
            </div>

            <!-- 상담사 답변 -->
            <div v-if="review.counselor_reply" class="counselor-reply">
              <div class="reply-header">
                <div class="reply-icon">💬</div>
                <div class="reply-label">{{ review.counselor?.nickname || '상담사' }} 선생님의 답변</div>
                <div class="reply-date">{{ new Date(review.counselor_replied_at || review.created_at).toLocaleString() }}</div>
              </div>
              <div class="reply-content">
                {{ review.counselor_reply }}
              </div>
            </div>

            <div class="review-actions">
              <button class="review-button edit-button" @click="openEditModal(review)">수정</button>
              <button class="review-button delete-button" @click="deleteReview(review.review_id)">삭제</button>
            </div>
          </div>
          <div ref="infiniteSentinel" class="h-8"></div>
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
            :disabled="!isValidReview || submitting"
          >
            {{ submitting ? '처리중...' : (isEditing ? '수정완료' : '작성완료') }}
          </button>
        </div>
      </div>
    </div>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'
import { ref, computed, onMounted } from 'vue'
import { useNuxtApp } from 'nuxt/app'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useNotify } from '~/composables/utils/useNotify'
import { useCdn } from '~/composables/utils/useCdn'

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

// API 상태
const summary = ref<any>(null)
const reviewItems = ref<any[]>([])
const pendingItems = ref<any[]>([])
const page = ref(1)
const totalPages = ref(1)
const limit = 10
const isLoading = ref(false)
const infiniteSentinel = ref<HTMLDivElement | null>(null)
const { cdnUrl } = useCdn()
const getCounselorImage = (path?: string | null) => {
  return cdnUrl('cs', path || '')
}

// 초기 데이터 로드
const { createUserReview, updateUserReview, deleteUserReview, fetchUserReviewSummary, fetchUserReviews } = useUserQueries()
const { notifyConfirm, notifySuccess, notifyError } = useNotify()

const loadSummary = async () => {
  const res = await fetchUserReviewSummary()
  summary.value = res
}

const fetchList = async () => {
  if (page.value > totalPages.value) return
  const res = await fetchUserReviews({ searchtype: activeTab.value === 'completed' ? 'my_reviews' : 'pending_reviews', page: page.value, limit })
  const items = (res.data as any[]) || []
  const tp = (res.meta as any)?.pagination?.total_pages
  totalPages.value = typeof tp === 'number' && tp > 0 ? tp : 1
  if (activeTab.value === 'completed') {
    reviewItems.value.push(...items)
  } else {
    pendingItems.value.push(...items)
  }
}

const switchTab = async (tab: 'completed' | 'pending') => {
  if (activeTab.value === tab) return
  activeTab.value = tab
  // reset list
  page.value = 1
  reviewItems.value = []
  pendingItems.value = []
  await fetchList()
}

onMounted(async () => {
  await loadSummary()
  await fetchList()
  // infinite scroll
  const io = new IntersectionObserver((entries) => {
    entries.forEach(async (e) => {
      if (e.isIntersecting && !isLoading.value && page.value < totalPages.value) {
        isLoading.value = true
        page.value += 1
        try { await fetchList() } finally { isLoading.value = false }
      }
    })
  })
  if (infiniteSentinel.value) io.observe(infiniteSentinel.value)
})

const isValidReview = computed(() => {
  return modalRating.value > 0 && modalContent.value.length >= 20
})

const submitting = ref(false)

// 유틸리티 함수
const formatDate = (date: Date) => {
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const formatPendingMinutes = (sec?: number | null) => {
  const s = Number(sec || 0)
  return Math.max(1, Math.ceil(s / 60))
}

// 모달 관련 함수
const openWriteModal = (item: any) => {
  isEditing.value = false
  currentPendingReview.value = item
  // reset only input fields, keep selection
  modalRating.value = 0
  modalTags.value = []
  modalContent.value = ''
  hoverRating.value = 0
  editingReview.value = null
  showModal.value = true
}

const openEditModal = (review: any) => {
  isEditing.value = true
  editingReview.value = review
  modalRating.value = review.rating
  modalTags.value = Array.isArray(review.review_tags) ? [...review.review_tags] : []
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

  if (isEditing.value && editingReview.value) {
    submitting.value = true
    try {
      await updateUserReview({ session_id: editingReview.value.session_id, rating: modalRating.value, content: modalContent.value, review_tags: [...modalTags.value] })
      // refresh
      page.value = 1
      reviewItems.value = []
      await loadSummary()
      await fetchList()
      closeModal()
    } finally {
      submitting.value = false
    }
  } else if (currentPendingReview.value) {
    submitting.value = true
    try {
      const sid = Number((currentPendingReview.value as any)?.session_id)
      if (!sid || Number.isNaN(sid)) {
        console.error('Invalid session_id for review creation')
        return
      }
      await createUserReview({ session_id: sid, rating: modalRating.value, content: modalContent.value, review_tags: [...modalTags.value] })
      // refresh both lists and summary
      page.value = 1
      reviewItems.value = []
      pendingItems.value = []
      await loadSummary()
      await fetchList()
      closeModal()
    } finally {
      submitting.value = false
    }
  }
}

const deleteReview = async (reviewId: number) => {
  const confirmed = await notifyConfirm('해당 후기를 삭제하시겠습니까?')
  if (!confirmed) return
  try {
    await deleteUserReview(reviewId)
    notifySuccess('삭제되었습니다.')
    // refresh
    page.value = 1
    reviewItems.value = []
    await loadSummary()
    await fetchList()
  } catch (e: any) {
    notifyError(e?.message || '삭제에 실패했습니다.')
  }
}
</script>

<style src="~/assets/css/user/reviews.css" scoped></style>