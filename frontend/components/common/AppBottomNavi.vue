<template>
  <nav v-if="!shouldHide" class="bottom-nav" style="background: rgba(10, 10, 15, 0.95) !important; backdrop-filter: blur(10px) !important; position: sticky !important; bottom: 0 !important; z-index: 9999 !important; margin-top: auto !important;">
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '~/composables/auth/useAuth'

const route = useRoute()
const { isCounselor } = useAuth()
const mypagePath = computed(() => isCounselor.value ? '/counselor/mypage' : '/user/mypage')

// 페이지 메타에서 hideBottomNav 설정 확인
const shouldHide = computed(() => route.meta?.hideBottomNav === true)
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