<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 검색 섹션 -->
        <div class="inquiry-search-section">
          <div class="inquiry-search-form">
            <input
              v-model="searchQuery"
              type="text"
              class="inquiry-search-input"
              placeholder="제목 또는 내용으로 검색"
              @keyup.enter="handleSearch"
            >
            <button class="inquiry-search-button" @click="handleSearch">
              🔍
            </button>
          </div>

          <!-- 필터 버튼들 -->
          <div class="inquiry-filters">
            <button
              class="inquiry-filter-btn"
              :class="{ active: filter === 'all' }"
              @click="filter = 'all'"
            >
              전체
            </button>
            <button
              class="inquiry-filter-btn"
              :class="{ active: filter === 'waiting' }"
              @click="filter = 'waiting'"
            >
              답변대기
            </button>
            <button
              class="inquiry-filter-btn"
              :class="{ active: filter === 'completed' }"
              @click="filter = 'completed'"
            >
              답변완료
            </button>
          </div>
        </div>

        <!-- 문의 목록 -->
        <div class="inquiry-list-container">
          <!-- 로딩 중 -->
          <div v-if="isLoading" class="inquiry-loading-skeleton">
            <div class="skeleton-item"></div>
            <div class="skeleton-item"></div>
            <div class="skeleton-item"></div>
          </div>

          <!-- 문의 없음 -->
          <div v-else-if="!inquiries || inquiries.length === 0" class="inquiry-empty-state">
            <div class="inquiry-empty-icon">📝</div>
            <p class="inquiry-empty-text">
              {{ currentSearch ? '검색 결과가 없습니다' : '문의 내역이 없습니다' }}
            </p>
            <NuxtLink v-if="!currentSearch" to="/cs/write" class="inquiry-empty-button">
              첫 문의하기
            </NuxtLink>
          </div>

          <!-- 문의 목록 -->
          <div v-else class="inquiry-list-items">
            <div
              v-for="inquiry in inquiries"
              :key="inquiry.inquiry_id"
              class="inquiry-list-item"
              @click="openInquiryModal(inquiry)"
            >
              <div class="inquiry-list-item-header">
                <div class="inquiry-list-category">{{ getInquiryTypeLabel(inquiry.inquiry_type) }}</div>
                <div class="inquiry-list-date">{{ formatDate(inquiry.created_at) }}</div>
              </div>
              <div class="inquiry-list-title-text">{{ inquiry.title || '제목 없음' }}</div>
              <div class="inquiry-list-content">
                {{ inquiry.content }}
              </div>
              <div class="inquiry-list-footer">
                <div class="inquiry-list-status" :class="inquiry.has_reply ? 'completed' : 'waiting'">
                  <span class="inquiry-list-status-icon">{{ inquiry.has_reply ? '✓' : '⏳' }}</span>
                  <span>{{ inquiry.has_reply ? '답변완료' : '답변대기' }}</span>
                </div>
                <div class="inquiry-list-arrow">›</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="inquiries && inquiries.length > 0" class="inquiry-pagination">
          <button
            class="inquiry-page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            ‹
          </button>
          <button
            v-for="page in Math.min(totalPages, 5)"
            :key="page"
            class="inquiry-page-btn"
            :class="{ active: currentPage === page }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button
            class="inquiry-page-btn"
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            ›
          </button>
        </div>
      </section>
    </main>

    <!-- 플로팅 문의하기 버튼 -->
    <NuxtLink to="/cs/write" class="inquiry-floating-write-btn">
      <span>✏️</span>
      <span>문의하기</span>
    </NuxtLink>

    <!-- 문의 상세 모달 -->
    <Teleport to="body">
      <div v-if="isModalOpen" class="inquiry-modal-overlay" @click="closeInquiryModal">
        <div class="inquiry-modal-container" @click.stop>
          <!-- 모달 헤더 -->
          <div class="inquiry-modal-header">
            <h2 class="inquiry-modal-title">문의 상세</h2>
            <button class="inquiry-modal-close" @click="closeInquiryModal">✕</button>
          </div>

          <!-- 모달 콘텐츠 -->
          <div class="inquiry-modal-content">
            <div v-if="selectedInquiry">
              <!-- 문의 정보 -->
              <div class="inquiry-detail-info">
                <div class="inquiry-detail-category">{{ getInquiryTypeLabel(selectedInquiry.inquiry_type) }}</div>
                <div class="inquiry-detail-status" :class="selectedInquiry.has_reply ? 'completed' : 'waiting'">
                  <span class="inquiry-detail-status-icon">{{ selectedInquiry.has_reply ? '✓' : '⏳' }}</span>
                  <span>{{ selectedInquiry.has_reply ? '답변완료' : '답변대기' }}</span>
                </div>
              </div>

              <!-- 문의 제목 -->
              <h3 class="inquiry-detail-subject">
                {{ selectedInquiry.title || '제목 없음' }}
              </h3>

              <!-- 문의 메타 정보 -->
              <div class="inquiry-detail-meta">
                <span>작성일: {{ formatDate(selectedInquiry.created_at) }}</span>
              </div>

              <!-- 문의 내용 -->
              <div class="inquiry-detail-content">
                <p style="white-space: pre-wrap;">{{ selectedInquiry.content }}</p>
              </div>

              <!-- 답변 섹션 -->
              <div v-if="selectedInquiry.reply_content" class="inquiry-reply-container">
                <div class="inquiry-reply-header">
                  <div class="inquiry-reply-icon">💬</div>
                  <div class="inquiry-reply-title">고객센터 답변</div>
                </div>
                <div v-if="selectedInquiry.answered_at" class="inquiry-reply-meta">
                  <span>답변일: {{ formatDate(selectedInquiry.answered_at) }}</span>
                </div>
                <div class="inquiry-reply-content">
                  <p style="white-space: pre-wrap;">{{ selectedInquiry.reply_content }}</p>
                </div>
              </div>

              <!-- 하단 버튼 -->
              <div class="inquiry-detail-actions">
                <button class="inquiry-detail-action-btn secondary" @click="closeInquiryModal">
                  닫기
                </button>
                <NuxtLink to="/cs/write" class="inquiry-detail-action-btn primary">
                  새 문의하기
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInquiryQueries } from '~/composables/api/useInquiryQueries'
import { getInquiryTypeLabel, formatDate, type InquiryItem } from '~/types/inquiry'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// 검색 및 필터 상태
const searchQuery = ref('')
const currentSearch = ref('')
const filter = ref<'all' | 'waiting' | 'completed'>('all')
const currentPage = ref(1)
const limit = 10

