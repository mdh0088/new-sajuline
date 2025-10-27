<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <div class="mileage-header">
      <div class="mileage-header-top">
        <button class="mileage-back-button" @click="$router.back()">←</button>
        <h1 class="mileage-header-title">마일리지 샵</h1>
        <div class="mileage-header-actions">
          <button class="mileage-icon-btn">🔔</button>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="mileage-main-content">
      <!-- 페이지 타이틀 섹션 -->
      <div class="mileage-page-title-section">
        <h1 class="mileage-page-title">마일리지 샵</h1>
        <p class="mileage-page-subtitle">마일리지로 다양한 혜택을 만나보세요</p>
      </div>

      <!-- 마일리지 정보 -->
      <div class="mileage-info">
        <span class="mileage-icon">💎</span>
        <span class="mileage-shop-amount">{{ currentMileage.toLocaleString() }}</span>
        <span class="mileage-label">마일리지 보유</span>
      </div>

      <!-- 카테고리 필터 -->
      <!-- <div class="mileage-category-filters">
        <div
          v-for="category in categories"
          :key="category"
          :class="['mileage-category-chip', { active: activeCategory === category }]"
          @click="activeCategory = category"
        >
          {{ category }}
        </div>
      </div> -->

      <!-- 로딩 상태 -->
      <div v-if="isProductsLoading || isUserLoading" class="mileage-loading">
        <div class="mileage-spinner"></div>
        <p>마일리지 상품을 불러오는 중...</p>
      </div>

      <!-- 상품 그리드 -->
      <div v-else class="mileage-products-grid">
        <div
          v-for="product in products"
          :key="product.mileage_id"
          class="mileage-product-card"
          @click="selectProduct(product)"
        >
          <div class="mileage-product-header">
            <div class="mileage-product-icon">
              <img
                v-if="getProductImageUrl(product)"
                :src="getProductImageUrl(product)"
                :alt="product.m_product_name"
                class="mileage-product-image"
              />
              <span v-else>💎</span>
            </div>
            <div class="mileage-product-price">
              <div class="mileage-price-amount">{{ product.m_product_value.toLocaleString() }}M</div>
              <div class="mileage-price-label">마일리지</div>
            </div>
          </div>
          <div class="mileage-product-info">
            <div class="mileage-product-title">{{ product.m_product_name }}</div>
            <div class="mileage-product-description">{{ product.description }}</div>
            <div class="mileage-product-tags">
              <span
                v-for="tag in getProductTags(product)"
                :key="tag"
                class="mileage-product-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
          <button
            class="mileage-purchase-button"
            :disabled="product.m_product_value > currentMileage || isPurchasing"
            @click.stop="openPurchaseModal(product)"
          >
            {{ product.m_product_value > currentMileage ? '마일리지 부족' : '구매하기' }}
          </button>
        </div>
      </div>
    </main>

    <!-- 모달 오버레이 -->
    <div
      v-show="showModal"
      class="mileage-modal-overlay"
      @click="closePurchaseModal"
    ></div>

    <!-- 구매 확인 모달 -->
    <div
      v-show="showModal && !showSuccessModal"
      class="mileage-purchase-modal"
      @click.stop
    >
      <div class="mileage-modal-header">
        <h3 class="mileage-modal-title">구매 확인</h3>
        <p class="mileage-modal-subtitle">상품 정보와 마일리지 사용 내역을 확인해주세요</p>
        <button class="mileage-close-button" @click="closePurchaseModal">×</button>
      </div>
      <div class="mileage-modal-content" v-if="selectedProduct">
        <!-- 상품 정보 -->
        <div class="mileage-modal-product-info">
          <div class="mileage-modal-product-header">
            <div class="mileage-modal-product-icon">
              <img
                v-if="getProductImageUrl(selectedProduct)"
                :src="getProductImageUrl(selectedProduct)"
                :alt="selectedProduct.m_product_name"
                class="mileage-product-image"
              />
              <span v-else>💎</span>
            </div>
            <div class="mileage-modal-product-details">
              <div class="mileage-modal-product-title">{{ selectedProduct.m_product_name }}</div>
              <div class="mileage-modal-product-description">{{ selectedProduct.description }}</div>
            </div>
            <div class="mileage-modal-product-price">
              <div class="mileage-modal-price-amount">{{ selectedProduct.m_product_value.toLocaleString() }}M</div>
              <div class="mileage-modal-price-label">상품 가격</div>
            </div>
          </div>
        </div>

        <!-- 마일리지 사용 내역 -->
        <div class="mileage-breakdown">
          <div class="mileage-breakdown-title">💎 마일리지 사용 내역</div>
          <div class="mileage-breakdown-item">
            <span class="mileage-breakdown-label">보유 마일리지</span>
            <span class="mileage-breakdown-value">{{ currentMileage.toLocaleString() }}M</span>
          </div>
          <div class="mileage-breakdown-item">
            <span class="mileage-breakdown-label">사용 마일리지</span>
            <span class="mileage-breakdown-value">{{ selectedProduct.m_product_value.toLocaleString() }}M</span>
          </div>
          <div class="mileage-breakdown-item">
            <span class="mileage-breakdown-label">구매 후 잔여 마일리지</span>
            <span class="mileage-breakdown-value mileage-highlight">{{ (currentMileage - selectedProduct.m_product_value).toLocaleString() }}M</span>
          </div>
          <div class="mileage-breakdown-item">
            <span class="mileage-breakdown-label">충전될 포인트</span>
            <span class="mileage-breakdown-value mileage-highlight">{{ selectedProduct.charge_point.toLocaleString() }}P</span>
          </div>
        </div>

        <!-- 마일리지 이용안내 -->
        <div class="mileage-guide-section">
          <div
            class="mileage-guide-header"
            @click="showGuide = !showGuide"
          >
            <span class="mileage-guide-title">📋 마일리지 이용안내</span>
            <span class="mileage-guide-toggle">{{ showGuide ? '▲' : '▼' }}</span>
          </div>
          <div v-show="showGuide" class="mileage-guide-content">
            <div class="mileage-guide-item">
              <h4>상담권 이용안내</h4>
              <ul>
                <li>선불(포인트)상담 진행 시 마일리지가 적립됩니다</li>
                <li>적립된 마일리지로 상품 구매 시 상담포인트 자동 충전</li>
                <li>원하시는 선생님과 선불(포인트)상담과 동일하게 진행</li>
              </ul>
            </div>
            <div class="mileage-guide-item">
              <h4>유의사항</h4>
              <ul>
                <li>마일리지 구매 포인트는 환불 및 양도 불가</li>
                <li>1마일리지 = 1포인트로 환산</li>
                <li>마일리지상품 구매 후 상담포인트 구매시 합산</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 마일리지 부족 경고 -->
        <div
          v-show="selectedProduct.m_product_value > currentMileage"
          class="mileage-insufficient-notice"
        >
          <div class="mileage-notice-icon">⚠️</div>
          <div class="mileage-notice-text">마일리지가 부족합니다<br>추가 마일리지를 충전해주세요</div>
        </div>

        <!-- 액션 버튼들 -->
        <div class="mileage-modal-actions">
          <button class="mileage-modal-cancel-btn" @click="closePurchaseModal" :disabled="isPurchasing">취소</button>
          <button
            class="mileage-modal-confirm-btn"
            :disabled="selectedProduct.m_product_value > currentMileage || isPurchasing"
            @click="confirmPurchase"
          >
            {{ isPurchasing ? '처리 중...' : (selectedProduct.m_product_value > currentMileage ? '마일리지 부족' : '구매하기') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 구매 완료 모달 -->
    <div
      v-show="showModal && showSuccessModal"
      class="mileage-purchase-modal"
      @click.stop
    >
      <div class="mileage-success-modal">
        <div class="mileage-success-icon">✅</div>
        <div class="mileage-success-title">구매 완료!</div>
        <div class="mileage-success-message">
          {{ selectedProduct?.m_product_name }}을(를)<br>
          성공적으로 구매했습니다.
        </div>
        <button class="mileage-success-button" @click="closeSuccessModal">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { MileageProduct } from '~/types/mileage'
import { useMileageProductApi } from '~/composables/api/useMileageProduct'
import { useUserQueries } from '~/composables/api/useUserQueries'
import { useNotify } from '~/composables/utils/useNotify'
import { useCdn } from '~/composables/utils/useCdn'

// API 및 유틸리티
const { useMileageProducts, usePurchaseMileage } = useMileageProductApi()
const { useUserMypage } = useUserQueries()
const { notifySuccess, notifyError, notifyConfirm } = useNotify()
const { cdnUrl } = useCdn()
const router = useRouter()

// 사용자 정보 조회 (로그인 체크)
const { data: userData, isLoading: isUserLoading, error: userError } = useUserMypage()

// 로그인 체크
if (userError.value) {
  notifyError('로그인이 필요합니다')
  router.push('/auth/login')
}

// 마일리지 상품 목록 조회
const { data: products, isLoading: isProductsLoading } = useMileageProducts()

// 마일리지 구매 뮤테이션
const { mutateAsync: purchaseProduct, isPending: isPurchasing } = usePurchaseMileage()

// UI 상태
const showModal = ref(false)
const showSuccessModal = ref(false)
const selectedProduct = ref<MileageProduct | null>(null)
const showGuide = ref(false)

// 현재 사용자 마일리지
const currentMileage = computed(() => userData.value?.user_info?.mileage_point || 0)

// 상품 이미지 URL 생성
const getProductImageUrl = (product: MileageProduct): string => {
  if (!product.m_product_img) return ''
  // S3 /mileage 경로에서 이미지 로드
  return cdnUrl('mileage', product.m_product_img)
}

// 태그 배열 생성
const getProductTags = (product: MileageProduct): string[] => {
  if (!product.tags) return []
  return product.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
}

const selectProduct = (product: MileageProduct) => {
  console.log('상품 상세 보기:', product.m_product_name)
}

const openPurchaseModal = (product: MileageProduct) => {
  selectedProduct.value = product
  showModal.value = true
  showSuccessModal.value = false
}

const closePurchaseModal = () => {
  showModal.value = false
  showSuccessModal.value = false
  selectedProduct.value = null
}

const confirmPurchase = async () => {
  if (!selectedProduct.value || selectedProduct.value.m_product_value > currentMileage.value) {
    return
  }

  const confirmed = await notifyConfirm(
    `${selectedProduct.value.m_product_name}을(를) 구매하시겠습니까?\n마일리지 ${selectedProduct.value.m_product_value.toLocaleString()}M이 차감되고 포인트 ${selectedProduct.value.charge_point.toLocaleString()}P가 충전됩니다.`
  )

  if (!confirmed) {
    return
  }

  try {
    const result = await purchaseProduct({
      mileage_id: selectedProduct.value.mileage_id
    })

    showSuccessModal.value = true
    notifySuccess('마일리지 상품 구매가 완료되었습니다')

    console.log('구매 완료:', result)
  } catch (error: any) {
    notifyError(error.message || '구매 처리 중 오류가 발생했습니다')
    closePurchaseModal()
  }
}

const closeSuccessModal = () => {
  showModal.value = false
  showSuccessModal.value = false
  selectedProduct.value = null
}
</script>

<style scoped>
/* 로딩 상태 */
.mileage-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  min-height: 300px;
}

.mileage-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.mileage-loading p {
  margin-top: 1rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

/* 상품 이미지 */
.mileage-product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.mileage-product-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  font-size: 2rem;
}

.mileage-modal-product-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  font-size: 1.75rem;
}

.mileage-modal-product-icon .mileage-product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
</style>