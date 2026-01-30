<template>
  <div class="relative p-6 bg-gradient-to-br from-red-600/10 to-red-700/5 border border-red-600/20 rounded-2xl overflow-hidden max-w-md mx-auto text-center">
    <!-- 사주 정보 미등록 시 -->
    <template v-if="isSajuRequired">
      <div class="text-4xl mb-4">🎂</div>
      <h2 class="text-lg font-bold text-white mb-2">사주 정보가 필요해요</h2>
      <p class="text-sm text-white/70 mb-6 leading-relaxed">
        운세를 확인하려면 먼저 생년월일시 정보를 등록해주세요.
      </p>
      <NuxtLink
        to="/user/edit"
        class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors duration-300"
      >
        사주 정보 등록하기
      </NuxtLink>
    </template>

    <!-- 일반 에러 시 -->
    <template v-else>
      <div class="text-4xl mb-4">😢</div>
      <h2 class="text-lg font-bold text-white mb-2">운세를 불러올 수 없어요</h2>
      <p class="text-sm text-white/70 mb-6 leading-relaxed">
        {{ message || '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' }}
      </p>
      <button
        type="button"
        class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors duration-300"
        @click="emit('retry')"
      >
        다시 시도
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
// Props 정의
interface Props {
  /** 에러 메시지 */
  message?: string | null
  /** 사주 정보 미등록 여부 */
  isSajuRequired?: boolean
}

withDefaults(defineProps<Props>(), {
  message: null,
  isSajuRequired: false
})

// Emits 정의
const emit = defineEmits<{
  retry: []
}>()
</script>
