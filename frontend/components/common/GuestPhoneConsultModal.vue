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
              <span>{{ counselor.emoji }}</span>
            </div>
            <div class="counselor-info">
              <div class="counselor-badge">탑로</div>
              <div class="counselor-name-group">
                <span class="counselor-name">{{ counselor.name }}</span>
                <span class="counselor-number">{{ counselor.number }}번</span>
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
            060상담(후불) <strong>{{ counselor.rate060 }}원</strong>(30초)(vat별도)
          </p>

          <!-- 상담 안내 -->
          <div class="guide-section">
            <p class="guide-title">상담안내</p>
            <p class="guide-text">
              전화상담 연결 후, 고유번호 {{ counselor.number }}번 누르세요.
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
interface Counselor {
  id: number
  name: string
  number: string
  emoji: string
  specialties: string[]
  pointRate: number
  rate060: number
}

interface Props {
  counselor: Counselor
  isVisible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  start060Consult: [counselorId: number]
  goToRegisterLogin: []
}>()

const closeModal = () => {
  emit('close')
}

const start060Consult = () => {
  emit('start060Consult', props.counselor.id)
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
</style>