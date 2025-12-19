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
          <div ref="tagsWrapperRef" class="counselor-tags-wrapper">
            <div
              ref="tagsContainerRef"
              class="counselor-tags-small"
              :class="{ 'scrolling': shouldScroll }"
              :style="shouldScroll ? { animationDuration } : {}"
            >
              <span v-for="(tag, idx) in tags" :key="`tag-1-${idx}`" class="tag-small">{{ tag }}</span>
              <span v-if="shouldScroll" v-for="(tag, idx) in tags" :key="`tag-2-${idx}`" class="tag-small">{{ tag }}</span>
            </div>
          </div>
          <div class="counselor-desc-small">{{ shortIntro }}</div>
        </div>
        <div class="counselor-right-info">
          <div class="counselor-price-small">{{ (counselor.after_amount || 0).toLocaleString() }}P/30초</div>
          <div class="counselor-rating-small">
            <span class="rating-stars-small">
              <img
                v-for="i in 5"
                :key="i"
                :src="i <= Math.round(counselor.rating_avg || 0) ? '/images/favorite.png' : '/images/favorite.png'"
                :class="i <= Math.round(counselor.rating_avg || 0) ? 'star-filled' : 'star-empty'"
                alt="별점"
                class="star-icon"
              />
            </span>
            <span class="rating-score">{{ Number(counselor.rating_avg || 0).toFixed(1) }}</span>
          </div>
          <div class="counselor-experience">리뷰 {{ (counselor.review_count || 0).toLocaleString() }}</div>
          <button
            :class="['consult-button', consultButtonClass]"
            @click.stop="handleConsultClick"
            :disabled="isConsultDisabled"
          >
            {{ consultButtonText }}
          </button>
        </div>
      </div>
    </div>

    <!-- 접속 알림 설정 모달 -->
    <Teleport to="body">
      <div v-if="showNotificationModal" class="notification-modal-backdrop" @click.self="closeNotificationModal">
        <div class="notification-modal" @click.stop>
          <div class="notification-modal-content">
            <h3 class="notification-modal-title">{{ notificationModalTitle }}</h3>
            <p class="notification-modal-desc" v-html="notificationModalDesc.replace('\n', '<br>')"></p>
            <div class="notification-modal-buttons">
              <button class="notification-button notification-button-primary" @click.stop="handleSetNotification">
                🔔 알림 설정
              </button>
              <button class="notification-button notification-button-secondary" @click.stop="closeNotificationModal">
                닫기
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

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
import { computed, ref, onMounted, nextTick } from 'vue'
import { useRouter, navigateTo } from 'nuxt/app'
import type { CounselorSearchItem } from '~/types/counselor/search'
import { useCdn } from '~/composables/utils/useCdn'
import { useAuth } from '~/composables/auth/useAuth'
import { useUserPoints } from '~/composables/user/useUserPoints'
import { useNotify } from '~/composables/utils/useNotify'
import { useNotificationWaitQueries } from '~/composables/api/useNotificationWaitQueries'

interface Props {
  // API 검색 결과 아이템 그대로 사용
  counselor: CounselorSearchItem
}

const props = defineProps<Props>()
const router = useRouter()
const { cdnUrl } = useCdn()
const { isUser } = useAuth()
const { points: storePoints } = useUserPoints()
const { notifySuccess, notifyError, notifyWarning } = useNotify()
const { useRegisterNotificationWait } = useNotificationWaitQueries()
const registerMutation = useRegisterNotificationWait()

// 모달 상태
const showPhoneModal = ref(false)
const showNotificationModal = ref(false)
const userPoints = computed(() => storePoints.value)

// 키워드 스크롤 관련 refs
const tagsWrapperRef = ref<HTMLElement | null>(null)
const tagsContainerRef = ref<HTMLElement | null>(null)
const animationDuration = ref('20s')

