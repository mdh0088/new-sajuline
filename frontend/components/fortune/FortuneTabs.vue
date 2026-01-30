<template>
  <div
    role="tablist"
    class="flex gap-2 px-5 pb-4"
    aria-label="운세 기간 선택"
  >
    <button
      v-for="(tab, index) in FORTUNE_TABS"
      :key="tab.value"
      :ref="(el) => setTabRef(index, el as HTMLButtonElement | null)"
      role="tab"
      :id="`fortune-tab-${tab.value}`"
      :aria-selected="modelValue === tab.value"
      :aria-controls="`fortune-panel-${tab.value}`"
      :tabindex="modelValue === tab.value ? 0 : -1"
      :class="[
        'px-4 py-2 rounded-full text-sm font-medium transition-all duration-200',
        'min-w-[56px] min-h-[44px]',
        'focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 focus:ring-offset-slate-950',
        modelValue === tab.value
          ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
          : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80'
      ]"
      @click="handleTabClick(tab.value)"
      @keydown="(e) => handleKeydown(e, index)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { FortuneType } from '~/types/fortune'
import { FORTUNE_TABS } from '~/types/fortune'

// Props 정의 (AC 1)
interface Props {
  modelValue: FortuneType
}

const props = defineProps<Props>()

// Emits 정의
const emit = defineEmits<{
  'update:modelValue': [value: FortuneType]
}>()

// 탭 버튼 refs - 함수형 ref로 순서 보장 (Code Review 수정)
const tabRefs: (HTMLButtonElement | null)[] = []

const setTabRef = (index: number, el: HTMLButtonElement | null) => {
  tabRefs[index] = el
}

// 탭 클릭 핸들러
const handleTabClick = (value: FortuneType) => {
  emit('update:modelValue', value)
}

// 키보드 네비게이션 핸들러 (AC 5: NFR-A2, NFR-A3)
const handleKeydown = (e: KeyboardEvent, index: number) => {
  let newIndex = index

  if (e.key === 'ArrowRight') {
    // 오른쪽 화살표: 다음 탭으로 이동
    newIndex = (index + 1) % FORTUNE_TABS.length
  } else if (e.key === 'ArrowLeft') {
    // 왼쪽 화살표: 이전 탭으로 이동
    newIndex = (index - 1 + FORTUNE_TABS.length) % FORTUNE_TABS.length
  } else if (e.key === 'Home') {
    // Home: 첫 번째 탭으로 이동
    newIndex = 0
  } else if (e.key === 'End') {
    // End: 마지막 탭으로 이동
    newIndex = FORTUNE_TABS.length - 1
  } else if (e.key === 'Enter' || e.key === ' ') {
    // Enter/Space: 현재 탭 선택
    e.preventDefault()
    const tab = FORTUNE_TABS[index]
    if (tab) {
      emit('update:modelValue', tab.value)
    }
    return
  } else {
    return
  }

  e.preventDefault()
  const newTab = FORTUNE_TABS[newIndex]
  if (newTab) {
    emit('update:modelValue', newTab.value)
  }

  // 포커스 이동 - 인덱스 기반으로 정확한 버튼 접근
  const buttonRef = tabRefs[newIndex]
  if (buttonRef) {
    buttonRef.focus()
  }
}
</script>
