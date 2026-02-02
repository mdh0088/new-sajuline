<template>
  <div
    class="relative p-6 border rounded-2xl overflow-hidden max-w-md mx-auto text-center"
    :class="containerClass"
    role="alert"
    aria-live="assertive"
  >
    <!-- 아이콘 (Task 2.3) -->
    <div class="text-4xl mb-4">{{ errorConfig.icon }}</div>

    <!-- 타이틀 -->
    <h2 class="text-lg font-bold text-white mb-2">{{ errorConfig.title }}</h2>

    <!-- 설명 (Task 2.4) -->
    <p class="text-sm text-white/70 mb-6 leading-relaxed">
      {{ errorConfig.description }}
    </p>

    <!-- 액션 버튼 -->
    <NuxtLink
      v-if="errorConfig.actionLink"
      :to="errorConfig.actionLink"
      class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors duration-300"
    >
      {{ errorConfig.actionLabel }}
    </NuxtLink>
    <button
      v-else
      type="button"
      class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors duration-300"
      @click="emit('retry')"
    >
      {{ errorConfig.actionLabel }}
    </button>

    <!-- 네트워크 오류 시 오프라인 아이콘 표시 (Task 2.5) - 접근성 개선: aria-live 영역 내부 -->
    <p v-if="errorType === 'network'" class="mt-4 text-white/50 text-sm flex items-center justify-center gap-2">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
      </svg>
      <span>오프라인 상태</span>
    </p>
  </div>
</template>

<script setup lang="ts">
import type { FortuneErrorType } from '~/types/fortune'

interface Props {
  /** 에러 메시지 */
  message?: string | null
  /** 에러 유형 (AC 3, 4, 5) */
  errorType?: FortuneErrorType
}

const props = withDefaults(defineProps<Props>(), {
  message: null,
  errorType: 'general'
})

// Emits 정의
const emit = defineEmits<{
  retry: []
}>()

// 에러 타입별 설정 (Task 2.3, 2.4)
interface ErrorConfig {
  icon: string
  title: string
  description: string
  actionLabel: string
  actionLink: string | null
}

const errorConfig = computed<ErrorConfig>(() => {
  switch (props.errorType) {
    case 'saju_required':
      return {
        icon: '🎂',
        title: '사주 정보가 필요해요',
        description: '운세를 확인하려면 먼저 생년월일시 정보를 등록해주세요.',
        actionLabel: '사주 정보 등록하기',
        actionLink: '/user/edit'
      }
    case 'network':
      return {
        icon: '📡',
        title: '네트워크 오류',
        description: '네트워크 연결을 확인해주세요.',
        actionLabel: '다시 시도',
        actionLink: null
      }
    default:
      return {
        icon: '😢',
        title: '운세를 불러올 수 없어요',
        description: props.message || '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        actionLabel: '다시 시도',
        actionLink: null
      }
  }
})

// 컨테이너 스타일 분기
const containerClass = computed(() => {
  if (props.errorType === 'network') {
    // 네트워크 오류: 노란/주황색 톤
    return 'bg-gradient-to-br from-amber-600/10 to-orange-700/5 border-amber-600/20'
  }
  // 기본: 빨간색 톤
  return 'bg-gradient-to-br from-red-600/10 to-red-700/5 border-red-600/20'
})
</script>
