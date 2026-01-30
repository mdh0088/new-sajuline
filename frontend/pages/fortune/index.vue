<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 페이지 헤더 (Task 2.5: 동적 헤더) -->
    <header class="px-5 pt-6 pb-4">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <span>{{ pageIcon }}</span>
        {{ pageTitle }}
      </h1>
      <p class="text-sm text-white/60 mt-1">{{ formattedDate }}</p>
    </header>

    <!-- 탭 컴포넌트 (AC 1) - Code Review: v-model만 사용 -->
    <FortuneTabs v-model="activeTab" />

    <!-- 운세 콘텐츠 영역 (스와이프 제스처 지원) -->
    <div
      id="fortune-content"
      :aria-labelledby="`fortune-tab-${activeTab}`"
      role="tabpanel"
      class="transition-transform duration-300"
      :style="{ transform: `translateX(${swipeOffset}px)` }"
      @touchstart.passive="handleTouchStart"
      @touchmove.passive="handleTouchMove"
      @touchend.passive="handleTouchEnd"
    >
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="px-5 py-6">
        <FortuneCardSkeleton />
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="px-5 py-6">
        <FortuneError
          :message="errorMessage"
          :is-saju-required="isSajuRequired"
          @retry="handleRetry"
        />
      </div>

      <!-- 운세 카드 -->
      <FortuneCard v-else-if="fortune" :fortune="fortune" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import FortuneTabs from '~/components/fortune/FortuneTabs.vue'
import FortuneCard from '~/components/fortune/FortuneCard.vue'
import FortuneCardSkeleton from '~/components/fortune/FortuneCardSkeleton.vue'
import FortuneError from '~/components/fortune/FortuneError.vue'
import { useFortuneApi } from '~/composables/api/useFortune'
import { getTodayKoreanDate } from '~/utils/dateFormat'
import type { FortuneType } from '~/types/fortune'
import { FORTUNE_TYPES } from '~/types/fortune'

// 인증 미들웨어 설정 (AC 4)
definePageMeta({
  requiresAuth: true,
  requireRole: 'user'
})

// Router 설정 (Task 2.3, 2.4)
const route = useRoute()
const router = useRouter()

// =============================================================================
// 타입 가드 유틸리티 (Code Review: 타입 안전성 개선)
// =============================================================================

/**
 * FortuneType 유효성 검사
 */
const isValidFortuneType = (value: unknown): value is FortuneType => {
  return typeof value === 'string' && FORTUNE_TYPES.includes(value as FortuneType)
}

/**
 * API 에러 응답에서 에러 코드 추출
 */
interface ApiErrorData {
  error?: { code?: string; message?: string }
  detail?: { code?: string; message?: string }
}

const extractErrorCode = (err: unknown): string | undefined => {
  if (!err || typeof err !== 'object') return undefined

  const errorObj = err as { data?: ApiErrorData }
  const errorData = errorObj.data

  if (!errorData) return undefined

  return errorData.error?.code ?? errorData.detail?.code
}

// =============================================================================
// 상태 관리
// =============================================================================

// URL에서 초기 탭 타입 추출 (AC 4: URL 쿼리 파라미터 동기화)
const getInitialTab = (): FortuneType => {
  const queryType = route.query.type
  if (isValidFortuneType(queryType)) {
    return queryType
  }
  return 'daily'
}

const activeTab = ref<FortuneType>(getInitialTab())

// 운세 API composable 사용 (Task 2.2: useFortune 통합 composable)
const { useFortune, getFortuneErrorMessage, invalidateFortuneCache } = useFortuneApi()
const { data: fortune, isLoading, error, refetch } = useFortune(activeTab)

// =============================================================================
// 페이지 메타데이터
// =============================================================================

// 페이지 타이틀 및 아이콘 동적 변경 (Task 2.5)
const pageTitle = computed(() => {
  const titles: Record<FortuneType, string> = {
    daily: '오늘의 운세',
    weekly: '이번 주 운세',
    monthly: '이번 달 운세',
    yearly: '올해의 운세',
  }
  return titles[activeTab.value]
})

const pageIcon = computed(() => {
  const icons: Record<FortuneType, string> = {
    daily: '🔮',
    weekly: '📅',
    monthly: '🌙',
    yearly: '⭐',
  }
  return icons[activeTab.value]
})

