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
            :class="activeTab === 'charge' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''"
            @click="activeTab = 'charge'"
          >
            충전 내역
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
          :empty-text="activeTab === 'charge' ? '충전 내역이 없습니다' : '사용 내역이 없습니다'"
          @update:page="onUpdatePage"
        >
          <template #default="{ items }">
            <!-- 충전 내역 카드 -->
            <div v-if="activeTab === 'charge'" class="transaction-list">
              <div
                v-for="transaction in items"
                :key="transaction.id"
                class="transaction-item"
              >
                <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                <div class="trans-bottom">
                  <div class="trans-desc">
                    <span class="trans-icon">💰</span>
                    <span>{{ transaction.description }}</span>
                  </div>
                  <div class="trans-amount amount-positive">
                    <span>+</span>
                    <span>{{ Math.abs(transaction.amount).toLocaleString() }}P</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 사용 내역 카드 (/user/cslog 스타일 차용) -->
            <div v-else class="space-y-4">
              <div v-for="item in items" :key="item.id" class="history-item">
                <div class="flex justify-between items-start gap-4 mb-2">
                  <div class="flex items-center gap-4">
                    <div>
                      <img
                        v-if="item.counselor_image_url"
                        :src="item.counselor_image_url"
                        alt="프로필 이미지"
                        class="w-12 h-12 rounded-full object-cover border border-white/10"
                        width="48"
                        height="48"
                        loading="lazy"
                      />
                      <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
                    </div>
                    <div class="flex flex-col gap-1">
                      <span class="counselor-name">{{ item.counselor_name }}</span>
                    </div>
                  </div>
                  <div class="flex flex-col gap-1 items-end">
                    <span class="session-date">{{ formatDate(item.date) }}</span>
                  </div>
                </div>

                <div class="flex justify-between items-end mt-2">
                  <div class="session-time">상담 시간: {{ item.duration }}</div>
                  <div class="trans-amount amount-negative">
                    <span>-</span>
                    <span>{{ Math.abs(item.amount).toLocaleString() }}P</span>
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
import { computed, ref, watch, watchEffect, onMounted } from 'vue'
import type { APIResponse } from '~/types/common/api'
import type { PointChargeHistoryItem, PointUseHistoryItem } from '~/types/user/models'
import { useCdn } from '~/composables/utils/useCdn'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// SEO 메타 데이터 설정
useHead({
  title: '포인트 내역 - 사주라인',
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
const activeTab = ref<'charge' | 'usage'>('charge')

// 정렬 상태
const sortOrder = ref<'latest' | 'highest' | 'lowest'>('latest')

// 페이지네이션 (탭별 분리)
const chargePage = ref(1)
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
const chargeItems = ref<PointChargeHistoryItem[]>([])
const usageItems = ref<PointUseHistoryItem[]>([])
const chargeLoading = ref(false)
const usageLoading = ref(false)
const chargeTotalPages = ref(1)
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
    // 초기 진입: 충전 내역 최신순만 조회
    qStart.value = startDate.value
    qEnd.value = endDate.value
    chargePage.value = 1
    fetchCharge()
  }
})

// 화면 표시용 VM 타입 분리
type ChargeVM = { id: string; amount: number; created_at: string; description: string }
type UsageVM = { id: string; amount: number; date: string; counselor_name: string; counselor_image_url?: string; duration: string }

// API 데이터를 화면용으로 매핑
const chargeVM = computed<ChargeVM[]>(() => {
  return (chargeItems.value || []).map((it, idx) => ({
    id: `${it.paid_at || ''}-${it.product_name || ''}-${idx}`,
    amount: Number(it.point_amount || 0),
    created_at: it.paid_at || new Date().toISOString(),
    description: it.product_name || '포인트 충전'
  }))
})

const usageVM = computed<UsageVM[]>(() => {
  const { cdnUrl } = useCdn()
  const formatDuration = (seconds?: number | null) => {
    const s = Number(seconds || 0)
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    if (h > 0) return `${h}시간 ${m}분`
    return `${m}분`
  }
  return (usageItems.value || []).map((it, idx) => {
    const name = (it as any)?.counselor?.nickname || (it as any)?.counselor?.name || '상담사'
    const img = cdnUrl('cs', (it as any)?.counselor?.profile_image_url || '')
    const date = it?.chatstart || it?.chatend || new Date().toISOString()
    return {
      id: `${it.chatstart || ''}-${it.chatend || ''}-${idx}`,
      amount: -Number(it.usepoint || 0),
      date,
      counselor_name: name,
      counselor_image_url: img || undefined,
      duration: formatDuration((it as any)?.realchattm)
    }
  })
})

