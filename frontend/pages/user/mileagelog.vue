<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <main class="pb-24">
      <!-- 검색 영역 -->
      <div class="search-section mx-5 mt-5">
        <div class="search-title">날짜 검색</div>
        <div class="date-search">
          <div class="date-input-wrapper" @click="openStartDatePicker">
            <input
              ref="startDateInput"
              type="date"
              class="date-input"
              v-model="startDate"
              placeholder="시작일"
            >
          </div>
          <span class="text-white/50">~</span>
          <div class="date-input-wrapper" @click="openEndDatePicker">
            <input
              ref="endDateInput"
              type="date"
              class="date-input"
              v-model="endDate"
              placeholder="종료일"
            >
          </div>
          <button class="search-btn" @click="searchTransactions">검색</button>
        </div>
      </div>

      <!-- 탭 섹션 -->
      <div class="mx-5 mt-5">
        <div class="p-1 rounded-xl bg-white/5 border border-white/10 flex">
          <button
            class="flex-1 py-3 rounded-lg text-sm font-semibold"
            :class="activeTab === 'earn' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''"
            @click="activeTab = 'earn'"
          >
            적립 내역
          </button>
          <button
            class="flex-1 py-3 rounded-lg text-sm font-semibold"
            :class="activeTab === 'usage' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''"
            @click="activeTab = 'usage'"
          >
            사용 내역
          </button>
        </div>

        <!-- 정렬 버튼 -->
        <div class="sort-buttons mt-4">
          <button
            class="sort-btn"
            :class="sortOrder === 'latest' ? 'active' : ''"
            @click="sortOrder = 'latest'"
          >
            최신순
          </button>
          <button
            class="sort-btn"
            :class="sortOrder === 'highest' ? 'active' : ''"
            @click="sortOrder = 'highest'"
          >
            높은순
          </button>
          <button
            class="sort-btn"
            :class="sortOrder === 'lowest' ? 'active' : ''"
            @click="sortOrder = 'lowest'"
          >
            낮은순
          </button>
        </div>

        <!-- PagedSection으로 리스트 표시 -->
        <PagedSection
          :items="itemsForActiveTab"
          :page="pageForActiveTab"
          :total-pages="totalPages"
          :loading="isLoading"
          :error="error"
          :empty-text="activeTab === 'earn' ? '적립 내역이 없습니다' : '사용 내역이 없습니다'"
          @update:page="onUpdatePage"
        >
          <template #default="{ items }">
            <!-- 적립 내역 카드 -->
            <div v-if="activeTab === 'earn'" class="transaction-list">
              <div
                v-for="transaction in items"
                :key="transaction.transaction_id"
                class="transaction-item"
              >
                <div class="trans-left">
                  <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                  <div class="trans-desc">
                    <span class="trans-icon"><img src="/images/milage.png" alt="마일리지" style="width: 16px; height: 16px; object-fit: contain;" /></span>
                    <span>{{ transaction.description || '마일리지 적립' }}</span>
                  </div>
                </div>
                <div class="trans-right">
                  <div class="trans-amount amount-positive">
                    <span>+</span>
                    <span>{{ Math.abs(transaction.amount).toLocaleString() }}M</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 사용 내역 카드 -->
            <div v-else class="transaction-list">
              <div
                v-for="transaction in items"
                :key="transaction.transaction_id"
                class="transaction-item"
              >
                <div class="trans-left">
                  <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                  <div class="trans-desc">
                    <span class="trans-icon"><img src="/images/event.png" alt="이벤트" style="width: 16px; height: 16px; object-fit: contain;" /></span>
                    <span>{{ transaction.description || '마일리지 사용' }}</span>
                  </div>
                </div>
                <div class="trans-right">
                  <div class="trans-amount amount-negative">
                    <span>-</span>
                    <span>{{ Math.abs(transaction.amount).toLocaleString() }}M</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </PagedSection>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import PagedSection from '~/components/common/PagedSection.vue'
