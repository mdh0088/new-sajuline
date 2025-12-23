<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- SEO H1 태그 (시각적으로 숨김, 검색엔진용) -->
      <h1 class="sr-only">사주라인 - AI와 전문가의 사주, 타로, 신점 상담 플랫폼</h1>

      <!-- 히어로 배너 -->
      <MainBannerCarousel />

      <!-- 빠른 상담 카테고리 -->
      <section class="quick-consult">
        <div class="section-header">
          <h2 class="section-title">어떤 고민이 있으신가요?</h2>
          <NuxtLink to="/categories" class="see-all">전체보기 →</NuxtLink>
        </div>
        <div class="category-grid">
          <div
            v-for="category in categories"
            :key="category.name"
            class="category-card"
            @click="$router.push(category.path)"
          >
            <div class="category-icon">
              <img v-if="category.icon.startsWith('/')" :src="category.icon" :alt="category.name" />
              <span v-else>{{ category.icon }}</span>
            </div>
            <div class="category-name">{{ category.name }}</div>
          </div>
        </div>
      </section>

      <!-- 프로모션 배너 (주석처리) -->
      <!-- <section class="promotion-banner">
        <div class="promotion-content">
          <h3 class="promotion-title">🎉 첫 충전 100% 보너스</h3>
          <p class="promotion-desc">지금 충전하면 2배로 돌려드려요!</p>
          <button class="promotion-button" @click="$router.push('/point')">혜택 받기</button>
        </div>
      </section> -->

      <!-- 실시간 인기 상담사 - 그리드 레이아웃 -->
      <section class="counselor-grid">
        <div class="section-header">
          <h2 class="section-title">실시간 인기 상담사</h2>
        </div>

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
          <div class="filter-chips-right">
            <div
              v-for="(filter, index) in categoryFilters"
              :key="typeof filter === 'string' ? filter : filter.text"
              :class="['chip', { active: activeCategoryFilter === index }]"
              @click="setActiveCategoryFilter(index)"
            >
              <img v-if="typeof filter === 'object' && filter.icon" :src="filter.icon" :alt="filter.text" class="chip-icon" />
              <span>{{ typeof filter === 'string' ? filter : filter.text }}</span>
            </div>
          </div>
        </div>

        <!-- 상담사 카드들 -->
        <div class="counselor-grid-container">
          <CounselorCardCompact
            v-for="c in items"
            :key="c.counselor_code"
            :counselor="c"
          />
        </div>

        <!-- 무한 스크롤 센티넬 -->
        <div ref="sentinelRef" style="height: 1px; width: 100%;"></div>

        <!-- 로딩 표시 -->
        <div v-if="isLoading" class="loading-more">
          <div class="loading-spinner-small"></div>
          <span>더 많은 상담사를 불러오는 중...</span>
        </div>
      </section>
    </main>

    <!-- 플로팅 버튼 -->
    <!-- <button class="floating-button" @click="openChat">💬</button> -->
  </div>
</template>


definePageMeta({
  requiresAuth: false
})

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useHead, useRoute, useSeoMeta } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'
import MainBannerCarousel from '~/components/home/MainBannerCarousel.vue'
import CounselorCardCompact from '~/components/counselor/CounselorCardCompact.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import type { CounselorSearchParams, CounselorSearchItem } from '~/types/counselor/search'

const { notifySuccess, notifyInfo } = useNotify()

// SEO 메타 데이터 설정
useSeoMeta({
  title: '사주라인 - 당신의 운명을 밝히는 빛',
  description: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주, 타로, 신점 상담을 받아보세요. 실시간 채팅 상담과 AI 운세 분석 서비스를 제공합니다.',
  keywords: '사주상담, 타로상담, 신점, AI운세, 실시간상담, 온라인상담, 사주라인, 운세, 점집',
  ogTitle: '사주라인 - 당신의 운명을 밝히는 빛',
  ogDescription: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 신뢰할 수 있는 전문가와 실시간 상담을 시작하세요.',
  ogImage: 'https://sajuline.com/images/og-image.jpg',
  ogUrl: 'https://sajuline.com',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: '사주라인 - 당신의 운명을 밝히는 빛',
  twitterDescription: 'AI와 전문가의 하이브리드 사주 상담 플랫폼',
  twitterImage: 'https://sajuline.com/images/og-image.jpg',
  robots: 'index,follow'
})

// JSON-LD 구조화 데이터
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "사주라인",
  "url": "https://sajuline.com",
  "logo": "https://sajuline.com/logo.png",
  "description": "AI와 전문가의 하이브리드 사주 상담 플랫폼",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+82-2-6212-0465",
    "contactType": "customer service",
    "availableLanguage": "Korean"
  },
  "sameAs": [
    "https://www.instagram.com/sajuline",
    "https://pf.kakao.com/_xjPxlxgC"
  ]
}

