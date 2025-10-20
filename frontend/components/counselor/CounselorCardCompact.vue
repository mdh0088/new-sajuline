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
          <div class="counselor-name-row">
            <span class="counselor-name-small">{{ counselor.nickname }}</span>
            <span class="counselor-code">{{ counselor.counselor_code }}</span>
          </div>
          <div class="counselor-specialty-small">{{ specialtyLabel }}</div>
          <div class="counselor-tags-small">
            <span v-for="tag in tags.slice(0, 3)" :key="tag" class="tag-small">{{ tag }}</span>
          </div>
          <div class="counselor-desc-small">{{ shortIntro }}</div>
        </div>
        <div class="counselor-right-info">
          <div class="counselor-price-small">{{ (counselor.after_amount || 0).toLocaleString() }}P/30초</div>
          <div class="counselor-rating-small">
            <span class="rating-stars-small">
              <span v-for="i in 5" :key="i">{{ i <= Math.round(counselor.rating_avg || 0) ? '⭐' : '☆' }}</span>
            </span>
            <span class="rating-score">{{ Number(counselor.rating_avg || 0).toFixed(1) }}</span>
          </div>
          <div class="counselor-experience">리뷰 {{ (counselor.review_count || 0).toLocaleString() }}</div>
          <button class="consult-button" @click.stop="handleConsultClick">
            상담하기
          </button>
        </div>
      </div>
    </div>

    <!-- 전화 상담 모달 (로그인 유저용) -->
    <PhoneConsultModal
      v-if="isUser"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      :user-points="userPoints"
      @close="closePhoneModal"
      @start-point-consult="handlePointConsult"
      @start060-consult="handle060Consult"
      @go-to-charge="goToCharge"
    />

    <!-- 전화 상담 모달 (비로그인 유저용) -->
    <GuestPhoneConsultModal
      v-if="!isUser"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      @close="closePhoneModal"
      @start060-consult="handle060Consult"
      @go-to-register-login="goToRegisterLogin"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, navigateTo } from 'nuxt/app'
import type { CounselorSearchItem } from '~/types/counselor/search'
import { useCdn } from '~/composables/utils/useCdn'
import { useAuth } from '~/composables/auth/useAuth'
import { useUserPoints } from '~/composables/user/useUserPoints'

interface Props {
  // API 검색 결과 아이템 그대로 사용
  counselor: CounselorSearchItem
}

const props = defineProps<Props>()
const router = useRouter()
const { cdnUrl } = useCdn()
const { isUser } = useAuth()
const { points: storePoints } = useUserPoints()

// 모달 상태
const showPhoneModal = ref(false)
const userPoints = computed(() => storePoints.value)

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

// PhoneConsultModal에 전달할 데이터 형식 변환
const modalCounselorData = computed(() => {
  return {
    code: props.counselor.counselor_code,
    nickname: props.counselor.nickname,
    profile_image_url: props.counselor.profile_image_url,
    specialties: [specialtyLabel.value],
    afterAmount: props.counselor.after_amount ?? null,
    beforeAmount: null // CounselorSearchItem에는 before_amount가 없으므로 null
  }
})

const handleClick = () => {
  router.push(`/counselor/${props.counselor.counselor_code}`)
}

const handleConsultClick = () => {
  // 상담하기 버튼 클릭 시 모달 팝업 표시
  showPhoneModal.value = true
}

const closePhoneModal = () => {
  showPhoneModal.value = false
}

const handlePointConsult = (counselorId: string) => {
  console.log('포인트 상담 시작:', counselorId)
  // TODO: 포인트 상담 시작 API 호출
}

const handle060Consult = (counselorId: string) => {
  console.log('060 상담 시작:', counselorId)
  // TODO: 060 상담 연결 로직
}

const goToCharge = () => {
  navigateTo('/point')
}

const goToRegisterLogin = () => {
  navigateTo('/login')
}
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';
</style>