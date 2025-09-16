<template>
  <div class="notice-page">
    <!-- 헤더 -->
    <AppHeader title="공지사항" :show-back="true" />

    <!-- 메인 콘텐츠 -->
    <main class="notice-list-container">
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
import '~/assets/css/notice/list.css';

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
</style>