const itemsForActiveTab = computed(() => (activeTab.value === 'charge' ? chargeVM.value : usageVM.value))

// 총 페이지 수
const totalPages = computed(() => (activeTab.value === 'charge' ? chargeTotalPages.value : usageTotalPages.value))

// 활성 탭의 현재 페이지 getter/setter
const pageForActiveTab = computed({
  get: () => (activeTab.value === 'charge' ? chargePage.value : usagePage.value),
  set: (val: number) => {
    if (activeTab.value === 'charge') chargePage.value = val
    else usagePage.value = val
  }
})

// 활성 탭 기준 로딩 상태
const isLoading = computed(() => activeTab.value === 'charge' ? chargeLoading.value : usageLoading.value)

// 트랜잭션 아이콘 반환
const getTransactionIcon = (type: string) => {
  switch (type) {
    case 'charge':
      return '💰'
    case 'consultation':
      return '🎯'
    case 'bonus':
      return '🎁'
    default:
      return '💳'
  }
}

// 트랜잭션 설명 반환
const getTransactionDescription = (type: string) => {
  switch (type) {
    case 'charge':
      return '포인트 충전'
    case 'consultation':
      return '상담 이용'
    case 'bonus':
      return '이벤트 보너스'
    default:
      return '기타'
  }
}

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

// 탭별 API 호출
const fetchCharge = async () => {
  if (!qStart.value || !qEnd.value) return
  const { $api } = useNuxtApp()
  error.value = ''
  try {
    chargeLoading.value = true
    const res = await $api<APIResponse<PointChargeHistoryItem[]>>(`/api/v1/users/points/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&search_type=point_charge&order_type=${encodeURIComponent(sortOrder.value)}&page=${chargePage.value}&limit=${itemsPerPage}`)
    if (!res?.success) throw new Error(res && (res as any).error?.message || '충전 내역 조회 실패')
    chargeItems.value = (res.data as PointChargeHistoryItem[]) || []
    const tp = (res.meta as any)?.pagination?.total_pages
    chargeTotalPages.value = typeof tp === 'number' && tp > 0 ? tp : 1
  } catch (e: any) {
    error.value = e?.message || '충전 내역 조회 실패'
  } finally {
    chargeLoading.value = false
  }
}

const fetchUsage = async () => {
  if (!qStart.value || !qEnd.value) return
  const { $api } = useNuxtApp()
  error.value = ''
  try {
    usageLoading.value = true
    const res2 = await $api<APIResponse<PointUseHistoryItem[]>>(`/api/v1/users/points/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&search_type=point_use&order_type=${encodeURIComponent(sortOrder.value)}&page=${usagePage.value}&limit=${itemsPerPage}`)
    if (!res2?.success) throw new Error(res2 && (res2 as any).error?.message || '사용 내역 조회 실패')
    usageItems.value = (res2.data as PointUseHistoryItem[]) || []
    const tp2 = (res2.meta as any)?.pagination?.total_pages
    usageTotalPages.value = typeof tp2 === 'number' && tp2 > 0 ? tp2 : 1
  } catch (e: any) {
    error.value = e?.message || '사용 내역 조회 실패'
  } finally {
    usageLoading.value = false
  }
}

const onUpdatePage = async (val: number) => {
  if (activeTab.value === 'charge') {
    chargePage.value = val
    await fetchCharge()
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
  chargePage.value = 1
  usagePage.value = 1
  if (activeTab.value === 'charge') await fetchCharge()
  else await fetchUsage()
}


// 정렬 변경 시 활성 탭만 재조회
watch(sortOrder, async () => {
  if (!qStart.value || !qEnd.value) return
  if (activeTab.value === 'charge') await fetchCharge()
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
@import '~/assets/css/user/pointlog.css';
@import '~/assets/css/user/cslog.css';
</style>