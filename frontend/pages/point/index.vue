<template>
  <div class="min-h-screen bg-slate-950 text-white">
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
        <div class="section-header">
          <h2 class="section-title">이용약관 동의</h2>
        </div>

        <!-- 전체 동의 -->
        <div class="terms-item all-agree">
          <div
            :class="['checkbox', { checked: allTermsAgreed }]"
            @click="toggleAllTerms"
          ></div>
          <div class="terms-text">
            위 주문 내용을 확인 하였으며, 아래 모든 약관에 동의합니다.
          </div>
        </div>

        <!-- 개별 약관 -->
        <div class="terms-item">
          <div
            :class="['checkbox', { checked: provisionAgreed }]"
            @click="provisionAgreed = !provisionAgreed"
          ></div>
          <div class="terms-text">
            <span class="required-badge">[필수]</span> 쇼핑몰 이용약관 동의
          </div>
          <button class="terms-detail-btn" @click="openProvisionModal">자세히</button>
        </div>

        <div class="terms-item">
          <div
            :class="['checkbox', { checked: privacyAgreed }]"
            @click="privacyAgreed = !privacyAgreed"
          ></div>
          <div class="terms-text">
            <span class="required-badge">[필수]</span> 개인정보 수집 및 이용 동의
          </div>
          <button class="terms-detail-btn" @click="openPrivacyModal">자세히</button>
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

    <!-- 이용약관 모달 -->
    <div v-if="showProvisionModal" class="terms-modal-backdrop" @click.self="showProvisionModal = false">
      <div class="terms-modal">
        <div class="terms-modal-header">
          <h3 class="terms-modal-title">쇼핑몰 이용약관</h3>
          <button class="terms-modal-close" @click="showProvisionModal = false">✕</button>
        </div>
        <div class="terms-modal-body">
          <div class="terms-content">
            <p>본 약관은 피플라인(이하 "회사")이 운영하는 사주라인 서비스(이하 "서비스")의 이용과 관련하여 회사와 이용자 간의 권리, 의무 및 책임사항을 규정함을 목적으로 합니다.</p>

            <h4>제1조 (목적)</h4>
            <p>본 약관은 회사가 제공하는 서비스의 이용조건 및 절차에 관한 사항과 기타 필요한 사항을 규정함을 목적으로 합니다.</p>

            <h4>제2조 (약관의 효력 및 변경)</h4>
            <p>1. 본 약관은 서비스를 이용하고자 하는 모든 이용자에 대하여 그 효력을 발생합니다.</p>
            <p>2. 회사는 필요한 경우 관련 법령을 위배하지 않는 범위 내에서 본 약관을 변경할 수 있습니다.</p>

            <h4>제3조 (서비스의 제공)</h4>
            <p>1. 회사는 다음과 같은 서비스를 제공합니다:</p>
            <ul>
              <li>AI 운세 분석 서비스</li>
              <li>전문 상담사와의 실시간 채팅 상담</li>
              <li>포인트 충전 및 결제 서비스</li>
              <li>기타 회사가 추가 개발하거나 제휴계약 등을 통해 제공하는 서비스</li>
            </ul>

            <h4>제4조 (서비스 이용요금)</h4>
            <p>1. 회사가 제공하는 서비스는 기본적으로 유료입니다.</p>
            <p>2. 이용자는 포인트를 충전하여 서비스를 이용할 수 있습니다.</p>
            <p>3. 충전된 포인트는 환불이 불가능합니다.</p>

            <h4>제5조 (책임의 제한)</h4>
            <p>1. 회사는 천재지변 또는 이에 준하는 불가항력으로 인하여 서비스를 제공할 수 없는 경우에는 서비스 제공에 관한 책임이 면제됩니다.</p>
            <p>2. 회사는 이용자의 귀책사유로 인한 서비스 이용의 장애에 대하여는 책임을 지지 않습니다.</p>

            <h4>제6조 (개인정보보호)</h4>
            <p>회사는 이용자의 개인정보를 보호하기 위하여 정보통신망법 및 개인정보보호법 등 관계 법령에서 정하는 바를 준수합니다.</p>
          </div>
        </div>
        <div class="terms-modal-footer">
          <button class="terms-confirm-btn" @click="confirmProvision">확인</button>
        </div>
      </div>
    </div>

    <!-- 개인정보 수집 및 이용 동의 모달 -->
    <div v-if="showPrivacyModal" class="terms-modal-backdrop" @click.self="showPrivacyModal = false">
      <div class="terms-modal">
        <div class="terms-modal-header">
          <h3 class="terms-modal-title">개인정보 수집 및 이용 동의</h3>
          <button class="terms-modal-close" @click="showPrivacyModal = false">✕</button>
        </div>
        <div class="terms-modal-body">
          <div class="terms-content">
            <p>회사는 서비스 제공을 위하여 다음과 같이 개인정보를 수집·이용합니다.</p>

            <h4>1. 수집하는 개인정보 항목</h4>
            <ul>
              <li>필수항목: 이름, 이메일, 휴대폰번호, 생년월일</li>
              <li>선택항목: 프로필 사진, 관심사</li>
              <li>자동수집: 서비스 이용 기록, 접속 로그, 쿠키, 결제 기록</li>
            </ul>

            <h4>2. 개인정보의 수집 및 이용 목적</h4>
            <ul>
              <li>회원 가입 및 관리: 본인 확인, 개인 식별, 가입 의사 확인</li>
              <li>서비스 제공: 운세 분석, 상담사 매칭, 포인트 관리</li>
              <li>결제 서비스: 포인트 충전, 결제 처리, 영수증 발행</li>
              <li>고객 상담: 문의사항 접수 및 답변, 불만처리</li>
            </ul>

            <h4>3. 개인정보의 보유 및 이용 기간</h4>
            <p>회사는 원칙적으로 개인정보 수집 및 이용목적이 달성된 후에는 해당 정보를 지체 없이 파기합니다. 단, 관계법령의 규정에 의하여 보존할 필요가 있는 경우 회사는 아래와 같이 관계법령에서 정한 일정한 기간 동안 회원정보를 보관합니다:</p>
            <ul>
              <li>계약 또는 청약철회 등에 관한 기록: 5년</li>
              <li>대금결제 및 재화 등의 공급에 관한 기록: 5년</li>
              <li>소비자의 불만 또는 분쟁처리에 관한 기록: 3년</li>
              <li>접속에 관한 기록: 3개월</li>
            </ul>

            <h4>4. 개인정보 제공 거부 권리</h4>
            <p>이용자는 개인정보 수집 및 이용 동의를 거부할 권리가 있습니다. 다만, 필수 항목에 대한 동의를 거부할 경우 서비스 이용이 제한될 수 있습니다.</p>

            <h4>5. 개인정보 보호책임자</h4>
            <p>- 책임자: 김진형</p>
            <p>- 연락처: 02-6212-0465</p>
            <p>- 이메일: help@sajutarot.com</p>
          </div>
        </div>
        <div class="terms-modal-footer">
          <button class="terms-confirm-btn" @click="confirmPrivacy">확인</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  requiresAuth: true
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
    name: '카카오페이',
    description: '간편결제',
    code: 'kakaopay'
  }
])

