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
            v-for="(item, index) in products"
            :key="index"
            :class="['charge-item', {
              selected: selectedIndex === index
            }]"
            @click="selectItem(index)"
          >
            <div class="charge-amount">{{ item.product_name }}</div>
            <div v-if="item.bonus_point > 0" class="charge-bonus">+{{ item.bonus_point.toLocaleString() }} P 보너스</div>
            <div class="charge-price">
              <div v-if="item.discount_rate > 0" class="price-with-discount">
                <div class="discount-badge">{{ item.discount_rate }}% 할인</div>
                <span class="original-price">{{ item.price.toLocaleString() }}원</span>
                <span class="discounted-price">{{ discountedPrice(item.price, item.discount_rate).toLocaleString() }}원</span>
              </div>
              <div v-else class="price-normal">
                <span>{{ item.price.toLocaleString() }}원</span>
              </div>
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
        </section>
        <!-- 환불 불가 약관 - 추후 필요시 사용
        <div class="terms-item">
          <div
            :class="['checkbox', { checked: refundAgreed }]"
            @click="refundAgreed = !refundAgreed"
          ></div>
          <div class="terms-text">
            충전한 포인트는 환불이 불가함을 확인했습니다
          </div>
        </div>
        -->

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
            <span class="point-value">{{ selectedProduct?.point_amount.toLocaleString() || '0' }} P</span>
          </div>
          <div v-if="(selectedProduct?.bonus_point || 0) > 0" class="summary-row point-row">
            <span class="summary-label">보너스 포인트</span>
            <span class="bonus-value">+{{ selectedProduct?.bonus_point.toLocaleString() }} P</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-row">
            <span class="summary-label">상품 가격</span>
            <span class="summary-value">{{ originalPrice.toLocaleString() }}원</span>
          </div>
          <div v-if="discountRate > 0" class="summary-row">
            <span class="summary-label">할인 가격</span>
            <span class="summary-value amount-negative">-{{ discountAmount.toLocaleString() }}원</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">VAT</span>
            <span class="summary-value amount-positive">+{{ vatAmount.toLocaleString() }}원</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">결제금액(VAT 포함)</span>
            <span class="payment-amount">{{ finalAmount.toLocaleString() }}원</span>
          </div>
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
        {{ finalAmount.toLocaleString() }}원 결제하기
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

    <!-- PC 결제 모달 -->
    <div v-if="showPaymentModal" class="payment-modal-backdrop" @click.self="showPaymentModal = false">
      <div class="payment-modal">
        <div class="payment-modal-header">
          <div class="payment-modal-title">결제창</div>
          <button class="payment-modal-close" @click="showPaymentModal = false">✕</button>
        </div>
        <div class="payment-modal-body">
          <iframe v-if="paymentPageUrl" class="payment-iframe" :src="paymentPageUrl" title="Payletter Payment"></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useHead } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'
import { usePointProductApi, type PointProduct } from '~/composables/api/usePointProduct'
import { usePaymentApi } from '~/composables/api/usePayment'
import { useMediaQuery } from '@vueuse/core'

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

// 현재 포인트 (임시 값: 실제로는 사용자 포인트 API로 교체 가능)
const currentPoints = ref(1200)

// API 연동: 포인트 상품 목록
const { usePublicPointProducts } = usePointProductApi()
const { data: productList, isLoading } = usePublicPointProducts()
const products = computed<PointProduct[]>(() => productList?.value ?? [])

// 결제 수단 목록
const paymentMethods = ref([
  {
    icon: '💳',
    name: '신용/체크카드',
    description: '모든 카드 결제 가능',
    code: 'allthegate'
  },
  {
    icon: '🏦',
    name: '가상계좌',
    description: '무통장입금',
    code: 'virtualaccount'
  },
  {
    icon: '💛',
    name: '카카오페이',
    description: '간편결제',
    code: 'kakaopay'
  }
])

