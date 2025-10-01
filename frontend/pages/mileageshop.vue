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
      <div class="mileage-category-filters">
        <div
          v-for="category in categories"
          :key="category"
          :class="['mileage-category-chip', { active: activeCategory === category }]"
          @click="activeCategory = category"
        >
          {{ category }}
        </div>
      </div>

      <!-- 상품 그리드 -->
      <div class="mileage-products-grid">
        <div
          v-for="product in products"
          :key="product.id"
          class="mileage-product-card"
          @click="selectProduct(product)"
        >
          <div class="mileage-product-header">
            <div class="mileage-product-icon">{{ product.icon }}</div>
            <div class="mileage-product-price">
              <div class="mileage-price-amount">{{ product.price.toLocaleString() }}M</div>
              <div class="mileage-price-label">마일리지</div>
            </div>
          </div>
          <div class="mileage-product-info">
            <div class="mileage-product-title">{{ product.title }}</div>
            <div class="mileage-product-description">{{ product.description }}</div>
            <div class="mileage-product-tags">
              <span
                v-for="tag in product.tags"
                :key="tag"
                class="mileage-product-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
          <button
            class="mileage-purchase-button"
            :disabled="product.price > currentMileage"
            @click.stop="openPurchaseModal(product)"
          >
            {{ product.price > currentMileage ? '마일리지 부족' : '구매하기' }}
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
            <div class="mileage-modal-product-icon">{{ selectedProduct.icon }}</div>
            <div class="mileage-modal-product-details">
              <div class="mileage-modal-product-title">{{ selectedProduct.title }}</div>
              <div class="mileage-modal-product-description">{{ selectedProduct.description }}</div>
            </div>
            <div class="mileage-modal-product-price">
              <div class="mileage-modal-price-amount">{{ selectedProduct.price.toLocaleString() }}M</div>
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
            <span class="mileage-breakdown-value">{{ selectedProduct.price.toLocaleString() }}M</span>
          </div>
          <div class="mileage-breakdown-item">
            <span class="mileage-breakdown-label">구매 후 잔여 마일리지</span>
            <span class="mileage-breakdown-value mileage-highlight">{{ (currentMileage - selectedProduct.price).toLocaleString() }}M</span>
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
          v-show="selectedProduct.price > currentMileage"
          class="mileage-insufficient-notice"
        >
          <div class="mileage-notice-icon">⚠️</div>
          <div class="mileage-notice-text">마일리지가 부족합니다<br>추가 마일리지를 충전해주세요</div>
        </div>

        <!-- 액션 버튼들 -->
        <div class="mileage-modal-actions">
          <button class="mileage-modal-cancel-btn" @click="closePurchaseModal">취소</button>
          <button
            class="mileage-modal-confirm-btn"
            :disabled="selectedProduct.price > currentMileage"
            @click="confirmPurchase"
          >
            {{ selectedProduct.price > currentMileage ? '마일리지 부족' : '구매하기' }}
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
          {{ selectedProduct?.title }}을(를)<br>
          성공적으로 구매했습니다.
        </div>
        <button class="mileage-success-button" @click="closeSuccessModal">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

interface Product {
  id: number
  icon: string
  title: string
  description: string
  price: number
  tags: string[]
  category: string
}

const currentMileage = ref(450000)
const activeCategory = ref('전체')
const showModal = ref(false)
const showSuccessModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const showGuide = ref(false)

const categories = ref(['전체', '포인트'])

const products = ref<Product[]>([
  {
    id: 1,
    icon: '💎',
    title: '포인트 300,000P',
    description: '마일리지 300,000M을 사용하여 포인트 300,000P를 충전할 수 있습니다.',
    price: 300000,
    tags: ['최대용량', '프리미엄'],
    category: '포인트'
  },
  {
    id: 2,
    icon: '💰',
    title: '포인트 100,000P',
    description: '마일리지 100,000M을 사용하여 포인트 100,000P를 충전할 수 있습니다.',
    price: 100000,
    tags: ['대용량', '인기'],
    category: '포인트'
  },
  {
    id: 3,
    icon: '🪙',
    title: '포인트 50,000P',
    description: '마일리지 50,000M을 사용하여 포인트 50,000P를 충전할 수 있습니다.',
    price: 50000,
    tags: ['중용량', '추천'],
    category: '포인트'
  },
  {
    id: 4,
    icon: '💸',
    title: '포인트 30,000P',
    description: '마일리지 30,000M을 사용하여 포인트 30,000P를 충전할 수 있습니다.',
    price: 30000,
    tags: ['중간', '실속'],
    category: '포인트'
  },
  {
    id: 5,
    icon: '🟡',
    title: '포인트 10,000P',
    description: '마일리지 10,000M을 사용하여 포인트 10,000P를 충전할 수 있습니다.',
    price: 10000,
    tags: ['소용량', '기본'],
    category: '포인트'
  }
])

const selectProduct = (product: Product) => {
  console.log('상품 상세 보기:', product.title)
}

const openPurchaseModal = (product: Product) => {
  selectedProduct.value = product
  showModal.value = true
  showSuccessModal.value = false
}

const closePurchaseModal = () => {
  showModal.value = false
  showSuccessModal.value = false
  selectedProduct.value = null
}

const confirmPurchase = () => {
  if (!selectedProduct.value || selectedProduct.value.price > currentMileage.value) {
    return
  }

  currentMileage.value -= selectedProduct.value.price
  showSuccessModal.value = true

  console.log('구매 완료:', selectedProduct.value.title, selectedProduct.value.price + 'M')
  console.log('잔여 마일리지:', currentMileage.value + 'M')
}

const closeSuccessModal = () => {
  showModal.value = false
  showSuccessModal.value = false
  selectedProduct.value = null
}
</script>

<style scoped>
/* 컴포넌트별 스코프 스타일이 필요한 경우 여기에 추가 */
</style>