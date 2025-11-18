<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <!-- 상단 안내 섹션 -->
      <section class="cs-info-section">
        <div class="cs-info-icon">🚀</div>
        <h2 class="cs-info-title">빠르고 정확한 답변</h2>
        <p class="cs-info-desc">
          궁금하신 사항을 빠르게 해결해드립니다<br>
          평균 응답시간 10분 이내
        </p>
      </section>

      <!-- 운영시간 및 전화상담 안내 -->
      <div class="cs-info-banners">
        <div class="cs-hours-banner">
          <div class="cs-hours-icon">⏰</div>
          <div class="cs-hours-content">
            <div class="cs-hours-title">고객센터 운영시간</div>
            <div class="cs-hours-time">평일 09:00 - 22:00 | 주말 10:00 - 20:00</div>
          </div>
        </div>

        <div class="cs-phone-banner">
          <div class="cs-phone-icon">📞</div>
          <div class="cs-phone-content">
            <div class="cs-phone-title">전화 상담</div>
            <div class="cs-phone-number">02-6212-0465</div>
          </div>
        </div>
      </div>

      <!-- 빠른 문의 카테고리 -->
      <section class="cs-quick-category-section">
        <h3 class="cs-section-title">무엇을 도와드릴까요?</h3>
        <div class="cs-category-grid">
          <div @click="handleCategoryClick('결제/환불')" class="cs-category-card">
            <div class="cs-category-icon">💳</div>
            <div class="cs-category-name">결제/환불</div>
            <div class="cs-category-desc">포인트 충전, 환불 관련</div>
          </div>
          <div @click="handleCategoryClick('계정 문의')" class="cs-category-card">
            <div class="cs-category-icon">👤</div>
            <div class="cs-category-name">계정 문의</div>
            <div class="cs-category-desc">로그인, 비밀번호 찾기</div>
          </div>
          <div @click="handleCategoryClick('상담 문의')" class="cs-category-card">
            <div class="cs-category-icon">💬</div>
            <div class="cs-category-name">상담 문의</div>
            <div class="cs-category-desc">상담 진행, 상담사 관련</div>
          </div>
          <div @click="handleCategoryClick('이벤트/혜택')" class="cs-category-card">
            <div class="cs-category-icon">🎁</div>
            <div class="cs-category-name">이벤트/혜택</div>
            <div class="cs-category-desc">프로모션, 쿠폰 사용</div>
          </div>
        </div>
      </section>

      <!-- 문의내역 섹션 - 로그인 상태에 따라 다르게 표시 -->
      <!-- 로딩 중일 때는 스켈레톤 표시 -->
      <section v-if="isAuthChecking" class="cs-inquiry-section">
        <div class="cs-inquiry-header">
          <h2 class="cs-inquiry-title">
            <span>📝</span>
            <span>내 문의내역</span>
          </h2>
        </div>
        <div class="cs-loading-skeleton">
          <div class="skeleton-item"></div>
          <div class="skeleton-item"></div>
        </div>
      </section>

      <!-- 로그인 상태 -->
      <section v-else-if="isAuthenticated" class="cs-inquiry-section">
        <div class="cs-inquiry-header">
          <h2 class="cs-inquiry-title">
            <span>📝</span>
            <span>내 문의내역</span>
          </h2>
          <div class="cs-inquiry-actions">
            <button class="cs-view-all" @click="goToInquiries">
              <span>전체보기</span>
              <span>›</span>
            </button>
            <button class="cs-inquiry-button" @click="goToWrite">
              <span>✏️</span>
              <span>문의하기</span>
            </button>
          </div>
        </div>
        <div class="cs-inquiry-list">
          <!-- 로딩 중 -->
          <div v-if="isLoadingInquiries" class="cs-loading-skeleton">
            <div class="skeleton-item"></div>
            <div class="skeleton-item"></div>
          </div>

          <!-- 문의 없음 -->
          <div v-else-if="!latestInquiries || latestInquiries.length === 0" class="cs-no-inquiries">
            <div class="cs-no-inquiries-icon">📝</div>
            <p class="cs-no-inquiries-text">문의 내역이 없습니다</p>
          </div>

          <!-- 문의 목록 (최근 2개) -->
          <NuxtLink
            v-else
            v-for="inquiry in latestInquiries"
            :key="inquiry.inquiry_id"
            :to="`/cs/inquiries/${inquiry.inquiry_id}`"
            class="cs-inquiry-item"
          >
            <div class="cs-inquiry-item-header">
              <span class="cs-inquiry-category">{{ getInquiryTypeLabel(inquiry.inquiry_type) }}</span>
              <span class="cs-inquiry-date">{{ formatDate(inquiry.created_at) }}</span>
            </div>
            <div class="cs-inquiry-content">
              {{ inquiry.content }}
            </div>
            <div class="cs-inquiry-status" :class="inquiry.has_reply ? 'completed' : 'waiting'">
              <span class="cs-status-icon">{{ inquiry.has_reply ? '✓' : '⏳' }}</span>
              <span>{{ inquiry.has_reply ? '답변완료' : '답변대기' }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <!-- 비로그인 상태 안내 -->
      <section v-else class="cs-inquiry-section">
        <div class="cs-login-required">
          <div class="cs-login-icon">🔒</div>
          <h3 class="cs-login-title">로그인이 필요합니다</h3>
          <p class="cs-login-desc">
            문의 내역을 확인하고 새로운 문의를 작성하려면<br>
            로그인해 주세요.
          </p>
          <NuxtLink to="/login" class="cs-login-button">
            로그인하기
          </NuxtLink>
        </div>
      </section>

      <!-- 자주 묻는 질문 -->
      <section class="cs-faq-section">
        <h3 class="cs-section-title">자주 묻는 질문 TOP 5</h3>
        <div class="cs-faq-list">
          <div
            v-for="(faq, index) in faqList"
            :key="index"
            class="cs-faq-item"
            :class="{ active: activeFaq === index }"
            @click="toggleFaq(index)"
          >
            <div class="cs-faq-question">
              <div class="cs-faq-text">
                <span class="cs-faq-q-icon">Q.</span>
                {{ faq.question }}
              </div>
              <span class="cs-faq-arrow">›</span>
            </div>
            <div class="cs-faq-answer">
              {{ faq.answer }}
            </div>
          </div>
        </div>
      </section>

      <!-- 공지사항 링크 -->
      <NuxtLink to="/notices" class="cs-notice-link">
        <div class="cs-notice-content">
          <span class="cs-notice-icon">📢</span>
          <span class="cs-notice-text">공지사항</span>
        </div>
        <div class="cs-notice-right">
          <span class="cs-notice-badge">NEW</span>
          <span class="cs-notice-arrow">›</span>
        </div>
      </NuxtLink>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useInquiryQueries } from '~/composables/api/useInquiryQueries'
