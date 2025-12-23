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
          @keyup.enter="addSearchTag"
        >
        <span class="search-icon" @click="addSearchTag"><img src="/images/search.png" alt="검색" width="20" height="20" /></span>
      </div>
    </section>

    <!-- 필터 영역 -->
    <section class="filter-section">
      <!-- 활성 필터 (검색 태그) -->
      <div class="active-filters-container" v-if="searchTags.length > 0">
        <div class="active-filters">
          <div
            class="active-filter-tag"
            v-for="(tag, index) in searchTags"
            :key="index"
          >
            <span class="tag-text" @click="searchByTag(tag)">{{ tag }}</span>
            <span class="remove-filter" @click.stop="removeSearchTag(index)">×</span>
          </div>
        </div>
      </div>

      <!-- 필터 버튼들 -->
      <div class="filter-buttons">
        <button class="filter-btn" :class="{ active: selectedFilters.style }" @click="openFilterModal('style')">
          <img src="/images/setting.png" alt="필터" width="16" height="16" />
          <span>{{ styleFilterLabel }}</span>
        </button>
        <button class="filter-btn" :class="{ active: selectedFilters.sort }" @click="openFilterModal('sort')">
          <img src="/images/target.png" alt="정렬" width="16" height="16" />
          <span>{{ sortFilterLabel }}</span>
        </button>
      </div>
    </section>

    <!-- 메인 콘텐츠 -->
    <main class="main-content" :class="{ 'has-active-filters': searchTags.length > 0 }">
      <!-- 검색 결과 정보 -->
      <div class="search-info">
        <span class="result-count">총 <strong>{{ totalCount }}명</strong>의 상담사</span>
      </div>

      <!-- 상담사 리스트 -->
      <div class="counselor-grid-container">
        <CounselorCardCompact
          v-for="counselor in sortedCounselors"
          :key="counselor.counselor_code"
          :counselor="counselor"
        />
      </div>

      <!-- 빈 상태 -->
      <div class="empty-state" v-if="sortedCounselors.length === 0 && !isLoading">
        <div class="empty-icon"><img src="/images/search.png" alt="검색" width="48" height="48" /></div>
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
            <img :src="option.icon" :alt="option.label" class="radio-icon" width="20" height="20" />
            <span class="radio-label">{{ option.label }}</span>
          </div>
        </div>
        <button class="modal-action" @click="applySortFilter">적용하기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import CounselorCardCompact from '~/components/counselor/CounselorCardCompact.vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import type { CounselorSearchParams, CounselorSearchItem } from '~/types/counselor/search'

definePageMeta({
  requiresAuth: false
})

// 반응형 데이터
const searchQuery = ref('')
const searchTags = ref<string[]>([])
const isLoading = ref(false)
const showModal = ref(false)
const currentModal = ref('')
const selectedModalOption = ref('')

// 필터 상태
const selectedFilters = ref({
  style: '' as string,
  sort: '' as string
})

// 필터 옵션들
const styleOptions = [
  { value: '', label: '전체' },
  { value: 'TARO', label: '타로' },
  { value: 'SAJU', label: '사주/신점' },
  { value: 'FORTUNE', label: '운세' }
]

const sortOptions = [
  { value: '', label: '전체', icon: '/images/review.png' },
  { value: 'review', label: '리뷰 높은 순', icon: '/images/favorite.png' },
  { value: 'price', label: '가격 낮은 순', icon: '/images/point.png' }
]

// 필터 레이블 computed
const styleFilterLabel = computed(() => {
  // 빈 문자열이면 기본 레이블 표시
  if (!selectedFilters.value.style || selectedFilters.value.style === '') {
    return '상담 스타일'
  }
  const option = styleOptions.find(opt => opt.value === selectedFilters.value.style)
  return option ? option.label : '상담 스타일'
})

const sortFilterLabel = computed(() => {
  // 빈 문자열이면 기본 레이블 표시
  if (!selectedFilters.value.sort || selectedFilters.value.sort === '') {
    return '정렬'
  }
  const option = sortOptions.find(opt => opt.value === selectedFilters.value.sort)
  return option ? option.label : '정렬'
})

// API 검색 결과
const { searchPublic, getAllCounselorCodes, searchPublicByCodes } = useCounselorQueries()
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

// 셔플된 상담사 코드 목록 (필터 없을 때 사용)
const allCounselorCodes = ref<string[]>([])
const codesInitialized = ref(false)

// 필터가 적용되어 있는지 확인하는 computed
const hasFilters = computed(() => {
  return searchTags.value.length > 0 ||
    (selectedFilters.value.style !== '' && selectedFilters.value.style !== null)
})

// 검색 태그 추가 (최대 4개, FIFO)
const addSearchTag = () => {
  const trimmed = searchQuery.value.trim()
  if (!trimmed) return

  // 중복 체크
  if (searchTags.value.includes(trimmed)) {
    searchQuery.value = ''
    return
  }

  // 최대 4개 제한, FIFO
  if (searchTags.value.length >= 4) {
    searchTags.value.shift() // 첫 번째 요소 제거
  }

  searchTags.value.push(trimmed)
  searchQuery.value = ''
}

// 검색 태그 제거
const removeSearchTag = (index: number) => {
  searchTags.value.splice(index, 1)
}

