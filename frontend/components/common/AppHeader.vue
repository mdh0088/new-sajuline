<template>
  <header class="header" style="background: rgba(10, 10, 15, 0.95) !important; backdrop-filter: blur(10px) !important; position: sticky !important; top: 0 !important; z-index: 9999 !important;">
    <div class="header-top">
      <!-- 왼쪽: 뒤로가기 버튼 (서브페이지일 때) 또는 로고 (메인페이지일 때) -->
      <div v-if="isSubPage">
        <button class="icon-btn" @click="goBack">
          ←
        </button>
      </div>
      <NuxtLink v-else to="/" class="logo">사주라인</NuxtLink>

      <!-- 중앙: 페이지 제목 (서브페이지일 때만) -->
      <div v-if="isSubPage" class="page-title-center">{{ pageTitle }}</div>

      <!-- 오른쪽 액션 영역 -->
      <div class="header-actions">
        <!-- 포인트 표시 -->
        <div v-if="isAuthenticated" class="coin-balance" @click="$router.push('/point')">
          <span>💰</span>
          <span>{{ userPoints }}P</span>
        </div>

        <!-- 로그인/로그아웃 버튼 -->
        <button
          v-if="!isAuthenticated"
          class="auth-button login-button"
          @click="$router.push('/login')"
        >
          로그인
        </button>
        <button
          v-else
          class="auth-button logout-button"
          @click="handleLogout"
        >
          로그아웃
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useAuthQueries } from '~/composables/api/useAuthQueries'
import { useRoute, useRouter } from 'vue-router'

const { isAuthenticated, isUser, isCounselor, logout, setRole } = useAuth()
const { useWhoAmI } = useAuthQueries()
const { refetch } = useWhoAmI()
const route = useRoute()
const router = useRouter()

// 사용자 포인트 (임시 값)
const userPoints = ref(1200)

// 서브페이지 판단 로직
const isSubPage = computed(() => {
  const path = route.path
  // 메인페이지들 정의 (하단 네비게이션이 있는 페이지들)
  const mainPages = ['/', '/search', '/events', '/user/favorite']
  return !mainPages.includes(path)
})

// 페이지 제목 매핑
const pageTitleMap: Record<string, string> = {
  '/login': '로그인',
  '/user/mypage': '마이페이지',
  '/user/favorite': '즐겨찾기',
  '/user/pointlog': '포인트 내역',
  '/user/cs': '고객센터',
  '/user/reviews': '리뷰 관리',
  '/counselor/mypage': '상담사 마이페이지',
  '/point': '포인트 충전',
  '/categories': '카테고리',
  '/events': '이벤트',
}

const pageTitle = computed(() => {
  const path = route.path
  // 동적 라우트 처리 (예: /counselor/123)
  if (path.startsWith('/counselor/') && path !== '/counselor/mypage') {
    return '상담사 정보'
  }
  if (path.startsWith('/events/') && path !== '/events') {
    return '이벤트 상세'
  }
  return pageTitleMap[path] || '페이지'
})

onMounted(async () => {
  // 로그인 상태에서만 whoAmI 요청 (게스트는 호출하지 않음)
  if (!isAuthenticated.value) return
  try {
    const result = await refetch()
    if (result.data) {
      setRole(result.data.role)
    }
  } catch (_e) {
    // 무시 (토큰 만료 등 전역 인터셉터에서 처리)
  }
})

// 이벤트 핸들러
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const handleNotificationClick = () => {
  console.log('알림 버튼 클릭')
}

const handleMenuClick = () => {
  console.log('메뉴 버튼 클릭')
}

const handleUserClick = () => {
  console.log('유저 버튼 클릭')
}

const handleLogout = async () => {
  await logout()
}
</script>

<style scoped>
@import '~/assets/css/main-page.css';

.page-title-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

/* 로그인/로그아웃 버튼 스타일 */
.auth-button {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  white-space: nowrap;
}

.login-button {
  background: linear-gradient(135deg, #9333EA 0%, #7C3AED 100%);
  color: white;
}

.login-button:hover {
  background: linear-gradient(135deg, #7C3AED 0%, #6B21A8 100%);
  transform: translateY(-1px);
}

.logout-button {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.auth-button:active {
  transform: scale(0.98);
}

/* header-actions 내부 요소들 간격 조정 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>