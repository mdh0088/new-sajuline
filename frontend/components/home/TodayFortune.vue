<template>
  <section class="px-5 py-6">
    <div class="relative p-5 bg-gradient-to-br from-purple-600/10 to-purple-700/5 border border-purple-600/20 rounded-2xl overflow-hidden max-w-md mx-auto">
      <div class="absolute top-0 right-0 text-8xl opacity-10 pointer-events-none">✨</div>
      
      <div class="relative z-10">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold flex items-center gap-2">
            <span>🔮</span>
            오늘의 운세
          </h2>
          <span class="text-sm text-white/60">{{ todayDate }}</span>
        </div>
        
        <p class="text-sm text-white/80 leading-relaxed mb-4">
          {{ fortune.content }}
        </p>
        
        <div class="grid grid-cols-3 gap-4">
          <div 
            v-for="(meter, index) in fortune.meters" 
            :key="index"
            class="text-center"
          >
            <div class="text-xs text-white/60 mb-2">{{ meter.label }}</div>
            <div class="h-1 bg-white/10 rounded-full overflow-hidden mb-1">
              <div 
                class="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-1000"
                :style="{ width: `${meter.value}%` }"
              ></div>
            </div>
            <div class="text-sm font-semibold text-purple-300">{{ meter.value }}%</div>
          </div>
        </div>
        
        <!-- AI 상세 분석 버튼 -->
        <div class="mt-4 pt-4 border-t border-white/10">
          <button
            @click="requestAIAnalysis"
            class="w-full py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-600/30 rounded-xl font-medium text-sm transition-all duration-300"
          >
            AI 상세 분석 받기 🤖
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Props 정의
interface FortuneMeter {
  label: string
  value: number
}

interface FortuneData {
  content: string
  meters: FortuneMeter[]
}

interface Props {
  fortune?: FortuneData
}

const props = withDefaults(defineProps<Props>(), {
  fortune: () => ({
    content: '오늘은 중요한 결정을 내리기에 좋은 날입니다. 자신감을 갖고 한 걸음 나아가 보세요.',
    meters: [
      { label: '종합', value: 85 },
      { label: '연애', value: 72 },
      { label: '재물', value: 91 }
    ]
  })
})

// Emits 정의
const emit = defineEmits<{
  aiAnalysisRequest: []
}>()

// 오늘 날짜
const todayDate = computed(() => {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
})

// 이벤트 핸들러
const requestAIAnalysis = () => {
  console.log('AI 상세 분석 요청')
  emit('aiAnalysisRequest')
}
</script>