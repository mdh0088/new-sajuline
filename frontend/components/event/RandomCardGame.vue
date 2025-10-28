<template>
  <div class="random-card-game">
    <!-- 타이틀 -->
    <div class="text-center mb-8" v-if="!isFlipping && !showResult">
      <p class="title-subtitle">꽝 없는 포인트 추가 적립!</p>
      <h1 class="title-main">
        <span class="title-highlight">포인트 랜덤카드</span>
      </h1>
      <h2 class="title-sub">뽑기 이벤트</h2>
    </div>

    <!-- 카드 영역 -->
    <div class="card-container">
      <div class="cards-wrapper" :class="{ 'cards-selecting': isFlipping }">
        <div
          v-for="position in (['left', 'center', 'right'] as const)"
          :key="position"
          :class="['card', `card-${position}`, {
            'card-flipping': isFlipping && selectedCard === position,
            'card-hidden': isFlipping && selectedCard !== position
          }]"
          @click="selectCard(position as 'left' | 'center' | 'right')"
        >
          <div class="card-inner">
            <div class="card-front">
              <div class="card-icon">💰</div>
              <div class="card-label">포인트 카드</div>
            </div>
            <div class="card-back">
              <div class="card-result">
                <div class="result-icon">🎉</div>
                <div class="result-amount">{{ rewardAmount }}P</div>
                <div class="result-label">당첨!</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 당첨 결과 화면 -->
    <div v-if="showResult" class="result-screen">
      <div class="result-confetti">✨ 🎊 ✨</div>
      <h2 class="result-title">축하합니다!</h2>
      <div class="result-prize">
        <div class="prize-amount">{{ rewardAmount }}P</div>
        <div class="prize-label">포인트를 획득했어요!</div>
      </div>
      <button @click="resetGame" class="result-button">다시 뽑기</button>
    </div>

    <!-- 안내 텍스트 -->
    <div class="text-center mt-12 mb-8" v-if="!isFlipping && !showResult">
      <p class="info-text">원하는 카드 한 장을 뽑아</p>
      <p class="info-text">오늘의 보상을 확인해 보세요.</p>
    </div>

    <!-- 뽑을 수 있는 기회 -->
    <div class="chance-box" v-if="!isFlipping && !showResult">
      <div class="chance-content">
        <span class="chance-icon">❓</span>
        <span class="chance-text">뽑을 수 있는 기회</span>
        <span class="chance-count">{{ remainingChances }}회</span>
      </div>
    </div>

    <!-- 뽑기 기회 획득 방법 -->
    <div class="text-center mt-8" v-if="!isFlipping && !showResult">
      <button class="hint-button" @click="showHintModal = true">
        <span>뽑기 기회 획득 방법</span>
        <span class="hint-icon">?</span>
      </button>
    </div>

    <!-- 뽑기 기회 획득 방법 모달 -->
    <div v-if="showHintModal" class="modal-overlay" @click="showHintModal = false">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">뽑기 기회 획득 방법</h3>
        <div class="modal-body">
          <p class="modal-highlight">
            상담 이용 최소 {{ config.min_consultation_minutes }}분 이상 완료 시<br>
            <span class="modal-emphasis">랜덤카드 뽑을 수 있는 기회 1회</span>를<br>
            획득할 수 있어요.
          </p>
          <ul class="modal-list">
            <li>획득한 랜덤카드 뽑기 기회의 유효기간은 {{ config.chance_expiry_days }}일입니다.</li>
            <li>뽑기를 통해 적립된 이벤트 마일리지의 유효기간은 {{ config.reward_expiry_days }}일입니다.</li>
            <li>뽑기 기회와 이벤트 마일리지는 유효기간 경과 시 자동 소멸됩니다.</li>
            <li>결제에 실패한 경우 뽑기 기회는 지급되지 않습니다.</li>
            <li>당사 사정에 따라 이벤트 내용 및 방침 보상은 변경될 수 있습니다.</li>
          </ul>
        </div>
        <button class="modal-button" @click="showHintModal = false">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface RandomCardConfig {
  rewards: number[]
  weights: number[]
  min_consultation_minutes: number
  chance_expiry_days: number
  reward_expiry_days: number
}

interface Props {
  config?: RandomCardConfig
  userChances?: number
}

const props = withDefaults(defineProps<Props>(), {
  config: () => ({
    rewards: [5, 10, 50, 100, 500, 1000, 5000, 10000],
    weights: [30, 25, 20, 15, 7, 2, 0.9, 0.1],
    min_consultation_minutes: 15,
    chance_expiry_days: 30,
    reward_expiry_days: 90
  }),
  userChances: 999 // 프로토타입 - 무제한
})

// 상태 관리
const isFlipping = ref(false)
const showResult = ref(false)
const selectedCard = ref<'left' | 'center' | 'right' | null>(null)
const rewardAmount = ref(0)
const remainingChances = ref(props.userChances)
const showHintModal = ref(false)

// 카드 선택
const selectCard = (card: 'left' | 'center' | 'right') => {
  if (isFlipping.value || remainingChances.value <= 0) return

  selectedCard.value = card
  isFlipping.value = true

  // 랜덤 포인트 생성
  rewardAmount.value = getWeightedRandom(props.config.rewards, props.config.weights)

  // 카드 뒤집기 애니메이션 후 결과 표시
  setTimeout(() => {
    showResult.value = true
    isFlipping.value = false
    // TODO: 백엔드 API 호출하여 실제 포인트 지급 및 기회 차감
    // remainingChances.value--
  }, 1500)
}

// 가중치 기반 랜덤 선택
const getWeightedRandom = (values: number[], weights: number[]): number => {
  const totalWeight = weights.reduce((sum, weight) => sum + weight, 0)
  let random = Math.random() * totalWeight

  for (let i = 0; i < values.length; i++) {
    const weight = weights[i]
    if (weight !== undefined && random < weight) {
      return values[i] ?? values[0] ?? 5
    }
    if (weight !== undefined) {
      random -= weight
    }
  }

  return values[0] ?? 5
}

// 게임 리셋
const resetGame = () => {
  showResult.value = false
  selectedCard.value = null
  rewardAmount.value = 0
}
</script>

<style scoped>
@import '~/assets/css/event/random-card.css';
</style>
