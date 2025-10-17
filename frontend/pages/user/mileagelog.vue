<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <main class="pt-[60px] pb-24">
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
                :key="transaction.id"
                class="transaction-item"
              >
                <div class="trans-left">
                  <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                  <div class="trans-desc">
                    <span class="trans-icon">⭐</span>
                    <span>{{ transaction.description }}</span>
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
                :key="transaction.id"
                class="transaction-item"
              >
                <div class="trans-left">
                  <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                  <div class="trans-desc">
                    <span class="trans-icon">🎁</span>
                    <span>{{ transaction.description }}</span>
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
import { computed, ref, watch, onMounted } from 'vue'
import type { APIResponse } from '~/types/common/api'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// 마일리지 내역 타입 정의
interface MileageHistoryItem {
  id: string
  amount: number
  created_at: string
  description: string
  type: 'earn' | 'usage'
}

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

// 로딩 및 에러 상태
const error = ref('')

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

// API 결과 상태
const earnItems = ref<MileageHistoryItem[]>([])
const usageItems = ref<MileageHistoryItem[]>([])
const earnLoading = ref(false)
const usageLoading = ref(false)
const earnTotalPages = ref(1)
const usageTotalPages = ref(1)

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
    // 초기 진입: 적립 내역 최신순만 조회
    qStart.value = startDate.value
    qEnd.value = endDate.value
    earnPage.value = 1
    fetchEarn()
  }
})

const itemsForActiveTab = computed(() => (activeTab.value === 'earn' ? earnItems.value : usageItems.value))

// 총 페이지 수
const totalPages = computed(() => (activeTab.value === 'earn' ? earnTotalPages.value : usageTotalPages.value))

// 활성 탭의 현재 페이지 getter/setter
const pageForActiveTab = computed({
  get: () => (activeTab.value === 'earn' ? earnPage.value : usagePage.value),
  set: (val: number) => {
    if (activeTab.value === 'earn') earnPage.value = val
    else usagePage.value = val
  }
})

// 활성 탭 기준 로딩 상태
const isLoading = computed(() => activeTab.value === 'earn' ? earnLoading.value : usageLoading.value)

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

// 탭별 API 호출 (TODO: 실제 API 엔드포인트로 변경 필요)
const fetchEarn = async () => {
  if (!qStart.value || !qEnd.value) return
  const { $api } = useNuxtApp()
  error.value = ''
  try {
    earnLoading.value = true
    // TODO: 실제 마일리지 적립 내역 API로 변경
    // const res = await $api<APIResponse<MileageHistoryItem[]>>(`/api/v1/users/mileage/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&type=earn&order_type=${encodeURIComponent(sortOrder.value)}&page=${earnPage.value}&limit=${itemsPerPage}`)

    // 임시 데이터 (실제 API 연동 전까지)
    const mockData: MileageHistoryItem[] = [
      {
        id: '1',
        amount: 1000,
        created_at: new Date().toISOString(),
        description: '회원 가입 보너스',
        type: 'earn'
      },
      {
        id: '2',
        amount: 500,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        description: '상담 후기 작성',
        type: 'earn'
      }
    ]

    earnItems.value = mockData
    earnTotalPages.value = 1
  } catch (e: any) {
    error.value = e?.message || '적립 내역 조회 실패'
  } finally {
    earnLoading.value = false
  }
}

const fetchUsage = async () => {
  if (!qStart.value || !qEnd.value) return
  const { $api } = useNuxtApp()
  error.value = ''
  try {
    usageLoading.value = true
    // TODO: 실제 마일리지 사용 내역 API로 변경
    // const res = await $api<APIResponse<MileageHistoryItem[]>>(`/api/v1/users/mileage/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&type=usage&order_type=${encodeURIComponent(sortOrder.value)}&page=${usagePage.value}&limit=${itemsPerPage}`)

    // 임시 데이터 (실제 API 연동 전까지)
    const mockData: MileageHistoryItem[] = [
      {
        id: '1',
        amount: 300,
        created_at: new Date().toISOString(),
        description: '마일리지 샵 - 포인트 전환',
        type: 'usage'
      }
    ]

    usageItems.value = mockData
    usageTotalPages.value = 1
  } catch (e: any) {
    error.value = e?.message || '사용 내역 조회 실패'
  } finally {
    usageLoading.value = false
  }
}

const onUpdatePage = async (val: number) => {
  if (activeTab.value === 'earn') {
    earnPage.value = val
    await fetchEarn()
  } else {
    usagePage.value = val
    await fetchUsage()
  }
}

// 검색 버튼 클릭 → 활성 탭만 조회
const searchTransactions = async () => {
  if (!startDate.value || !endDate.value) return
  qStart.value = startDate.value
  qEnd.value = endDate.value
  earnPage.value = 1
  usagePage.value = 1
  if (activeTab.value === 'earn') await fetchEarn()
  else await fetchUsage()
}

// 정렬 변경 시 활성 탭만 재조회
watch(sortOrder, async () => {
  if (!qStart.value || !qEnd.value) return
  if (activeTab.value === 'earn') await fetchEarn()
  else await fetchUsage()
})

// 탭 변경 시 사용 탭 최초 진입이면 조회
watch(activeTab, async (tab) => {
  if (!qStart.value || !qEnd.value) return
  if (tab === 'usage' && usageItems.value.length === 0) {
    usagePage.value = 1
    await fetchUsage()
  }
})
</script>

<style scoped>
@import '~/assets/css/user/mileagelog.css';
</style>
