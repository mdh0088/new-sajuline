<template>
  <div class="min-h-screen bg-slate-950 text-white">

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
            <div class="review-top">
              <div class="counselor-profile">
                <div class="profile-image">
                  <img
                    v-if="getCounselorImage(item.counselor?.profile_image_url)"
                    :src="getCounselorImage(item.counselor?.profile_image_url)"
                    alt="프로필 이미지"
                    width="40"
                    height="40"
                    loading="lazy"
                  />
                  <div v-else class="profile-placeholder">🔮</div>
                </div>
                <div class="counselor-info-text">
                  <div class="counselor-name">{{ item.counselor?.nickname || '상담사' }}</div>
                  <div class="review-meta">
                    <span>{{ formatDateTime(item.starttm || '') }} 상담</span>
                    <span class="meta-divider">·</span>
                    <span>{{ formatPendingMinutes(item.realchattm) }}분</span>
                  </div>
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
          </div>
          <div
            v-for="review in reviewItems"
            :key="review.review_id"
            class="review-card"
          >
            <div class="review-top">
              <div class="counselor-profile">
                <div class="profile-image">
                  <img
                    v-if="getCounselorImage(review.counselor?.profile_image_url)"
                    :src="getCounselorImage(review.counselor?.profile_image_url)"
                    alt="프로필 이미지"
                    width="40"
                    height="40"
                    loading="lazy"
                  />
                  <div v-else class="profile-placeholder">🔮</div>
                </div>
                <div class="counselor-info-text">
                  <div class="counselor-name">{{ review.counselor?.nickname || '상담사' }}</div>
                  <div class="review-meta">
                    <span>{{ formatDateTime(review.starttm || review.created_at) }} 상담</span>
                    <span v-if="review.realchattm" class="meta-divider">·</span>
                    <span v-if="review.realchattm">{{ formatPendingMinutes(review.realchattm) }}분</span>
                  </div>
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
                <div class="reply-date">{{ formatDateTime(review.counselor_replied_at || review.created_at) }}</div>
              </div>
              <div class="reply-content">
                {{ review.counselor_reply }}
              </div>
            </div>
          </div>
          <div ref="infiniteSentinel" class="h-8"></div>
        </template>
      </div>
    </main>

    <!-- 리뷰 작성/수정 모달 -->
    <ReviewWriteModal
      :is-visible="showModal"
      :is-editing="isEditing"
      :initial-data="modalData"
      :submitting="submitting"
      @close="closeModal"
      @submit="handleModalSubmit"
    />

  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'
import { ref, computed, onMounted } from 'vue'
import { useNuxtApp } from 'nuxt/app'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useNotify } from '~/composables/utils/useNotify'
import { useCdn } from '~/composables/utils/useCdn'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// SEO 메타 데이터 설정
useHead({
  title: '내 리뷰 관리 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

// 반응형 데이터
const activeTab = ref<'completed' | 'pending'>('completed')
const showModal = ref(false)
const isEditing = ref(false)
const editingReview = ref<any>(null)
const currentPendingReview = ref<any>(null)

// 모달 데이터
const modalData = ref({
  rating: 0,
  tags: [] as string[],
  content: ''
})

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
  return modalData.value.rating > 0 && modalData.value.content.length >= 20
})

const submitting = ref(false)

// 유틸리티 함수
const formatDate = (date: Date) => {
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}.${month}.${day} ${hours}:${minutes}`
}

const formatPendingMinutes = (sec?: number | null) => {
  const s = Number(sec || 0)
  return Math.max(1, Math.ceil(s / 60))
}

// 모달 관련 함수
const openWriteModal = (item: any) => {
  isEditing.value = false
  currentPendingReview.value = item
  editingReview.value = null
  // 모달 데이터 초기화
  modalData.value = {
    rating: 0,
    tags: [],
    content: ''
  }
  showModal.value = true
}

const openEditModal = (review: any) => {
  isEditing.value = true
  editingReview.value = review
  currentPendingReview.value = null
  // 기존 리뷰 데이터로 초기화
  modalData.value = {
    rating: review.rating,
    tags: Array.isArray(review.review_tags) ? [...review.review_tags] : [],
    content: review.content
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  resetModalForm()
}

const resetModalForm = () => {
  modalData.value = {
    rating: 0,
    tags: [],
    content: ''
  }
  editingReview.value = null
  currentPendingReview.value = null
}

const handleModalSubmit = async (data: { rating: number, tags: string[], content: string }) => {
  submitting.value = true
  try {
    if (isEditing.value && editingReview.value) {
      await updateUserReview({
        session_id: editingReview.value.session_id,
        rating: data.rating,
        content: data.content,
        review_tags: [...data.tags]
      })
    } else if (currentPendingReview.value) {
      const sid = Number((currentPendingReview.value as any)?.session_id)
      if (!sid || Number.isNaN(sid)) {
        console.error('Invalid session_id for review creation')
        return
      }
      await createUserReview({
        session_id: sid,
        rating: data.rating,
        content: data.content,
        review_tags: [...data.tags]
      })
    }

    // refresh
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