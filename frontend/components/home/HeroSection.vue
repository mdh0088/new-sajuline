<template>
  <section class="relative px-5 py-8 overflow-hidden">
    <!-- 배경 애니메이션 -->
    <div class="absolute inset-0 bg-gradient-to-b from-purple-600/30 via-transparent to-transparent"></div>
    <div class="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
      <div class="absolute top-10 right-10 text-8xl animate-pulse">✨</div>
      <div class="absolute bottom-20 left-10 text-6xl animate-bounce">🌟</div>
    </div>
    
    <div class="relative z-10 text-center">
      <!-- 서비스 배지 -->
      <div class="inline-flex items-center gap-1.5 px-4 py-1.5 bg-purple-600/10 border border-purple-600/30 rounded-full text-xs text-purple-300 mb-4 font-medium">
        <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        AI × 전문가 하이브리드 상담
      </div>
      
      <!-- 메인 타이틀 -->
      <h1 class="text-3xl sm:text-4xl font-bold mb-3 leading-tight bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">
        당신의 운명을<br />밝히는 빛
      </h1>
      
      <!-- 서브 타이틀 -->
      <p class="text-base text-white/70 mb-6 leading-relaxed max-w-md mx-auto">
        AI 기술과 전문가의 지혜가 만나<br />새로운 사주 상담 경험을 제공합니다
      </p>
      
      <!-- CTA 버튼 -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto">
        <button
          @click="requestAIFortune"
          class="relative px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-full font-bold text-base shadow-lg shadow-purple-600/40 hover:shadow-purple-600/60 transition-all duration-300 active:scale-98 overflow-hidden group"
        >
          <span class="relative z-10">AI 운세 보기</span>
          <div class="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-active:opacity-100 transition-opacity duration-300"></div>
        </button>
        <button
          @click="requestExpertConsult"
          class="relative px-8 py-4 bg-white/10 border border-white/20 rounded-full font-bold text-base hover:bg-white/15 transition-all duration-300 active:scale-98"
        >
          전문가 상담 받기
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Emits 정의
const emit = defineEmits<{
  aiFortuneRequest: []
  expertConsultRequest: []
}>()

// 이벤트 핸들러
const requestAIFortune = () => {
  console.log('AI 운세 요청')
  emit('aiFortuneRequest')
}

const requestExpertConsult = () => {
  console.log('전문가 상담 요청')
  emit('expertConsultRequest')
}
</script>

<style scoped>
.active\:scale-98:active {
  transform: scale(0.98);
}
</style>