import { getInquiryTypeLabel, formatDate } from '~/types/inquiry'

definePageMeta({
  layout: 'default'
})

// SEO 메타 데이터 설정
useSeoMeta({
  title: '고객센터 - 사주라인',
  description: '사주라인 고객센터입니다. 문의사항은 평일 09:00-22:00, 주말 10:00-20:00에 운영되며 평균 응답시간은 10분 이내입니다. 전화상담은 02-6212-0465로 연락 주세요.',
  keywords: '고객센터, 문의하기, 사주라인 고객지원, 상담문의, 결제문의, FAQ',
  ogTitle: '고객센터 - 사주라인',
  ogDescription: '빠르고 정확한 답변을 제공하는 사주라인 고객센터. 평균 응답시간 10분 이내',
  ogImage: 'https://sajuline.com/images/og-cs.jpg',
  ogUrl: 'https://sajuline.com/cs',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: '고객센터 - 사주라인',
  twitterDescription: '빠르고 정확한 답변을 제공하는 사주라인 고객센터',
  twitterImage: 'https://sajuline.com/images/og-cs.jpg',
  robots: 'index,follow'
})

useHead({
  link: [{ rel: 'canonical', href: 'https://sajuline.com/cs' }]
})

// 인증 상태 관리
const { isAuthenticated, isAuthChecking, restoreSession } = useAuth()

