<template>
  <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
    <div class="flex justify-between items-center px-5 py-4 h-[60px]">
      <div class="flex items-center">
        <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 via-purple-300 to-purple-500 bg-clip-text text-transparent">
          사주라인
        </h1>
      </div>
      
      <div class="flex items-center gap-2">
        <!-- 로그인 버튼 -->
        <NuxtLink 
          to="/login"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-xl transition-all duration-300 active:scale-95"
        >
          로그인
        </NuxtLink>
        
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
// 이벤트 핸들러
const handleNotificationClick = () => {
  console.log('알림 버튼 클릭')
}

const handleMenuClick = () => {
  console.log('메뉴 버튼 클릭')
}
</script>

<style scoped>
.active\:scale-95:active {
  transform: scale(0.95);
}
</style>