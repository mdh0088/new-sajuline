<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl border-t border-white/10 px-5 py-3 z-50 pointer-events-auto">
    <div class="flex justify-around max-w-md mx-auto">
      <button 
        class="flex flex-col items-center gap-1 text-purple-400 transition-colors"
        @click="handleNavClick('home')"
      >
        <span class="text-xl">🏠</span>
        <span class="text-xs font-medium">홈</span>
      </button>
      <NuxtLink to="/fortune" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
        <span class="text-xl">🔮</span>
        <span class="text-xs font-medium">운세</span>
      </NuxtLink>
      <NuxtLink to="/chat" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
        <span class="text-xl">💬</span>
        <span class="text-xs font-medium">상담</span>
      </NuxtLink>
      <NuxtLink :to="mypagePath" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
        <span class="text-xl">👤</span>
        <span class="text-xs font-medium">마이페이지</span>
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'

const { isCounselor } = useAuth()
const mypagePath = computed(() => isCounselor.value ? '/counselor/mypage' : '/mypage')
// 네비게이션 클릭 처리
const handleNavClick = (tab: 'home' | 'fortune' | 'chat' | 'profile') => {
  if (tab === 'home') return navigateTo('/')
  if (tab === 'fortune') return navigateTo('/fortune')
  if (tab === 'chat') return navigateTo('/chat')
  if (tab === 'profile') return navigateTo(mypagePath.value)
}
</script>