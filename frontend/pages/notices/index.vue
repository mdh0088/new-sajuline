<template>
  <div class="notice-page">
    <!-- 헤더 -->
    <AppHeader title="공지사항" :show-back="true" />

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 페이지 제목 -->
      <div class="page-header">
        <h1 class="page-title">공지사항</h1>
        <p class="page-desc">서비스 관련 중요한 소식을 확인하세요</p>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="notice-loading">
        <div class="loading-spinner"></div>
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="!notices.length" class="notice-empty">
        <div class="notice-empty-icon">📢</div>
        <h3 class="notice-empty-title">공지사항이 없습니다</h3>
        <p class="notice-empty-desc">
          새로운 공지사항이 등록되면<br />
          이곳에서 확인하실 수 있습니다.
        </p>
      </div>

      <!-- 공지사항 리스트 -->
      <template v-else>
        <div class="notice-list">
          <NuxtLink
            v-for="notice in notices"
            :key="notice.id"
            :to="`/notices/${notice.id}`"
            class="notice-item"
          >
            <div class="notice-header">
              <div class="notice-title-wrapper">
                <span
                  v-if="notice.category === 'update'"
                  class="notice-badge update"
                >
                  UPDATE
                </span>
                <span
                  v-if="notice.category === 'event'"
                  class="notice-badge event"
                >
                  EVENT
                </span>
                <span
                  v-if="notice.category === 'important'"
                  class="notice-badge important"
                >
                  중요
                </span>
                <h3 class="notice-title">{{ notice.title }}</h3>
              </div>
              <span class="notice-date">{{ formatDate(notice.createdAt) }}</span>
            </div>
            <p class="notice-content">{{ cleanText(notice.summary) }}</p>
          </NuxtLink>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            class="page-btn prev"
            :class="{ disabled: currentPage === 1 }"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            이전
          </button>

          <template v-for="page in displayPages" :key="page">
            <button
              v-if="page !== '...'"
              class="page-btn"
              :class="{ active: page === currentPage }"
              @click="changePage(page as number)"
            >
              {{ page }}
            </button>
            <span v-else class="page-dots">...</span>
          </template>

          <button
            class="page-btn next"
            :class="{ disabled: currentPage === totalPages }"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            다음
          </button>
        </div>
      </template>
    </main>

    <!-- 하단 네비게이션 -->
    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { INoticeListItem, NoticeCategory } from '~/types/notice';
import { useNoticeApi } from '~/composables/api/useNotice';

// 상태 관리
const notices = ref<INoticeListItem[]>([]);
const currentPage = ref(1);
const totalPages = ref(1);
const isLoading = ref(false);
const { useNoticeList } = useNoticeApi();

// API 쿼리
const { data: listData, isFetching } = useNoticeList({
  // 목록은 전체 반환(API 설계), 여기서 그대로 사용
})

// 페이지네이션 표시 페이지 계산
const displayPages = computed(() => {
  const pages: (number | string)[] = [];
  const maxDisplay = 5;
  const halfDisplay = Math.floor(maxDisplay / 2);

  if (totalPages.value <= maxDisplay) {
    // 전체 페이지가 maxDisplay 이하면 모두 표시
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i);
    }
  } else {
    // 현재 페이지 주변 페이지 표시
    let start = Math.max(1, currentPage.value - halfDisplay);
    let end = Math.min(totalPages.value, currentPage.value + halfDisplay);

    // 시작 부분
    if (start > 1) {
      pages.push(1);
      if (start > 2) pages.push('...');
    }

    // 중간 부분
    for (let i = start; i <= end; i++) {
      if (i !== 1 && i !== totalPages.value) {
        pages.push(i);
      }
    }

    // 끝 부분
    if (end < totalPages.value) {
      if (end < totalPages.value - 1) pages.push('...');
      pages.push(totalPages.value);
    }
  }

  return pages;
});

// 배지 텍스트 가져오기
const getBadgeText = (category: NoticeCategory): string => {
  const badgeTexts: Record<NoticeCategory, string> = {
    new: 'NEW',
    event: '이벤트',
    update: '업데이트',
    important: '중요',
    general: '일반',
  };
  return badgeTexts[category] || '';
};

