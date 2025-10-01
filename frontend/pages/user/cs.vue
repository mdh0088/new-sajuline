<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <!-- 상단 안내 섹션 -->
      <section class="cs-info-section">
        <div class="cs-info-icon">🚀</div>
        <h2 class="cs-info-title">빠르고 정확한 답변</h2>
        <p class="cs-info-desc">
          궁금하신 사항을 빠르게 해결해드립니다<br>
          평균 응답시간 10분 이내
        </p>
      </section>

      <!-- 운영시간 및 전화상담 안내 -->
      <div class="cs-info-banners">
        <div class="cs-hours-banner">
          <div class="cs-hours-icon">⏰</div>
          <div class="cs-hours-content">
            <div class="cs-hours-title">고객센터 운영시간</div>
            <div class="cs-hours-time">평일 09:00 - 22:00 | 주말 10:00 - 20:00</div>
          </div>
        </div>

        <div class="cs-phone-banner">
          <div class="cs-phone-icon">📞</div>
          <div class="cs-phone-content">
            <div class="cs-phone-title">전화 상담</div>
            <div class="cs-phone-number">02-6212-0465</div>
          </div>
        </div>
      </div>
        <!-- 빠른 문의 카테고리 -->
            <section class="cs-quick-category-section">
        <h3 class="cs-section-title">무엇을 도와드릴까요?</h3>
        <div class="cs-category-grid">
          <div class="cs-category-card" @click="() => goInquiryWrite('결제/환불')">
            <div class="cs-category-icon">💳</div>
            <div class="cs-category-name">결제/환불</div>
            <div class="cs-category-desc">포인트 충전, 환불 관련</div>
          </div>
          <div class="cs-category-card" @click="() => goInquiryWrite('계정 문의')">
            <div class="cs-category-icon">👤</div>
            <div class="cs-category-name">계정 문의</div>
            <div class="cs-category-desc">로그인, 비밀번호 찾기</div>
          </div>
          <div class="cs-category-card" @click="() => goInquiryWrite('상담 문의')">
            <div class="cs-category-icon">💬</div>
            <div class="cs-category-name">상담 문의</div>
            <div class="cs-category-desc">상담 진행, 상담사 관련</div>
          </div>
          <div class="cs-category-card" @click="() => goInquiryWrite('이벤트/혜택')">
            <div class="cs-category-icon">🎁</div>
            <div class="cs-category-name">이벤트/혜택</div>
            <div class="cs-category-desc">프로모션, 쿠폰 사용</div>
          </div>
        </div>
      </section>

      <!-- 문의내역 섹션 -->
      <section class="cs-inquiry-section">
        <div class="cs-inquiry-header">
          <h2 class="cs-inquiry-title">
            <span>📝</span>
            <span>내 문의내역</span>
          </h2>
          <div class="cs-inquiry-actions">
            <NuxtLink to="/user/cs/inquiries" class="cs-view-all">
              <span>전체보기</span>
              <span>›</span>
            </NuxtLink>
            <button class="cs-inquiry-button" @click="() => goInquiryWrite()">
              <span>✏️</span>
              <span>문의하기</span>
            </button>
          </div>
        </div>
        <div class="cs-inquiry-list">
          <div class="cs-inquiry-item" @click="() => goInquiryDetail(1)">
            <div class="cs-inquiry-item-header">
              <span class="cs-inquiry-category">결제문의</span>
              <span class="cs-inquiry-date">2024.03.15</span>
            </div>
            <div class="cs-inquiry-content">
              포인트 충전이 되지 않아 문의드립니다. 결제는 완료되었는데 포인트가 반영되지 않았습니다.
            </div>
            <div class="cs-inquiry-status completed">
              <span class="cs-status-icon">✓</span>
              <span>답변완료</span>
            </div>
          </div>
          <div class="cs-inquiry-item" @click="() => goInquiryDetail(2)">
            <div class="cs-inquiry-item-header">
              <span class="cs-inquiry-category">서비스문의</span>
              <span class="cs-inquiry-date">2024.03.14</span>
            </div>
            <div class="cs-inquiry-content">
              AI 운세 서비스 이용 중 오류가 발생했습니다. 화면이 계속 로딩 중입니다.
            </div>
            <div class="cs-inquiry-status waiting">
              <span class="cs-status-icon">⏳</span>
              <span>답변대기</span>
            </div>
          </div>
        </div>
      </section>



      <!-- 자주 묻는 질문 -->
      <section class="cs-faq-section">
        <h3 class="cs-section-title">자주 묻는 질문 TOP 5</h3>
        <div class="cs-faq-list">
          <div
            v-for="(faq, index) in faqList"
            :key="index"
            class="cs-faq-item"
            :class="{ active: activeFaq === index }"
            @click="() => toggleFaq(index)"
          >
            <div class="cs-faq-question">
              <div class="cs-faq-text">
                <span class="cs-faq-q-icon">Q.</span>
                {{ faq.question }}
              </div>
              <span class="cs-faq-arrow">›</span>
            </div>
            <div class="cs-faq-answer">
              {{ faq.answer }}
            </div>
          </div>
        </div>
      </section>


      <!-- 공지사항 링크 -->
      <NuxtLink to="/notices" class="cs-notice-link">
        <div class="cs-notice-content">
          <span class="cs-notice-icon">📢</span>
          <span class="cs-notice-text">공지사항</span>
        </div>
        <div class="cs-notice-right">
          <span class="cs-notice-badge">NEW</span>
          <span class="cs-notice-arrow">›</span>
        </div>
      </NuxtLink>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

