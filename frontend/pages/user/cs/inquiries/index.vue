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
            >
            <button class="inquiry-search-button">
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
          <div class="inquiry-list-items">
            <!-- 문의 항목 1 -->
            <div
              class="inquiry-list-item"
              @click="openInquiryModal(inquiries[0])"
            >
              <div class="inquiry-list-item-header">
                <div class="inquiry-list-category">결제문의</div>
                <div class="inquiry-list-date">2024.03.15</div>
              </div>
              <div class="inquiry-list-title-text">포인트 충전이 되지 않습니다</div>
              <div class="inquiry-list-content">
                포인트 충전이 되지 않아 문의드립니다. 결제는 완료되었는데 포인트가 반영되지 않았습니다.
              </div>
              <div class="inquiry-list-footer">
                <div class="inquiry-list-status completed">
                  <span class="inquiry-list-status-icon">✓</span>
                  <span>답변완료</span>
                </div>
                <div class="inquiry-list-arrow">›</div>
              </div>
            </div>

            <!-- 문의 항목 2 -->
            <div class="inquiry-list-item" @click="openInquiryModal(inquiries[1])">
              <div class="inquiry-list-item-header">
                <div class="inquiry-list-category">서비스문의</div>
                <div class="inquiry-list-date">2024.03.14</div>
              </div>
              <div class="inquiry-list-title-text">AI 운세 서비스 오류</div>
              <div class="inquiry-list-content">
                AI 운세 서비스 이용 중 오류가 발생했습니다. 화면이 계속 로딩 중입니다.
              </div>
              <div class="inquiry-list-footer">
                <div class="inquiry-list-status waiting">
                  <span class="inquiry-list-status-icon">⏳</span>
                  <span>답변대기</span>
                </div>
                <div class="inquiry-list-arrow">›</div>
              </div>
            </div>

            <!-- 문의 항목 3 -->
            <div class="inquiry-list-item" @click="openInquiryModal(inquiries[2])">
              <div class="inquiry-list-item-header">
                <div class="inquiry-list-category">계정문의</div>
                <div class="inquiry-list-date">2024.03.13</div>
              </div>
              <div class="inquiry-list-title-text">비밀번호 재설정이 안됩니다</div>
              <div class="inquiry-list-content">
                비밀번호 찾기를 클릭해도 이메일이 오지 않습니다. 스팸함도 확인했는데 없습니다.
              </div>
              <div class="inquiry-list-footer">
                <div class="inquiry-list-status completed">
                  <span class="inquiry-list-status-icon">✓</span>
                  <span>답변완료</span>
                </div>
                <div class="inquiry-list-arrow">›</div>
              </div>
            </div>

            <!-- 문의 항목 4 -->
            <div class="inquiry-list-item" @click="openInquiryModal(inquiries[3])">
              <div class="inquiry-list-item-header">
                <div class="inquiry-list-category">이벤트/혜택</div>
                <div class="inquiry-list-date">2024.03.12</div>
              </div>
              <div class="inquiry-list-title-text">신규 회원 쿠폰이 지급되지 않았습니다</div>
              <div class="inquiry-list-content">
                회원가입을 완료했는데 첫 상담 무료 쿠폰이 지급되지 않았습니다. 언제 받을 수 있나요?
              </div>
              <div class="inquiry-list-footer">
                <div class="inquiry-list-status completed">
                  <span class="inquiry-list-status-icon">✓</span>
                  <span>답변완료</span>
                </div>
                <div class="inquiry-list-arrow">›</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div class="inquiry-pagination">
          <button class="inquiry-page-btn" disabled>‹</button>
          <button class="inquiry-page-btn active">1</button>
          <button class="inquiry-page-btn">2</button>
          <button class="inquiry-page-btn">3</button>
          <button class="inquiry-page-btn">›</button>
        </div>
      </section>
    </main>

    <!-- 플로팅 문의하기 버튼 -->
    <NuxtLink to="/user/cs/write" class="inquiry-floating-write-btn">
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
                <div class="inquiry-detail-category">{{ selectedInquiry.category }}</div>
                <div class="inquiry-detail-status" :class="selectedInquiry.status">
                  <span class="inquiry-detail-status-icon">{{ selectedInquiry.statusIcon }}</span>
                  <span>{{ selectedInquiry.statusText }}</span>
                </div>
              </div>

              <!-- 문의 제목 -->
              <h3 class="inquiry-detail-subject">
                {{ selectedInquiry.title }}
              </h3>

              <!-- 문의 메타 정보 -->
              <div class="inquiry-detail-meta">
                <span>작성일: {{ selectedInquiry.date }}</span>
                <span class="inquiry-detail-divider">|</span>
                <span>조회수: {{ selectedInquiry.views }}</span>
              </div>

              <!-- 문의 내용 -->
              <div class="inquiry-detail-content">
                <p v-html="selectedInquiry.content" />
              </div>

              <!-- 답변 섹션 -->
              <div v-if="selectedInquiry.reply" class="inquiry-reply-container">
                <div class="inquiry-reply-header">
                  <div class="inquiry-reply-icon">💬</div>
                  <div class="inquiry-reply-title">고객센터 답변</div>
                </div>
                <div class="inquiry-reply-meta">
                  <span>답변일: {{ selectedInquiry.reply.date }}</span>
                </div>
                <div class="inquiry-reply-content">
                  <p v-html="selectedInquiry.reply.content" />
                </div>
              </div>

              <!-- 하단 버튼 -->
              <div class="inquiry-detail-actions">
                <button class="inquiry-detail-action-btn secondary" @click="closeInquiryModal">
                  닫기
                </button>
                <NuxtLink to="/user/cs/write" class="inquiry-detail-action-btn primary">
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
import { ref } from 'vue'

