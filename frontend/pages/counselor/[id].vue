<template>
  <div class="counselor-detail-page">

    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <!-- 로딩 상태 -->
      <div v-if="pending" class="loading-container">
        <div class="loading-spinner"></div>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="error-container">
        <p>상담사 정보를 불러올 수 없습니다.</p>
        <button @click="refresh" class="retry-button">다시 시도</button>
      </div>

      <!-- 상담사 정보 -->
      <template v-else-if="counselor">
        <!-- 프로필 섹션 -->
        <section class="profile-section">
          <div class="profile-avatar">
            <img v-if="profileImageUrl" :src="profileImageUrl" alt="프로필" />
            <div v-else class="avatar-skeleton" />
          </div>
          <div class="profile-name-row">
            <h1 class="profile-name">{{ counselor.nickname }}</h1>
            <span class="profile-counselor-code">{{ counselor.counselor_code }}</span>
          </div>
          <div class="profile-specialty">{{ specialtyLabel }}</div>
          <p class="profile-intro">{{ counselor.introduction_short }}</p>

          <div class="profile-stats">
            <div class="stat">
              <div class="stat-value">{{ (counselor.rating_avg ?? 0).toFixed(1) }}</div>
              <div class="stat-label">평점</div>
            </div>
            <div class="stat">
              <div class="stat-value">{{ (counselor.consultation_count ?? 0).toLocaleString() }}</div>
              <div class="stat-label">상담건수</div>
            </div>
          </div>
        </section>

        <!-- 전문 분야 -->
        <section class="expertise-section">
          <h3 class="section-title">전문 분야</h3>
          <div class="expertise-tags">
            <div
              v-for="kw in keywordList"
              :key="kw"
              class="expertise-tag"
            >
              {{ kw }}
            </div>
          </div>
        </section>

        <!-- 상담사 소개 -->
        <section class="intro-section">
          <h3 class="section-title">상담사 소개</h3>
          <div class="intro-content">
            <p v-html="counselor.greeting_message || ''"></p>
          </div>

          <div class="highlight-box">
            <div class="highlight-title">{{ counselor.nickname }} 선생님만의 특별함</div>
            <div class="highlight-text" v-if="careerList.length">
              <div v-for="item in careerList" :key="item">✔{{ item }}</div>
            </div>
          </div>
        </section>

        <!-- 활동시간 섹션 -->
        <section class="activity-time-section">
          <h3 class="section-title">활동 시간</h3>
          <div class="activity-time-content">
            <div class="time-info">
              {{ counselor.work_time || '' }}
            </div>
          </div>
        </section>

        <!-- 상담후기/상담문의 탭 섹션 -->
        <section class="tabs-section">
          <div class="tab-header">
            <button
              :class="['tab-button', { active: activeTab === 'reviews' }]"
              @click="activeTab = 'reviews'"
            >
              상담 후기
            </button>
            <button
              :class="['tab-button', { active: activeTab === 'inquiries' }]"
              @click="activeTab = 'inquiries'"
            >
              상담 문의
            </button>
          </div>

          <!-- 상담 후기 탭 -->
          <div v-if="activeTab === 'reviews'" class="tab-content">
            <div class="tab-header-actions">
              <!-- <div class="review-summary">
                <div class="rating-large">{{ counselor.rating }}</div>
                <div class="rating-details">
                  <div class="stars">
                    <img
                      v-for="i in 5"
                      :key="i"
                      src="/images/favorite.png"
                      alt="별점"
                      class="star"
                      :class="{ filled: i <= Math.floor(counselor.rating), 'star-empty': i > Math.floor(counselor.rating) }"
                      width="16"
                      height="16"
                    />
                  </div>
                  <div class="review-count">{{ counselor.reviewCount.toLocaleString() }}개의 리뷰</div>
                </div>
              </div> -->
              <!-- <button class="tab-action-button" @click="writeReview">
                <span class="button-icon">✏️</span>
                <span>후기 작성하기</span>
              </button> -->
            </div>

            <div class="scrollable-content" ref="reviewScrollEl">
              <div
                v-for="review in reviewItems"
                :key="review.review_id"
                class="review-card"
              >
                <div class="review-header">
                  <div class="reviewer-info">
                    <span class="reviewer-name">{{ maskName(review.user_id) }}</span>
                    <span class="review-date">{{ formatDate(review.created_at) }}</span>
                  </div>
                  <div class="review-rating">
                    <img
                      v-for="i in 5"
                      :key="i"
                      src="/images/favorite.png"
                      alt="별점"
                      class="star"
                      :class="{ filled: i <= review.rating, 'star-empty': i > review.rating }"
                      width="14"
                      height="14"
                    />
                  </div>
                </div>
                <div class="review-content">
                  {{ review.content }}
                </div>
              </div>
              <div ref="reviewSentinel" />
              <div v-if="isLoadingMoreReviews" class="loading-spinner" style="padding: 12px 0; text-align: center;"></div>
              <div v-else-if="!reviewHasMore && reviewItems.length > 0" style="padding: 8px 0; text-align: center; color: rgba(255,255,255,0.5); font-size: 12px;">더 이상 항목이 없습니다</div>
            </div>
          </div>

          <!-- 상담 문의 탭 -->
          <div v-if="activeTab === 'inquiries'" class="tab-content">
            <div class="tab-header-actions">
              <button class="tab-action-button" @click="writeInquiry">
                <span class="button-icon"><img src="/images/cs.png" alt="문의" width="18" height="18" /></span>
                <span>문의하기</span>
              </button>
            </div>

            <div class="scrollable-content" ref="inquiryScrollEl">
              <div
                v-for="inquiry in inquiryItems"
                :key="inquiry.inquiry_id"
                class="inquiry-card"
                :class="{ 'has-reply': inquiry.has_reply && canViewInquiry(inquiry), 'expanded': isInquiryExpanded(inquiry.inquiry_id), 'is-secret': !canViewInquiry(inquiry) }"
                @click="inquiry.has_reply && canViewInquiry(inquiry) && toggleInquiryExpand(inquiry.inquiry_id)"
              >
                <div class="inquiry-header">
                  <div class="inquirer-info">
                    <span class="inquirer-name">{{ maskName(inquiry.inquirer_id || '손님') }}</span>
                    <span class="inquiry-date">{{ formatDate(inquiry.created_at) }}</span>
                  </div>
                  <div v-if="!canViewInquiry(inquiry)" class="secret-badge">🔒 비밀글</div>
                </div>
                <div class="inquiry-content">
                  <template v-if="canViewInquiry(inquiry)">
                    {{ inquiry.content || '' }}
                  </template>
                  <template v-else>
                    <div class="secret-message">
                      <span class="secret-icon">🔒</span>
                      <span>비밀글입니다</span>
                    </div>
                  </template>
                </div>
                <div v-if="inquiry.has_reply && canViewInquiry(inquiry)" class="reply-indicator">
                  <span class="reply-icon">💬</span>
                  <span class="reply-text">상담사 답변</span>
                  <span class="expand-icon">{{ isInquiryExpanded(inquiry.inquiry_id) ? '▲' : '▼' }}</span>
                </div>
                <div v-if="inquiry.has_reply && canViewInquiry(inquiry) && isInquiryExpanded(inquiry.inquiry_id)" class="counselor-reply">
                  <div class="reply-header">
                    <span class="reply-author">{{ counselor.nickname }} 선생님</span>
                    <span class="reply-date">{{ formatDate(getInquiryAnsweredAt(inquiry)) }}</span>
                  </div>
                  <div class="reply-content">
                    {{ getInquiryReply(inquiry) || '답변이 등록되었습니다.' }}
                  </div>
                </div>
              </div>
              <div ref="inquirySentinel" />
              <div v-if="isLoadingMoreInquiries" class="loading-spinner" style="padding: 12px 0; text-align: center;"></div>
              <div v-else-if="!inquiryHasMore && inquiryItems.length > 0" style="padding: 8px 0; text-align: center; color: rgba(255,255,255,0.5); font-size: 12px;">더 이상 항목이 없습니다</div>
            </div>
          </div>
        </section>

      </template>
    </div>

    <!-- 하단 CTA -->
    <div v-if="counselor" class="bottom-cta">
      <div class="cta-buttons">
        <button v-if="showFavorite" class="favorite-button" :disabled="favoritePending" @click="toggleFavorite">
          <span class="star-icon" :class="{ 'filled': isFavorite }">⭐</span>
        </button>
        <!-- 채팅 상담 버튼 - 주석 처리 -->
        <!--
        <button class="cta-button cta-secondary" @click="startChatConsult">
          <span>💬</span>
          <span>채팅 상담</span>
        </button>
        -->
        <button class="cta-button cta-primary" @click="openPhoneModal">
          <span>📞</span>
          <span>전화 상담</span>
        </button>
      </div>
    </div>

    <!-- 전화 상담 모달 (로그인 유저용) -->
    <PhoneConsultModal
      v-if="modalCounselorData && isUser"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      :user-points="userPoints"
      @close="closePhoneModal"
      @start-point-consult="handlePointConsult"
      @start060-consult="handle060Consult"
      @go-to-charge="goToCharge"
    />

    <!-- 전화 상담 모달 (비로그인 유저용) -->
    <GuestPhoneConsultModal
      v-if="modalCounselorData && !isUser"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      @close="closePhoneModal"
      @start060-consult="handle060Consult"
      @go-to-register-login="goToRegisterLogin"
    />

    <!-- 후기 작성 모달 -->
    <ReviewWriteModal
      :is-visible="showReviewModal"
      :is-editing="false"
      :initial-data="reviewData"
      :submitting="reviewSubmitting"
      @close="closeReviewModal"
      @submit="submitReview"
    />

    <!-- 문의하기 모달 -->
    <InquiryWriteModal
      :is-visible="showInquiryModal"
      :submitting="inquirySubmitting"
      @close="closeInquiryModal"
      @submit="submitInquiry"
    />
  </div>
