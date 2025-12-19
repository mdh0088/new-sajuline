<template>
  <div class="desktop-layout">
    <!-- 좌측 광고 영역 -->
    <aside class="desktop-sidebar">
      <div class="sidebar-header">
        <img src="/logo.png" alt="사주라인" class="sidebar-logo" />
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
            :src="ad.image"
            :alt="ad.title"
            @error="$event.target.src = '/images/placeholder-ad.jpg'"
          />
          <div class="banner-overlay">
            <h3>{{ ad.title }}</h3>
            <p>{{ ad.description }}</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- 중앙 모바일 뷰포트 -->
    <main class="mobile-viewport">
      <div class="mobile-container">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
// 좌측 광고 영역용 별도 배너들 (메인 배너와 독립적)
const adBanners = ref([
  {
    id: 1,
    title: '',
    description: '',
    image: '/images/banners/banner-1.jpg',
    link: '/signup'
  },
  {
    id: 2,
    title: '',
    description: '',
    image: '/images/banners/banner-2.jpg',
    link: '/categories'
  },
  {
    id: 3,
    title: '',
    description: '',
    image: '/images/banners/banner-3.jpg',
    link: '/reviews'
  }
])

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

/* 데스크톱에서만 표시하고 모든 스타일 적용 */
@media (min-width: 1024px) {
  .desktop-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    max-width: 1200px;
    margin: 0 auto;
    gap: 40px;
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    padding: 20px;
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

  .sidebar-logo {
    width: 180px;
    height: auto;
    object-fit: contain;
    display: block;
    margin: 0 auto 8px auto;
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

  .mobile-viewport {
    position: relative;
    height: 100vh;
  }

  .mobile-container {
    width: 100%;
    max-width: 480px;
    height: 100vh;
    background: #0a0a0f;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    display: flex;
    flex-direction: column;
  }

  /* mobile-container 안의 mobile-app-wrapper 스타일 */
  .mobile-container .mobile-app-wrapper {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0a0a0f;
  }

  /* 데스크톱 모드에서 헤더를 모바일 컨테이너 안으로 제한 */
  .mobile-container .header {
    position: absolute !important;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    /* fixed를 absolute로 강제 변경 */
  }

  /* 데스크톱 모드에서 하단 네비게이션을 모바일 컨테이너 안으로 제한 */
  .mobile-container .bottom-nav {
    position: absolute !important;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    /* fixed를 absolute로 강제 변경 */
  }

  /* mobile-container 안의 메인 콘텐츠는 스크롤 가능 */
  .mobile-container .main-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    margin-top: 0 !important;
    padding-top: 60px !important; /* 헤더 높이만큼 */
    padding-bottom: 80px !important; /* 하단 네비게이션 높이만큼 */
    background-color: #0a0a0f;
    min-height: auto;
  }

  /* mobile-container 안의 플로팅 버튼 */
  .mobile-container .floating-button {
    position: absolute !important;
    bottom: 100px;
    right: 20px;
    z-index: 1001;
  }

  /* 스크롤바 스타일링 */
  .mobile-container .main-content::-webkit-scrollbar {
    width: 4px;
  }

  .mobile-container .main-content::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }

  .mobile-container .main-content::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }

  .mobile-container .main-content::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }
}

/* 큰 화면에서 고정 너비 */
@media (min-width: 1400px) {
  .desktop-layout {
    grid-template-columns: 320px 480px !important;
    justify-content: center;
  }
}
</style>