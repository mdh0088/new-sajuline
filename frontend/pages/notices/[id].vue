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
              v-if="notice.prevNotice"
              :to="`/notices/${notice.prevNotice.id}`"
              class="nav-button prev"
            >
              <span class="nav-button-label">이전글</span>
              <span class="nav-button-title">{{ notice.prevNotice.title }}</span>
            </NuxtLink>
            <div v-else class="nav-button disabled prev">
              <span class="nav-button-label">이전글</span>
              <span class="nav-button-title">첫 번째 글입니다</span>
            </div>

            <NuxtLink
              v-if="notice.nextNotice"
              :to="`/notices/${notice.nextNotice.id}`"
              class="nav-button next"
            >
              <span class="nav-button-label">다음글</span>
              <span class="nav-button-title">{{ notice.nextNotice.title }}</span>
            </NuxtLink>
            <div v-else class="nav-button disabled next">
              <span class="nav-button-label">다음글</span>
              <span class="nav-button-title">마지막 글입니다</span>
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
import '~/assets/css/notice/detail.css';

const route = useRoute();

// 상태 관리
const notice = ref<INoticeDetail | null>(null);
const isLoading = ref(false);
const error = ref(false);

// 임시 데이터 (API 구현 전까지 사용)
const mockNotices: INoticeDetail[] = [
  {
    id: 1,
    title: '시스템 점검 안내',
    content: `안녕하세요, 사주라인입니다.

더 나은 서비스 제공을 위해 시스템 점검을 진행할 예정입니다.

<strong>점검 일시</strong>
2024년 3월 20일 (수) 02:00 ~ 06:00
점검 시간 동안 서비스 이용이 제한됩니다.

<strong>점검 내용</strong>
• 서버 시스템 업그레이드
• 데이터베이스 최적화
• 보안 시스템 강화
• 신규 기능 추가 준비

<strong>참고 사항</strong>
• 점검 시간은 작업 진행 상황에 따라 변경될 수 있습니다.
• 점검 완료 후 일부 캐시 데이터가 초기화될 수 있습니다.
• 진행 중이던 상담은 점검 이후 이어서 진행 가능합니다.

이용에 참고 부탁드리며, 불편을 드려 죄송합니다.
더 나은 서비스로 보답하겠습니다.

감사합니다.`,
    category: 'new',
    viewCount: 1234,
    createdAt: '2024-03-15T10:00:00',
    prevNotice: null,
    nextNotice: {
      id: 2,
      title: '봄맞이 이벤트 안내',
    },
  },
  {
    id: 2,
    title: '봄맞이 이벤트 안내',
    content: `안녕하세요, 사주라인입니다.

따뜻한 봄을 맞이하여 특별한 이벤트를 준비했습니다!

<strong>이벤트 기간</strong>
2024년 3월 1일 ~ 3월 31일

<strong>이벤트 내용</strong>
• 신규 회원 가입 시 <span class="highlight">3,000 포인트</span> 즉시 지급
• 첫 상담 이용 시 <span class="highlight">20% 할인</span> 쿠폰 제공
• 친구 추천 시 추천인과 신규 회원 모두 <span class="highlight">5,000 포인트</span> 지급
• 매일 출석 체크 시 최대 <span class="highlight">1,000 포인트</span> 적립

<strong>참여 방법</strong>
1. 사주라인 앱에 로그인
2. 이벤트 페이지에서 참여하기 버튼 클릭
3. 각 이벤트별 미션 완료
4. 자동으로 포인트 지급

<strong>주의 사항</strong>
• 이벤트는 조기 종료될 수 있습니다.
• 부정한 방법으로 이벤트 참여 시 포인트가 회수될 수 있습니다.
• 자세한 내용은 이벤트 페이지를 참고해 주세요.

많은 참여 부탁드립니다!`,
    category: 'event',
    viewCount: 856,
    createdAt: '2024-03-10T14:30:00',
    prevNotice: {
      id: 1,
      title: '시스템 점검 안내',
    },
    nextNotice: {
      id: 3,
      title: '앱 버전 업데이트 안내',
    },
  },
  {
    id: 3,
    title: '앱 버전 업데이트 안내',
    content: `안녕하세요, 사주라인입니다.

더 나은 서비스 이용을 위한 앱 업데이트를 안내드립니다.

<strong>업데이트 버전</strong>
v2.5.0 (2024.03.05 배포)

<strong>주요 업데이트 내용</strong>
• AI 운세 분석 기능 개선
• 채팅 상담 UI/UX 개선
• 상담사 프로필 상세 정보 추가
• 포인트 충전 프로세스 간소화
• 알림 설정 기능 추가
• 버그 수정 및 성능 개선

<strong>업데이트 방법</strong>
• iOS: App Store에서 '사주라인' 검색 후 업데이트
• Android: Google Play Store에서 '사주라인' 검색 후 업데이트

<strong>참고 사항</strong>
• 원활한 서비스 이용을 위해 최신 버전으로 업데이트해 주세요.
• 업데이트 후 문제가 발생하면 고객센터로 문의해 주세요.

감사합니다.`,
    category: 'update',
    viewCount: 543,
    createdAt: '2024-03-05T09:00:00',
    prevNotice: {
      id: 2,
      title: '봄맞이 이벤트 안내',
    },
    nextNotice: {
      id: 4,
      title: '개인정보처리방침 개정 안내',
    },
  },
  {
    id: 4,
    title: '개인정보처리방침 개정 안내',
    content: `안녕하세요, 사주라인입니다.

개인정보처리방침이 일부 개정되었음을 안내드립니다.

<strong>개정 일자</strong>
2024년 2월 28일

<strong>주요 개정 내용</strong>
• 수집하는 개인정보 항목 명확화
• 개인정보 보유 및 이용 기간 상세화
• 제3자 제공 관련 내용 업데이트
• 이용자 권리 및 행사 방법 안내 강화

<strong>개정 사유</strong>
• 개인정보보호법 개정사항 반영
• 서비스 개선을 위한 수집 항목 추가
• 이용자 권익 보호 강화

<strong>확인 방법</strong>
설정 > 약관 및 정책 > 개인정보처리방침

변경된 개인정보처리방침은 공지일로부터 7일 후인 2024년 3월 7일부터 적용됩니다.

개정된 내용에 동의하지 않으실 경우, 고객센터를 통해 회원 탈퇴를 요청하실 수 있습니다.

감사합니다.`,
    category: 'important',
    viewCount: 1523,
    createdAt: '2024-02-28T16:00:00',
    prevNotice: {
      id: 3,
      title: '앱 버전 업데이트 안내',
    },
    nextNotice: {
      id: 5,
      title: '신규 상담사 입점 안내',
    },
  },
  {
    id: 5,
    title: '신규 상담사 입점 안내',
    content: `안녕하세요, 사주라인입니다.

이번 달 새롭게 입점하신 전문 상담사분들을 소개합니다.

<strong>신규 입점 상담사</strong>
• 김미래 상담사 - 타로, 신점 전문
• 박운세 상담사 - 사주, 궁합 전문
• 이신비 상담사 - 꿈해몽, 작명 전문
• 정마음 상담사 - 심리상담, 연애 전문
• 최행운 상담사 - 재물운, 사업운 전문

<strong>특별 혜택</strong>
• 신규 상담사 첫 상담 <span class="highlight">30% 할인</span>
• 상담 후기 작성 시 <span class="highlight">1,000 포인트</span> 적립
• 3월 한정 예약 상담 <span class="highlight">10% 추가 할인</span>

<strong>상담사 확인 방법</strong>
1. 홈 화면에서 '상담사 찾기' 메뉴 선택
2. 'NEW' 배지가 표시된 상담사 확인
3. 프로필을 통해 전문 분야 확인
4. 원하는 시간에 상담 예약

다양한 분야의 전문가들과 함께 더욱 풍성해진 사주라인을 즐겨주세요!

감사합니다.`,
    category: 'general',
    viewCount: 432,
    createdAt: '2024-02-25T11:00:00',
    prevNotice: {
      id: 4,
      title: '개인정보처리방침 개정 안내',
    },
    nextNotice: null,
  },
];

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
    // API 구현 전까지 임시 데이터 사용
    await new Promise(resolve => setTimeout(resolve, 500)); // 로딩 시뮬레이션

    const noticeId = parseInt(id);
    const foundNotice = mockNotices.find(n => n.id === noticeId);

    if (foundNotice) {
      notice.value = foundNotice;
      // 조회수 증가 시뮬레이션 (실제로는 API에서 처리)
      notice.value.viewCount++;
    } else {
      error.value = true;
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