</template>

<script setup lang="ts">
// 컴포넌트 import (Nuxt auto-import)
// AppHeader와 PhoneConsultModal은 자동 import됨
import { computed, ref, onMounted, onBeforeUnmount, watch, watchEffect } from 'vue'
import { useRoute, useSeoMeta, navigateTo } from 'nuxt/app'

definePageMeta({
  hideBottomNav: true // 하단 네비게이션 숨김
})
import { useUserPoints } from '~/composables/user/useUserPoints'
import { useNotify } from '~/composables/utils/useNotify'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { useBookmarkQueries } from '~/composables/api/useBookmarkQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { useCdn } from '~/composables/utils/useCdn'
import type { CounselorPublic } from '~/types/counselor/detail'
import type { ReviewSummary } from '~/types/counselor/review'
import type { InquirySummary } from '~/types/counselor/inquiry'
interface CounselorReview {
  id: number
  userName: string
  rating: number
  content: string
  createdAt: string
  counselorReply?: string
  replyCreatedAt?: string
}

interface CounselorInquiry {
  id: number
  userName: string
  content: string
  status: 'pending' | 'answered' | 'closed'
  createdAt: string
  counselorReply?: string
  replyCreatedAt?: string
}

interface CounselorDetail {
  id: number
  name: string
  title: string
  experience: number
  emoji: string
  isOnline: boolean
  rating: number
  consultCount: number
  reviewCount: number
  specialties: string[]
  introduction: string
  highlights?: string[]
  activityTime?: string
  reviews: CounselorReview[]
  inquiries: CounselorInquiry[]
  chatRate: number
  phoneRate: number
  pointRate: number
  rate060: number
  firstDiscountRate?: number
}