definePageMeta({
  layout: 'default'
})

interface IInquiry {
  id: number
  category: string
  title: string
  content: string
  date: string
  views: number
  status: 'completed' | 'waiting'
  statusIcon: string
  statusText: string
  reply?: {
    date: string
    content: string
  }
}

// 검색 및 필터 상태
const searchQuery = ref('')
const filter = ref<'all' | 'waiting' | 'completed'>('all')

// 모달 상태
const isModalOpen = ref(false)
const selectedInquiry = ref<IInquiry | null>(null)

// 문의 데이터
const inquiries: IInquiry[] = [
  {
    id: 1,
    category: '결제문의',
    title: '포인트 충전이 되지 않습니다',
    content: `포인트 충전이 되지 않아 문의드립니다.<br>
결제는 완료되었는데 포인트가 반영되지 않았습니다.<br><br>

결제 정보:<br>
- 결제 금액: 50,000원<br>
- 결제 시간: 2024.03.15 14:20<br>
- 결제 수단: 신용카드<br><br>

빠른 처리 부탁드립니다.`,
    date: '2024.03.15 14:32',
    views: 1,
    status: 'completed',
    statusIcon: '✓',
    statusText: '답변완료',
    reply: {
      date: '2024.03.15 15:10',
      content: `안녕하세요, 사주라인 고객센터입니다.<br><br>

문의하신 포인트 충전 건에 대해 확인해드렸습니다.<br>
결제는 정상적으로 완료되었으나, 시스템 지연으로 인해 포인트 반영이 늦어진 것으로 확인되었습니다.<br><br>

현재 50,000P가 정상적으로 충전되었음을 확인하였습니다.<br>
불편을 드려 죄송합니다.<br><br>

추가 문의사항이 있으시면 언제든 연락 주세요.<br>
감사합니다.`
    }
  },
  {
    id: 2,
    category: '서비스문의',
    title: 'AI 운세 서비스 오류',
    content: 'AI 운세 서비스 이용 중 오류가 발생했습니다. 화면이 계속 로딩 중입니다.',
    date: '2024.03.14 16:20',
    views: 2,
    status: 'waiting',
    statusIcon: '⏳',
    statusText: '답변대기'
  },
  {
    id: 3,
    category: '계정문의',
    title: '비밀번호 재설정이 안됩니다',
    content: '비밀번호 찾기를 클릭해도 이메일이 오지 않습니다. 스팸함도 확인했는데 없습니다.',
    date: '2024.03.13 10:15',
    views: 3,
    status: 'completed',
    statusIcon: '✓',
    statusText: '답변완료',
    reply: {
      date: '2024.03.13 11:30',
      content: `안녕하세요, 사주라인 고객센터입니다.<br><br>

비밀번호 재설정 이메일이 발송되지 않는 문제에 대해 확인해드렸습니다.<br>
가입하신 이메일 주소가 정확한지 확인 부탁드립니다.<br><br>

추가 문의사항이 있으시면 언제든 연락 주세요.<br>
감사합니다.`
    }
  },
  {
    id: 4,
    category: '이벤트/혜택',
    title: '신규 회원 쿠폰이 지급되지 않았습니다',
    content: '회원가입을 완료했는데 첫 상담 무료 쿠폰이 지급되지 않았습니다. 언제 받을 수 있나요?',
    date: '2024.03.12 09:45',
    views: 1,
    status: 'completed',
    statusIcon: '✓',
    statusText: '답변완료',
    reply: {
      date: '2024.03.12 10:20',
      content: `안녕하세요, 사주라인 고객센터입니다.<br><br>

신규 회원 쿠폰은 회원가입 후 24시간 이내에 자동으로 지급됩니다.<br>
현재 쿠폰함을 확인하시면 정상적으로 지급된 쿠폰을 확인하실 수 있습니다.<br><br>

감사합니다.`
    }
  }
]

const openInquiryModal = (inquiry: IInquiry | undefined) => {
  if (!inquiry) return
  selectedInquiry.value = inquiry
  isModalOpen.value = true
  document.body.style.overflow = 'hidden'
}

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
</style>
