<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-top">
        <button class="back-button" @click="$router.back()">←</button>
        <h1 class="header-title">충전하기</h1>
        <div class="header-actions">
          <button class="icon-btn" @click="$router.push('/search')">🔍</button>
          <button class="icon-btn" @click="$router.push('/login')">👤</button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 현재 포인트 -->
      <section class="current-point">
        <div class="point-label">현재 보유 포인트</div>
        <div class="point-value">
          <span class="point-icon">💰</span>
          <span>{{ currentPoints.toLocaleString() }} P</span>
        </div>
      </section>

      <!-- 프로모션 배너 -->
      <section class="promo-banner">
        <div class="promo-icon">🎉</div>
        <div class="promo-content">
          <div class="promo-title">첫 충전 100% 보너스!</div>
          <div class="promo-desc">지금 충전하면 2배로 받을 수 있어요</div>
        </div>
      </section>

      <!-- 충전 금액 선택 -->
      <section class="charge-section">
        <div class="section-header">
          <h2 class="section-title">충전할 금액을 선택하세요</h2>
          <NuxtLink to="/point/guide" class="guide-link">
            <span class="icon">ℹ️</span>
            <span>이용안내</span>
          </NuxtLink>
        </div>

        <div class="charge-grid">
          <div
            v-for="(item, index) in chargeItems"
            :key="index"
            :class="['charge-item', {
              popular: item.popular,
              selected: selectedChargeIndex === index
            }]"
            @click="selectChargeItem(index)"
          >
            <div v-if="item.popular" class="popular-badge">인기</div>
            <div class="charge-amount">{{ item.points.toLocaleString() }} P</div>
            <div class="charge-bonus">+{{ item.bonus.toLocaleString() }} P 보너스</div>
            <div class="charge-price">
              <span v-if="item.originalPrice" class="original-price">{{ item.originalPrice.toLocaleString() }}원</span>
              <span>{{ item.price.toLocaleString() }}원</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 결제 수단 -->
      <section class="payment-section">
        <h2 class="section-title">결제 수단</h2>

        <div class="payment-methods">
          <div
            v-for="(method, index) in paymentMethods"
            :key="index"
            :class="['payment-method', { selected: selectedPaymentIndex === index }]"
            @click="selectPaymentMethod(index)"
          >
            <div class="payment-icon">{{ method.icon }}</div>
            <div class="payment-info">
              <div class="payment-name">{{ method.name }}</div>
              <div class="payment-desc">{{ method.description }}</div>
            </div>
            <div class="radio-button"></div>
          </div>
        </div>
      </section>

      <!-- 약관 동의 -->
      <section class="terms-section">
        <div class="terms-item">
          <div
            :class="['checkbox', { checked: termsAgreed }]"
            @click="termsAgreed = !termsAgreed"
          ></div>
          <div class="terms-text">
            <NuxtLink to="/terms/payment" class="terms-link">결제 이용약관</NuxtLink>에 동의합니다
          </div>
        </div>
        <div class="terms-item">
          <div
            :class="['checkbox', { checked: refundAgreed }]"
            @click="refundAgreed = !refundAgreed"
          ></div>
          <div class="terms-text">
            충전한 포인트는 환불이 불가함을 확인했습니다
          </div>
        </div>
      </section>

      <!-- 결제 내역 -->
      <div class="payment-summary">
        <div class="summary-header">
          <div class="summary-title">
            <span>결제 내역</span>
          </div>
        </div>
        <div class="summary-content">
          <div class="summary-row point-row">
            <span class="summary-label">충전 포인트</span>
            <span class="point-value">{{ selectedChargeItem?.points.toLocaleString() || '0' }} P</span>
          </div>
          <div class="summary-row point-row">
            <span class="summary-label">보너스 포인트</span>
            <span class="bonus-value">+{{ selectedChargeItem?.bonus.toLocaleString() || '0' }} P</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-row">
            <span class="summary-label">결제 금액</span>
            <span class="payment-amount">{{ selectedChargeItem?.price.toLocaleString() || '0' }}원</span>
          </div>
          <div class="vat-note">* VAT 별도</div>
        </div>
      </div>
    </main>

    <!-- 하단 결제 버튼 -->
    <div class="bottom-cta">
      <button
        class="payment-button"
        :disabled="!canProceedPayment"
        @click="processPayment"
      >
        {{ selectedChargeItem?.price.toLocaleString() || '0' }}원 결제하기
      </button>
    </div>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <NuxtLink to="/" class="nav-item">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">홈</span>
      </NuxtLink>
      <NuxtLink to="/events" class="nav-item">
        <span class="nav-icon">🎁</span>
        <span class="nav-label">이벤트</span>
      </NuxtLink>
      <NuxtLink to="/user/favorite" class="nav-item">
        <span class="nav-icon">⭐</span>
        <span class="nav-label">즐겨찾기</span>
      </NuxtLink>
      <NuxtLink to="/user/mypage" class="nav-item">
        <span class="nav-icon">👤</span>
        <span class="nav-label">마이</span>
      </NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useHead } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'

