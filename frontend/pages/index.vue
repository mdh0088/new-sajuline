<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-top">
        <div class="logo">사주라인</div>
        <div class="header-actions">
          <div class="coin-balance" @click="$router.push('/payment')">
            <span>💰</span>
            <span>{{ userPoints }}P</span>
          </div>
          <button class="icon-btn" @click="$router.push('/search')">
            🔍
          </button>
          <button class="icon-btn" @click="$router.push('/login')">
            👤
          </button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 히어로 섹션 -->
      <section class="hero-section">
        <div class="hero-background"></div>
        <div class="hero-content">
          <div class="hero-badge">
            <span>✨</span>
            <span>오늘만 특별 혜택</span>
          </div>
          <h1 class="hero-title">당신의 운명을<br>밝히는 빛</h1>
          <p class="hero-subtitle">검증된 전문가가 읽어주는<br>나만의 맞춤 운세</p>
          <div class="cta-container">
            <button class="cta-button" @click="startFreeTrial">첫 상담 무료체험</button>
            <button class="cta-button cta-secondary" @click="requestAIFortune">AI 운세</button>
          </div>
        </div>
      </section>

      <!-- 실시간 지표 -->
      <section class="live-stats">
        <div class="stat-item">
          <div class="stat-number">{{ liveStats.consulting.toLocaleString() }}</div>
          <div class="stat-label">현재 상담중</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ liveStats.satisfaction }}%</div>
          <div class="stat-label">만족도</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ liveStats.totalConsultations }}+</div>
          <div class="stat-label">누적 상담</div>
        </div>
      </section>

      <!-- 오늘의 운세 카드 -->
      <section class="today-fortune">
        <div class="fortune-header">
          <h3 class="fortune-title">
            <span>🌟</span>
            <span>오늘의 운세</span>
          </h3>
          <span class="fortune-date">{{ todayDate }}</span>
        </div>
        <p class="fortune-content">{{ todayFortune.content }}</p>
        <div class="fortune-meters">
          <div
            v-for="meter in todayFortune.meters"
            :key="meter.label"
            class="meter-item"
          >
            <div class="meter-label">{{ meter.label }}</div>
            <div class="meter-bar">
              <div class="meter-fill" :style="{ width: meter.value + '%' }"></div>
            </div>
            <div class="meter-value">{{ meter.value }}%</div>
          </div>
        </div>
      </section>

      <!-- AI 추천 배너 -->
      <section class="ai-recommendation" @click="$router.push('/ai-counselor')">
        <div class="ai-icon">🤖</div>
        <div class="ai-content">
          <h3 class="ai-title">AI가 추천하는 맞춤 상담사</h3>
          <p class="ai-desc">당신의 고민을 분석해 최적의 상담사를 찾아드려요</p>
        </div>
        <span class="arrow">→</span>
      </section>

      <!-- 빠른 상담 카테고리 -->
      <section class="quick-consult">
        <div class="section-header">
          <h2 class="section-title">어떤 고민이 있으신가요?</h2>
          <NuxtLink to="/categories" class="see-all">전체보기 →</NuxtLink>
        </div>
        <div class="category-grid">
          <div
            v-for="category in categories"
            :key="category.name"
            class="category-card"
            @click="$router.push(category.path)"
          >
            <div class="category-icon">{{ category.icon }}</div>
            <div class="category-name">{{ category.name }}</div>
          </div>
        </div>
      </section>

      <!-- 프로모션 배너 -->
      <section class="promotion-banner">
        <div class="promotion-content">
          <h3 class="promotion-title">🎉 첫 충전 100% 보너스</h3>
          <p class="promotion-desc">지금 충전하면 2배로 돌려드려요!</p>
          <button class="promotion-button" @click="$router.push('/payment')">혜택 받기</button>
        </div>
      </section>

      <!-- 상담사 리스트 -->
      <section class="counselor-list">
        <div class="section-header">
          <h2 class="section-title">실시간 인기 상담사</h2>
        </div>

        <div class="filter-chips">
          <div
            v-for="(filter, index) in filters"
            :key="filter"
            :class="['chip', { active: activeFilter === index }]"
            @click="setActiveFilter(index)"
          >
            {{ filter }}
          </div>
        </div>

        <!-- 상담사 카드들 -->
        <div
          v-for="counselor in counselors"
          :key="counselor.id"
          class="counselor-card"
          @click="$router.push(`/counselor/${counselor.id}`)"
        >
          <div class="counselor-header">
            <div :class="['counselor-avatar', { online: counselor.isOnline }]">
              {{ counselor.avatar }}
            </div>
            <div class="counselor-info">
              <div class="counselor-name">{{ counselor.name }}</div>
              <div class="counselor-status">
                <span class="status-dot" :style="{ background: counselor.isOnline ? '#4CAF50' : '#FFA500' }"></span>
                <span>{{ counselor.isOnline ? '상담가능' : '상담중' }}</span>
              </div>
              <div class="counselor-specialty">{{ counselor.specialty }}</div>
            </div>
          </div>

          <div class="counselor-tags">
            <span v-for="tag in counselor.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <p class="counselor-desc">{{ counselor.description }}</p>

          <div class="counselor-footer">
            <div class="rating">
              <div class="rating-stars">
                <span v-for="n in 5" :key="n" class="star">⭐</span>
              </div>
              <div class="rating-info">
                <span class="rating-score">{{ counselor.rating }}</span>
                <span class="rating-count">(리뷰 {{ counselor.reviewCount.toLocaleString() }})</span>
              </div>
            </div>
            <div class="counselor-pricing">
              <div class="price">{{ counselor.price.toLocaleString() }}<span class="price-unit">원/분</span></div>
              <div v-if="counselor.discount" class="discount-badge">{{ counselor.discount }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <NuxtLink to="/" class="nav-item active">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">홈</span>
      </NuxtLink>
      <NuxtLink to="/ai-fortune" class="nav-item">
        <span class="nav-icon">🤖</span>
        <span class="nav-label">AI운세</span>
      </NuxtLink>
      <NuxtLink to="/events" class="nav-item">
        <span class="nav-icon">🎁</span>
        <span class="nav-label">이벤트</span>
      </NuxtLink>
      <NuxtLink to="/favorites" class="nav-item">
        <span class="nav-icon">⭐</span>
        <span class="nav-label">즐겨찾기</span>
      </NuxtLink>
      <NuxtLink to="/mypage" class="nav-item">
        <span class="nav-icon">👤</span>
        <span class="nav-label">마이</span>
      </NuxtLink>
    </nav>

    <!-- 플로팅 버튼 -->
    <button class="floating-button" @click="openChat">💬</button>
  </div>
</template>


definePageMeta({
  requiresAuth: false
})

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useHead, useRoute } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'

