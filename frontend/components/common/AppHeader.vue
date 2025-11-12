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

      <!-- 오른쪽 액션 영역 -->
      <div class="header-actions">
        <!-- 포인트 표시 -->
        <div v-if="isAuthenticated" class="coin-balance" @click="$router.push('/point')">
          <span>💰</span>
          <span>{{ formattedUserPoints }}P</span>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useAuthQueries } from '~/composables/api/useAuthQueries'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useRoute, useRouter } from 'vue-router'

const { isAuthenticated, isUser, isCounselor, logout, setRole } = useAuth()
const { useWhoAmI } = useAuthQueries()
const { useUserMypage } = useUserQueries()
const { refetch } = useWhoAmI()
const route = useRoute()
const router = useRouter()

// ✅ Computed를 명시적으로 생성하여 Vue 반응성 보장
const isAuthenticatedComputed = computed(() => isAuthenticated.value)

// 마이페이지 데이터 조회 (포인트 포함)
// ✅ enabled 옵션에 computed 전달 → Vue Query가 반응성 감지
const { data: mypageData, refetch: refetchMypage } = useUserMypage({
  enabled: isAuthenticatedComputed
})

// 사용자 포인트
const userPoints = computed(() => mypageData.value?.current_points ?? 0)

// 포인트 천 단위 구분자 포맷팅
const formattedUserPoints = computed(() => {
  return userPoints.value.toLocaleString('ko-KR')
})

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

// ✅ isAuthenticated 변경 감지 → 로그인 시 데이터 refetch
watch(isAuthenticated, async (newValue, oldValue) => {
  // false → true로 변경될 때만 실행 (로그인 시)
  if (newValue && !oldValue) {
    console.log('✅ [AppHeader] User logged in, refetching data...')
    try {
      // whoAmI refetch
      const result = await refetch()
      if (result.data) {
        setRole(result.data.role)
      }

      // mypage refetch
      await refetchMypage()
      console.log('✅ [AppHeader] Data refreshed successfully')
    } catch (error) {
      console.error('❌ [AppHeader] Failed to refresh data:', error)
      await logout()
    }
  }
})

onMounted(async () => {
  // 초기 마운트 시에만 실행 (로그인 상태에서만 whoAmI 요청)
  if (!isAuthenticated.value) return
  try {
    const result = await refetch()
    if (result.data) {
      setRole(result.data.role)
    }
  } catch (error) {
    // API 호출 실패 시 명시적 로그아웃 (토큰 만료 등)
    console.error('❌ 인증 확인 실패 - 로그아웃 처리:', error)
    await logout()
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