// 날짜 포맷팅
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// HTML 태그 및 특수문자 정리
const cleanText = (text: string): string => {
  if (!text) return '';

  return text
    // HTML 태그 제거
    .replace(/<[^>]*>/g, '')
    // HTML 엔티티 디코딩
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    // 연속된 공백을 하나로 축약
    .replace(/\s+/g, ' ')
    // 앞뒤 공백 제거
    .trim();
};

// 페이지 변경
const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) {
    return;
  }
  currentPage.value = page;
  loadNotices();
};

// 공지사항 로드
const loadNotices = async () => {
  isLoading.value = true;

  try {
    const items = listData.value ?? []
    const pageSize = 10
    const start = (currentPage.value - 1) * pageSize
    const end = start + pageSize
    notices.value = items.slice(start, end)
    totalPages.value = Math.max(1, Math.ceil(items.length / pageSize))
  } catch (error) {
    console.error('공지사항 로드 실패:', error);
    notices.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 컴포넌트 마운트 시 초기 로드
onMounted(() => {
  loadNotices();
});

// 데이터 변경 시 자동 재계산
watch(
  () => listData.value,
  () => {
    loadNotices()
  }
)

// SEO 설정
useHead({
  title: '공지사항 - 사주라인',
  meta: [
    {
      name: 'description',
      content: '사주라인의 공지사항과 새로운 소식을 확인하세요.',
    },
  ],
});
</script>

<style scoped>
.notice-page {
  min-height: 100vh;
  background-color: #0a0a0f;
  color: #ffffff;
}

/* 메인 콘텐츠 */
.main-content {
    margin-top: 60px;
    padding: 20px;
    padding-bottom: 80px;
    max-width: 100%;
}

/* 공지사항 리스트 */
.notice-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.notice-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    color: inherit;
}

.notice-item:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.05);
}

.notice-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.notice-title {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    margin-right: 12px;
}

.notice-date {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
}

.notice-content {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}

.notice-badge {
    display: inline-block;
    padding: 4px 8px;
    background: rgba(147, 51, 234, 0.2);
    color: #B794F6;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
}

/* 공지사항 상세 */
.notice-detail {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}

.notice-detail-header {
    margin-bottom: 20px;
}

.notice-detail-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.notice-detail-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: rgba(255, 255, 255, 0.5);
    font-size: 14px;
}

.notice-detail-content {
    font-size: 15px;
    line-height: 1.8;
    color: rgba(255, 255, 255, 0.8);
}

.notice-detail-content p {
    margin-bottom: 16px;
}

.notice-detail-content strong {
    color: #B794F6;
    font-weight: 600;
}

.notice-detail-content ul {
    list-style: none;
    margin: 16px 0;
    padding-left: 20px;
}

.notice-detail-content li {
    position: relative;
    margin-bottom: 8px;
    padding-left: 16px;
}

.notice-detail-content li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: #B794F6;
}

/* 페이지네이션 */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin-top: 24px;
}

.page-btn {
    min-width: 36px;
    height: 36px;
    padding: 0 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #fff;
    transition: all 0.3s ease;
    cursor: pointer;
}

.page-btn:hover {
    background: rgba(147, 51, 234, 0.1);
    transform: translateY(-1px);
}

.page-btn.active {
    background: rgba(147, 51, 234, 0.2);
    color: #B794F6;
    border-color: rgba(147, 51, 234, 0.3);
}

.page-btn.disabled {
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.3);
    cursor: not-allowed;
}

.page-dots {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
  user-select: none;
}

/* 로딩 및 빈 상태 스타일 */
.notice-loading, .notice-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    text-align: center;
}

.loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid #B794F6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.notice-empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.notice-empty-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #ffffff;
}

.notice-empty-desc {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    line-height: 1.5;
}

.notice-title-wrapper {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
    gap: 8px;
}

/* 페이지 헤더 스타일 */
.page-header {
    margin-bottom: 24px;
}

.page-title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

.page-desc {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    line-height: 1.4;
}
</style>