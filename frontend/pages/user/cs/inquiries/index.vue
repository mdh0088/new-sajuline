<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 헤더 섹션 -->
        <div class="inquiry-list-header">
          <button class="back-button" @click="$router.back()">
            <span class="back-icon">←</span>
          </button>
          <h1 class="inquiry-list-title">문의내역</h1>
        </div>

        <!-- 검색 섹션 -->
        <div class="inquiry-search-section">
          <div class="inquiry-search-form">
            <input
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
            <button class="inquiry-filter-btn active">전체</button>
            <button class="inquiry-filter-btn">답변대기</button>
            <button class="inquiry-filter-btn">답변완료</button>
          </div>
        </div>

        <!-- 문의 목록 -->
        <div class="inquiry-list-container">
          <div class="inquiry-list-items">
            <!-- 문의 항목 1 -->
            <div class="inquiry-list-item" @click="() => goInquiryDetail(1)">
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
            <div class="inquiry-list-item" @click="() => goInquiryDetail(2)">
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
            <div class="inquiry-list-item" @click="() => goInquiryDetail(3)">
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
            <div class="inquiry-list-item" @click="() => goInquiryDetail(4)">
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

          <!-- 빈 상태 (조건부 표시, UI만) -->
          <!-- <div class="inquiry-empty-state">
            <div class="inquiry-empty-icon">📝</div>
            <div class="inquiry-empty-title">문의내역이 없습니다</div>
            <div class="inquiry-empty-desc">궁금한 사항이 있으시면 언제든 문의해 주세요.</div>
            <NuxtLink to="/user/cs/write" class="inquiry-empty-button">
              문의하기
            </NuxtLink>
          </div> -->
        </div>

        <!-- 페이지네이션 (UI만) -->
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

  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

const router = useRouter()

// 네비게이션 함수 (UI만)
const goInquiryDetail = (id: number) => {
  router.push(`/user/cs/inquiries/${id}`)
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';
</style>