// SEO 메타데이터 동적 설정 (Task 2.6)
const seoTitle = computed(() => `${pageTitle.value} - 사주라인`)
const seoDescription = computed(() => {
  const descriptions: Record<FortuneType, string> = {
    daily: 'AI가 분석한 오늘의 일일 운세를 확인하세요. 총운, 애정운, 직장운, 건강운, 재물운을 한눈에 볼 수 있습니다.',
    weekly: 'AI가 분석한 이번 주 운세를 확인하세요. 주간 총운과 세부 운세를 확인할 수 있습니다.',
    monthly: 'AI가 분석한 이번 달 운세를 확인하세요. 월간 총운과 세부 운세를 확인할 수 있습니다.',
    yearly: 'AI가 분석한 올해의 운세를 확인하세요. 연간 총운과 세부 운세를 확인할 수 있습니다.',
  }
  return descriptions[activeTab.value]
})

useSeoMeta({
  title: seoTitle,
  description: seoDescription,
  ogTitle: seoTitle,
  ogDescription: seoDescription,
})

// 오늘 날짜 포맷팅
const formattedDate = computed(() => getTodayKoreanDate())

// 에러 메시지 계산
const errorMessage = computed(() => {
  return error.value ? getFortuneErrorMessage(error.value) : null
})

// 사주 정보 미등록 여부 확인
const isSajuRequired = computed(() => {
  if (!error.value) return false
  return extractErrorCode(error.value) === 'SAJU_INFO_REQUIRED'
})

// =============================================================================
// 이벤트 핸들러
// =============================================================================

// URL 쿼리 파라미터 변경 감지 (뒤로가기 대응) - Code Review: watch로 URL 동기화
watch(() => route.query.type, (newType) => {
  if (isValidFortuneType(newType) && newType !== activeTab.value) {
    activeTab.value = newType
  }
})

// 탭 변경 시 URL 업데이트 - Code Review: v-model 변경 감지
watch(activeTab, (type) => {
  if (route.query.type !== type) {
    router.push({ query: { type } })
  }
})

// 다시 시도 핸들러 (캐시 무효화 후 재요청)
const handleRetry = async () => {
  invalidateFortuneCache(activeTab.value)
  await refetch()
}

// =============================================================================
// 모바일 스와이프 제스처 (AC 6, Task 4)
// =============================================================================

const SWIPE_THRESHOLD = 30 // 최소 스와이프 거리 (px)

let touchStartX = 0
let touchStartY = 0
let isSwiping = false

const swipeOffset = ref(0)

const handleTouchStart = (e: TouchEvent) => {
  const touch = e.changedTouches[0]
  if (!touch) return
  touchStartX = touch.screenX
  touchStartY = touch.screenY
  isSwiping = false
}

const handleTouchMove = (e: TouchEvent) => {
  const touch = e.changedTouches[0]
  if (!touch) return

  const touchMoveX = touch.screenX
  const touchMoveY = touch.screenY

  const diffX = touchMoveX - touchStartX
  const diffY = Math.abs(touchMoveY - touchStartY)

  // 수평 스와이프가 수직 스와이프보다 큰 경우에만 스와이프로 처리
  if (Math.abs(diffX) > diffY && Math.abs(diffX) > 10) {
    isSwiping = true
    // 스와이프 중 피드백 애니메이션 (최대 50px)
    swipeOffset.value = Math.max(-50, Math.min(50, diffX * 0.3))
  }
}

const handleTouchEnd = (e: TouchEvent) => {
  const touch = e.changedTouches[0]
  if (!touch) return

  const touchEndX = touch.screenX
  const diff = touchStartX - touchEndX

  // 스와이프 오프셋 초기화
  swipeOffset.value = 0

  if (!isSwiping || Math.abs(diff) < SWIPE_THRESHOLD) return

  const currentIndex = FORTUNE_TYPES.indexOf(activeTab.value)

  if (diff > 0 && currentIndex < FORTUNE_TYPES.length - 1) {
    // 왼쪽 스와이프 → 다음 탭 (일 → 주 → 월 → 연)
    const nextTab = FORTUNE_TYPES[currentIndex + 1]
    if (nextTab) {
      activeTab.value = nextTab
    }
  } else if (diff < 0 && currentIndex > 0) {
    // 오른쪽 스와이프 → 이전 탭 (연 → 월 → 주 → 일)
    const prevTab = FORTUNE_TYPES[currentIndex - 1]
    if (prevTab) {
      activeTab.value = prevTab
    }
  }
}
</script>