const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "사주라인",
  "url": "https://sajuline.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://sajuline.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}

useHead({
  link: [{ rel: 'canonical', href: 'https://sajuline.com' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(organizationSchema)
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(websiteSchema)
    }
  ]
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: false
})

// 사용자 포인트 (주석처리 - 미사용)
// const userPoints = ref(1200)

// 카테고리 목록
const categories = ref([
  { name: '타로', path: '/categories?category=TARO', icon: '/images/tarot.png' },
  { name: '사주', path: '/categories?category=SAJU', icon: '/images/shaman.png' },
  { name: '신점', path: '/categories?category=FORTUNE', icon: '/images/fortune.png' },
  { name: '전체 후기', path: '/reviews', icon: '/images/review.png' }
])

// 필터 목록 - 상태 필터와 카테고리 필터 분리
const statusFilters = ref(['전체', '상담중', '부재중', '대기중'])
const categoryFilters = ref(['전체', { text: 'HOT', icon: '/images/best.png' }, { text: '베스트', icon: '/images/Best_1.png' }, { text: '신규', icon: '/images/new.png' }])
const activeStatusFilter = ref(0)
const activeCategoryFilter = ref(0)

// 상담사 목록 (SSR 호환 API 연동)
const params = ref<CounselorSearchParams>({ page: 1, limit: 10, cs_status: null, is_best: null, is_new: null, cs_specialties: null, cs_keywords: null, search_name: null })
const { searchPublic, getAllCounselorCodes, searchPublicByCodes } = useCounselorQueries()

// 페이징 처리를 위한 로컬 상태
const items = ref<CounselorSearchItem[]>([])
const totalPages = ref(1)
const isLoading = ref(false)

// 셔플된 상담사 코드 목록 (필터 없을 때 사용)
const allCounselorCodes = ref<string[]>([])
const codesInitialized = ref(false)

// 필터가 적용되어 있는지 확인하는 computed
const hasFilters = computed(() => {
  return params.value.cs_status !== null ||
    params.value.is_best === true ||
    params.value.is_new === true
})

