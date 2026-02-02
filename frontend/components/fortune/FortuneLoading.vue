<template>
  <div class="text-center py-8">
    <!-- 로딩 인디케이터 (Task 1.5: pulse + spin 조합) -->
    <div class="relative mx-auto w-16 h-16 mb-4">
      <!-- 배경 링 -->
      <div class="absolute inset-0 rounded-full border-4 border-purple-600/20" />
      <!-- 회전 링 -->
      <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-600 animate-spin" />
      <!-- 중앙 아이콘 -->
      <div class="absolute inset-2 flex items-center justify-center text-2xl animate-pulse">
        🔮
      </div>
    </div>

    <!-- 로딩 메시지 (AC 1, AC 2) -->
    <p
      class="text-white/80 mb-6"
      role="status"
      aria-live="polite"
    >
      {{ loadingMessage }}
    </p>

    <!-- 스켈레톤 UI (Task 1.6) -->
    <FortuneCardSkeleton />
  </div>
</template>

<script setup lang="ts">
import FortuneCardSkeleton from './FortuneCardSkeleton.vue'

// Task 1.2: Props 정의
interface Props {
  /** 3초 이상 로딩 상태 여부 (AC 2) */
  isExtendedLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isExtendedLoading: false
})

// Task 1.3, 1.4: 로딩 메시지 분기
const loadingMessage = computed(() => {
  return props.isExtendedLoading
    ? 'AI가 사주를 분석하고 있어요. 잠시만 기다려주세요'
    : '운세를 분석 중입니다...'
})
</script>
