<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <main class="pt-[60px] pb-24">
      <!-- 헤더 -->
      <header class="fixed top-0 left-0 right-0 bg-slate-950/80 backdrop-blur-md z-50 border-b border-white/10">
        <div class="flex items-center justify-between px-5 py-4">
          <button @click="goBack" class="text-2xl text-white">←</button>
          <div class="absolute left-1/2 transform -translate-x-1/2">
            <span class="text-lg font-semibold text-white">포인트 랜덤카드</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-white">3,689</span>
            <span class="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center text-white text-xs">M</span>
          </div>
        </div>
      </header>

      <!-- 메인 콘텐츠 -->
      <div class="px-5 pt-8">
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
              class="card card-left"
              :class="{
                'card-flipping': isFlipping && selectedCard === 'left',
                'card-hidden': isFlipping && selectedCard !== 'left'
              }"
              @click="selectCard('left')"
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
            <div
              class="card card-center"
              :class="{
                'card-flipping': isFlipping && selectedCard === 'center',
                'card-hidden': isFlipping && selectedCard !== 'center'
              }"
              @click="selectCard('center')"
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
            <div
              class="card card-right"
              :class="{
                'card-flipping': isFlipping && selectedCard === 'right',
                'card-hidden': isFlipping && selectedCard !== 'right'
              }"
              @click="selectCard('right')"
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
      </div>

      <!-- 뽑기 기회 획득 방법 모달 -->
      <div v-if="showHintModal" class="modal-overlay" @click="showHintModal = false">
        <div class="modal-content" @click.stop>
          <h3 class="modal-title">뽑기 기회 획득 방법</h3>
          <div class="modal-body">
            <p class="modal-highlight">
              상담 이용 최소 15분 이상 완료 시<br>
              <span class="modal-emphasis">랜덤카드 뽑을 수 있는 기회 1회</span>를<br>
              획득할 수 있어요.
            </p>
            <ul class="modal-list">
              <li>획득한 랜덤카드 뽑기 기회의 유효기간은 30일입니다.</li>
              <li>뽑기를 통해 적립된 이벤트 마일리지의 유효기간은 90일입니다.</li>
              <li>뽑기 기회와 이벤트 마일리지는 유효기간 경과 시 자동 소멸됩니다.</li>
              <li>결제에 실패한 경우 뽑기 기회는 지급되지 않습니다.</li>
              <li>당사 사정에 따라 이벤트 내용 및 방침 보상은 변경될 수 있습니다.</li>
            </ul>
          </div>
          <button class="modal-button" @click="showHintModal = false">확인</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// SEO 설정
useHead({
  title: '랜덤카드 뽑기 - 사주라인',
  meta: [
    {
      name: 'description',
      content: '사주라인 포인트 랜덤카드 뽑기 이벤트',
    },
  ],
})

const router = useRouter()

// 상태 관리
const isFlipping = ref(false)
const showResult = ref(false)
const selectedCard = ref<'left' | 'center' | 'right' | null>(null)
const rewardAmount = ref(0)
const remainingChances = ref(999) // 프로토타입 - 무제한 테스트
const showHintModal = ref(false)

const goBack = () => {
  router.back()
}

// 카드 선택
const selectCard = (card: 'left' | 'center' | 'right') => {
  if (isFlipping.value || remainingChances.value <= 0) return

  selectedCard.value = card
  isFlipping.value = true

  // 랜덤 포인트 생성 (테스트용 - 추후 백엔드 연동)
  const rewards = [5, 10, 50, 100, 500, 1000, 5000, 10000]
  const weights = [30, 25, 20, 15, 7, 2, 0.9, 0.1] // 확률 가중치
  rewardAmount.value = getWeightedRandom(rewards, weights)

  // 카드 뒤집기 애니메이션 후 결과 표시
  setTimeout(() => {
    showResult.value = true
    isFlipping.value = false
    // 프로토타입이므로 기회 차감하지 않음
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
