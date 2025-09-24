<template>
  <div
    class="counselor-card-compact"
    @click="handleClick"
  >
    <div :class="['counselor-avatar-small', stateClass]">
      <img v-if="imageUrl" :src="imageUrl" :alt="counselor.nickname" />
      <span v-else>🔮</span>
    </div>
    <div class="counselor-info-compact">
      <div class="counselor-main-info">
        <div class="counselor-left-info">
          <div class="counselor-name-small">{{ counselor.nickname }}</div>
          <div class="counselor-specialty-small">{{ specialtyLabel }}</div>
          <div class="counselor-tags-small">
            <span v-for="tag in tags.slice(0, 3)" :key="tag" class="tag-small">{{ tag }}</span>
          </div>
        </div>
        <div class="counselor-right-info">
          <div class="counselor-price-small">{{ (counselor.after_amount || 0).toLocaleString() }}원/분</div>
          <div class="counselor-rating-small">
            <span class="rating-stars-small">
              <span v-for="i in 5" :key="i">{{ i <= Math.round(counselor.rating_avg || 0) ? '⭐' : '☆' }}</span>
            </span>
            <span class="rating-score">{{ Number(counselor.rating_avg || 0).toFixed(1) }}</span>
          </div>
          <div class="counselor-experience">리뷰 {{ (counselor.review_count || 0).toLocaleString() }}</div>
        </div>
      </div>
      <div class="counselor-desc-small">{{ shortIntro }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRuntimeConfig } from 'nuxt/app'
import type { CounselorSearchItem } from '~/types/counselor/search'
import { useCdn } from '~/composables/utils/useCdn'

interface Props {
  // API 검색 결과 아이템 그대로 사용
  counselor: CounselorSearchItem
}

const props = defineProps<Props>()
const router = useRouter()
const { cdnUrl } = useCdn()

const specialtyMap: Record<string, string> = {
  TARO: '타로 마스터',
  SAJU: '사주 마스터',
  FORTUNE: '운세 마스터'
}

const specialtyLabel = computed(() => {
  const list = (props.counselor.specialty_types ?? []) as string[]
  const first = Array.isArray(list) ? list[0] : undefined
  if (!first) return ''
  return specialtyMap[first] ?? first
})

const tags = computed(() => {
  return (props.counselor.keywords || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
})

const shortIntro = computed(() => {
  const s = (props.counselor.introduction_short || '').trim()
  if (s.length <= 32) return s
  return s.slice(0, 32) + '...'
})

const imageUrl = computed(() => {
  const raw = (props.counselor.profile_image_url || '').trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return cdnUrl(raw)
  return cdnUrl('cs', raw)
})

const stateClass = computed(() => {
  // 1 대기중(green), 2 상담중(red), 3 부재중(yellow/none)
  const m = (props.counselor.m_state || '').trim()
  if (m === '1') return 'online'
  if (m === '2') return 'busy'
  if (m === '3') return 'away'
  return ''
})

const handleClick = () => {
  router.push(`/counselor/${props.counselor.counselor_code}`)
}
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';
</style>