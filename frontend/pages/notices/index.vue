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
                  v-if="notice.category !== 'general'"
                  :class="['notice-badge', notice.category]"
                >
                  {{ getBadgeText(notice.category) }}
                </span>
                <h3 class="notice-title">{{ notice.title }}</h3>
              </div>
              <span class="notice-date">{{ formatDate(notice.createdAt) }}</span>
            </div>
            <p class="notice-content">{{ notice.summary }}</p>
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
import { ref, computed, onMounted } from 'vue';
import type { INoticeListItem, NoticeCategory } from '~/types/notice';
import '~/assets/css/notice/list.css';

// 상태 관리
const notices = ref<INoticeListItem[]>([]);
const currentPage = ref(1);
const totalPages = ref(1);
const isLoading = ref(false);

// 임시 데이터 (API 구현 전까지 사용)
const mockNotices: INoticeListItem[] = [
  {
    id: 1,
    title: '시스템 점검 안내',
    summary: '더 나은 서비스 제공을 위해 시스템 점검을 진행할 예정입니다. 점검 시간 동안 서비스 이용이 제한됩니다.',
    category: 'new',
    viewCount: 1234,
    createdAt: '2024-03-15T10:00:00',
    isFixed: true,
  },
  {
    id: 2,
    title: '봄맞이 이벤트 안내',
    summary: '봄을 맞이하여 진행되는 특별 이벤트를 안내드립니다. 다양한 혜택과 함께 즐거운 시간 보내세요.',
    category: 'event',
    viewCount: 856,
    createdAt: '2024-03-10T14:30:00',
  },
  {
    id: 3,
    title: '앱 버전 업데이트 안내',
    summary: '더 나은 서비스 이용을 위한 앱 업데이트를 안내드립니다. 새로운 기능과 개선사항을 확인해보세요.',
    category: 'update',
    viewCount: 543,
    createdAt: '2024-03-05T09:00:00',
  },
  {
    id: 4,
    title: '개인정보처리방침 개정 안내',
    summary: '개인정보처리방침이 일부 개정되었습니다. 변경된 내용을 확인하시고 서비스를 이용해 주시기 바랍니다.',
    category: 'important',
    viewCount: 1523,
    createdAt: '2024-02-28T16:00:00',
  },
  {
    id: 5,
    title: '신규 상담사 입점 안내',
    summary: '새로운 전문 상담사분들이 입점하셨습니다. 다양한 분야의 전문가들과 상담을 진행해보세요.',
    category: 'general',
    viewCount: 432,
    createdAt: '2024-02-25T11:00:00',
  },
];

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
  return `${year}.${month}.${day}`;
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
    // API 구현 전까지 임시 데이터 사용
    await new Promise(resolve => setTimeout(resolve, 500)); // 로딩 시뮬레이션

    // 페이지네이션 시뮬레이션
    const pageSize = 10;
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize;

    notices.value = mockNotices.slice(start, end);
    totalPages.value = Math.ceil(mockNotices.length / pageSize);
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