// 문의 API
const { useInquiryList } = useInquiryQueries()

// 문의 목록 조회
const params = computed(() => ({
  page: currentPage.value,
  limit,
  search: currentSearch.value || undefined
}))

const { data: inquiryData, isLoading } = useInquiryList(params)

// 문의 목록 및 페이징 정보
const inquiries = computed(() => {
  const items = inquiryData.value?.items || []
  if (filter.value === 'all') return items
  return items.filter(item =>
    filter.value === 'completed' ? item.has_reply : !item.has_reply
  )
})
const totalCount = computed(() => inquiryData.value?.total || 0)
const totalPages = computed(() => Math.ceil(totalCount.value / limit) || 1)

// 모달 상태
const isModalOpen = ref(false)
const selectedInquiry = ref<InquiryItem | null>(null)

// 검색 핸들러
const handleSearch = () => {
  currentSearch.value = searchQuery.value.trim()
  currentPage.value = 1
}

// 페이지 이동
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 모달 열기
const openInquiryModal = (inquiry: InquiryItem) => {
  if (!inquiry) return
  selectedInquiry.value = inquiry
  isModalOpen.value = true
  document.body.style.overflow = 'hidden'
}

// 모달 닫기
const closeInquiryModal = () => {
  isModalOpen.value = false
  selectedInquiry.value = null
  document.body.style.overflow = 'auto'
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';

/* 모달 오버레이 */
.inquiry-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

/* 모달 컨테이너 */
.inquiry-modal-container {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 모달 헤더 */
.inquiry-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  background: #0f172a;
  z-index: 10;
}

.inquiry-modal-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.inquiry-modal-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s;
}

.inquiry-modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* 모달 콘텐츠 */
.inquiry-modal-content {
  padding: 24px;
}

/* 문의 상세 페이지 전용 스타일 */
.inquiry-detail-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.inquiry-detail-category {
  display: inline-flex;
  padding: 6px 12px;
  background: rgba(147, 51, 234, 0.2);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #a78bfa;
}

.inquiry-detail-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.inquiry-detail-status.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #4ade80;
}

.inquiry-detail-status.waiting {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
}

.inquiry-detail-status-icon {
  font-size: 14px;
}

.inquiry-detail-subject {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.4;
  color: white;
}

.inquiry-detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.inquiry-detail-divider {
  color: rgba(255, 255, 255, 0.2);
}

.inquiry-detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20px;
}

.inquiry-detail-content p {
  margin: 0;
  white-space: pre-wrap;
}

.inquiry-reply-container {
  background: rgba(147, 51, 234, 0.05);
  border: 1px solid rgba(147, 51, 234, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.inquiry-reply-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.inquiry-reply-icon {
  font-size: 20px;
}

.inquiry-reply-title {
  font-size: 16px;
  font-weight: 700;
  color: #a78bfa;
}

.inquiry-reply-meta {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.inquiry-reply-content {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.inquiry-reply-content p {
  margin: 0;
  white-space: pre-wrap;
}

.inquiry-detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.inquiry-detail-action-btn {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inquiry-detail-action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.inquiry-detail-action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.inquiry-detail-action-btn.primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.inquiry-detail-action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}

/* 리스트 아이템 클릭 가능하게 */
.inquiry-list-item {
  cursor: pointer;
}

/* 로딩 스켈레톤 */
.inquiry-loading-skeleton {
  padding: 20px 0;
}

.skeleton-item {
  height: 120px;
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

/* 빈 상태 */
.inquiry-empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.inquiry-empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.inquiry-empty-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px;
}

.inquiry-empty-button {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.inquiry-empty-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}
</style>
