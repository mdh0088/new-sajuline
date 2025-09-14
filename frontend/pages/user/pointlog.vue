<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

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
          :items="filteredTransactions"
          :page="currentPage"
          :total-pages="totalPages"
          :loading="isLoading"
          :error="error"
          :empty-text="activeTab === 'charge' ? '충전 내역이 없습니다' : '사용 내역이 없습니다'"
          @update:page="val => currentPage = val"
        >
          <template #default="{ items }">
            <div class="transaction-list">
              <div 
                v-for="transaction in items" 
                :key="transaction.id" 
                class="transaction-item"
              >
                <div class="trans-left">
                  <span class="trans-date">{{ formatDate(transaction.created_at) }}</span>
                  <div class="trans-desc">
                    <span class="trans-icon">{{ getTransactionIcon(transaction.type) }}</span>
                    <span>{{ getTransactionDescription(transaction.type) }}</span>
                  </div>
                </div>
                <div class="trans-right">
                  <div 
                    class="trans-amount"
                    :class="transaction.amount > 0 ? 'amount-positive' : 'amount-negative'"
                  >
                    <span>{{ transaction.amount > 0 ? '+' : '-' }}</span>
                    <span>{{ Math.abs(transaction.amount).toLocaleString() }}P</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </PagedSection>
      </div>
    </main>

    <AppBottomNavi />
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

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
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

// 페이지네이션
const currentPage = ref(1)
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
    searchTransactions()
  }
})

// 화면 표시용 VM 타입
type VM = { id: string; type: 'charge' | 'consultation'; amount: number; created_at: string; description: string }

// API 데이터를 화면용으로 매핑
const chargeVM = computed<VM[]>(() => {
  return (chargeItems.value || []).map((it, idx) => ({
    id: `${it.paid_at || ''}-${it.product_name || ''}-${idx}`,
    type: 'charge',
    amount: Number(it.point_amount || 0),
    created_at: it.paid_at || new Date().toISOString(),
    description: it.product_name || '포인트 충전'
  }))
})

const usageVM = computed<VM[]>(() => {
  return (usageItems.value || []).map((it, idx) => ({
    id: `${it.chatstart || ''}-${it.chatend || ''}-${idx}`,
    type: 'consultation',
    amount: -Number(it.usepoint || 0),
    created_at: it.chatstart || it.chatend || new Date().toISOString(),
    description: it?.counselor?.nickname ? `상담 - ${it.counselor.nickname}` : '상담 이용'
  }))
})

const filteredByTab = computed<VM[]>(() => (activeTab.value === 'charge' ? chargeVM.value : usageVM.value))

// 서버에서 이미 정렬되어 옴 - 클라이언트 정렬 제거
const filteredTransactions = computed(() => {
  // 서버에서 order_type으로 정렬되어 반환되므로 클라이언트 정렬 불필요
  return filteredByTab.value
})

// 총 페이지 수
const totalPages = computed(() => (activeTab.value === 'charge' ? chargeTotalPages.value : usageTotalPages.value))

// 활성 탭 기준 로딩 상태
const isLoading = computed(() => activeTab.value === 'charge' ? chargeLoading.value : usageLoading.value)

// 탭 변경 시 페이지를 1로 초기화
watchEffect(() => {
  currentPage.value = 1
}, { flush: 'sync' })

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

// 검색 기능: API 호출
const searchTransactions = async () => {
  if (!startDate.value || !endDate.value) return
  qStart.value = startDate.value
  qEnd.value = endDate.value
  currentPage.value = 1

  const { $api } = useNuxtApp()
  error.value = ''

  // 충전 내역
  try {
    chargeLoading.value = true
    const res = await $api<APIResponse<PointChargeHistoryItem[]>>(`/api/v1/users/points/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&search_type=point_charge&order_type=${encodeURIComponent(sortOrder.value)}&page=${currentPage.value}&limit=${itemsPerPage}`)
    if (!res?.success) throw new Error(res && (res as any).error?.message || '충전 내역 조회 실패')
    chargeItems.value = (res.data as PointChargeHistoryItem[]) || []
    const tp = (res.meta as any)?.pagination?.total_pages
    chargeTotalPages.value = typeof tp === 'number' && tp > 0 ? tp : 1
  } catch (e: any) {
    error.value = e?.message || '충전 내역 조회 실패'
  } finally {
    chargeLoading.value = false
  }

  // 사용 내역
  try {
    usageLoading.value = true
    const res2 = await $api<APIResponse<PointUseHistoryItem[]>>(`/api/v1/users/points/history?start_dt=${encodeURIComponent(qStart.value)}&end_dt=${encodeURIComponent(qEnd.value)}&search_type=point_use&order_type=${encodeURIComponent(sortOrder.value)}&page=${currentPage.value}&limit=${itemsPerPage}`)
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


// 정렬 변경 시 재조회
watch(sortOrder, () => {
  if (qStart.value && qEnd.value) searchTransactions()
})

// 페이지 변경 시 재조회
watch(currentPage, () => {
  if (qStart.value && qEnd.value) searchTransactions()
})
</script>

<style scoped>
@import '~/assets/css/user/pointlog.css';
</style>