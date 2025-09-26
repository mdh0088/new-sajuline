<template>
  <Teleport to="body">
    <div
      v-if="isVisible"
      class="guest-phone-modal-overlay"
      :class="{ active: isVisible }"
      @click="closeModal"
    >
      <div
        class="guest-phone-modal"
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
              <div class="counselor-badge">
                <span
                  v-for="specialty in counselor.specialties"
                  :key="specialty"
                  class="specialty-tag"
                >
                  {{ specialty }}
                </span>
              </div>
              <div class="counselor-name-group">
                <span class="counselor-name">{{ counselor.nickname }}</span>
                <span class="counselor-number">#{{ resolvedCode }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 콘텐츠 -->
        <div class="modal-content">
          <!-- 회원 혜택 안내 -->
          <div class="member-benefit-section">
            <h3 class="section-title">회원 혜택</h3>
            <p class="question">아직 회원이 아니신가요?</p>
            <p class="benefit-text">
              회원가입/로그인하시면 더 많은 사주관련만의 혜택(이벤트, 할인)을 누리실 수 있습니다.
            </p>
          </div>

          <!-- 회원가입/로그인 버튼 -->
          <button
            class="register-login-button"
            @click="goToRegisterLogin"
          >
            포인트 상담 회원가입&로그인
          </button>

          <!-- 060 후불 상담 옵션 -->
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

          <!-- 상담 안내 -->
          <div class="guide-section">
            <p class="guide-title">상담안내</p>
            <p class="guide-text">
              전화상담 연결 후, 고유번호 {{ resolvedCode }}번 누르세요.
            </p>
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
import { computed, onMounted, onUnmounted } from 'vue'
import { useCdn } from '~/composables/utils/useCdn'
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
}

const props = defineProps<Props>()
const { cdnUrl } = useCdn()
const imageUrl = computed(() => {
  const raw = (props.counselor.profile_image_url || '').trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return cdnUrl(raw)
  return cdnUrl('cs', raw)
})

const resolvedCode = computed(() => {
  const c: any = props.counselor as any
  return (c.code ?? c.number ?? c.counselor_code ?? c.id ?? '')
})
const resolvedBeforeAmount = computed(() => {
  const c: any = props.counselor as any
  if (c.beforeAmount) return c.beforeAmount
  if (c.before_amount) return c.before_amount
  if (c.rate060) return `${c.rate060}원`
  return '0원'
})

const emit = defineEmits<{
  close: []
  start060Consult: [counselorCode: string]
  goToRegisterLogin: []
}>()

const closeModal = () => {
  emit('close')
}

const start060Consult = () => {
  emit('start060Consult', resolvedCode.value)
}

const goToRegisterLogin = () => {
  emit('goToRegisterLogin')
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
@import '~/assets/css/common/guest-phone-consult-modal.css';
@import '~/assets/css/common/phone-consult-modal.css';
</style>