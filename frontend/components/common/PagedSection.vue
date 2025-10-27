<template>
  <div>
    <slot name="header"></slot>
    <div v-if="loading" class="empty-state text-center py-10 text-white/60">
      <div class="loading-spinner mx-auto"></div>
    </div>
    <div v-else-if="error" class="empty-state text-center py-10 text-red-300">{{ error }}</div>
    <div v-else>
      <div v-if="items.length === 0" class="empty-state text-center py-10 text-white/40">
        <div class="text-5xl mb-3">📭</div>
        <div class="text-sm">{{ emptyText }}</div>
      </div>
      <div v-else>
        <slot :items="items"></slot>
        <div class="mt-3 flex items-center justify-between text-sm text-white/70">
          <button class="px-3 py-2 rounded-lg bg-white/5 border border-white/10 disabled:opacity-30" :disabled="page<=1" @click="$emit('update:page', page-1)">이전</button>
          <div>{{ page }} / {{ totalPages }}</div>
          <button class="px-3 py-2 rounded-lg bg-white/5 border border-white/10 disabled:opacity-30" :disabled="page>=totalPages" @click="$emit('update:page', page+1)">다음</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props<T=any> {
  items: T[]
  page: number
  totalPages: number
  loading?: boolean
  error?: string
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  items: () => [],
  page: 1,
  totalPages: 1,
  loading: false,
  error: '',
  emptyText: '표시할 항목이 없습니다'
})

defineEmits<{
  (e: 'update:page', value: number): void
}>()
</script>

<style scoped>
</style>


