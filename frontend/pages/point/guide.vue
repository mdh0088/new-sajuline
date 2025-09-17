<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-top">
        <button class="back-button" @click="$router.back()">←</button>
        <h1 class="header-title">충전 안내</h1>
        <div class="header-actions">
          <button class="icon-btn" @click="$router.push('/search')">🔍</button>
          <button class="icon-btn" @click="$router.push('/login')">👤</button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 탭 버튼 -->
      <div class="tabs">
        <div
          :class="['tab-btn', { active: activeTab === 'prepay' }]"
          @click="setActiveTab('prepay')"
        >
          선불(포인트) 상담
        </div>
        <div
          :class="['tab-btn', { active: activeTab === 'postpay' }]"
          @click="setActiveTab('postpay')"
        >
          후불(060) 상담
        </div>
      </div>

      <!-- 선불(포인트) 상담 탭 -->
      <div v-if="activeTab === 'prepay'" class="tab-content">
        <!-- 인포 카드 -->
        <div class="content-card">
          <h3><span class="icon">💡</span>사주라인 포인트 상담의 장점</h3>
          <ol>
            <li>원하는 만큼만 충전할 수 있어, 남은 포인트는 언제든 사용할 수 있습니다.</li>
            <li>이용요금이 선불로 납부되어 명세서에 별도 요금이 표시되지 않습니다.</li>
            <li>후불 전화(30초당 1,500원) 대비 파격 할인된 요금으로 이용할 수 있습니다.</li>
          </ol>
        </div>

        <!-- 이용방법 -->
        <div class="content-card">
          <h3><span class="icon">📞</span>1. 포인트 상담 이용방법</h3>
          <ol>
            <li>
              <strong>홈페이지에서 충전 후 연결하기</strong><br>
              1) 사주라인 홈페이지에서 회원가입 후 포인트 충전<br>
              2) 원하는 상담사 프로필에서 <em>상담하기</em> 클릭 → 상담하기 화면에서 <em>(포인트) 전화상담하기</em> 버튼 클릭<br>
              3) 전화 연결 시 선택한 상담사와 바로 연결됩니다.
            </li>
            <li>
              <strong>전화로 직접 연결하기</strong><br>
              - 포인트 상담번호 <code>02-6209-0808</code>로 전화 후, 상담사의 고유번호(3자리)를 입력 → 상담사 연결
            </li>
          </ol>
        </div>

        <!-- 필수 확인사항 -->
        <div class="content-card">
          <h3><span class="icon">⚠️</span>2. 포인트 상담 필수 확인사항</h3>
          <ol>
            <li>상담사와 연결되기 전까지 포인트는 차감되지 않습니다.</li>
            <li>30초당 상담사가 설정한 금액만큼 포인트가 차감됩니다.</li>
            <li>전화 중 종료 1분 전까지 충전이 가능하니, 연장을 원하시면 종료 1분 전까지 충전하세요.</li>
          </ol>
        </div>
      </div>

      <!-- 후불(060) 상담 탭 -->
      <div v-if="activeTab === 'postpay'" class="tab-content">
        <!-- 이용방법 -->
        <div class="content-card">
          <h3><span class="icon">📞</span>1. 홈페이지를 통한 후불(060) 상담</h3>
          <ol>
            <li>사주라인 홈페이지에서 원하는 상담사 프로필에서 <em>상담하기</em> 클릭 → 상담하기 화면에서 <em>(060) 전화상담하기</em> 버튼 클릭</li>
            <li>연결 후 상담사의 고유번호(3자리)를 입력 → 상담사 연결</li>
          </ol>
        </div>

        <div class="content-card">
          <h3><span class="icon">📲</span>2. 전화로 직접 연결하기</h3>
          <ol>
            <li>060 상담번호 <code>060-800-1300</code> 또는 <code>060-800-1500</code>으로 전화 후, 상담사의 고유번호(3자리)를 입력 → 상담사 연결</li>
          </ol>
        </div>

        <!-- 필수 확인사항 -->
        <div class="content-card">
          <h3><span class="icon">⚠️</span>3. 후불 전화 필수 확인사항</h3>
          <ol>
            <li>전화 연결 후 첫 40초간은 요금이 부과되지 않습니다.</li>
            <li>40초 이후부터 상담사가 설정한 30초당 금액(VAT 별도)이 부과됩니다.</li>
            <li>이용료는 다음 달 이용 요금 명세서에 합산되어 청구됩니다.</li>
          </ol>
          <p>※ 포인트 상담을 이용할 경우, 후불(060) 상담보다 저렴한 요금으로 이용하실 수 있습니다.</p>
        </div>
      </div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <NuxtLink to="/" class="nav-item">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">홈</span>
      </NuxtLink>
      <NuxtLink to="/events" class="nav-item">
        <span class="nav-icon">🎁</span>
        <span class="nav-label">이벤트</span>
      </NuxtLink>
      <NuxtLink to="/user/favorite" class="nav-item">
        <span class="nav-icon">⭐</span>
        <span class="nav-label">즐겨찾기</span>
      </NuxtLink>
      <NuxtLink to="/user/mypage" class="nav-item">
        <span class="nav-icon">👤</span>
        <span class="nav-label">마이</span>
      </NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useHead } from 'nuxt/app'

// SEO 및 메타 데이터 설정
useHead({
  title: '충전 안내 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 포인트 충전 및 상담 이용 방법을 안내합니다.' },
    { property: 'og:title', content: '충전 안내 - 사주라인' },
    { property: 'og:description', content: '사주라인 포인트 충전 및 상담 이용 방법을 안내합니다.' }
  ]
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: false,
  layout: 'default'
})

// 활성 탭
const activeTab = ref<'prepay' | 'postpay'>('prepay')

// 탭 변경 메서드
function setActiveTab(tab: 'prepay' | 'postpay') {
  activeTab.value = tab
}
</script>

<style scoped>
/* point-guide.css 파일을 import하여 사용 */
@import '~/assets/css/point-guide.css';
</style>