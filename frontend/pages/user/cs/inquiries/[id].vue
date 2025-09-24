<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 헤더 섹션 -->
        <div class="inquiry-detail-header">
          <button class="back-button" @click="$router.back()">
            <span class="back-icon">←</span>
          </button>
          <h1 class="inquiry-detail-title">문의 상세</h1>
        </div>

        <!-- 문의 정보 -->
        <div class="inquiry-detail-container">
          <!-- 문의 상태 및 기본 정보 -->
          <div class="inquiry-detail-info">
            <div class="inquiry-detail-info-header">
              <div class="inquiry-detail-category">결제문의</div>
              <div class="inquiry-detail-status completed">
                <span class="inquiry-detail-status-icon">✓</span>
                <span>답변완료</span>
              </div>
            </div>
            <div class="inquiry-detail-meta">
              <div class="inquiry-detail-date">작성일: 2024.03.15 14:30</div>
              <div class="inquiry-detail-id">문의번호: #INQ-240315-001</div>
            </div>
          </div>

          <!-- 문의 제목 -->
          <div class="inquiry-detail-title-section">
            <h2 class="inquiry-detail-question-title">포인트 충전이 되지 않습니다</h2>
          </div>

          <!-- 문의 내용 -->
          <div class="inquiry-detail-content-section">
            <h3 class="inquiry-detail-section-title">문의 내용</h3>
            <div class="inquiry-detail-question-content">
              <p>안녕하세요.</p>
              <p>포인트 충전이 되지 않아 문의드립니다.</p>
              <p>결제는 완료되었는데 포인트가 반영되지 않았습니다.</p>
              <p>결제 완료 시간: 2024.03.15 13:45</p>
              <p>결제 금액: 50,000원</p>
              <p>결제 방법: 신용카드</p>
              <p>확인 부탁드립니다.</p>
            </div>
          </div>

          <!-- 첨부파일 (있는 경우) -->
          <div class="inquiry-detail-attachments">
            <h3 class="inquiry-detail-section-title">첨부파일</h3>
            <div class="inquiry-detail-file-list">
              <div class="inquiry-detail-file-item">
                <span class="inquiry-detail-file-icon">📄</span>
                <span class="inquiry-detail-file-name">결제완료_스크린샷.png</span>
                <button class="inquiry-detail-file-download">다운로드</button>
              </div>
            </div>
          </div>

          <!-- 답변 섹션 -->
          <div class="inquiry-detail-answer-section">
            <h3 class="inquiry-detail-section-title">답변</h3>
            <div class="inquiry-detail-answer">
              <div class="inquiry-detail-answer-header">
                <div class="inquiry-detail-answer-author">
                  <span class="inquiry-detail-answer-icon">👨‍💼</span>
                  <span class="inquiry-detail-answer-name">고객센터</span>
                </div>
                <div class="inquiry-detail-answer-date">2024.03.15 15:20</div>
              </div>
              <div class="inquiry-detail-answer-content">
                <p>안녕하세요. 피플라인 고객센터입니다.</p>
                <p>결제 관련 문의해 주셔서 감사합니다.</p>
                <p>확인 결과, 결제는 정상적으로 완료되었으나 시스템 오류로 인해 포인트 적립이 지연된 것을 확인했습니다.</p>
                <p>지금 즉시 50,000 포인트를 회원님 계정에 추가 적립해 드렸습니다.</p>
                <p>이용에 불편을 드려 죄송하며, 앞으로 더 나은 서비스를 제공하도록 노력하겠습니다.</p>
                <p>추가 문의사항이 있으시면 언제든지 연락 부탁드립니다.</p>
                <p>감사합니다.</p>
              </div>
            </div>
          </div>

          <!-- 만족도 평가 -->
          <div class="inquiry-detail-satisfaction">
            <h3 class="inquiry-detail-section-title">답변은 도움이 되셨나요?</h3>
            <div class="inquiry-detail-satisfaction-buttons">
              <button class="inquiry-satisfaction-btn satisfied">
                <span>😊</span>
                <span>만족</span>
              </button>
              <button class="inquiry-satisfaction-btn">
                <span>😐</span>
                <span>보통</span>
              </button>
              <button class="inquiry-satisfaction-btn">
                <span>😞</span>
                <span>불만족</span>
              </button>
            </div>
            <div class="inquiry-detail-satisfaction-note">
              답변에 대한 평가를 남겨주세요. 서비스 개선에 도움이 됩니다.
            </div>
          </div>

          <!-- 액션 버튼들 -->
          <div class="inquiry-detail-actions">
            <button class="inquiry-detail-action-btn secondary" @click="$router.push('/user/cs/inquiries')">
              목록으로
            </button>
            <button class="inquiry-detail-action-btn primary" @click="$router.push('/user/cs/write')">
              새 문의하기
            </button>
          </div>
        </div>
      </section>
    </main>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

// URL에서 id 파라미터 가져오기 (실제로는 이를 이용해 API 호출)
const route = useRoute()
const inquiryId = route.params.id
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';
</style>