const { notifySuccess, notifyError, notifyInfo } = useNotify()

// SEO 및 메타 데이터 설정
useHead({
  title: '포인트 충전 - 사주라인',
  meta: [
    { name: 'description', content: '안전하고 간편한 포인트 충전으로 사주 상담을 받아보세요.' },
    { property: 'og:title', content: '포인트 충전 - 사주라인' },
    { property: 'og:description', content: '안전하고 간편한 포인트 충전으로 사주 상담을 받아보세요.' }
  ]
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: true,
  layout: 'default'
})

// 현재 포인트
const currentPoints = ref(1200)

// 충전 아이템 목록
const chargeItems = ref([
  {
    points: 5000,
    bonus: 1000,
    price: 5000,
    originalPrice: null,
    popular: false
  },
  {
    points: 10000,
    bonus: 3000,
    price: 10000,
    originalPrice: null,
    popular: true
  },
  {
    points: 30000,
    bonus: 10000,
    price: 27000,
    originalPrice: 30000,
    popular: false
  },
  {
    points: 50000,
    bonus: 20000,
    price: 43000,
    originalPrice: 50000,
    popular: false
  },
  {
    points: 100000,
    bonus: 50000,
    price: 79000,
    originalPrice: 100000,
    popular: false
  },
  {
    points: 200000,
    bonus: 120000,
    price: 149000,
    originalPrice: 200000,
    popular: false
  }
])

// 결제 수단 목록
const paymentMethods = ref([
  {
    icon: '💳',
    name: '신용/체크카드',
    description: '모든 카드 결제 가능'
  },
  {
    icon: '📱',
    name: '휴대폰 결제',
    description: '통신사 소액결제'
  },
  {
    icon: '🏦',
    name: '계좌이체',
    description: '실시간 계좌이체'
  },
  {
    icon: '💛',
    name: '카카오페이',
    description: '간편결제'
  }
])

// 선택된 항목들
const selectedChargeIndex = ref(1) // 기본으로 인기 상품 선택
const selectedPaymentIndex = ref(0) // 기본으로 신용카드 선택

// 약관 동의
const termsAgreed = ref(false)
const refundAgreed = ref(false)

// 계산된 속성들
const selectedChargeItem = computed(() => {
  const index = selectedChargeIndex.value
  if (index >= 0 && index < chargeItems.value.length) {
    return chargeItems.value[index]
  }
  return null
})

const selectedPaymentMethod = computed(() => {
  const index = selectedPaymentIndex.value
  if (index >= 0 && index < paymentMethods.value.length) {
    return paymentMethods.value[index]
  }
  return null
})

const canProceedPayment = computed(() => {
  return selectedChargeItem.value !== null &&
         selectedPaymentMethod.value !== null &&
         termsAgreed.value &&
         refundAgreed.value
})

// 메서드들
function selectChargeItem(index: number) {
  selectedChargeIndex.value = index
}

function selectPaymentMethod(index: number) {
  selectedPaymentIndex.value = index
}

function processPayment() {
  if (!canProceedPayment.value) {
    notifyError('결제 진행 전 필수 항목을 확인해주세요.')
    return
  }

  const chargeItem = selectedChargeItem.value
  const paymentMethod = selectedPaymentMethod.value

  // null 체크를 통한 타입 안전성 확보
  if (!chargeItem || !paymentMethod) {
    notifyError('충전 금액 또는 결제 수단을 선택해주세요.')
    return
  }

  notifyInfo(`${paymentMethod.name}로 ${chargeItem.price.toLocaleString()}원 결제를 진행합니다.`)

  // TODO: 실제 결제 API 연동
  // 임시로 성공 메시지만 표시
  setTimeout(() => {
    notifySuccess('🎉 결제가 완료되었습니다!')
    // 결제 완료 후 처리 로직
  }, 2000)
}
</script>

<style scoped>
/* point.css 파일을 import하여 사용 */
@import '~/assets/css/point.css';
</style>