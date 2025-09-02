<template>
  <div class="form-section">
    <div class="completion-section">
      <div class="completion-icon">✅</div>
      <h2 class="completion-title">회원가입 완료!</h2>
      <p class="completion-desc">사주라인 회원이 되신 것을 환영합니다</p>

      <div class="welcome-bonus">
        <div class="bonus-title">🎁 가입 축하 혜택</div>
        <div class="bonus-desc">
          신규 회원님께 1,000P를 선물로 드렸습니다!<br>
          첫 상담 10분 무료 쿠폰도 확인해보세요.
        </div>
      </div>

      <button type="button" class="next-button" @click="goToLogin">로그인하러 가기</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  'go-to-login': []
}>()

const goToLogin = () => {
  emit('go-to-login')
}
</script>