const router = useRouter()

// FAQ 관련 상태
const activeFaq = ref(-1)

// FAQ 데이터 (UI만)
const faqList = ref([
  {
    question: '포인트는 어떻게 충전하나요?',
    answer: '마이페이지 > 포인트 충전 메뉴에서 원하시는 금액을 선택하여 충전하실 수 있습니다. 신용카드, 휴대폰 결제, 계좌이체, 카카오페이 등 다양한 결제 수단을 지원합니다.'
  },
  {
    question: '상담사님과 연결이 안 돼요',
    answer: '선택하신 상담사님이 다른 상담 중이실 수 있습니다. 상담사 프로필에서 \'예약하기\'를 선택하시면 상담 가능 시간에 알림을 받으실 수 있습니다.'
  },
  {
    question: '첫 상담 무료체험은 어떻게 받나요?',
    answer: '신규 회원님께는 첫 상담 10분 무료 쿠폰이 자동으로 지급됩니다. 상담사 선택 후 결제 단계에서 쿠폰을 적용하시면 됩니다.'
  },
  {
    question: '상담 내용은 비밀이 보장되나요?',
    answer: '네, 모든 상담 내용은 철저히 비밀이 보장됩니다. 상담 내용은 암호화되어 저장되며, 본인 외에는 누구도 확인할 수 없습니다.'
  },
  {
    question: '환불은 어떻게 받을 수 있나요?',
    answer: '사용하지 않은 포인트는 충전일로부터 7일 이내 100% 환불 가능합니다. 고객센터로 문의 주시면 빠르게 처리해드립니다.'
  }
])

// FAQ 토글 (UI만)
const toggleFaq = (index: number) => {
  if (activeFaq.value === index) {
    activeFaq.value = -1
  } else {
    activeFaq.value = index
  }
}

// 네비게이션 함수들
const goInquiryWrite = (category?: string) => {
  console.log('goInquiryWrite 호출됨:', category)
  if (category) {
    router.push(`/user/cs/write?category=${encodeURIComponent(category)}`)
  } else {
    router.push('/user/cs/write')
  }
}

const goInquiryDetail = (id: number) => {
  console.log('goInquiryDetail 호출됨:', id)
  router.push(`/user/cs/inquiries/${id}`)
}
</script>

<style>
@import '~/assets/css/cs.css';
</style>