// 태그 클릭 시 해당 태그만으로 검색
const searchByTag = (tag: string) => {
  // 클릭한 태그만 남기고 나머지 제거
  searchTags.value = [tag]
  // watch가 자동으로 검색 실행
}

// 다음 페이지 로드
async function fetchNext() {
  if (isLoading.value) return
  isLoading.value = true
  try {
    let result

    if (hasFilters.value) {
      // 필터가 있으면 기존 API 사용 (셔플 없음)
      // 검색 태그를 cs_keywords로 변환
      const csKeywords = searchTags.value.length > 0 ? searchTags.value : null

      // cs_specialties 매핑 (빈 문자열이면 null)
      const csSpecialties = selectedFilters.value.style && selectedFilters.value.style !== ''
        ? [selectedFilters.value.style]
        : null

      searchParams.value.cs_specialties = csSpecialties
      searchParams.value.cs_keywords = csKeywords

      result = await searchPublic(searchParams.value)
    } else {
      // 필터가 없으면 m_codes 기반 API 사용
      if (!codesInitialized.value || allCounselorCodes.value.length === 0) {
        // 코드 목록이 없으면 먼저 가져오기
        const codesData = await getAllCounselorCodes()
        allCounselorCodes.value = codesData.codes
        codesInitialized.value = true
      }

      // 현재 페이지에 해당하는 코드들만 추출
      const limit = searchParams.value.limit || 10
      const page = searchParams.value.page || 1
      const startIdx = (page - 1) * limit
      const endIdx = startIdx + limit
      const pageCodes = allCounselorCodes.value.slice(startIdx, endIdx)

      if (pageCodes.length === 0) {
        // 더 이상 데이터가 없음
        result = { items: [], page, limit, total: allCounselorCodes.value.length, total_pages: Math.ceil(allCounselorCodes.value.length / limit) }
      } else {
        result = await searchPublicByCodes({ page: 1, limit: pageCodes.length, m_codes: pageCodes })
        // total_pages는 전체 코드 수 기준으로 재계산
        result.total = allCounselorCodes.value.length
        result.total_pages = Math.ceil(allCounselorCodes.value.length / limit)
        result.page = page
      }
    }

    totalPages.value = Math.max(1, result.total_pages || 1)
    totalCount.value = result.total || 0

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

// 정렬된 상담사 목록
const sortedCounselors = computed(() => {
  const list = [...counselors.value]

  // 정렬 필터가 '전체'이거나 없으면 원래 순서 유지
  if (!selectedFilters.value.sort || selectedFilters.value.sort === '') {
    return list
  }

  if (selectedFilters.value.sort === 'review') {
    // 리뷰 수 내림차순
    return list.sort((a, b) => (b.review_count || 0) - (a.review_count || 0))
  } else if (selectedFilters.value.sort === 'price') {
    // 가격 오름차순
    return list.sort((a, b) => (a.after_amount || 0) - (b.after_amount || 0))
  }

  // 기본: 원래 순서
  return list
})

// Watch: 검색 태그 변경 시 자동 검색
watch(searchTags, () => {
  resetAndFetch()
}, { deep: true })

// Watch: 필터 변경 시 자동 검색
watch(() => selectedFilters.value.style, () => {
  resetAndFetch()
})

watch(() => selectedFilters.value.sort, () => {
  // 정렬은 클라이언트 사이드에서 처리되므로 API 호출 불필요
})

// 모달 메서드들
const openFilterModal = (type: string) => {
  currentModal.value = type
  selectedModalOption.value = selectedFilters.value[type as keyof typeof selectedFilters.value] || ''
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
  // 빈 문자열('')도 허용 ('전체' 옵션)
  selectedFilters.value.style = selectedModalOption.value
  closeFilterModal()
}

const applySortFilter = () => {
  // 빈 문자열('')도 허용 ('전체' 옵션)
  selectedFilters.value.sort = selectedModalOption.value
  closeFilterModal()
}

// 초기 로드 및 무한 스크롤 설정
onMounted(async () => {
  await resetAndFetch()

  // IntersectionObserver 설정 (index.vue와 동일한 패턴)
  const sentinel = document.createElement('div')
  sentinel.style.height = '1px'
  sentinel.setAttribute('data-sentinel', 'counselor-search')
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

// SEO 메타 데이터 설정
useSeoMeta({
  title: '상담사 검색 - 사주라인',
  description: '사주라인 상담사 검색 서비스입니다. 타로, 사주, 신점 전문가를 상담 분야, 평점, 경력으로 검색하고 실시간 상담을 시작하세요.',
  keywords: '상담사 검색, 타로 상담사, 사주 상담사, 신점 전문가, 운세 전문가, 실시간 상담',
  ogTitle: '상담사 검색 - 사주라인',
  ogDescription: '타로, 사주, 신점 전문가 검색. 상담 분야와 평점으로 최적의 상담사를 찾으세요.',
  ogImage: 'https://sajuline.com/images/og-search.jpg',
  ogUrl: 'https://sajuline.com/search',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: '상담사 검색 - 사주라인',
  twitterDescription: '타로, 사주, 신점 전문가 검색',
  twitterImage: 'https://sajuline.com/images/og-search.jpg',
  robots: 'index,follow'
})

useHead({
  link: [{ rel: 'canonical', href: 'https://sajuline.com/search' }]
})
</script>

<style scoped>
@import '~/assets/css/search-page.css';
</style>