// 라우트 파라미터
const route = useRoute()
const counselorCode = computed(() => route.params.id as string)

// 상태
const pending = ref(true)
const error = ref<Error | null>(null)

const counselor = ref<CounselorPublic | null>(null)
const reviewItems = ref<ReviewSummary[]>([])
const inquiryItems = ref<InquirySummary[]>([])

// 페이징/무한스크롤 상태 (후기)
const reviewPage = ref(1)
const reviewTotalPages = ref(1)
const reviewHasMore = computed(() => reviewPage.value < reviewTotalPages.value)
const isLoadingMoreReviews = ref(false)
const reviewSentinel = ref<HTMLElement | null>(null)
const reviewScrollEl = ref<HTMLElement | null>(null)
let reviewObserver: IntersectionObserver | null = null

// 페이징/무한스크롤 상태 (문의)
const inquiryPage = ref(1)
const inquiryTotalPages = ref(1)
const inquiryHasMore = computed(() => inquiryPage.value < inquiryTotalPages.value)
const isLoadingMoreInquiries = ref(false)
const inquirySentinel = ref<HTMLElement | null>(null)
const inquiryScrollEl = ref<HTMLElement | null>(null)
let inquiryObserver: IntersectionObserver | null = null

// 로그인 유저 포인트 (store)
const { points: storePoints } = useUserPoints()
const userPoints = computed(() => storePoints.value)

