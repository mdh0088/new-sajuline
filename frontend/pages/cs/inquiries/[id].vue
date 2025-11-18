<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 로딩 중 -->
        <div v-if="isLoading" class="inquiry-loading-skeleton">
          <div class="skeleton-box"></div>
          <div class="skeleton-box"></div>
          <div class="skeleton-box"></div>
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="isError" class="inquiry-error-state">
          <div class="inquiry-error-icon">⚠️</div>
          <p class="inquiry-error-text">문의를 불러올 수 없습니다</p>
          <button @click="goBack" class="inquiry-error-button">
            목록으로 돌아가기
          </button>
        </div>

        <!-- 문의 상세 -->
        <template v-else-if="inquiry">
          <!-- 문의 상세 카드 -->
          <div class="inquiry-detail-container">
            <!-- 문의 정보 -->
            <div class="inquiry-detail-info">
              <div class="inquiry-detail-category">{{ getInquiryTypeLabel(inquiry.inquiry_type) }}</div>
              <div class="inquiry-detail-status" :class="inquiry.has_reply ? 'completed' : 'waiting'">
                <span class="inquiry-detail-status-icon">{{ inquiry.has_reply ? '✓' : '⏳' }}</span>
                <span>{{ inquiry.has_reply ? '답변완료' : '답변대기' }}</span>
              </div>
            </div>

            <!-- 문의 제목 -->
            <h2 class="inquiry-detail-subject">
              {{ inquiry.title || '제목 없음' }}
            </h2>

            <!-- 문의 메타 정보 -->
            <div class="inquiry-detail-meta">
              <span>작성일: {{ formatDate(inquiry.created_at) }}</span>
            </div>

            <!-- 문의 내용 -->
            <div class="inquiry-detail-content">
              <p style="white-space: pre-wrap;">{{ inquiry.content }}</p>
            </div>
          </div>

          <!-- 답변 섹션 -->
          <div v-if="inquiry.reply_content" class="inquiry-reply-container">
            <div class="inquiry-reply-header">
              <div class="inquiry-reply-icon">💬</div>
              <div class="inquiry-reply-title">고객센터 답변</div>
            </div>
            <div v-if="inquiry.answered_at" class="inquiry-reply-meta">
              <span>답변일: {{ formatDate(inquiry.answered_at) }}</span>
            </div>
            <div class="inquiry-reply-content">
              <p style="white-space: pre-wrap;">{{ inquiry.reply_content }}</p>
            </div>
          </div>

          <!-- 하단 버튼 -->
          <div class="inquiry-detail-actions">
            <button @click="goBack" class="inquiry-detail-action-btn secondary">
              목록으로
            </button>
            <NuxtLink to="/cs/write" class="inquiry-detail-action-btn primary">
              새 문의하기
            </NuxtLink>
          </div>
        </template>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInquiryQueries } from '~/composables/api/useInquiryQueries'
import { getInquiryTypeLabel, formatDate } from '~/types/inquiry'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// SEO 메타 데이터 설정
useHead({
  title: '문의 상세 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const router = useRouter()
const route = useRoute()

// URL에서 ID 가져오기
const inquiryId = computed(() => Number(route.params.id))

// 문의 API
const { useInquiryDetail } = useInquiryQueries()

// 문의 상세 조회
const { data: inquiry, isLoading, isError } = useInquiryDetail(inquiryId)

// 목록으로 돌아가기
const goBack = () => {
  router.push('/cs/inquiries')
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';

/* 문의 상세 페이지 전용 스타일 */
.inquiry-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.inquiry-detail-title {
  font-size: 24px;
  font-weight: 700;
}

.inquiry-detail-container {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
}

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
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.4;
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
}

.inquiry-detail-content p {
  margin: 0;
  white-space: pre-wrap;
}

.inquiry-reply-container {
  background: rgba(147, 51, 234, 0.05);
  border: 1px solid rgba(147, 51, 234, 0.2);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
}

.inquiry-reply-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.inquiry-reply-icon {
  font-size: 24px;
}

.inquiry-reply-title {
  font-size: 18px;
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

/* 로딩 스켈레톤 */
.inquiry-loading-skeleton {
  padding: 20px 0;
}

.skeleton-box {
  height: 200px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 16px;
  margin-bottom: 20px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 에러 상태 */
.inquiry-error-state {
  text-align: center;
  padding: 80px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.inquiry-error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.inquiry-error-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 24px;
}

.inquiry-error-button {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.inquiry-error-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}
</style>
