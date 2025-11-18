<template>
  <nav
    v-if="!shouldHide"
    class="bottom-nav"
    :class="{ 'nav-hidden': !isNavVisible }"
    style="background: rgba(10, 10, 15, 0.95) !important; backdrop-filter: blur(10px) !important; position: sticky !important; bottom: 0 !important; z-index: 9999 !important; margin-top: auto !important;"
  >
    <NuxtLink to="/" :class="['nav-item', { active: $route.path === '/' }]">
      <span class="nav-icon">🏠</span>
      <span class="nav-label">홈</span>
    </NuxtLink>

    <NuxtLink to="/user/favorite" :class="['nav-item', { active: $route.path === '/user/favorite' }]">
      <span class="nav-icon">⭐</span>
      <span class="nav-label">즐겨찾기</span>
    </NuxtLink>

    <NuxtLink to="/search" :class="['nav-item', { active: $route.path === '/search' }]">
      <span class="nav-icon">🔍</span>
      <span class="nav-label">검색</span>
    </NuxtLink>

    <NuxtLink to="/point" :class="['nav-item', { active: $route.path === '/point' }]">
      <span class="nav-icon">💰</span>
      <span class="nav-label">충전</span>
    </NuxtLink>

    <NuxtLink :to="mypagePath" :class="['nav-item', { active: $route.path.includes('/mypage') }]">
      <span class="nav-icon">👤</span>
      <span class="nav-label">마이</span>
    </NuxtLink>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '~/composables/auth/useAuth'

const route = useRoute()
const { isCounselor } = useAuth()
const mypagePath = computed(() => isCounselor.value ? '/counselor/mypage' : '/user/mypage')

// 페이지 메타에서 hideBottomNav 설정 확인
const shouldHide = computed(() => route.meta?.hideBottomNav === true)

// 스크롤 감지를 위한 상태
const isNavVisible = ref(true)
let lastScrollY = 0
let scrollTimeout: NodeJS.Timeout | null = null

// 스크롤 이벤트 핸들러
const handleScroll = () => {
  const currentScrollY = window.scrollY

  // 스크롤 방향 감지
  if (currentScrollY > lastScrollY && currentScrollY > 100) {
    // 아래로 스크롤 중이고 100px 이상 스크롤된 경우 숨김
    isNavVisible.value = false
  } else {
    // 위로 스크롤 중이거나 최상단 근처인 경우 표시
    isNavVisible.value = true
  }

  lastScrollY = currentScrollY

  // 스크롤이 멈추면 네비게이션 다시 표시
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
  scrollTimeout = setTimeout(() => {
    isNavVisible.value = true
  }, 1000) // 1초 동안 스크롤이 없으면 다시 표시
}

// 컴포넌트 마운트 시 스크롤 이벤트 리스너 추가
onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
})

// 네비게이션 클릭 처리
const handleNavClick = (tab: 'home' | 'fortune' | 'chat' | 'profile') => {
  if (tab === 'home') return navigateTo('/')
  if (tab === 'fortune') {
    // TODO: 운세 페이지 구현 후 라우트 변경
    return
  }
  if (tab === 'chat') {
    // TODO: 상담 페이지 구현 후 라우트 변경
    return
  }
  if (tab === 'profile') return navigateTo(mypagePath.value)
}
</script>

<style scoped>
@import '~/assets/css/main-page.css';
</style>