// 즐겨찾기 상태
const isFavorite = ref(false)
const favoritePending = ref(true)
const showFavorite = ref(false)

// 탭 상태 관리
const activeTab = ref<'reviews' | 'inquiries'>('reviews')

// 확장된 항목 추적
const expandedReviews = ref<Set<number>>(new Set())
const expandedInquiries = ref<Set<number>>(new Set())
// CDN 베이스를 사용해 프로필 이미지 절대 URL 생성 (mypage 참조 + 절대 URL 대응)
const { cdnUrl } = useCdn()
const profileImageUrl = computed(() => {
  const raw = (counselor.value?.profile_image_url || '').trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return cdnUrl(raw)
  return cdnUrl('cs', raw)
})


const refresh = () => {
  // 실제 API 연결 시 구현
}

// 전화 상담 모달
const showPhoneModal = ref(false)

// 후기 작성 모달
const showReviewModal = ref(false)
const reviewSubmitting = ref(false)
const reviewData = ref({
  rating: 0,
  tags: [],
  content: ''
})

// 문의하기 모달
const showInquiryModal = ref(false)
const inquirySubmitting = ref(false)

// Notivue 알림
const { notifySuccess, notifyError } = useNotify()

// PhoneConsultModal에 전달할 데이터 형식 변환
const modalCounselorData = computed(() => {
  if (!counselor.value) return null
  return {
    code: (counselor.value as any).counselor_code ?? counselor.value.counselor_id,
    nickname: counselor.value.nickname,
    profile_image_url: counselor.value.profile_image_url,
    specialties: specialtyList.value,
    // after_amount, before_amount may not exist in /public/{counselor_code}; allow undefined
    afterAmount: (counselor.value as any).after_amount ?? null,
    beforeAmount: (counselor.value as any).before_amount ?? null
  }
})

// 메서드들
const openPhoneModal = () => {
  showPhoneModal.value = true
}

const closePhoneModal = () => {
  showPhoneModal.value = false
}

const handlePointConsult = (counselorId: string) => {
  console.log('포인트 상담 시작:', counselorId)
  // TODO: 포인트 상담 시작 API 호출
}

const handle060Consult = (counselorId: string) => {
  console.log('060 상담 시작:', counselorId)
  // TODO: 060 상담 연결 로직
}

const goToCharge = () => {
  // 포인트 충전 페이지로 이동
  navigateTo('/point')
}

const goToRegisterLogin = () => {
  // 로그인/회원가입 페이지로 이동
  navigateTo('/login')
}

const startChatConsult = () => {
  // 채팅 상담 시작 (추후 구현)
  navigateTo(`/chat/${counselor.value?.counselor_id || counselorCode.value}`)
}

const { useCheckBookmark, useAddBookmark, useRemoveBookmark } = useBookmarkQueries()
const { isUser, currentUser } = useAuth()

const { data: _bookmarkChecked, refetch: refetchBookmark } = useCheckBookmark(computed(() => counselor.value?.counselor_id || ''), { enabled: computed(() => false) })
const addBookmarkMutation = useAddBookmark({
  onSuccess: () => {
    isFavorite.value = true
    notifySuccess('즐겨찾기에 등록되었습니다.')
  },
  onError: (err: any) => {
    notifyError(err?.message || '즐겨찾기 등록에 실패했습니다.')
  }
})
const removeBookmarkMutation = useRemoveBookmark({
  onSuccess: () => {
    isFavorite.value = false
    notifySuccess('즐겨찾기가 해제되었습니다.')
  },
  onError: (err: any) => {
    notifyError(err?.message || '즐겨찾기 해제에 실패했습니다.')
  }
})

const toggleFavorite = async () => {
  if (!counselor.value) return
  if (!isUser.value) return
  const cid = counselor.value.counselor_id
  try {
    if (isFavorite.value) {
      await removeBookmarkMutation.mutateAsync(cid)
    } else {
      await addBookmarkMutation.mutateAsync(cid)
    }
  } catch (_) {
    // 알림은 onError에서 처리됨
  }
}