// 상담사 목록 로드 함수
async function loadCounselors(page: number, isAppend = false) {
  if (isLoading.value) return
  isLoading.value = true

  try {
    let result

    if (hasFilters.value) {
      // 필터가 있으면 기존 API 사용 (셔플 없음)
      result = await searchPublic({ ...params.value, page })
    } else {
      // 필터가 없으면 m_codes 기반 API 사용
      if (!codesInitialized.value || allCounselorCodes.value.length === 0) {
        // 코드 목록이 없으면 먼저 가져오기
        const codesData = await getAllCounselorCodes()
        allCounselorCodes.value = codesData.codes
        codesInitialized.value = true
      }

      // 현재 페이지에 해당하는 코드들만 추출
      const limit = params.value.limit || 10
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

    if (isAppend && page > 1) {
      items.value = [...items.value, ...result.items]
    } else {
      items.value = result.items
    }
    totalPages.value = result.total_pages
  } catch (e) {
    console.error('상담사 목록 로드 실패:', e)
  } finally {
    isLoading.value = false
  }
}

// params 변경 감지 (필터 변경 시)
watch(() => [params.value.cs_status, params.value.is_best, params.value.is_new], () => {
  // 필터가 변경되면 1페이지부터 다시 로드
  params.value.page = 1
  items.value = []
  loadCounselors(1, false)
}, { deep: true })

// 초기 로드 (SSR에서는 클라이언트 마운트 시)
onMounted(() => {
  loadCounselors(1, false)
})

// 기존 목업 데이터 제거
const counselors = ref([
  {
    id: 1,
    name: '명월 선생님',
    avatar: '🌙',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '전화타로',
    experience: '20년 경력',
    tags: ['🔮 타로', '💕 연애', '🔄 재회'],
    description: '모든 인연에는 의미가 있습니다. 20년간 수만건의 상담을 통해 쌓은 통찰력으로 당신의 마음을 읽어드립니다.',
    rating: 4.9,
    reviewCount: 3456,
    price: 3900,
    discount: '첫상담 30% 할인'
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
    description: '정통 사주명리학과 신점을 통해 인생의 큰 그림을 그려드립니다. 중요한 결정을 앞두고 계신다면 명확한 방향을 제시해드립니다.',
    rating: 4.8,
    reviewCount: 2892,
    price: 4500,
    discount: null
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
    description: '타고난 영감과 신통력으로 막힌 운을 뚫어드립니다. 재물운, 사업운 상담에 특화되어 있으며 로또 당첨자를 다수 배출한 행운의 상담사입니다.',
    rating: 5.0,
    reviewCount: 1234,
    price: 5900,
    discount: '예약대기 5명'
  },
  {
    id: 4,
    name: '금성 선생님',
    avatar: '🌸',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '연애운 전문',
    experience: '12년 경력',
    tags: ['💕 연애', '💘 인연', '💍 결혼'],
    description: '연애와 인연에 대한 깊은 통찰력을 바탕으로 진정한 사랑을 찾아드립니다. 복잡한 연애 상황도 명확하게 해결해드려요.',
    rating: 4.7,
    reviewCount: 2156,
    price: 3200,
    discount: null
  },
  {
    id: 5,
    name: '수정 선생님',
    avatar: '💎',
    image: '/images/cs_2.png',
    isOnline: false,
    specialty: '재물운 전문',
    experience: '18년 경력',
    tags: ['💰 재물', '💼 사업', '📈 투자'],
    description: '재물운과 사업운을 전문으로 하는 상담사입니다. 투자 타이밍과 사업 방향에 대한 정확한 조언을 드립니다.',
    rating: 4.6,
    reviewCount: 1789,
    price: 4100,
    discount: null
  },
  {
    id: 6,
    name: '미래 선생님',
    avatar: '🔮',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '타로/사주',
    experience: '25년 경력',
    tags: ['🔮 타로', '📅 사주', '🔮 미래'],
    description: '타로와 사주를 결합한 독특한 방식으로 미래를 읽어드립니다. 정확한 예언과 실용적인 조언을 제공합니다.',
    rating: 4.9,
    reviewCount: 3234,
    price: 3800,
    discount: null
  },
  {
    id: 7,
    name: '별빛 선생님',
    avatar: '✨',
    image: '/images/cs_2.png',
    isOnline: false,
    specialty: '신점 전문',
    experience: '14년 경력',
    tags: ['✨ 신점', '🔮 영감', '🌟 직감'],
    description: '타고난 직감력과 영감으로 정확한 신점을 봐드립니다. 복잡한 상황도 명확하게 해석해드려요.',
    rating: 4.5,
    reviewCount: 1567,
    price: 3500,
    discount: null
  },
  {
    id: 8,
    name: '꽃길 선생님',
    avatar: '🌺',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '인연운 전문',
    experience: '16년 경력',
    tags: ['🌺 인연', '💕 만남', '💍 결혼'],
    description: '인연과 만남에 대한 깊은 이해를 바탕으로 진정한 인연을 찾아드립니다. 운명적인 만남의 시기를 알려드려요.',
    rating: 4.8,
    reviewCount: 2345,
    price: 4200,
    discount: null
  }
])

// 라우트 처리
const route = useRoute()

// 페이지 로드 시 처리
onMounted(() => {
  if (route.query.message === 'login_success') {
    notifySuccess('🎉 사주라인에 오신 것을 환영합니다!')
  } else if (route.query.message === 'social_login_success') {
    notifySuccess('🚀 간편하게 로그인되었습니다!')
  }
})

// 메서드들
function setActiveStatusFilter(index: number) {
  activeStatusFilter.value = index
  const map = [null, '2', '3', '1'] as (string | null)[]
  params.value.cs_status = map[index] || null
  // watch에서 loadCounselors 호출됨
}

function setActiveCategoryFilter(index: number) {
  activeCategoryFilter.value = index
  params.value.is_best = index === 2 ? true : null
  params.value.is_new = index === 3 ? true : null
  // watch에서 loadCounselors 호출됨
}

// function startFreeTrial() {
//   notifyInfo('🎉 첫 상담 무료체험을 시작합니다!')
//   // TODO: 무료체험 로직 구현
// }

function requestAIFortune() {
  notifyInfo('🤖 AI 운세를 준비 중입니다...')
  // TODO: AI 운세 요청 로직
}

function openChat() {
  notifyInfo('💬 채팅 상담을 시작합니다!')
  // TODO: 채팅 열기 로직
}

// 무한 스크롤 센티넬 ref
const sentinelRef = ref<HTMLElement | null>(null)

// 무한 스크롤 처리 (클라이언트에서만 실행)
onMounted(() => {
  // IntersectionObserver 설정
  if (sentinelRef.value) {
    const io = new IntersectionObserver(async (entries) => {
      const entry = entries[0]
      if (!entry || !entry.isIntersecting) return
      if (isLoading.value) return
      const currentPage = params.value.page || 1
      if (currentPage >= totalPages.value) return

      // 다음 페이지 로드
      const nextPage = currentPage + 1
      params.value.page = nextPage
      await loadCounselors(nextPage, true)
    }, {
      rootMargin: '100px' // 100px 전에 미리 로드
    })

    io.observe(sentinelRef.value)
  }
})
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';
@import '~/assets/css/banner/main-banner.css';

/* 추가 컴포넌트별 스타일이 필요한 경우 여기에 작성 */
</style>
