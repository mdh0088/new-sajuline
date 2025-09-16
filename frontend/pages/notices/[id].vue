<template>
  <div class="notice-detail-page">
    <!-- 헤더 -->
    <AppHeader title="공지사항" :show-back="true" />

    <!-- 메인 콘텐츠 -->
    <main class="notice-detail-container">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="notice-loading">
        <div class="loading-spinner"></div>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="notice-error">
        <div class="notice-error-icon">⚠️</div>
        <h3 class="notice-error-title">공지사항을 불러올 수 없습니다</h3>
        <p class="notice-error-desc">
          요청하신 공지사항을 찾을 수 없거나<br />
          일시적인 오류가 발생했습니다.
        </p>
        <NuxtLink to="/notices" class="error-button">
          목록으로 돌아가기
        </NuxtLink>
      </div>

      <!-- 공지사항 상세 -->
      <template v-else-if="notice">
        <div class="notice-detail">
          <!-- 헤더 -->
          <div class="notice-detail-header">
            <div class="notice-detail-title-wrapper">
              <span
                v-if="notice.category !== 'general'"
                :class="['notice-badge', notice.category]"
              >
                {{ getBadgeText(notice.category) }}
              </span>
              <h2 class="notice-detail-title">{{ notice.title }}</h2>
            </div>
            <div class="notice-detail-meta">
              <div class="notice-meta-item">
                <span class="notice-meta-label">작성일</span>
                <span>{{ formatDate(notice.createdAt) }}</span>
              </div>
              <div class="notice-meta-item">
                <span class="notice-meta-label">조회수</span>
                <span>{{ notice.viewCount.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <!-- 내용 -->
          <div class="notice-detail-content" v-html="formatContent(notice.content)"></div>

          <!-- 이전/다음 네비게이션 -->
          <div class="notice-navigation">
            <NuxtLink
              v-if="notice.before_notice_id"
              :to="`/notices/${notice.before_notice_id}`"
              class="nav-button prev"
            >
              <span class="nav-button-label">이전글</span>
            </NuxtLink>
            <div v-else class="nav-button disabled prev">
              <span class="nav-button-label">이전글</span>
            </div>

            <NuxtLink
              v-if="notice.after_notice_id"
              :to="`/notices/${notice.after_notice_id}`"
              class="nav-button next"
            >
              <span class="nav-button-label">다음글</span>
            </NuxtLink>
            <div v-else class="nav-button disabled next">
              <span class="nav-button-label">다음글</span>
            </div>
          </div>
        </div>

        <!-- 액션 버튼 -->
        <div class="notice-actions">
          <NuxtLink to="/notices" class="action-button secondary">
            목록으로
          </NuxtLink>
        </div>
      </template>
    </main>

    <!-- 하단 네비게이션 -->
    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import type { INoticeDetail, NoticeCategory } from '~/types/notice';
import { useNoticeApi } from '~/composables/api/useNotice'
import '~/assets/css/notice/detail.css';

const route = useRoute();

// 상태 관리
const notice = ref<INoticeDetail | null>(null);
const isLoading = ref(false);
const error = ref(false);
const { useNoticeDetail, useIncreaseView } = useNoticeApi()
const { mutateAsync: increaseView } = useIncreaseView()

// 임시 목데이터 제거: 실제 API 사용

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

// 내용 포맷팅 (줄바꿈, 강조 등 처리)
const formatContent = (content: string): string => {
  // 줄바꿈을 <br>로 변환
  let formatted = content.replace(/\n/g, '<br>');

  // <strong> 태그는 유지
  // <span class="highlight"> 태그도 유지
  // • 문자는 그대로 유지

  return formatted;
};

// 공지사항 로드
const loadNotice = async (id: string) => {
  isLoading.value = true;
  error.value = false;

  try {
    const noticeId = parseInt(id)
    const { data, refetch } = useNoticeDetail(noticeId)
    const result = data?.value ?? (await refetch()).data
    if (result) {
      notice.value = result as INoticeDetail
      await increaseView(noticeId)
    } else {
      error.value = true
    }
  } catch (err) {
    console.error('공지사항 로드 실패:', err);
    error.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 라우트 변경 감지
watch(
  () => route.params.id,
  (newId) => {
    if (newId && typeof newId === 'string') {
      loadNotice(newId);
    }
  }
);

// 컴포넌트 마운트 시 초기 로드
onMounted(() => {
  const id = route.params.id;
  if (id && typeof id === 'string') {
    loadNotice(id);
  }
});

// SEO 설정
useHead({
  title: () => notice.value ? `${notice.value.title} - 공지사항 - 사주라인` : '공지사항 - 사주라인',
  meta: [
    {
      name: 'description',
      content: () => notice.value ? notice.value.content.substring(0, 100) : '사주라인 공지사항',
    },
  ],
});
</script>

<style scoped>
.notice-detail-page {
  min-height: 100vh;
  background-color: #0a0a0f;
  color: #ffffff;
}

/* 내용 영역의 HTML 스타일 */
.notice-detail-content :deep(strong) {
  display: block;
  color: #B794F6;
  font-weight: 600;
  margin: 24px 0 12px;
  font-size: 16px;
}

.notice-detail-content :deep(.highlight) {
  background: rgba(147, 51, 234, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: #B794F6;
  font-weight: 500;
}

.notice-detail-content :deep(br) {
  display: block;
  content: "";
  margin-top: 0.5em;
}
</style>