// 유틸리티 함수들
const maskName = (name: string) => {
  if (name.length <= 1) return name
  return name.charAt(0) + '*'.repeat(name.length - 1)
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const getInquiryStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return '답변대기'
    case 'answered':
      return '답변완료'
    case 'closed':
      return '문의종료'
    default:
      return '알 수 없음'
  }
}

// 안전한 답변 헬퍼들 (백엔드 오타/이행기 대응)
const getReviewReply = (review: ReviewSummary): string | null => {
  return (review as any).counselor_reply ?? (review as any).content_reply ?? null
}
const getReviewRepliedAt = (review: ReviewSummary): string => {
  return ((review as any).counselor_replied_at ?? (review as any).counselor_repied_at ?? review.created_at) as string
}
const getInquiryReply = (inquiry: InquirySummary): string | null => {
  return (inquiry as any).reply_content ?? (inquiry as any).reply_contetn ?? null
}
const getInquiryAnsweredAt = (inquiry: InquirySummary): string => {
  return (inquiry.answered_at ?? inquiry.created_at) as string
}

// 후기 작성 모달 관련 함수들
const openReviewModal = () => {
  // 모달 데이터 초기화
  reviewData.value = {
    rating: 0,
    tags: [],
    content: ''
  }
  showReviewModal.value = true
}

const closeReviewModal = () => {
  showReviewModal.value = false
}

const submitReview = async (data: { rating: number, tags: string[], content: string }) => {
  reviewSubmitting.value = true
  try {
    // TODO: 실제 API 호출로 후기 작성
    console.log('후기 제출:', {
      counselorId: counselorCode.value,
      ...data
    })

    // 성공 처리 (예시)
    await new Promise(resolve => setTimeout(resolve, 1000)) // 임시 딜레이

    // 성공 메시지 (Notivue)
    notifySuccess('후기가 성공적으로 작성되었습니다.')

    closeReviewModal()
  } catch (error: any) {
    console.error('후기 작성 실패:', error)
    notifyError(error?.message || '후기 작성에 실패했습니다. 다시 시도해주세요.')
  } finally {
    reviewSubmitting.value = false
  }
}

// 버튼 핸들러 함수들
const writeReview = () => {
  openReviewModal()
}

// 문의하기 모달 관련 함수들
const openInquiryModal = () => {
  showInquiryModal.value = true
}

const closeInquiryModal = () => {
  showInquiryModal.value = false
}

const submitInquiry = async (data: { content: string }) => {
  inquirySubmitting.value = true
  try {
    await createUserInquiry({
      counselor_id: counselor.value!.counselor_id,
      content: data.content
    })
    // 성공 후 목록 재조회
    inquiryItems.value = []
    inquiryPage.value = 1
    await fetchInquiries(1, false)
    notifySuccess('문의가 성공적으로 등록되었습니다.')
    closeInquiryModal()
  } catch (error: any) {
    console.error('문의 작성 실패:', error)
    notifyError(error?.message || '문의 작성에 실패했습니다. 다시 시도해주세요.')
  } finally {
    inquirySubmitting.value = false
  }
}

const writeInquiry = () => {
  openInquiryModal()
}

// 답변 확장/축소 토글
const toggleReviewExpand = (reviewId: number) => {
  if (expandedReviews.value.has(reviewId)) {
    expandedReviews.value.delete(reviewId)
  } else {
    expandedReviews.value.add(reviewId)
  }
}

const toggleInquiryExpand = (inquiryId: number) => {
  if (expandedInquiries.value.has(inquiryId)) {
    expandedInquiries.value.delete(inquiryId)
  } else {
    expandedInquiries.value.add(inquiryId)
  }
}

const isReviewExpanded = (reviewId: number) => {
  return expandedReviews.value.has(reviewId)
}

const isInquiryExpanded = (inquiryId: number) => {
  return expandedInquiries.value.has(inquiryId)
}

// 문의 내용 열람 권한 확인 (본인 작성만 볼 수 있음)
const canViewInquiry = (inquiry: InquirySummary) => {
  if (!isUser.value) return false
  if (!currentUser.value?.user_id) return false
  return inquiry.inquirer_id === currentUser.value.user_id
}