const specialtyMap: Record<string, string> = {
  TARO: '전화타로',
  SAJU: '전화사주',
  FORTUNE: '전화신점'
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

// 키워드가 많을 때만 스크롤 활성화 (3개 이상)
const shouldScroll = computed(() => {
  return tags.value.length > 3
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

// 상담 버튼 텍스트
const consultButtonText = computed(() => {
  const m = (props.counselor.m_state || '').trim()
  if (m === '1') return '상담하기'
  if (m === '2') return '상담중'
  if (m === '3') return '부재중'
  return '상담하기'
})

// 상담 버튼 스타일 클래스
const consultButtonClass = computed(() => {
  const m = (props.counselor.m_state || '').trim()
  if (m === '2') return 'consult-button-busy'
  if (m === '3') return 'consult-button-away'
  return ''
})

// 상담 버튼 비활성화 여부 - 모든 상태에서 클릭 가능
const isConsultDisabled = computed(() => {
  return false
})

// 알림 모달 제목 (상담중/부재중 구분)
const notificationModalTitle = computed(() => {
  const m = (props.counselor.m_state || '').trim()
  if (m === '2') {
    return `${props.counselor.nickname} 선생님은 현재 상담중입니다`
  }
  return `${props.counselor.nickname} 선생님은 현재 부재중입니다`
})

// 알림 모달 설명 (상담중/부재중 구분)
const notificationModalDesc = computed(() => {
  const m = (props.counselor.m_state || '').trim()
  if (m === '2') {
    return '상담사 접속 알림을 설정하시면,\n상담 종료 후 카톡 알림톡을 통하여 안내드립니다.'
  }
  return '상담사 접속 알림을 설정하시면,\n상담 가능시 카톡 알림톡을 통하여 안내드립니다.'
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
  const m = (props.counselor.m_state || '').trim()

  // 상담중 또는 부재중일 때는 알림 설정 모달 표시
  if (m === '2' || m === '3') {
    showNotificationModal.value = true
    return
  }

  // 대기중일 때는 상담 모달 표시
  showPhoneModal.value = true
}

const closePhoneModal = () => {
  showPhoneModal.value = false
}

const closeNotificationModal = () => {
  showNotificationModal.value = false
}

const handleSetNotification = async () => {
  if (!isUser.value) {
    notifyWarning('로그인이 필요합니다.')
    closeNotificationModal()
    return
  }

  try {
    await registerMutation.mutateAsync(props.counselor.counselor_id)
    notifySuccess('알림 신청이 등록되었습니다.')
  } catch (error: any) {
    notifyError(error.message || '알림 신청에 실패했습니다.')
  } finally {
    closeNotificationModal()
  }
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

// 키워드 스크롤 애니메이션 설정
onMounted(() => {
  if (shouldScroll.value && tagsContainerRef.value) {
    nextTick(() => {
      const container = tagsContainerRef.value
      if (container) {
        const scrollWidth = container.scrollWidth / 2 // 복제된 절반 너비
        // 너비에 비례한 속도 계산 (더 느리게)
        const duration = Math.max(25, scrollWidth / 30)
        animationDuration.value = `${duration}s`
      }
    })
  }
})
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';

/* 키워드 자동 롤링 스타일 - 완전히 재작성 */
.counselor-tags-wrapper {
  position: relative;
  max-width: 165px !important;
  height: 22px;
  overflow: hidden !important;
  margin-top: 2px;
  display: block !important;
}

/* 스크롤 활성화 시에만 페이드 효과 표시 */
.counselor-tags-wrapper:has(.scrolling)::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 30px;
  height: 100%;
  background: linear-gradient(to right, transparent 0%, rgb(137 34 229 / 20%) 40%, rgba(147, 51, 234, 0.2) 100%);
  pointer-events: none;
  z-index: 2;
}

/* 기본 상태 - 스크롤 없음 */
.counselor-tags-small {
  display: flex !important;
  gap: 6px;
  flex-wrap: nowrap !important;
  align-items: center;
  height: 22px;
}

/* 스크롤 활성화 시 */
.counselor-tags-small.scrolling {
  display: inline-flex !important;
  width: fit-content !important;
  min-width: fit-content !important;
  flex-wrap: nowrap !important;
  animation-name: scroll-tags;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  will-change: transform;
}

.counselor-tags-small.scrolling:hover {
  animation-play-state: paused;
}

/* 개별 태그 스타일 */
.counselor-tags-small .tag-small {
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  display: inline-block !important;
}

@keyframes scroll-tags {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* 모바일 최적화 */
@media (max-width: 768px) {
  .counselor-tags-wrapper:has(.scrolling)::after {
    width: 30px;
  }
}

/* 상담 버튼 상태별 스타일 */
.consult-button-busy {
  background: linear-gradient(135deg, #0076e5 0%, #00b0a1 100%) !important;
  border-color: transparent !important;
  color: #fff !important;
  cursor: not-allowed !important;
  opacity: 1 !important;
}

.consult-button-away {
  background: rgba(156, 163, 175, 0.2) !important;
  border-color: rgba(156, 163, 175, 0.4) !important;
  color: rgba(156, 163, 175, 1) !important;
}

.consult-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 알림 설정 모달 */
.notification-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9000;
  padding: 20px;
}

.notification-modal {
  background: #1e293b;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 400px;
  width: 100%;
  animation: modalSlideUp 0.3s ease-out;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notification-modal-content {
  padding: 32px 24px;
  text-align: center;
}

.notification-modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  line-height: 1.4;
}

.notification-modal-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 24px;
}

.notification-modal-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-button {
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.notification-button-primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #fff;
}

.notification-button-primary:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-1px);
}

.notification-button-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.notification-button-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>