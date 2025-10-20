<template>
  <!-- 데스크톱 레이아웃 (1024px 이상에서만 표시) -->
  <div class="desktop-layout desktop-only">
    <!-- 좌측 광고 영역 -->
    <aside class="desktop-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">사주라인</h2>
        <p class="sidebar-subtitle">당신의 운명을 밝히는 빛</p>
      </div>

      <!-- 광고 배너들 -->
      <div class="ad-banners">
        <div
          class="ad-banner"
          v-for="ad in adBanners"
          :key="ad.id"
          @click="handleAdClick(ad)"
        >
          <img
            v-if="ad.imageLoaded !== false"
            :src="ad.image"
            :alt="ad.title"
            @error="handleImageError(ad)"
          />
          <div class="banner-overlay">
            <h3>{{ ad.title }}</h3>
            <p>{{ ad.description }}</p>
          </div>
        </div>
      </div>

      <!-- QR 코드 영역 -->
      <div class="qr-section">
        <h3>모바일 앱 설치하고</h3>
        <p>더욱 편리하게 만나보세요</p>
        <div class="qr-code">
          <div class="qr-placeholder">QR 코드</div>
        </div>
      </div>
    </aside>

    <!-- 중앙 모바일 뷰포트 -->
    <main class="mobile-viewport">
      <div class="mobile-container">
        <!-- 헤더를 mobile-container 바로 아래로 이동 -->
        <AppHeader />
        <div style="display: flex; flex-direction: column;">
          <div style="flex: 1;">
            <slot />
          </div>
        </div>
        <!-- 하단 네비게이션을 mobile-container 맨 하단으로 이동 -->
        <AppBottomNavi />
      </div>
    </main>
  </div>

  <!-- 모바일 레이아웃 (1024px 미만에서만 표시) -->
  <div class="mobile-only">
    <AppHeader />
    <div style="display: flex; flex-direction: column;">
      <div style="flex: 1;">
        <slot />
      </div>
    </div>
    <!-- 모바일에서도 하단 네비게이션을 컨테이너 맨 하단으로 이동 -->
    <AppBottomNavi />
  </div>
</template>

<script setup>
// 좌측 광고 영역용 별도 배너들 (메인 배너와 독립적)
const adBanners = ref([
  {
    id: 1,
    title: '첫 상담 50% 할인',
    description: '신규 회원 특별 혜택',
    image: '/images/sidebar-ad-1.jpg',
    link: '/point'
  },
  {
    id: 2,
    title: '인기 상담사 추천',
    description: '평점 4.9 이상 전문가들',
    image: '/images/sidebar-ad-2.jpg',
    link: '/categories'
  },
  {
    id: 3,
    title: 'AI 운세 무료 체험',
    description: '오늘의 운세를 확인하세요',
    image: '/images/sidebar-ad-3.jpg',
    link: '/'
  }
])

// 이미지 로드 에러 처리 (무한 루프 방지)
const handleImageError = (ad) => {
  // 이미지 로드 실패 시 더 이상 표시하지 않음
  ad.imageLoaded = false
}

// 광고 배너 클릭 처리
const handleAdClick = (ad) => {
  if (ad.link) {
    navigateTo(ad.link)
  }
}
</script>

<style scoped>
/* 기본적으로 숨김 */
.desktop-layout {
  display: none;
}

.mobile-only {
  display: block;
}

/* 모바일에서는 기본 fixed 유지하고 헤더와 네비게이션이 보이도록 설정 */
@media (max-width: 1023px) {
  .mobile-only .header,
  .mobile-only .bottom-nav {
    position: fixed !important;
    display: block !important;
    visibility: visible !important;
  }

  /* 모바일에서 헤더 스타일 */
  .mobile-only .header {
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 9999 !important;
    width: 100% !important;
  }

  /* 모바일에서 하단 네비게이션 스타일 */
  .mobile-only .bottom-nav {
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 9999 !important;
    width: 100% !important;
    position: fixed !important;
    visibility: visible !important;
  }

  /* v-if로 숨겨진 경우 완전히 제거 */
  .mobile-only .bottom-nav:not([style*="display: none"]) {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    align-items: center !important;
  }

  /* 모바일에서 하단 네비게이션 내부 요소들 */
  .mobile-only .bottom-nav > * {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
  }

  /* 모바일에서 네비게이션 링크들 */
  .mobile-only .bottom-nav a,
  .mobile-only .bottom-nav button {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    width: 100% !important;
  }
}