// 페이지 메타데이터
useSeoMeta({
  title: () => counselor.value ? `${counselor.value.nickname} 선생님 - 사주라인` : '상담사 상세',
  description: () => counselor.value
    ? `${counselor.value.nickname} 선생님 | ${counselor.value.introduction_short || '전문 사주 상담사'}`
    : '전문 상담사와 함께하는 사주 상담 서비스',
  ogTitle: () => counselor.value ? `${counselor.value.nickname} 선생님 - 사주라인` : '상담사 상세',
  ogDescription: () => counselor.value?.introduction_short || '전문 사주 상담사',
  ogImage: () => counselor.value?.profile_image_url || 'https://sajuline.com/images/og-counselor-default.jpg',
  ogUrl: () => `https://sajuline.com${route.path}`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => counselor.value ? `${counselor.value.nickname} 선생님` : '상담사 상세',
  twitterDescription: () => counselor.value?.introduction_short || '전문 사주 상담사',
  twitterImage: () => counselor.value?.profile_image_url || 'https://sajuline.com/images/og-counselor-default.jpg'
})

// JSON-LD Person 스키마
const structuredData = computed(() => {
  if (!counselor.value) return null

  return {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": counselor.value.nickname,
    "jobTitle": "사주 전문 상담사",
    "description": counselor.value.introduction_short || counselor.value.greeting_message,
    "image": counselor.value.profile_image_url,
    "aggregateRating": counselor.value.rating_avg ? {
      "@type": "AggregateRating",
      "ratingValue": counselor.value.rating_avg,
      "reviewCount": counselor.value.consultation_count || 0,
      "bestRating": "5",
      "worstRating": "1"
    } : undefined,
    "makesOffer": {
      "@type": "Offer",
      "itemOffered": {
        "@type": "Service",
        "name": "사주 상담 서비스",
        "provider": {
          "@type": "Person",
          "name": counselor.value.nickname
        }
      }
    }
  }
})

// JSON-LD BreadcrumbList 스키마
const breadcrumbSchema = computed(() => {
  if (!counselor.value) return null

  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "홈",
        "item": "https://sajuline.com"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "상담사",
        "item": "https://sajuline.com/categories"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": counselor.value.nickname,
        "item": `https://sajuline.com${route.path}`
      }
    ]
  }
})

useHead({
  link: [
    { rel: 'canonical', href: `https://sajuline.com${route.path}` }
  ],
  script: computed(() => {
    const scripts = []
    if (structuredData.value) {
      scripts.push({
        type: 'application/ld+json',
        innerHTML: JSON.stringify(structuredData.value)
      })
    }
    if (breadcrumbSchema.value) {
      scripts.push({
        type: 'application/ld+json',
        innerHTML: JSON.stringify(breadcrumbSchema.value)
      })
    }
    return scripts
  })
})

// 데이터 로딩
// const { usePublicDetail, useCounselorReviews, useCounselorUserInquiries } = useCounselorQueries()
const specialtyMap: Record<string, string> = {
  SAJU: '전화사주',
  FOURTUNE: '전화신점',
  TARO: '전화타로'
}
const specialtyLabel = computed(() => {
  const list = (counselor.value?.specialty_types ?? []) as string[]
  if (!list || list.length === 0) return ''
  const mapped = list.map((k) => specialtyMap[k] || k)
  return mapped[0] ?? ''
})
const specialtyList = computed(() => {
  const list = (counselor.value?.specialty_types ?? []) as string[]
  return list.map((k) => specialtyMap[k] || k)
})

const keywordList = computed(() => {
  const raw = counselor.value?.keywords || ''
  return raw
    .split(',')
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
})

const careerList = computed(() => {
  const raw = counselor.value?.career_info || ''
  return raw
    .split('\n')
    .map((s) => s.trim().replace(/^✔\s*/, ''))
    .filter((s) => s.length > 0)
})

const { usePublicDetail, getPublicCounselorReviews, getPublicCounselorUserInquiries, createUserInquiry } = useCounselorQueries()
const { data: publicDetail, isFetching: isFetchingDetail, error: detailError } = usePublicDetail(counselorCode)

watchEffect(() => {
  pending.value = isFetchingDetail.value
  error.value = (detailError.value as any) || null
  if (publicDetail.value) {
    counselor.value = publicDetail.value
  }
})

const fetchReviews = async (page = 1, append = false) => {
  const res = await getPublicCounselorReviews({ counselor_id: counselor.value!.counselor_id, page, limit: 20, visible_only: true })
  if (append) {
    reviewItems.value = [...reviewItems.value, ...res.items]
  } else {
    reviewItems.value = res.items
  }
  reviewPage.value = res.page
  reviewTotalPages.value = res.total_pages
}

