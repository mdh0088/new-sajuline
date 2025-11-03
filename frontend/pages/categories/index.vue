<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 카테고리 탭 -->
    <section class="category-tabs">
      <button
        class="category-tab"
        :class="{ active: selectedCategory === category.value }"
        v-for="category in categories"
        :key="category.value"
        @click="selectCategory(category.value)"
      >
        <span class="tab-icon">{{ category.icon }}</span>
        <span class="tab-label">{{ category.label }}</span>
      </button>
    </section>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 상태 필터 칩 -->
      <div class="filter-chips-container">
        <div class="filter-chips-left">
          <div
            v-for="(filter, index) in statusFilters"
            :key="filter"
            :class="['chip', { active: activeStatusFilter === index }]"
            @click="setActiveStatusFilter(index)"
          >
            {{ filter }}
          </div>
        </div>
      </div>

      <!-- 검색 결과 정보 -->
      <div class="search-info">
        <span class="result-count">총 <strong>{{ totalCount }}명</strong>의 상담사</span>
      </div>

      <!-- 상담사 리스트 -->
      <div class="counselor-grid-container">
        <CounselorCardCompact
          v-for="counselor in counselors"
          :key="counselor.counselor_code"
          :counselor="counselor"
        />
      </div>

      <!-- 빈 상태 -->
      <div class="empty-state" v-if="counselors.length === 0 && !isLoading">
        <div class="empty-icon">😔</div>
        <div class="empty-title">해당 카테고리의 상담사가 없습니다</div>
        <div class="empty-desc">다른 카테고리를 선택해보세요</div>
      </div>

      <!-- 로딩 상태 -->
      <div class="loading-state" v-if="isLoading">
        <div class="loading-spinner"></div>
        <div class="empty-title">검색 중...</div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CounselorCardCompact from '~/components/counselor/CounselorCardCompact.vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import type { CounselorSearchParams, CounselorSearchItem } from '~/types/counselor/search'

definePageMeta({
  requiresAuth: false
})

const router = useRouter()
const route = useRoute()

// 반응형 데이터
const isLoading = ref(false)
const selectedCategory = ref('all')
const activeStatusFilter = ref(0)

// 카테고리 목록 (타로/사주/신점만)
const categories = [
  { value: 'all', label: '전체', icon: '🌟' },
  { value: 'TARO', label: '타로', icon: '🔮' },
  { value: 'SAJU', label: '사주', icon: '📜' },
  { value: 'FORTUNE', label: '신점', icon: '✨' }
]

// 상태 필터
const statusFilters = ref(['전체', '상담중', '부재중', '대기중'])

// 상태 필터 매핑 (인덱스 → cs_status 값)
// 0: 전체(null), 1: 상담중('2'), 2: 부재중('3'), 3: 대기중('1')
const statusMap = [null, '2', '3', '1']

// API 검색 결과
const { searchPublic } = useCounselorQueries()
const counselors = ref<CounselorSearchItem[]>([])
const searchParams = ref<CounselorSearchParams>({
  page: 1,
  limit: 10,
  cs_status: null,
  is_best: null,
  is_new: null,
  cs_specialties: null,
  cs_keywords: null,
  search_name: null
})
const totalPages = ref(1)
const totalCount = ref(0)

// 카테고리 선택
const selectCategory = (category: string) => {
  selectedCategory.value = category

  // URL 업데이트 (전체인 경우 쿼리 파라미터 제거)
  if (category === 'all') {
    router.replace('/categories')
  } else {
    router.replace(`/categories?category=${category}`)
  }

  // 선택된 탭으로 스크롤
  scrollToSelectedTab(category)
}

// 상태 필터 선택
const setActiveStatusFilter = (index: number) => {
  activeStatusFilter.value = index
}

// 선택된 탭으로 스크롤
const scrollToSelectedTab = (category: string) => {
  setTimeout(() => {
    const tabsContainer = document.querySelector('.category-tabs')
    const activeTab = document.querySelector('.category-tab.active')

    if (tabsContainer && activeTab) {
      const containerRect = tabsContainer.getBoundingClientRect()
      const tabRect = activeTab.getBoundingClientRect()

      // 탭이 화면 밖에 있으면 스크롤
      if (tabRect.right > containerRect.right || tabRect.left < containerRect.left) {
        activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
      }
    }
  }, 100)
}

// API 호출 함수
async function fetchNext() {
  if (isLoading.value) return
  isLoading.value = true

  try {
    // 카테고리 → cs_specialties 매핑
    const csSpecialties = selectedCategory.value !== 'all' && selectedCategory.value !== ''
      ? [selectedCategory.value]  // 'TARO' → ['TARO']
      : null

    // 상태 필터 → cs_status 매핑
    const csStatus = statusMap[activeStatusFilter.value]

    searchParams.value.cs_specialties = csSpecialties
    searchParams.value.cs_status = csStatus

    const result = await searchPublic(searchParams.value)

    totalPages.value = Math.max(1, result.total_pages || 1)
    totalCount.value = result.total || 0

    // 첫 페이지면 덮어쓰기, 아니면 추가 (무한 스크롤)
    if ((searchParams.value.page || 1) === 1) {
      counselors.value = result.items
    } else {
      counselors.value = [...counselors.value, ...result.items]
    }
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isLoading.value = false
  }
}

// 검색 초기화 및 재검색
async function resetAndFetch() {
  counselors.value = []
  searchParams.value.page = 1
  await fetchNext()
}

// Watch: 카테고리 변경 시 자동 검색
watch(() => selectedCategory.value, () => {
  resetAndFetch()
})

// Watch: 상태 필터 변경 시 자동 검색
watch(() => activeStatusFilter.value, () => {
  resetAndFetch()
})

// URL 쿼리 파라미터에서 초기 카테고리 설정
onMounted(async () => {
  const category = route.query.category as string
  if (category && categories.some(c => c.value === category)) {
    selectedCategory.value = category
    scrollToSelectedTab(category)
  }

  // 초기 로드
  await resetAndFetch()

  // 무한 스크롤 IntersectionObserver 설정
  const sentinel = document.createElement('div')
  sentinel.style.height = '1px'
  sentinel.setAttribute('data-sentinel', 'counselor-categories')
  document.body.appendChild(sentinel)

  const io = new IntersectionObserver(async (entries) => {
    const entry = entries[0]
    if (!entry || !entry.isIntersecting) return
    if (isLoading.value) return
    if ((searchParams.value.page || 1) >= totalPages.value) return

    searchParams.value.page = (searchParams.value.page || 1) + 1
    await fetchNext()
  })

  io.observe(sentinel)
})

// URL 쿼리 파라미터 변경 감지
watch(() => route.query.category, (newCategory) => {
  if (newCategory && typeof newCategory === 'string' && categories.some(c => c.value === newCategory)) {
    selectedCategory.value = newCategory
    scrollToSelectedTab(newCategory)
  } else if (!newCategory) {
    selectedCategory.value = 'all'
    scrollToSelectedTab('all')
  }
})

// SEO 설정
useHead({
  title: '카테고리별 상담사 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 카테고리별 상담사. 타로, 사주, 신점 전문가를 찾아보세요.' }
  ]
})
</script>

<style scoped>
@import '~/assets/css/categories-page.css';
</style>
