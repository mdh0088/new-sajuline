<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
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
            <div class="category-icon">{{ category.icon }}</div>
            <div class="category-name">{{ category.name }}</div>
          </div>
        </div>
      </section>

      <!-- 프로모션 배너 -->
      <section class="promotion-banner">
        <div class="promotion-content">
          <h3 class="promotion-title">🎉 첫 충전 100% 보너스</h3>
          <p class="promotion-desc">지금 충전하면 2배로 돌려드려요!</p>
          <button class="promotion-button" @click="$router.push('/point')">혜택 받기</button>
        </div>
      </section>

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
              :key="filter"
              :class="['chip', { active: activeCategoryFilter === index }]"
              @click="setActiveCategoryFilter(index)"
            >
              {{ filter }}
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
import { useHead, useRoute } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'
import MainBannerCarousel from '~/components/home/MainBannerCarousel.vue'
import CounselorCardCompact from '~/components/counselor/CounselorCardCompact.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import type { CounselorSearchParams, CounselorSearchItem } from '~/types/counselor/search'

const { notifySuccess, notifyInfo } = useNotify()

// SEO 및 메타 데이터 설정
useHead({
  title: '사주라인 - 당신의 운명을 밝히는 빛',
  meta: [
    { name: 'description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:title', content: '사주라인 - 당신의 운명을 밝히는 빛' },
    { property: 'og:description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:image', content: '/images/og-image.jpg' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
})

// 페이지 메타 설정
definePageMeta({
  requiresAuth: false
})

// 사용자 포인트
const userPoints = ref(1200)

// 카테고리 목록
const categories = ref([
  { name: '타로', path: '/categories?category=tarot', icon: '🔮' },
  { name: '사주', path: '/categories?category=saju', icon: '📜' },
  { name: '신점', path: '/categories?category=divine', icon: '✨' },
  { name: '연애운', path: '/categories?category=love', icon: '💕' },
  { name: '재물운', path: '/categories?category=money', icon: '💰' },
  { name: '직장운', path: '/categories?category=work', icon: '💼' }
])

// 필터 목록 - 상태 필터와 카테고리 필터 분리
const statusFilters = ref(['전체', '상담중', '부재중', '대기중'])
const categoryFilters = ref(['전체', '🔥 HOT', '⭐ 베스트', '🆕 신규'])
const activeStatusFilter = ref(0)
const activeCategoryFilter = ref(0)

// 상담사 목록 (API 연동)
const items = ref<CounselorSearchItem[]>([])
const params = ref<CounselorSearchParams>({ page: 1, limit: 10, cs_status: null, is_best: null, is_new: null, cs_specialties: null, cs_keywords: null, search_name: null })
const totalPages = ref(1)
const isLoading = ref(false)
const { usePublicSearch, searchPublic } = useCounselorQueries()
const { data: pageData } = usePublicSearch(params, { enabled: false })

// 기존 목업 데이터 제거
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
  resetAndFetch()
}

function setActiveCategoryFilter(index: number) {
  activeCategoryFilter.value = index
  params.value.is_best = index === 2 ? true : null
  params.value.is_new = index === 3 ? true : null
  resetAndFetch()
}

function startFreeTrial() {
  notifyInfo('🎉 첫 상담 무료체험을 시작합니다!')
  // TODO: 무료체험 로직 구현
}

function requestAIFortune() {
  notifyInfo('🤖 AI 운세를 준비 중입니다...')
  // TODO: AI 운세 요청 로직
}

function openChat() {
  notifyInfo('💬 채팅 상담을 시작합니다!')
  // TODO: 채팅 열기 로직
}

async function resetAndFetch() {
  items.value = []
  params.value.page = 1
  await fetchNext()
}

async function fetchNext() {
  if (isLoading.value) return
  isLoading.value = true
  try {
    const res = await searchPublic(params.value)
    totalPages.value = Math.max(1, res.total_pages || 1)
    if ((params.value.page || 1) === 1) items.value = res.items
    else items.value = [...items.value, ...res.items]
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await resetAndFetch()
  const sentinel = document.createElement('div')
  sentinel.style.height = '1px'
  sentinel.setAttribute('data-sentinel', 'counselor')
  document.body.appendChild(sentinel)
  const io = new IntersectionObserver(async (entries) => {
    const entry = entries[0]
    if (!entry || !entry.isIntersecting) return
    if (isLoading.value) return
    if ((params.value.page || 1) >= totalPages.value) return
    params.value.page = (params.value.page || 1) + 1
    await fetchNext()
  })
  io.observe(sentinel)
})
</script>

<style scoped>
/* main-page.css 파일을 import하여 사용 */
@import '~/assets/css/main-page.css';
@import '~/assets/css/banner/main-banner.css';

/* 추가 컴포넌트별 스타일이 필요한 경우 여기에 작성 */
</style>