const fetchInquiries = async (page = 1, append = false) => {
  const res = await getPublicCounselorUserInquiries({ counselor_id: counselor.value!.counselor_id, page, limit: 20 })
  if (append) {
    inquiryItems.value = [...inquiryItems.value, ...res.items]
  } else {
    inquiryItems.value = res.items
  }
  inquiryPage.value = res.page
  inquiryTotalPages.value = res.total_pages
}

// IntersectionObserver 설정 (후기)
const setupReviewObserver = () => {
  if (reviewObserver) {
    reviewObserver.disconnect()
    reviewObserver = null
  }
  if (!reviewSentinel.value) return
  reviewObserver = new IntersectionObserver(async (entries) => {
    const entry = entries[0]
    if (!entry || !entry.isIntersecting) return
    if (activeTab.value !== 'reviews') return
    if (!reviewHasMore.value) return
    if (isLoadingMoreReviews.value) return
    isLoadingMoreReviews.value = true
    try {
      await fetchReviews(reviewPage.value + 1, true)
    } finally {
      isLoadingMoreReviews.value = false
    }
  }, { root: reviewScrollEl.value, threshold: 0.1 })
  reviewObserver.observe(reviewSentinel.value)
}

// IntersectionObserver 설정 (문의)
const setupInquiryObserver = () => {
  if (inquiryObserver) {
    inquiryObserver.disconnect()
    inquiryObserver = null
  }
  if (!inquirySentinel.value) return
  inquiryObserver = new IntersectionObserver(async (entries) => {
    const entry = entries[0]
    if (!entry || !entry.isIntersecting) return
    if (activeTab.value !== 'inquiries') return
    if (!inquiryHasMore.value) return
    if (isLoadingMoreInquiries.value) return
    isLoadingMoreInquiries.value = true
    try {
      await fetchInquiries(inquiryPage.value + 1, true)
    } finally {
      isLoadingMoreInquiries.value = false
    }
  }, { root: inquiryScrollEl.value, threshold: 0.1 })
  inquiryObserver.observe(inquirySentinel.value)
}

onMounted(async () => {
  const unwatch = watch(
    () => counselor.value?.counselor_id,
    async (val) => {
      if (val) {
        // 초기화 후 첫 페이지 로드
        reviewPage.value = 1
        reviewTotalPages.value = 1
        reviewItems.value = []
        inquiryPage.value = 1
        inquiryTotalPages.value = 1
        inquiryItems.value = []
        await Promise.all([fetchReviews(1, false), fetchInquiries(1, false)])
        // 즐겨찾기 초기 상태 로딩
        showFavorite.value = isUser.value
        if (isUser.value) {
          try {
            favoritePending.value = true
            const res = await refetchBookmark()
            isFavorite.value = Boolean(res?.data)
          } catch (_) {
            isFavorite.value = false
          } finally {
            favoritePending.value = false
          }
        } else {
          favoritePending.value = false
        }
        unwatch()
      }
    }
  )
  // 탭별 옵저버 초기화
  if (activeTab.value === 'reviews') {
    setupReviewObserver()
  } else {
    setupInquiryObserver()
  }
})

// 탭 전환 시 옵저버 재설정
watch(activeTab, (tab) => {
  if (tab === 'reviews') {
    if (inquiryObserver) inquiryObserver.disconnect()
    setupReviewObserver()
  } else {
    if (reviewObserver) reviewObserver.disconnect()
    setupInquiryObserver()
  }
})

// 센티넬 엘리먼트 마운트 시 옵저버 재설정
watch(reviewSentinel, () => {
  if (activeTab.value === 'reviews') setupReviewObserver()
})
watch(inquirySentinel, () => {
  if (activeTab.value === 'inquiries') setupInquiryObserver()
})

watch(reviewScrollEl, () => {
  if (activeTab.value === 'reviews') setupReviewObserver()
})
watch(inquiryScrollEl, () => {
  if (activeTab.value === 'inquiries') setupInquiryObserver()
})

onBeforeUnmount(() => {
  if (reviewObserver) reviewObserver.disconnect()
  if (inquiryObserver) inquiryObserver.disconnect()
})
</script>

<style>
@import '~/assets/css/counselor/detail.css';
</style>