<template>
  <div class="min-h-screen bg-slate-950 text-white pb-24">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">전체 후기</h1>
      <p class="page-subtitle">다른 사용자들의 상담 후기를 확인하세요</p>
      <p class="review-count">총 {{ totalCount.toLocaleString() }}개</p>
    </div>

    <!-- 후기 리스트 -->
    <main class="main-content">
      <div class="review-list">
        <!-- 빈 상태 -->
        <div v-if="reviewItems.length === 0 && !isLoading" class="empty-state">
          <div class="empty-icon">📝</div>
          <div class="empty-title">등록된 후기가 없습니다</div>
          <div class="empty-desc">첫 번째 후기를 작성해보세요!</div>
        </div>

        <!-- 후기 카드 -->
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
            <div class="review-date">{{ formatDateTime(review.created_at) }}</div>
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

        <!-- 무한 스크롤 감지 -->
        <div ref="infiniteSentinel" class="h-8"></div>

        <!-- 로딩 상태 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <div class="loading-text">후기를 불러오는 중...</div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useCdn } from '~/composables/utils/useCdn'

definePageMeta({
  requiresAuth: false
})

// 반응형 데이터
const reviewItems = ref<any[]>([])
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const limit = 20
const isLoading = ref(false)
const infiniteSentinel = ref<HTMLDivElement | null>(null)

// CDN
const { cdnUrl } = useCdn()
const getCounselorImage = (path?: string | null) => {
  return cdnUrl('cs', path || '')
}

// API
const { fetchAllPublicReviews } = useUserQueries()

// 데이터 로드
const fetchList = async () => {
  if (page.value > totalPages.value) return

  isLoading.value = true
  try {
    const res = await fetchAllPublicReviews({ page: page.value, limit })
    const items = (res.data as any[]) || []
    const meta = res.meta as any
    const tp = meta?.pagination?.total_pages
    const total = meta?.pagination?.total

    totalPages.value = typeof tp === 'number' && tp > 0 ? tp : 1
    totalCount.value = typeof total === 'number' ? total : 0

    reviewItems.value.push(...items)
  } catch (error) {
    console.error('Failed to fetch reviews:', error)
  } finally {
    isLoading.value = false
  }
}

// 유틸리티 함수
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

// 초기 로드 및 무한 스크롤
onMounted(async () => {
  await fetchList()

  // IntersectionObserver 설정
  const io = new IntersectionObserver(async (entries) => {
    const entry = entries[0]
    if (!entry || !entry.isIntersecting) return
    if (isLoading.value) return
    if (page.value >= totalPages.value) return

    page.value += 1
    await fetchList()
  })

  if (infiniteSentinel.value) {
    io.observe(infiniteSentinel.value)
  }
})

// SEO 메타 데이터 설정
useSeoMeta({
  title: '전체 후기 - 사주라인',
  description: '사주라인 전체 상담 후기를 확인하세요. 실제 사용자들의 생생한 상담 경험과 평가를 통해 믿을 수 있는 상담사를 선택하세요.',
  keywords: '사주 후기, 타로 후기, 상담 후기, 사용자 리뷰, 상담 평가, 사주라인 후기',
  ogTitle: '전체 후기 - 사주라인',
  ogDescription: '실제 사용자들의 생생한 상담 후기와 평가. 믿을 수 있는 상담사 선택을 도와드립니다.',
  ogImage: 'https://sajuline.com/images/og-reviews.jpg',
  ogUrl: 'https://sajuline.com/reviews',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: '전체 후기 - 사주라인',
  twitterDescription: '실제 사용자들의 생생한 상담 후기와 평가',
  twitterImage: 'https://sajuline.com/images/og-reviews.jpg',
  robots: 'index,follow'
})

useHead({
  link: [{ rel: 'canonical', href: 'https://sajuline.com/reviews' }]
})
</script>

<style src="~/assets/css/user/reviews.css" scoped></style>

<style scoped>
/* 페이지 헤더 */
.page-header {
  padding: 80px 20px 24px;
  text-align: left;
  background: linear-gradient(180deg, rgba(147, 51, 234, 0.1) 0%, transparent 100%);
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #B794F6 0%, #9333EA 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.review-count {
  font-size: 13px;
  color: #B794F6;
  font-weight: 600;
  margin: 0;
}

/* 메인 콘텐츠 조정 */
.main-content {
  margin-top: 0;
  padding: 0 20px 100px;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #B794F6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* 후기 날짜 */
.review-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
