<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 현재 포인트 -->
      <section class="current-point">
        <template v-if="isUser">
          <div class="point-label">현재 보유 포인트</div>
          <div class="point-value">
            <span class="point-icon">💰</span>
            <span>{{ currentPoints.toLocaleString() }} P</span>
          </div>
        </template>
        <template v-else>
          <div class="login-required">
            <div class="login-message">포인트를 충전하려면 로그인이 필요합니다</div>
            <button class="login-button" @click="goToLogin">로그인하기</button>
          </div>
        </template>
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
            <div class="charge-amount">
              <span>{{ item.product_name }}</span>
              <span v-if="item.bonus_point > 0" class="charge-bonus">+{{ item.bonus_point.toLocaleString() }}P 보너스</span>
            </div>
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
            <div class="radio-button"></div>
            <div class="payment-icon">
              <img v-if="method.image" :src="method.image" :alt="method.name" class="payment-icon-img" />
              <span v-else>{{ method.icon }}</span>
            </div>
            <div class="payment-info">
              <div class="payment-name">{{ method.name }}</div>
              <div class="payment-desc">{{ method.description }}</div>
            </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useHead, navigateTo } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'
import { usePointProductApi, type PointProduct } from '~/composables/api/usePointProduct'
import { usePaymentApi } from '~/composables/api/usePayment'
import { useMediaQuery } from '@vueuse/core'
import { useAuth } from '~/composables/auth/useAuth'
import { useUserPoints } from '~/composables/user/useUserPoints'
import { useUserQueries } from '~/composables/api/useUserQueries'

const { notifySuccess, notifyError, notifyInfo } = useNotify()
const { isUser } = useAuth()
const { points: userPoints, setPoints } = useUserPoints()
const { useUserMypage } = useUserQueries()

// SEO 및 메타 데이터 설정
const route = useRoute()

useHead({
  title: '포인트 충전 - 사주라인',
  meta: [
    { name: 'description', content: '안전하고 간편한 포인트 충전으로 사주 상담을 받아보세요. 신용카드, 가상계좌, 카카오페이로 간편하게 충전하세요.' },
    { name: 'keywords', content: '포인트 충전, 사주 포인트, 카카오페이, 온라인 결제, 사주 상담 결제' },
    { property: 'og:title', content: '포인트 충전 - 사주라인' },
    { property: 'og:description', content: '안전하고 간편한 포인트 충전으로 사주 상담을 받아보세요.' },
    { property: 'og:image', content: 'https://sajuline.com/images/og-point.jpg' },
    { property: 'og:url', content: `https://sajuline.com${route.path}` },
    { property: 'og:type', content: 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: '포인트 충전 - 사주라인' },
    { name: 'twitter:description', content: '안전하고 간편한 포인트 충전' },
    { name: 'twitter:image', content: 'https://sajuline.com/images/og-point.jpg' },
    { name: 'robots', content: 'index,follow' }
  ],
  link: [
    { rel: 'canonical', href: `https://sajuline.com${route.path}` }
  ]
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: true
})

// 마이페이지 데이터 가져오기 (포인트 포함)
const { data: mypageData } = useUserMypage()

// 마이페이지 데이터가 로드되면 포인트 업데이트
watch(
  () => mypageData.value?.current_points,
  (newPoints) => {
    if (newPoints !== undefined) {
      setPoints(newPoints)
    }
  },
  { immediate: true }
)

// 현재 포인트 (실제 사용자 포인트)
const currentPoints = computed(() => userPoints.value ?? 0)

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
    //code: 'allthegate'
    code: 'creditcard'
  },
  {
    icon: '🏦',
    name: '가상계좌',
    description: '무통장입금',
    code: 'virtualaccount'
  },
  {
    icon: '💛',
    image: '/images/kakaopay.png',
    name: '카카오페이',
    description: '간편결제',
    code: 'kakaopay'
  }
])

// 선택된 항목들
const selectedIndex = ref(0)
const selectedPaymentIndex = ref(0) // 기본으로 신용카드 선택

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
         selectedPaymentMethod.value !== null
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

function goToLogin() {
  navigateTo('/login')
}

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

// PC 결제 완료 postMessage 이벤트 핸들러
function handlePaymentMessage(event: MessageEvent) {
  // Origin 검증 (보안 강화)
  const allowedOrigin = window.location.origin
  if (event.origin !== allowedOrigin) {
    console.warn('[Payment] Unauthorized message origin:', event.origin)
    return
  }

  console.log('[Payment] Received postMessage:', event.data)

  if (event.data?.type === 'payment_success') {
    showPaymentModal.value = false
    notifySuccess('결제가 성공적으로 완료되었습니다.')
    // 페이지 새로고침으로 포인트 갱신
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  } else if (event.data?.type === 'payment_fail') {
    showPaymentModal.value = false
    notifyError('결제가 실패했습니다. 다시 시도해주세요.')
  } else if (event.data?.type === 'payment_pending') {
    showPaymentModal.value = false
    const message = event.data.message || '가상계좌가 발급되었습니다. 입금해주세요.'
    notifyInfo(message)
    // 가상계좌 안내 페이지로 이동 (또는 현재 페이지에서 안내)
    setTimeout(() => {
      window.location.reload()
    }, 1500)
  }
}

// 컴포넌트 마운트 시 이벤트 리스너 등록
onMounted(() => {
  window.addEventListener('message', handlePaymentMessage)
})

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener('message', handlePaymentMessage)
})
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