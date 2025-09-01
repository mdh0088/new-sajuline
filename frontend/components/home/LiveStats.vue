<template>
  <section class="px-5 py-5 bg-white/2 border-y border-white/10">
    <div class="flex justify-around max-w-md mx-auto">
      <div 
        v-for="(stat, index) in stats" 
        :key="index"
        class="text-center"
      >
        <div class="text-2xl font-bold text-purple-300 mb-1">{{ stat.number }}</div>
        <div class="text-xs text-white/60">{{ stat.label }}</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Props 정의
interface Props {
  stats?: Array<{
    number: string
    label: string
  }>
}

const props = withDefaults(defineProps<Props>(), {
  stats: () => [
    { number: '15,234', label: '누적 상담' },
    { number: '4.9', label: '평균 평점' },
    { number: '89', label: '실시간 접속자' }
  ]
})
</script>