// 문의 API
const { useInquiryList } = useInquiryQueries()

// 문의 목록 조회 (최근 2개만)
const { data: inquiryData, isLoading: isLoadingInquiries } = useInquiryList(
  { page: 1, limit: 2 },
  { enabled: isAuthenticated }
)

// 최근 2개 문의
const latestInquiries = computed(() => inquiryData.value?.items || [])

// 페이지 로드 시 세션 복원 확인
onMounted(async () => {
  if (isAuthChecking.value) {
    await restoreSession()
  }
})

// FAQ 관련 상태
const activeFaq = ref(-1)

// FAQ 데이터
const faqList = ref([
  {
    question: '포인트는 어떻게 충전하나요?',
    answer: '마이페이지 > 포인트 충전 메뉴에서 원하시는 금액을 선택하여 충전하실 수 있습니다. 신용카드, 휴대폰 결제, 계좌이체, 카카오페이 등 다양한 결제 수단을 지원합니다.'
  },
  {
    question: '상담사님과 연결이 안 돼요',
    answer: '선택하신 상담사님이 다른 상담 중이실 수 있습니다. 상담사 프로필에서 \'예약하기\'를 선택하시면 상담 가능 시간에 알림을 받으실 수 있습니다.'
  },
  {
    question: '첫 상담 무료체험은 어떻게 받나요?',
    answer: '신규 회원님께는 첫 상담 10분 무료 쿠폰이 자동으로 지급됩니다. 상담사 선택 후 결제 단계에서 쿠폰을 적용하시면 됩니다.'
  },
  {
    question: '상담 내용은 비밀이 보장되나요?',
    answer: '네, 모든 상담 내용은 철저히 비밀이 보장됩니다. 상담 내용은 암호화되어 저장되며, 본인 외에는 누구도 확인할 수 없습니다.'
  },
  {
    question: '환불은 어떻게 받을 수 있나요?',
    answer: '사용하지 않은 포인트는 충전일로부터 7일 이내 100% 환불 가능합니다. 고객센터로 문의 주시면 빠르게 처리해드립니다.'
  }
])

// FAQ 토글
const toggleFaq = (index: number) => {
  if (activeFaq.value === index) {
    activeFaq.value = -1
  } else {
    activeFaq.value = index
  }
}

// 카테고리 클릭 핸들러
const handleCategoryClick = (category: string) => {
  if (!isAuthenticated.value) {
    navigateTo('/login')
    return
  }
  navigateTo(`/cs/write?category=${encodeURIComponent(category)}`)
}

// 네비게이션 함수
const goToInquiries = () => {
  if (!isAuthenticated.value) {
    navigateTo('/login')
    return
  }
  navigateTo('/cs/inquiries')
}

const goToWrite = () => {
  if (!isAuthenticated.value) {
    navigateTo('/login')
    return
  }
  navigateTo('/cs/write')
}
</script>

<style>
@import '~/assets/css/cs.css';

/* 로딩 스켈레톤 스타일 */
.cs-loading-skeleton {
  padding: 20px;
}

.skeleton-item {
  height: 100px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 12px;
  margin-bottom: 12px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 비로그인 상태 안내 스타일 */
.cs-login-required {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin: 20px;
}

.cs-login-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.cs-login-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
  color: white;
}

.cs-login-desc {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 24px;
}

.cs-login-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 14px 32px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.cs-login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}

/* 카테고리 카드 클릭 가능하게 */
.cs-category-card {
  cursor: pointer;
  transition: all 0.3s;
}
</style>