// 선택된 항목들
const selectedIndex = ref(0)
const selectedPaymentIndex = ref(0) // 기본으로 신용카드 선택

// 약관 동의
const provisionAgreed = ref(false)  // 이용약관 동의
const privacyAgreed = ref(false)    // 개인정보 동의
const allTermsAgreed = computed(() => provisionAgreed.value && privacyAgreed.value)

// 약관 모달 상태
const showProvisionModal = ref(false)
const showPrivacyModal = ref(false)

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
         provisionAgreed.value &&
         privacyAgreed.value
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

// 전체 약관 동의 토글
function toggleAllTerms() {
  const newValue = !allTermsAgreed.value
  provisionAgreed.value = newValue
  privacyAgreed.value = newValue
}

// 약관 모달 열기
function openProvisionModal() {
  showProvisionModal.value = true
}

function openPrivacyModal() {
  showPrivacyModal.value = true
}

// 약관 확인 (모달에서 확인 버튼 클릭 시)
function confirmProvision() {
  provisionAgreed.value = true
  showProvisionModal.value = false
}

function confirmPrivacy() {
  privacyAgreed.value = true
  showPrivacyModal.value = false
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

// PC 결제 완료 postMessage 이벤트 핸들러
function handlePaymentMessage(event: MessageEvent) {
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

/* 약관 섹션 스타일 */
.terms-item.all-agree {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.terms-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
}

.required-badge {
  color: #EF4444;
  font-weight: 600;
  font-size: 13px;
}

.terms-detail-btn {
  margin-left: auto;
  padding: 6px 12px;
  background: rgba(183, 148, 246, 0.1);
  border: 1px solid rgba(183, 148, 246, 0.3);
  color: #B794F6;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.terms-detail-btn:hover {
  background: rgba(183, 148, 246, 0.2);
  border-color: rgba(183, 148, 246, 0.5);
}

/* 약관 모달 */
.terms-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.terms-modal {
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  background: #1e293b;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.terms-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.terms-modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.terms-modal-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.terms-modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.terms-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.terms-content {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.7;
}

.terms-content h4 {
  font-size: 16px;
  font-weight: 700;
  color: #B794F6;
  margin: 24px 0 12px 0;
}

.terms-content h4:first-child {
  margin-top: 0;
}

.terms-content p {
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.terms-content ul {
  margin: 12px 0;
  padding-left: 20px;
}

.terms-content li {
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.terms-modal-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
}

.terms-confirm-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #9333EA 0%, #7C3AED 100%);
  border: none;
  border-radius: 8px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.terms-confirm-btn:hover {
  background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
  transform: translateY(-1px);
}

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