const { notifySuccess, notifyInfo } = useNotify()

// SEO 및 메타 데이터 설정
useHead({
  title: '사주라인 - 당신의 운명을 밝히는 빛',
  meta: [
    { name: 'description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:title', content: '사주라인 - 당신의 운명을 밝히는 빛' },
    { property: 'og:description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:image', content: '/images/og-image.jpg' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: false
})

// 사용자 포인트
const userPoints = ref(1200)

// 실시간 지표
const liveStats = ref({
  consulting: 1234,
  satisfaction: 98.3,
  totalConsultations: '50M'
})

// 오늘 날짜
const todayDate = computed(() => {
  const today = new Date()
  return `${today.getFullYear()}. ${(today.getMonth() + 1).toString().padStart(2, '0')}. ${today.getDate().toString().padStart(2, '0')}`
})

// 오늘의 운세
const todayFortune = ref({
  content: '오늘은 새로운 기회가 찾아올 수 있는 날입니다. 평소보다 적극적인 자세로 임한다면 좋은 결과를 얻을 수 있을 것입니다. 특히 오후 3시경에는 중요한 연락이 올 수 있으니 주의 깊게 살펴보세요.',
  meters: [
    { label: '연애운', value: 85 },
    { label: '재물운', value: 70 },
    { label: '건강운', value: 90 }
  ]
})

// 카테고리 목록
const categories = ref([
  { name: '타로', path: '/categories/tarot', icon: '🔮' },
  { name: '사주', path: '/categories/saju', icon: '📅' },
  { name: '신점', path: '/categories/divine', icon: '✨' },
  { name: '연애운', path: '/categories/love', icon: '💕' },
  { name: '재물운', path: '/categories/money', icon: '💰' },
  { name: '직장운', path: '/categories/career', icon: '💼' }
])

// 필터 목록
const filters = ref(['전체', '🔥 HOT', '⭐ 베스트', '🆕 신규', '💝 재회전문', '💼 커리어'])
const activeFilter = ref(0)

// 상담사 목록
const counselors = ref([
  {
    id: 1,
    name: '명월 선생님',
    avatar: '🌙',
    isOnline: true,
    specialty: '타로 마스터 · 20년 경력',
    tags: ['🔮 타로', '💕 연애', '🔄 재회', '✨ 심리상담'],
    description: '"모든 인연에는 의미가 있습니다" 20년간 수만건의 상담을 통해 쌓은 통찰력으로 당신의 마음을 읽어드립니다. 특히 복잡한 연애 문제와 재회 상담을 전문으로 합니다.',
    rating: 4.9,
    reviewCount: 3456,
    price: 3900,
    discount: '첫상담 30% 할인'
  },
  {
    id: 2,
    name: '천기누설 선생님',
    avatar: '🔥',
    isOnline: true,
    specialty: '사주/신점 전문 · 30년 경력',
    tags: ['📅 사주', '✨ 신점', '💼 취업', '🏠 이사'],
    description: '정통 사주명리학과 신점을 통해 인생의 큰 그림을 그려드립니다. 취업, 이직, 사업 등 중요한 결정을 앞두고 계신다면 명확한 방향을 제시해드립니다.',
    rating: 4.8,
    reviewCount: 2892,
    price: 4500,
    discount: null
  },
  {
    id: 3,
    name: '별빛 선생님',
    avatar: '💫',
    isOnline: false,
    specialty: '신통력 · 15년 경력',
    tags: ['🌟 신통력', '💰 재물', '🍀 행운'],
    description: '타고난 영감과 신통력으로 막힌 운을 뚫어드립니다. 재물운, 사업운 상담에 특화되어 있으며 로또 당첨자를 다수 배출한 행운의 상담사입니다.',
    rating: 5.0,
    reviewCount: 1234,
    price: 5900,
    discount: '예약대기 5명'
  }
])

// 라우트 처리
const route = useRoute()

// 페이지 로드 시 처리
onMounted(() => {
  if (route.query.message === 'login_success') {
    notifySuccess('🎉 사주라인에 오신 것을 환영합니다!')
  } else if (route.query.message === 'social_login_success') {
    notifySuccess('🚀 간편하게 로그인되었습니다!')
  }

  // 실시간 통계 업데이트
  startLiveStatsUpdate()
})

// 메서드들
function setActiveFilter(index: number) {
  activeFilter.value = index
}

function startFreeTrial() {
  notifyInfo('🎉 첫 상담 무료체험을 시작합니다!')
  // TODO: 무료체험 로직 구현
}

function requestAIFortune() {
  notifyInfo('🤖 AI 운세를 준비 중입니다...')
  // TODO: AI 운세 요청 로직
}

function openChat() {
  notifyInfo('💬 채팅 상담을 시작합니다!')
  // TODO: 채팅 열기 로직
}

// 실시간 통계 업데이트
function startLiveStatsUpdate() {
  setInterval(() => {
    const variation = Math.floor(Math.random() * 10) - 5
    liveStats.value.consulting = Math.max(1200, liveStats.value.consulting + variation)
  }, 3000)
}
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';

/* 추가 컴포넌트별 스타일이 필요한 경우 여기에 작성 */
</style>