/* 데스크톱에서만 표시하고 모든 스타일 적용 */
@media (min-width: 1024px) {
  .desktop-only {
    display: block;
  }

  .mobile-only {
    display: none;
  }

  .desktop-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    max-width: 100%;
    margin: 0 auto;
    gap: 40px;
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    padding: 20px;
  }

  /* 모바일 컨테이너 안에서만 헤더/네비게이션 표시 - 우선 모든 것을 표시하고 스타일링 */
  .desktop-layout .mobile-container header.header {
    display: block !important;
    visibility: visible !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
    width: 100% !important;
    background-color: rgba(255, 0, 0, 0.5) !important; /* 디버깅용: 빨간 배경 */
  }

  .desktop-layout .mobile-container nav.bottom-nav {
    display: flex !important;
    visibility: visible !important;
    position: sticky !important;
    bottom: 0 !important;
    z-index: 1000 !important;
    width: 100% !important;
    background-color: rgba(0, 255, 0, 0.5) !important; /* 디버깅용: 초록 배경 */
    margin-top: auto !important;
  }

  .desktop-sidebar {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    height: fit-content;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
  }

  .sidebar-header {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .sidebar-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #B794F6 0%, #9F7AEA 50%, #805AD5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
  }

  .sidebar-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    margin: 0;
  }

  .ad-banners {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 32px;
  }

  .ad-banner {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    min-height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .ad-banner:hover {
    transform: translateY(-2px);
  }

  .ad-banner img {
    width: 100%;
    height: 120px;
    object-fit: cover;
  }

  .banner-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
    padding: 16px;
    color: white;
  }

  .banner-overlay h3 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .banner-overlay p {
    margin: 0;
    font-size: 12px;
    opacity: 0.9;
  }

  .qr-section {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .qr-section h3 {
    color: white;
    font-size: 16px;
    margin: 0 0 8px 0;
  }

  .qr-section p {
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
    margin: 0 0 16px 0;
  }

  .qr-placeholder {
    width: 100px;
    height: 100px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    color: #333;
    font-size: 12px;
  }

  .mobile-viewport {
    position: relative;
    height: 100vh;
  }

  .mobile-container {
    width: 100%;
    max-width: 576px; /* 480px의 120% = 576px */
    height: 100vh;
    background: #0a0a0f;
    border-radius: 20px;
    overflow-y: auto;
    overflow-x: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    display: flex;
    flex-direction: column;
    contain: layout style paint;
  }

  /* 데스크톱 mobile-container 내부에서 모바일 스타일 적용 */
  .desktop-layout .mobile-container {
    /* 모바일 환경 시뮬레이션 */
    font-size: 14px;
  }

  /* mobile-container 내부의 모든 요소들에 모바일 반응형 적용 */
  .desktop-layout .mobile-container * {
    box-sizing: border-box;
  }

  /* 데스크톱 mobile-container 내부에서 헤더 스타일 */
  .desktop-layout .mobile-container .header {
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
    width: 100% !important;
    background: rgba(10, 10, 15, 0.95) !important;
    backdrop-filter: blur(10px) !important;
  }

  /* 데스크톱 mobile-container 내부에서 하단 네비게이션 스타일 */
  .desktop-layout .mobile-container .bottom-nav {
    position: sticky !important;
    bottom: 0 !important;
    z-index: 1000 !important;
    width: 100% !important;
    margin-top: auto !important;
    background: rgba(10, 10, 15, 0.95) !important;
    backdrop-filter: blur(10px) !important;
  }

  /* v-if로 숨겨진 경우 완전히 제거 */
  .desktop-layout .mobile-container .bottom-nav:not([style*="display: none"]) {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    align-items: center !important;
  }

  /* 모바일 컨테이너의 직접 자식 요소들 */
  .mobile-container > * {
    width: 100%;
    max-width: 100%;
  }


  /* mobile-container 안의 메인 콘텐츠는 스크롤 가능하고 모바일 스타일 적용 */
  .desktop-layout .mobile-container .main-content,
  .desktop-layout .mobile-container main {
    flex: 1 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    margin-top: 0 !important;
    padding-bottom: 120px !important;
    background-color: #0a0a0f !important;
    min-height: calc(100vh - 180px) !important;
    max-height: calc(100vh - 180px) !important;
    position: relative !important;
    -webkit-overflow-scrolling: touch !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  /* 데스크톱 mobile-container 내부의 모든 콘텐츠 영역들이 모바일처럼 동작 */
  .desktop-layout .mobile-container .content-card,
  .desktop-layout .mobile-container .section,
  .desktop-layout .mobile-container .grid,
  .desktop-layout .mobile-container .list {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
    box-sizing: border-box !important;
  }

  /* 데스크톱 mobile-container 내부의 그리드 시스템 모바일화 */
  .desktop-layout .mobile-container .counselor-grid,
  .desktop-layout .mobile-container .category-grid,
  .desktop-layout .mobile-container .charge-grid {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 16px !important;
    padding: 0 20px !important;
  }

  /* 모든 상담사 관련 그리드를 1열로 강제 */
  .desktop-layout .mobile-container [class*="grid"]:has([class*="counselor"]),
  .desktop-layout .mobile-container [class*="counselor"][class*="grid"],
  .desktop-layout .mobile-container [class*="favorite"][class*="list"] {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 16px !important;
    padding: 0 20px !important;
  }

  /* 상담사 카드 컴포넌트들이 포함된 모든 컨테이너를 1열로 */
  .desktop-layout .mobile-container *:has(> [class*="counselor-card"]),
  .desktop-layout .mobile-container *:has(> [class*="CounselorCard"]) {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 16px !important;
  }

  /* 데스크톱 mobile-container 내부의 카드 요소들 */
  .desktop-layout .mobile-container .counselor-card,
  .desktop-layout .mobile-container .category-card,
  .desktop-layout .mobile-container .charge-card {
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
  }

  /* 데스크톱 mobile-container 내부의 텍스트 크기 조정 */
  .desktop-layout .mobile-container h1 { font-size: 24px !important; }
  .desktop-layout .mobile-container h2 { font-size: 20px !important; }
  .desktop-layout .mobile-container h3 { font-size: 18px !important; }
  .desktop-layout .mobile-container h4 { font-size: 16px !important; }
  .desktop-layout .mobile-container p { font-size: 14px !important; }
  .desktop-layout .mobile-container span { font-size: 14px !important; }

  /* 데스크톱 mobile-container 내부의 버튼과 인터랙티브 요소들 */
  .desktop-layout .mobile-container button,
  .desktop-layout .mobile-container .btn {
    min-height: 44px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    touch-action: manipulation !important;
    -webkit-tap-highlight-color: transparent !important;
  }

  /* 데스크톱 mobile-container 내부의 링크 요소들 */
  .desktop-layout .mobile-container a {
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    touch-action: manipulation !important;
    -webkit-tap-highlight-color: transparent !important;
  }

  /* 데스크톱 mobile-container 내부의 입력 요소들 */
  .desktop-layout .mobile-container input,
  .desktop-layout .mobile-container select,
  .desktop-layout .mobile-container textarea {
    min-height: 44px !important;
    padding: 12px !important;
    font-size: 16px !important; /* iOS zoom 방지 */
    border-radius: 8px !important;
    box-sizing: border-box !important;
  }

  /* 데스크톱 mobile-container 내부의 이미지들 */
  .desktop-layout .mobile-container img {
    max-width: 100% !important;
    height: auto !important;
    object-fit: cover !important;
  }

  /* 데스크톱 mobile-container 내부의 플렉스 레이아웃 */
  .desktop-layout .mobile-container .flex,
  .desktop-layout .mobile-container .d-flex {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
  }

  /* 데스크톱 mobile-container 내부의 마진과 패딩 조정 */
  .desktop-layout .mobile-container .container,
  .desktop-layout .mobile-container .page-container {
    padding: 20px !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  /* 1. 메인 페이지 실시간 인기 상담사 필터 반응형 */
  .desktop-layout .mobile-container .filter-chips-container {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    padding: 0 20px !important;
    margin-bottom: 16px !important;
    width: 100% !important;
  }

  .desktop-layout .mobile-container .filter-chips-left,
  .desktop-layout .mobile-container .filter-chips-right {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
  }

  .desktop-layout .mobile-container .chip {
    flex-shrink: 0 !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    border-radius: 20px !important;
    white-space: nowrap !important;
    min-width: auto !important;
    width: auto !important;
  }

  /* 메인 페이지 상담사 그리드 컨테이너 */
  .desktop-layout .mobile-container .counselor-grid-container {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 16px !important;
    padding: 0 20px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  /* 2. 즐겨찾기 페이지 상담사 카드들 반응형 - 메인페이지와 동일한 스타일 */
  .desktop-layout .mobile-container .favorite-list {
    grid-template-columns: 1fr !important;
    gap: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .desktop-layout .mobile-container .favorite-item {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    position: relative !important;
    box-sizing: border-box !important;
  }

  /* 즐겨찾기 페이지 내부의 상담사 카드 컴포넌트들도 1열로 */
  .desktop-layout .mobile-container .favorite-item > * {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* 3. 마이페이지 상단 프로필/멤버십/마일리지 영역 반응형 */
  .desktop-layout .mobile-container .profile-section {
    width: 100% !important;
    padding: 0 !important;
    box-sizing: border-box !important;
  }

  /* 모바일과 데스크톱 모바일 뷰포트 모두에서 적용 */
  .desktop-layout .mobile-container .profile-info-container,
  .mobile-only .profile-info-container {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    grid-template-rows: auto auto !important;
    gap: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  /* 프로필은 첫 번째 행 첫 번째 열 */
  .desktop-layout .mobile-container .profile-section-item:nth-child(1),
  .mobile-only .profile-section-item:nth-child(1) {
    grid-column: 1 / 2 !important;
    grid-row: 1 / 2 !important;
  }

  /* 멤버십은 첫 번째 행 두 번째 열 */
  .desktop-layout .mobile-container .profile-section-item:nth-child(2),
  .mobile-only .profile-section-item:nth-child(2) {
    grid-column: 2 / 3 !important;
    grid-row: 1 / 2 !important;
  }

  /* 마일리지는 두 번째 행 전체 열 */
  .desktop-layout .mobile-container .profile-section-item:nth-child(3),
  .mobile-only .profile-section-item:nth-child(3) {
    grid-column: 1 / 3 !important;
    grid-row: 2 / 3 !important;
  }

  .desktop-layout .mobile-container .profile-section-item,
  .mobile-only .profile-section-item {
    width: 100% !important;
    padding: 16px !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
  }

  .desktop-layout .mobile-container .profile-user-info,
  .desktop-layout .mobile-container .membership-content,
  .desktop-layout .mobile-container .mileage-content {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    width: 100% !important;
  }

  .desktop-layout .mobile-container .profile-main-info,
  .desktop-layout .mobile-container .membership-main-info,
  .desktop-layout .mobile-container .mileage-main-info {
    width: 100% !important;
    text-align: left !important;
  }

  .desktop-layout .mobile-container .profile-stats-mini,
  .desktop-layout .mobile-container .membership-benefits,
  .desktop-layout .mobile-container .mileage-actions {
    width: 100% !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
  }

  /* 추가적인 공통 반응형 패턴들 */

  /* 모든 그리드 컨테이너들을 모바일 친화적으로 */
  .desktop-layout .mobile-container .grid-container,
  .desktop-layout .mobile-container .cards-grid,
  .desktop-layout .mobile-container .items-grid {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 16px !important;
    padding: 0 20px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  /* 모든 flex 컨테이너들을 모바일 친화적으로 */
  .desktop-layout .mobile-container .flex-container,
  .desktop-layout .mobile-container .flex-row,
  .desktop-layout .mobile-container .flex-wrap {
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    width: 100% !important;
  }

  /* 가로 배치가 필요한 요소들만 row로 유지 */
  .desktop-layout .mobile-container .flex-row-mobile,
  .desktop-layout .mobile-container .horizontal-flex {
    flex-direction: row !important;
    flex-wrap: wrap !important;
  }

  /* 카드 요소들의 통일된 스타일 */
  .desktop-layout .mobile-container .card,
  .desktop-layout .mobile-container .item-card,
  .desktop-layout .mobile-container .content-item {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 16px !important;
    box-sizing: border-box !important;
    border-radius: 12px !important;
  }

  /* 섹션 헤더들 */
  .desktop-layout .mobile-container .section-header,
  .desktop-layout .mobile-container .page-section-title {
    padding: 0 20px !important;
    margin-bottom: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  /* 리스트 아이템들 */
  .desktop-layout .mobile-container .list-item,
  .desktop-layout .mobile-container .menu-item {
    width: 100% !important;
    padding: 12px 20px !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
  }

  /* 상태 표시 요소들 */
  .desktop-layout .mobile-container .status-badge,
  .desktop-layout .mobile-container .tag,
  .desktop-layout .mobile-container .chip {
    font-size: 12px !important;
    padding: 4px 8px !important;
    border-radius: 12px !important;
    white-space: nowrap !important;
  }

  /* 헤더 아래 여백 제거 - 모든 페이지의 pt-[60px] 클래스 무효화 */
  .desktop-layout .mobile-container .pt-\[60px\],
  .mobile-only .pt-\[60px\],
  .desktop-layout .mobile-container [class*="pt-[60px]"],
  .mobile-only [class*="pt-[60px]"],
  .desktop-layout .mobile-container main,
  .mobile-only main {
    padding-top: 0 !important;
  }

  /* 모든 main 요소와 콘텐츠 컨테이너의 상단 여백 제거 */
  .desktop-layout .mobile-container > div > main,
  .mobile-only > div > main,
  .desktop-layout .mobile-container .main-content,
  .mobile-only .main-content,
  .desktop-layout .mobile-container main.main-content,
  .mobile-only main.main-content {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }

  /* notices 페이지 및 기타 페이지의 margin-top 제거 */
  .desktop-layout .mobile-container [class*="main"],
  .mobile-only [class*="main"],
  .desktop-layout .mobile-container [class*="content"],
  .mobile-only [class*="content"] {
    margin-top: 0 !important;
  }

  /* 전체 페이지 래퍼도 스크롤 가능하게 */
  .desktop-layout .mobile-container > div {
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    position: relative !important;
  }

  /* 메인 콘텐츠가 아닌 직접 콘텐츠 영역도 스크롤 가능 */
  .desktop-layout .mobile-container > div:not(.main-content) {
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding-bottom: 120px !important; /* 더 넉넉하게 120px */
    box-sizing: border-box !important;
  }

  /* mobile-container 안의 플로팅 버튼 */
  .mobile-container .floating-button {
    position: absolute !important;
    bottom: 100px;
    right: 20px;
    z-index: 1001;
  }

  /* 모든 고정 위치 요소들을 mobile-container 안에 가두기 */
  .mobile-container * {
    max-width: 100%;
  }

  /* 하단 네비게이션 겹침 방지를 위한 추가 여백 */
  .desktop-layout .mobile-container .counselor-grid-container,
  .desktop-layout .mobile-container .category-grid,
  .desktop-layout .mobile-container .charge-grid {
    margin-bottom: 40px !important;
    padding-bottom: 40px !important;
  }

  /* 마지막 요소들에 추가 하단 여백 */
  .desktop-layout .mobile-container section:last-of-type,
  .desktop-layout .mobile-container .content-card:last-child {
    margin-bottom: 40px !important;
    padding-bottom: 40px !important;
  }

  /* 모든 섹션 요소에 하단 여백 추가 */
  .desktop-layout .mobile-container section {
    margin-bottom: 20px !important;
  }

  /* 스크롤바 스타일링 */
  .mobile-container ::-webkit-scrollbar {
    width: 4px;
  }

  .mobile-container ::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }

  .mobile-container ::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }

  .mobile-container ::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }

  /* 모바일 컨테이너의 스크롤 동작 강화 */
  .desktop-layout .mobile-container {
    scroll-behavior: smooth !important;
  }

}



/* 큰 화면에서 고정 너비 */
@media (min-width: 1400px) {
  .desktop-layout {
    grid-template-columns: 320px 576px !important; /* 480px의 120% = 576px */
    justify-content: center;
  }
}
</style>