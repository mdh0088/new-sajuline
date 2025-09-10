<template>
  <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
    <div class="flex justify-between items-center px-5 py-4 h-[60px]">
      <div class="flex items-center">
        <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 via-purple-300 to-purple-500 bg-clip-text text-transparent">
          사주라인
        </h1>
      </div>
      
      <div class="flex items-center gap-2">
        <!-- 역할 배지 -->
        <div v-if="isAuthenticated" class="px-3 py-1 rounded-full text-xs font-semibold border" :class="roleBadgeClass" aria-live="polite">
          {{ roleLabel }}
        </div>

        <!-- 로그인 버튼 (비로그인 시) -->
        <NuxtLink 
          v-if="!isAuthenticated"
          to="/login"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-xl transition-all duration-300 active:scale-95"
        >
          로그인
        </NuxtLink>

        <!-- 로그아웃 버튼 (로그인 시) -->
        <button 
          v-else
          class="px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm transition-all duration-300 active:scale-95"
          @click="handleLogout"
        >
          로그아웃
        </button>

        <!-- 알림 버튼 -->
        <button 
          class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95"
          @click="handleNotificationClick"
        >
          🔔
        </button>
        
        <!-- 메뉴 버튼 -->
        <button 
          class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95"
          @click="handleMenuClick"
        >
          ☰
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useAuthQueries } from '~/composables/api/useAuthQueries'

const { isAuthenticated, isUser, isCounselor, logout, setRole } = useAuth()
const { useWhoAmI } = useAuthQueries()
const { refetch } = useWhoAmI()

const roleLabel = computed(() => isCounselor.value ? '상담사' : '유저')
const roleBadgeClass = computed(() => isCounselor.value 
  ? 'bg-purple-600/20 border-purple-500/40 text-purple-200'
  : 'bg-teal-600/20 border-teal-500/40 text-teal-200'
)

onMounted(async () => {
  // 초기 렌더 시 서버의 토큰 정보를 우선 반영 (규격: API 컴포저블 사용)
  try {
    const result = await refetch()
    if (result.data) {
      setRole(result.data.role)
    }
  } catch (e) {
    // 무시 (비로그인 등)
  }
})

// 이벤트 핸들러
const handleNotificationClick = () => {
  console.log('알림 버튼 클릭')
}

const handleMenuClick = () => {
  console.log('메뉴 버튼 클릭')
}

const handleLogout = async () => {
  await logout()
}
</script>

<style scoped>
.active\:scale-95:active {
  transform: scale(0.95);
}
</style>