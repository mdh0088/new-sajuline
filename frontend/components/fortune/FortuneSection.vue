<template>
  <div
    class="p-4 bg-white/5 rounded-xl border border-white/10 transition-all duration-300"
    :class="{ 'cursor-pointer hover:bg-white/10': collapsible }"
    @click="toggleExpanded"
  >
    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-lg">{{ icon }}</span>
        <h3 class="font-medium text-white">{{ title }}</h3>
      </div>
      <button
        v-if="collapsible"
        type="button"
        class="p-2 -mr-2 min-w-[44px] min-h-[44px] flex items-center justify-center text-white/60 hover:text-white transition-colors"
        :aria-expanded="isExpanded"
        :aria-label="isExpanded ? `${title} 섹션 접기` : `${title} 섹션 펼치기`"
      >
        <svg
          class="w-5 h-5 transition-transform duration-300"
          :class="{ 'rotate-180': isExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- 콘텐츠 -->
    <div
      v-show="isExpanded || !collapsible"
      class="mt-3 text-sm text-white/80 leading-relaxed"
    >
      {{ content }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Props 정의
interface Props {
  /** 섹션 제목 */
  title: string
  /** 섹션 아이콘 (이모지) */
  icon: string
  /** 섹션 콘텐츠 */
  content: string
  /** 확장/축소 가능 여부 (기본: true) */
  collapsible?: boolean
  /** 초기 확장 상태 (기본: false) */
  expanded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsible: true,
  expanded: false
})

// 확장 상태 관리
const isExpanded = ref(props.expanded)

// expanded prop 변경 시 동기화
watch(() => props.expanded, (newValue) => {
  isExpanded.value = newValue
})

// 확장/축소 토글
const toggleExpanded = () => {
  if (props.collapsible) {
    isExpanded.value = !isExpanded.value
  }
}
</script>
