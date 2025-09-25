<template>
  <Teleport to="body">
    <div
      v-if="isVisible"
      class="phone-modal-overlay"
      :class="{ active: isVisible }"
      @click="closeModal"
    >
      <div
        class="phone-modal"
        @click.stop
      >
        <!-- 헤더 -->
        <div class="modal-header">
          <div class="counselor-profile">
            <div class="counselor-avatar">
              <img
                v-if="imageUrl"
                :src="imageUrl"
                alt="프로필 이미지"
                class="w-12 h-12 rounded-full object-cover"
                width="48"
                height="48"
                loading="lazy"
              />
              <span v-else>🔮</span>
            </div>
            <div class="counselor-info">
              <div class="counselor-name-group">
                <span class="counselor-name">{{ counselor.nickname }}</span>
                <span class="counselor-number">#{{ resolvedCode }}</span>
              </div>
              <div class="specialty-tags-row">
                <span
                  v-for="specialty in counselor.specialties"
                  :key="specialty"
                  class="specialty-tag"
                >
                  {{ specialty }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 콘텐츠 -->
        <div class="modal-content">
          <!-- 포인트 상담 버튼 -->
          <button
            class="point-consult-button"
            @click="startPointConsult"
          >
            <span class="point-icon">P</span>
            <span>포인트 상담 (02-6209-0808)</span>
          </button>

          <p class="point-info">
            포인트상담(선불) <strong>{{ resolvedAfterAmount }}P</strong>(30초)
          </p>
          <p class="connect-info">
            전화연결시 선택한 선생님과 바로연결됩니다.
          </p>

          <!-- 포인트 상태 -->
          <div class="point-status">
            <div class="status-item">
              <span class="status-label">보유 포인트</span>
              <span class="status-value">{{ displayUserPoints }}P</span>
            </div>
            <div class="status-item">
              <span class="status-label">상담 가능 시간</span>
              <span class="status-value">{{ availableMinutes }}분</span>
            </div>
            <button
              class="charge-button"
              @click="goToCharge"
            >
              포인트 충전
            </button>
          </div>

          <!-- 060 후불 상담 옵션 -->
          <div class="prepay-option" :class="{ open: showPrepayDetails }">
            <button
              class="prepay-toggle"
              @click="togglePrepayDetails"
            >
              <span>060후불 상담 이용하기</span>
              <span class="arrow-down" :class="{ rotated: showPrepayDetails }">▼</span>
            </button>

            <div v-show="showPrepayDetails" class="prepay-details">
              <div class="prepay-content">
                <button
                  class="phone-060-button"
                  @click="start060Consult"
                >
                  <span class="phone-icon">📞</span>
                  <span>060상담 (060-800-1300)</span>
                </button>
                <p class="fee-info">
                  060상담(후불) <strong>{{ resolvedBeforeAmount }}</strong>(30초)(vat별도)
                </p>
                <p class="guide-title">상담안내</p>
                <p class="guide-text">
                  전화상담 연결 후, 고유번호 {{ resolvedCode }}번 누르세요.
                </p>
              </div>
            </div>
          </div>

          <!-- 닫기 버튼 -->
          <button
            class="close-button"
            @click="closeModal"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useCdn } from '~/composables/utils/useCdn'
import { useUserPoints } from '~/composables/user/useUserPoints'
interface Counselor {
  code: string
  nickname: string
  profile_image_url?: string | null
  specialties: string[]
  afterAmount?: number | null
  beforeAmount?: string | null
}

interface Props {
  counselor: Counselor
  isVisible: boolean
  userPoints?: number
}

const props = withDefaults(defineProps<Props>(), {
  userPoints: 0
})

const emit = defineEmits<{
  close: []
  startPointConsult: [counselorCode: string]
  start060Consult: [counselorCode: string]
  goToCharge: []
}>()

const showPrepayDetails = ref(false)

const { cdnUrl } = useCdn()
const imageUrl = computed(() => {
  const raw = (props.counselor.profile_image_url || '').trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return cdnUrl(raw)
  return cdnUrl('cs', raw)
})

const { points } = useUserPoints()
const displayUserPoints = computed(() => {
  const p = props.userPoints
  if (typeof p === 'number' && p >= 0) return p
  return points.value
})

const resolvedCode = computed(() => {
  const c: any = props.counselor as any
  return (c.code ?? c.number ?? c.counselor_code ?? c.id ?? '')
})
const resolvedAfterAmount = computed(() => {
  const c: any = props.counselor as any
  const v = c.afterAmount ?? c.after_amount ?? c.pointRate
  if (v === null || v === undefined) return 0
  const n = typeof v === 'string' ? Number(v) : Number(v)
  return isNaN(n) ? 0 : n
})
const resolvedBeforeAmount = computed(() => {
  const c: any = props.counselor as any
  if (c.beforeAmount) return c.beforeAmount
  if (c.before_amount) return c.before_amount
  if (c.rate060) return `${c.rate060}원`
  return '0원'
})

// 상담 가능 시간 계산 (30초당 포인트 소모)
const availableMinutes = computed(() => {
  const rate = resolvedAfterAmount.value
  if (!rate || rate === 0) return 0
  const totalSeconds = Math.floor(displayUserPoints.value / rate) * 30
  return Math.floor(totalSeconds / 60)
})

const closeModal = () => {
  emit('close')
}

const togglePrepayDetails = () => {
  showPrepayDetails.value = !showPrepayDetails.value
}

const startPointConsult = () => {
  emit('startPointConsult', resolvedCode.value)
}

const start060Consult = () => {
  emit('start060Consult', resolvedCode.value)
}

const goToCharge = () => {
  emit('goToCharge')
}

// ESC 키로 모달 닫기
onMounted(() => {
  const handleEsc = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      closeModal()
    }
  }
  document.addEventListener('keydown', handleEsc)
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEsc)
  })
})
</script>

<style>
@import '~/assets/css/common/phone-consult-modal.css';
</style>