// 선택된 항목들
const selectedIndex = ref(0)
const selectedPaymentIndex = ref(0) // 기본으로 신용카드 선택

// 약관 동의
const termsAgreed = ref(false)
// const refundAgreed = ref(false) // 환불 불가 약관 - 추후 필요시 사용

// 계산된 속성들
const selectedProduct = computed<PointProduct | null>(() => products.value[selectedIndex.value] ?? null)

const selectedPaymentMethod = computed(() => {
  const index = selectedPaymentIndex.value
  if (index >= 0 && index < paymentMethods.value.length) {
    return paymentMethods.value[index]
  }
  return null
})

const discountRate = computed(() => selectedProduct.value?.discount_rate ?? 0)
const originalPrice = computed(() => selectedProduct.value?.price ?? 0)
const discountAmount = computed(() => {
  const rate = discountRate.value
  const price = originalPrice.value
  return rate > 0 ? Math.floor((price * rate) / 100) : 0
})
const discountedPriceVal = computed(() => originalPrice.value - discountAmount.value)
const vatAmount = computed(() => Math.floor((originalPrice.value * 10) / 100))
const finalAmount = computed(() => discountedPriceVal.value + vatAmount.value)

const canProceedPayment = computed(() => {
  return selectedProduct.value !== null &&
         selectedPaymentMethod.value !== null &&
         termsAgreed.value
         // && refundAgreed.value // 환불 불가 약관 - 추후 필요시 사용
})

// 디바이스 구분 (VueUse)
const isMobile = useMediaQuery('(max-width: 767px)')

// PC 모달 상태
const showPaymentModal = ref(false)
const paymentPageUrl = ref('')

// 메서드들
function selectItem(index: number) { selectedIndex.value = index }

function selectPaymentMethod(index: number) {
  selectedPaymentIndex.value = index
}


function discountedPrice(price: number, rate: number) { return price - Math.floor((price * rate) / 100) }

function processPayment() {
  if (!canProceedPayment.value) {
    notifyError('결제 진행 전 필수 항목을 확인해주세요.')
    return
  }

  const product = selectedProduct.value
  const paymentMethod = selectedPaymentMethod.value

  // null 체크를 통한 타입 안전성 확보
  if (!product || !paymentMethod) {
    notifyError('충전 금액 또는 결제 수단을 선택해주세요.')
    return
  }

  notifyInfo(`${paymentMethod.name}로 ${finalAmount.value.toLocaleString()}원 결제를 진행합니다.`)

  const { requestPayment } = usePaymentApi()
  // 백엔드에는 pgcode를 전송
  requestPayment(product.product_id, (paymentMethod as any).code)
    .then((res) => {
      if (isMobile.value) {
        if (res.mobile_url) {
          window.location.href = res.mobile_url
        } else if (res.online_url) {
          window.location.href = res.online_url
        } else {
          notifyError('결제 페이지 URL을 찾을 수 없습니다')
        }
        return
      }

      // PC: 모달(iframe)로 online_url 표시
      if (res.online_url) {
        paymentPageUrl.value = res.online_url
        showPaymentModal.value = true
      } else if (res.mobile_url) {
        // online_url이 없으면 mobile_url로 폴백
        paymentPageUrl.value = res.mobile_url
        showPaymentModal.value = true
      } else {
        notifyError('결제 페이지 URL을 찾을 수 없습니다')
      }
    })
    .catch((err: any) => {
      notifyError(err?.message || '결제 요청 중 오류가 발생했습니다')
    })
}
</script>

<style scoped>
/* point.css 파일을 import하여 사용 */
@import '~/assets/css/point.css';

/* 결제 모달 */
.payment-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.payment-modal {
  width: 90vw;
  max-width: 960px;
  height: 85vh;
  background: #0f172a;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.payment-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.payment-modal-title { font-weight: 600; }
.payment-modal-close {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}
.payment-modal-body { flex: 1; }
.payment-iframe {
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
</style>