<template>
  <section class="px-5 py-6">
    <div class="relative p-5 bg-gradient-to-br from-purple-600/10 to-purple-700/5 border border-purple-600/20 rounded-2xl overflow-hidden max-w-md mx-auto">
      <!-- 배경 장식 -->
      <div class="absolute top-0 right-0 text-8xl opacity-10 pointer-events-none">🔮</div>

      <div class="relative z-10">
        <!-- 헤더: 날짜 + 일주 (AC 2) -->
        <div class="flex justify-between items-center mb-4">
          <div class="flex items-center gap-2">
            <span class="text-purple-300 font-medium">
              {{ fortune.day_pillar.stem }}{{ fortune.day_pillar.branch }}일
            </span>
            <span v-if="fortune.sipsung" class="text-xs px-2 py-0.5 bg-purple-600/20 rounded-full text-purple-300">
              {{ fortune.sipsung }}
            </span>
          </div>
          <span class="text-sm text-white/60">{{ formattedDate }}</span>
        </div>

        <!-- 운세 점수 및 행운 요소 -->
        <div v-if="fortune.luck_score || fortune.lucky_color || fortune.lucky_number" class="flex flex-wrap gap-3 mb-4">
          <!-- 운세 점수 (M2: 접근성 개선) -->
          <div
            v-if="fortune.luck_score"
            class="flex items-center gap-1"
            role="img"
            :aria-label="luckScoreLabel"
          >
            <span v-for="i in 5" :key="i" class="text-base" aria-hidden="true">
              {{ i <= fortune.luck_score ? '⭐' : '☆' }}
            </span>
          </div>
          <!-- 행운의 색 -->
          <div v-if="fortune.lucky_color" class="flex items-center gap-1 text-sm text-white/80">
            <span>🎨</span>
            <span>{{ fortune.lucky_color }}</span>
          </div>
          <!-- 행운의 숫자 -->
          <div v-if="fortune.lucky_number" class="flex items-center gap-1 text-sm text-white/80">
            <span>🔢</span>
            <span>{{ fortune.lucky_number }}</span>
          </div>
        </div>

        <!-- 총운 섹션 (AC 1) -->
        <FortuneSection
          title="총운"
          icon="🔮"
          :content="fortune.overall"
          :expanded="true"
        />

        <!-- 세부 운세 그리드 (AC 1) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
          <FortuneSection
            title="애정운"
            icon="💕"
            :content="fortune.love"
          />
          <FortuneSection
            title="직장운"
            icon="💼"
            :content="fortune.career"
          />
          <FortuneSection
            title="건강운"
            icon="🏃"
            :content="fortune.health"
          />
          <FortuneSection
            title="재물운"
            icon="💰"
            :content="fortune.wealth"
          />
        </div>

        <!-- 키워드 태그 -->
        <div v-if="fortune.keywords && fortune.keywords.length > 0" class="mt-4 pt-4 border-t border-white/10">
          <div class="flex flex-wrap gap-2">
            <span
              v-for="keyword in fortune.keywords"
              :key="keyword"
              class="px-3 py-1 text-xs bg-purple-600/20 text-purple-300 rounded-full"
            >
              #{{ keyword }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { IFortune } from '~/types/fortune'
import FortuneSection from '~/components/fortune/FortuneSection.vue'
import { formatKoreanDate } from '~/utils/dateFormat'

// Props 정의 (AC 1)
interface Props {
  fortune: IFortune
}

const props = defineProps<Props>()

// 날짜 포맷팅 (AC 2) - M3: 유틸리티 함수 사용
const formattedDate = computed(() => {
  if (!props.fortune.date) return ''
  return formatKoreanDate(props.fortune.date)
})

// M2: 접근성 - 별점 aria-label
const luckScoreLabel = computed(() => {
  if (!props.fortune.luck_score) return ''
  return `운세 점수 ${props.fortune.luck_score}점 (5점 만점)`
})
</script>
