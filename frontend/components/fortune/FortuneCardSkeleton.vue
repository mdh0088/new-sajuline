<template>
  <div class="relative p-5 bg-gradient-to-br from-purple-600/10 to-purple-700/5 border border-purple-600/20 rounded-2xl overflow-hidden max-w-md mx-auto animate-pulse">
    <!-- 배경 장식 -->
    <div class="absolute top-0 right-0 text-8xl opacity-5 pointer-events-none">🔮</div>

    <div class="relative z-10">
      <!-- 헤더 스켈레톤 -->
      <div class="flex justify-between items-center mb-4">
        <div class="h-5 w-24 bg-white/10 rounded" />
        <div class="h-4 w-32 bg-white/10 rounded" />
      </div>

      <!-- 점수/행운 요소 스켈레톤 -->
      <div class="flex gap-3 mb-4">
        <div class="h-5 w-20 bg-white/10 rounded" />
        <div class="h-5 w-16 bg-white/10 rounded" />
        <div class="h-5 w-12 bg-white/10 rounded" />
      </div>

      <!-- 총운 스켈레톤 -->
      <div class="p-4 bg-white/5 rounded-xl border border-white/10 mb-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="h-6 w-6 bg-white/10 rounded" />
          <div class="h-5 w-12 bg-white/10 rounded" />
        </div>
        <div class="space-y-2">
          <div class="h-4 w-full bg-white/10 rounded" />
          <div class="h-4 w-4/5 bg-white/10 rounded" />
          <div class="h-4 w-3/5 bg-white/10 rounded" />
        </div>
      </div>

      <!-- 세부 운세 그리드 스켈레톤 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="i in 4" :key="i" class="p-4 bg-white/5 rounded-xl border border-white/10">
          <div class="flex items-center gap-2 mb-3">
            <div class="h-5 w-5 bg-white/10 rounded" />
            <div class="h-4 w-14 bg-white/10 rounded" />
          </div>
          <div class="space-y-2">
            <div class="h-3 w-full bg-white/10 rounded" />
            <div class="h-3 w-4/5 bg-white/10 rounded" />
          </div>
        </div>
      </div>

      <!-- 키워드 스켈레톤 -->
      <div class="mt-4 pt-4 border-t border-white/10">
        <div class="flex gap-2">
          <div class="h-6 w-16 bg-white/10 rounded-full" />
          <div class="h-6 w-20 bg-white/10 rounded-full" />
          <div class="h-6 w-14 bg-white/10 rounded-full" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 로딩 스켈레톤 컴포넌트 - FortuneCard 형태 유지
</script>
