<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 검색 영역 -->
    <section class="search-section">
      <div class="search-wrapper">
        <input
          type="text"
          class="search-input"
          placeholder="상담사 이름 또는 전문분야 검색"
          v-model="searchQuery"
        >
        <span class="search-icon">🔍</span>
      </div>
    </section>

    <!-- 필터 영역 -->
    <section class="filter-section">
      <!-- 활성 필터 -->
      <div class="active-filters-container" v-if="activeFilters.length > 0">
        <div class="active-filters">
          <div
            class="active-filter-tag"
            v-for="(filter, index) in activeFilters"
            :key="index"
          >
            <span>{{ filter.text }}</span>
            <span class="remove-filter" @click="removeFilter(index)">×</span>
          </div>
        </div>
      </div>

      <!-- 필터 버튼들 -->
      <div class="filter-buttons">
        <button class="filter-btn" @click="openFilterModal('style')">
          <span>🗣️ {{ selectedFilters.style || '#상담스타일' }}</span>
        </button>
        <button class="filter-btn" @click="openFilterModal('topic')">
          <span>💘 {{ selectedFilters.topic || '#상담주제' }}</span>
        </button>
        <button class="filter-btn" @click="openFilterModal('sort')">
          <span>↕️ {{ selectedFilters.sort || '추천순' }}</span>
        </button>
      </div>
    </section>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 검색 결과 정보 -->
      <div class="search-info">
        <span class="result-count">총 <strong>{{ totalCount }}명</strong>의 상담사</span>
      </div>

      <!-- 상담사 리스트 -->
      <div class="counselor-grid-container">
        <div
          class="counselor-card-compact"
          v-for="counselor in counselors"
          :key="counselor.id"
          @click="goToCounselorDetail(counselor.id)"
        >
          <div class="counselor-avatar-small" :class="{ online: counselor.isOnline }">
            <img :src="counselor.image" :alt="counselor.name" v-if="counselor.image">
            <span v-else>{{ counselor.avatar }}</span>
          </div>
          <div class="counselor-info-compact">
            <div class="counselor-main-info">
              <div class="counselor-left-info">
                <div class="counselor-name-small">{{ counselor.name }}</div>
                <div class="counselor-specialty-small">{{ counselor.specialty }}</div>
                <div class="counselor-tags-small">
                  <span
                    class="tag-small"
                    v-for="tag in counselor.tags"
                    :key="tag"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div class="counselor-right-info">
                <div class="counselor-price-small">{{ counselor.price }}원/분</div>
                <div class="counselor-rating-small">
                  <span class="rating-stars-small">⭐⭐⭐⭐⭐</span>
                  <span class="rating-score">{{ counselor.rating }}</span>
                </div>
                <div class="counselor-experience">{{ counselor.experience }} · 리뷰 {{ counselor.reviewCount }}</div>
              </div>
            </div>
            <div class="counselor-desc-small">
              {{ counselor.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div class="empty-state" v-if="counselors.length === 0 && !isLoading">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">검색 결과가 없습니다</div>
        <div class="empty-desc">다른 키워드로 검색해보세요</div>
      </div>

      <!-- 로딩 상태 -->
      <div class="loading-state" v-if="isLoading">
        <div class="loading-spinner"></div>
        <div class="empty-title">검색 중...</div>
      </div>
    </main>

    <!-- 모달 오버레이 -->
    <div class="modal-overlay" @click="closeFilterModal" v-if="showModal"></div>

    <!-- 상담스타일 모달 -->
    <div class="filter-modal" :class="{ active: showModal && currentModal === 'style' }">
      <div class="modal-header">
        <h3 class="modal-title">상담 스타일 선택</h3>
        <p class="modal-subtitle">내 고민에 맞는 상담분야를 선택해 보세요.</p>
        <button class="close-button" @click="closeFilterModal">×</button>
      </div>
      <div class="modal-content">
        <div class="radio-group">
          <div
            class="radio-option"
            :class="{ selected: selectedModalOption === option.value }"
            v-for="option in styleOptions"
            :key="option.value"
            @click="selectModalOption(option.value)"
          >
            <div class="radio-button"></div>
            <span class="radio-label">{{ option.label }}</span>
          </div>
        </div>
        <button class="modal-action" @click="applyStyleFilter">선택 완료</button>
      </div>
    </div>

    <!-- 상담주제 모달 -->
    <div class="filter-modal" :class="{ active: showModal && currentModal === 'topic' }">
      <div class="modal-header">
        <h3 class="modal-title">상담 주제 선택</h3>
        <p class="modal-subtitle">가장 고민되는 분야의 전문가를 찾아보세요.</p>
        <button class="close-button" @click="closeFilterModal">×</button>
      </div>
      <div class="modal-content">
        <div class="radio-group">
          <div
            class="radio-option"
            :class="{ selected: selectedModalOption === option.value }"
            v-for="option in topicOptions"
            :key="option.value"
            @click="selectModalOption(option.value)"
          >
            <div class="radio-button"></div>
            <span class="radio-label">{{ option.label }}</span>
          </div>
        </div>
        <button class="modal-action" @click="applyTopicFilter">선택 완료</button>
      </div>
    </div>

    <!-- 정렬 모달 -->
    <div class="filter-modal" :class="{ active: showModal && currentModal === 'sort' }">
      <div class="modal-header">
        <h3 class="modal-title">정렬 기준</h3>
        <p class="modal-subtitle">원하는 순서로 상담사 리스트를 정렬합니다.</p>
        <button class="close-button" @click="closeFilterModal">×</button>
      </div>
      <div class="modal-content">
        <div class="radio-group">
          <div
            class="radio-option"
            :class="{ selected: selectedModalOption === option.value }"
            v-for="option in sortOptions"
            :key="option.value"
            @click="selectModalOption(option.value)"
          >
            <div class="radio-button"></div>
            <span class="radio-icon">{{ option.icon }}</span>
            <span class="radio-label">{{ option.label }}</span>
          </div>
        </div>
        <button class="modal-action" @click="applySortFilter">적용하기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

definePageMeta({
  requiresAuth: false
})

// 반응형 데이터
const searchQuery = ref('')
const isLoading = ref(false)
const showModal = ref(false)
const currentModal = ref('')
const selectedModalOption = ref('')

// 필터 상태
const activeFilters = ref([
  { text: '상담가능' },
  { text: '20년 이상' }
])

const selectedFilters = ref({
  style: '',
  topic: '',
  sort: ''
})

// 필터 옵션들
const styleOptions = [
  { value: 'tarot', label: '타로' },
  { value: 'saju', label: '사주/신점' },
  { value: 'fortune', label: '운세' }
]

const topicOptions = [
  { value: 'reunion', label: '재회/이별' },
  { value: 'love', label: '짝사랑/연애' },
  { value: 'career', label: '이직/취업' },
  { value: 'business', label: '사업/재물' }
]

const sortOptions = [
  { value: 'return-rate', label: '재상담률 높은 순', icon: '🔄' },
  { value: 'review', label: '리뷰 높은 순', icon: '⭐' },
  { value: 'price', label: '가격 낮은 순', icon: '💰' }
]

// 목업 상담사 데이터
const counselors = ref([
  {
    id: 1,
    name: '명월 선생님',
    avatar: '🌙',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '타로 마스터',
    experience: '20년 경력',
    tags: ['🔮 타로', '💕 연애', '🔄 재회'],
    description: '모든 인연에는 의미가 있습니다. 20년간 수만건의 상담을 통해 쌓은 통찰력으로 당신의 마음을 읽어드립니다.',
    rating: 4.9,
    reviewCount: 3456,
    price: 3900
  },
  {
    id: 2,
    name: '천기누설 선생님',
    avatar: '🔥',
    image: '/images/cs_2.png',
    isOnline: true,
    specialty: '사주/신점 전문',
    experience: '30년 경력',
    tags: ['📅 사주', '✨ 신점', '💼 취업'],
    description: '정통 사주명리학과 신점을 통해 인생의 큰 그림을 그려드립니다.',
    rating: 4.8,
    reviewCount: 2892,
    price: 4500
  },
  {
    id: 3,
    name: '별빛 선생님',
    avatar: '💫',
    image: '/images/cs_2.png',
    isOnline: false,
    specialty: '신통력',
    experience: '15년 경력',
    tags: ['🌟 신통력', '💰 재물', '🍀 행운'],
    description: '타고난 영감과 신통력으로 막힌 운을 뚫어드립니다.',
    rating: 5.0,
    reviewCount: 1234,
    price: 5900
  }
])

const totalCount = computed(() => counselors.value.length)

// 메서드들
const openFilterModal = (type: string) => {
  currentModal.value = type
  selectedModalOption.value = ''
  showModal.value = true
}

const closeFilterModal = () => {
  showModal.value = false
  currentModal.value = ''
  selectedModalOption.value = ''
}

const selectModalOption = (value: string) => {
  selectedModalOption.value = value
}

const applyStyleFilter = () => {
  if (selectedModalOption.value) {
    const option = styleOptions.find(opt => opt.value === selectedModalOption.value)
    if (option) {
      selectedFilters.value.style = option.label
    }
  }
  closeFilterModal()
}

const applyTopicFilter = () => {
  if (selectedModalOption.value) {
    const option = topicOptions.find(opt => opt.value === selectedModalOption.value)
    if (option) {
      selectedFilters.value.topic = option.label
    }
  }
  closeFilterModal()
}

const applySortFilter = () => {
  if (selectedModalOption.value) {
    const option = sortOptions.find(opt => opt.value === selectedModalOption.value)
    if (option) {
      selectedFilters.value.sort = option.label
    }
  }
  closeFilterModal()
}

const removeFilter = (index: number) => {
  activeFilters.value.splice(index, 1)
}

const goToCounselorDetail = (id: number) => {
  console.log('상담사 상세 페이지로 이동:', id)
  // 라우터 이동 로직 (기능 구현 시 추가)
}

// SEO 설정
useHead({
  title: '상담사 검색 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 상담사 검색. 타로, 사주, 운세 전문가를 찾아보세요.' }
  ]
})
</script>

<style scoped>
@import '~/assets/css/search-page.css';
</style>