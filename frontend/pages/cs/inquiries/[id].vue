<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 문의 상세 카드 -->
        <div class="inquiry-detail-container">
          <!-- 문의 정보 -->
          <div class="inquiry-detail-info">
            <div class="inquiry-detail-category">결제문의</div>
            <div class="inquiry-detail-status completed">
              <span class="inquiry-detail-status-icon">✓</span>
              <span>답변완료</span>
            </div>
          </div>

          <!-- 문의 제목 -->
          <h2 class="inquiry-detail-subject">
            포인트 충전이 되지 않습니다
          </h2>

          <!-- 문의 메타 정보 -->
          <div class="inquiry-detail-meta">
            <span>작성일: 2024.03.15 14:32</span>
            <span class="inquiry-detail-divider">|</span>
            <span>조회수: 1</span>
          </div>

          <!-- 문의 내용 -->
          <div class="inquiry-detail-content">
            <p>
              포인트 충전이 되지 않아 문의드립니다.<br>
              결제는 완료되었는데 포인트가 반영되지 않았습니다.<br><br>

              결제 정보:<br>
              - 결제 금액: 50,000원<br>
              - 결제 시간: 2024.03.15 14:20<br>
              - 결제 수단: 신용카드<br><br>

              빠른 처리 부탁드립니다.
            </p>
          </div>
        </div>

        <!-- 답변 섹션 -->
        <div class="inquiry-reply-container">
          <div class="inquiry-reply-header">
            <div class="inquiry-reply-icon">💬</div>
            <div class="inquiry-reply-title">고객센터 답변</div>
          </div>
          <div class="inquiry-reply-meta">
            <span>답변일: 2024.03.15 15:10</span>
          </div>
          <div class="inquiry-reply-content">
            <p>
              안녕하세요, 사주라인 고객센터입니다.<br><br>

              문의하신 포인트 충전 건에 대해 확인해드렸습니다.<br>
              결제는 정상적으로 완료되었으나, 시스템 지연으로 인해 포인트 반영이 늦어진 것으로 확인되었습니다.<br><br>

              현재 50,000P가 정상적으로 충전되었음을 확인하였습니다.<br>
              불편을 드려 죄송합니다.<br><br>

              추가 문의사항이 있으시면 언제든 연락 주세요.<br>
              감사합니다.
            </p>
          </div>
        </div>

        <!-- 하단 버튼 -->
        <div class="inquiry-detail-actions">
          <NuxtLink to="/cs/inquiries" class="inquiry-detail-action-btn secondary">
            목록으로
          </NuxtLink>
          <NuxtLink to="/cs/write" class="inquiry-detail-action-btn primary">
            새 문의하기
          </NuxtLink>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
  // TODO: 실제 구현 시 middleware: 'auth' 추가 (로그인 필수)
})

// URL에서 ID 가져오기
const route = useRoute()
const inquiryId = route.params.id

// TODO: 실제 API 연동 시 inquiryId로 데이터 조회
console.log('문의 ID:', inquiryId)
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
</style>