import { computed, ref, onMounted } from 'vue'
import { useMileageProductApi } from '~/composables/api/useMileageProduct'
import { useNotify } from '~/composables/utils/useNotify'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// SEO 메타 데이터 설정
useHead({
  title: '마일리지 내역 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

// 날짜 검색
const startDate = ref('')
const endDate = ref('')
const startDateInput = ref<HTMLInputElement>()
const endDateInput = ref<HTMLInputElement>()

// 탭 상태
const activeTab = ref<'earn' | 'usage'>('earn')

// 정렬 상태
const sortOrder = ref<'latest' | 'highest' | 'lowest'>('latest')

// 페이지네이션 (탭별 분리)
const earnPage = ref(1)
const usagePage = ref(1)
const itemsPerPage = 10

// 로딩 상태는 Vue Query에서 관리

// 날짜 입력 클릭 핸들러
const openStartDatePicker = () => {
  startDateInput.value?.showPicker?.()
}

const openEndDatePicker = () => {
  endDateInput.value?.showPicker?.()
}

// 검색 파라미터 (제출값)
const qStart = ref('')
const qEnd = ref('')


// 초기 기본 날짜 (최근 30일)
const initDefaultDates = () => {
  const today = new Date()
  const prior = new Date()
  prior.setDate(today.getDate() - 30)
  const fmt = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  startDate.value = fmt(prior)
  endDate.value = fmt(today)
  // 날짜 설정 후 바로 조회
  searchTransactions()
}

onMounted(() => {
  if (!startDate.value || !endDate.value) {
    initDefaultDates()
  } else {
    qStart.value = startDate.value
    qEnd.value = endDate.value
  }
})

// Composable 사용
const { useMileageHistory } = useMileageProductApi()
const { notifyWarning } = useNotify()

// 적립 내역 쿼리 파라미터
const earnQueryParams = computed(() => ({
  transaction_type: 'EARN' as const,
  start_dt: qStart.value,
  end_dt: qEnd.value,
  order_type: sortOrder.value,
  page: earnPage.value,
  limit: itemsPerPage,
}))

// 사용 내역 쿼리 파라미터
const useQueryParams = computed(() => ({
  transaction_type: 'USE' as const,
  start_dt: qStart.value,
  end_dt: qEnd.value,
  order_type: sortOrder.value,
  page: usagePage.value,
  limit: itemsPerPage,
}))

// 적립 내역 쿼리
const earnQuery = useMileageHistory(earnQueryParams, {
  enabled: computed(() => activeTab.value === 'earn' && !!qStart.value && !!qEnd.value),
})

// 사용 내역 쿼리
const useQuery = useMileageHistory(useQueryParams, {
  enabled: computed(() => activeTab.value === 'usage' && !!qStart.value && !!qEnd.value),
})

// 데이터 추출
const earnItems = computed(() => earnQuery.data.value?.items || [])
const useItems = computed(() => useQuery.data.value?.items || [])
const earnTotalPages = computed(() => {
  const total = earnQuery.data.value?.total || 0
  return Math.max(1, Math.ceil(total / itemsPerPage))
})
const useTotalPages = computed(() => {
  const total = useQuery.data.value?.total || 0
  return Math.max(1, Math.ceil(total / itemsPerPage))
})

// 화면 표시 데이터
const itemsForActiveTab = computed(() => (activeTab.value === 'earn' ? earnItems.value : useItems.value))
const totalPages = computed(() => (activeTab.value === 'earn' ? earnTotalPages.value : useTotalPages.value))
const pageForActiveTab = computed({
  get: () => (activeTab.value === 'earn' ? earnPage.value : usagePage.value),
  set: (val: number) => {
    if (activeTab.value === 'earn') earnPage.value = val
    else usagePage.value = val
  }
})
const isLoading = computed(() => activeTab.value === 'earn' ? earnQuery.isLoading.value : useQuery.isLoading.value)
const error = computed(() => {
  const err = activeTab.value === 'earn' ? earnQuery.error.value : useQuery.error.value
  return err?.message || ''
})

// 날짜 포맷팅
const formatDate = (isoString: string) => {
  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}.${month}.${day} ${hours}:${minutes}`
}

// 페이지 변경 핸들러
const onUpdatePage = (val: number) => {
  if (activeTab.value === 'earn') {
    earnPage.value = val
  } else {
    usagePage.value = val
  }
}

// 검색 버튼 클릭
const searchTransactions = () => {
  // 날짜 입력 확인
  if (!startDate.value || !endDate.value) {
    notifyWarning('시작일과 종료일을 모두 입력해주세요.')
    return
  }

  // 날짜 유효성 검사: 시작일이 종료일보다 뒤에 있는지 확인
  const start = new Date(startDate.value)
  const end = new Date(endDate.value)

  if (start > end) {
    notifyWarning('시작일은 종료일보다 앞서야 합니다.')
    return
  }

  qStart.value = startDate.value
  qEnd.value = endDate.value
  earnPage.value = 1
  usagePage.value = 1

  // Vue Query 명시적으로 재호출
  if (activeTab.value === 'earn') {
    earnQuery.refetch()
  } else {
    useQuery.refetch()
  }
}
</script>

<style scoped>
@import '~/assets/css/user/pointlog.css';
</style>
