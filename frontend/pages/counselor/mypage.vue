<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <main class="pt-[60px] pb-24">
      <!-- 상담사 마이페이지: 프로토타입 반영 -->
      <section class="px-5 py-5">
        <!-- 프로필 섹션 -->
        <div class="p-5 rounded-2xl border border-white/10 bg-gradient-to-b from-purple-600/15 to-transparent">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-4">
              <div>
                <img
                  v-if="profileImageUrl"
                  :src="profileImageUrl"
                  alt="프로필 이미지"
                  class="w-12 h-12 rounded-full object-cover border border-white/10"
                  width="48"
                  height="48"
                  loading="lazy"
                />
                <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
              </div>
              <div>
                <div class="text-lg font-bold">{{ nickname }}</div>
              </div>
            </div>
            <button disabled class="px-3 py-2 text-sm rounded-lg border border-white/10 bg-white/5 opacity-50 cursor-not-allowed">상담료 안내 (준비중)</button>
          </div>

          <div class="flex items-center gap-3">
            <div class="inline-flex p-1 rounded-full border border-white/10 bg-white/5">
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='ready' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="handleStatusChange('ready')">대기</button>
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='away' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="handleStatusChange('away')">부재중</button>
            </div>
          </div>

          <!-- 상담시간 카드 -->
          <div class="mt-5 p-5 rounded-2xl bg-gradient-to-br from-blue-900/70 to-blue-800/60 relative overflow-hidden">
            <div class="absolute -top-1/2 -right-1/2 w-[200%] h-[200%] rounded-full bg-white/10 opacity-20"></div>
            <div class="relative">
              <div class="text-base font-bold mb-3">상담시간</div>
              <div class="flex items-center justify-between">
                <button 
                  @click="previousMonth" 
                  :disabled="!canGoPrevious"
                  class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center transition-all"
                  :class="canGoPrevious ? 'hover:bg-white/20 active:scale-95' : 'opacity-30 cursor-not-allowed'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <div class="text-center">
                  <div class="text-sm text-white/80 mb-1">{{ currentMonthText }}</div>
                  <div class="space-y-1">
                    <div>
                      <div class="text-xs text-white/60">상담시간</div>
                      <div class="text-lg font-extrabold">
                        <span v-if="isFetchingMonthly">로딩중...</span>
                        <span v-else>{{ currentMonthHours }}</span>
                      </div>
                    </div>
                    <div>
                      <div class="text-xs text-white/60">상담 포인트</div>
                      <div class="text-lg font-extrabold text-yellow-400">
                        <span v-if="isFetchingMonthly">로딩중...</span>
                        <span v-else>{{ currentMonthPoints }}P</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <button 
                  @click="nextMonth" 
                  :disabled="!canGoNext"
                  class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center transition-all"
                  :class="canGoNext ? 'hover:bg-white/20 active:scale-95' : 'opacity-30 cursor-not-allowed'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 활동시간 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">활동시간</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveWorkTime">변경하기</button>
          </div>
          <input type="text" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" placeholder="매일 04:00~밤 새벽 1:00" v-model="workTime" />
        </div>

        <!-- 짧은 소개글 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">짧은 소개글</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveShortIntro">변경하기</button>
          </div>
          <textarea rows="3" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="shortIntro" placeholder="간단한 소개글을 입력해주세요" />
        </div>

        <!-- 인사말 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">인사말</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveGreeting">변경하기</button>
          </div>
          <textarea rows="4" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="greeting" placeholder="고객에게 전할 인사말을 입력해주세요" />
        </div>

        <!-- 경력사항 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">경력사항</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveCareer">변경하기</button>
          </div>
          <textarea rows="5" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="career" placeholder="상담 경력 및 전문 분야를 입력해주세요" />
        </div>

        <!-- 탭 섹션 -->
        <div class="mt-5">
          <div class="p-1 rounded-xl bg-white/5 border border-white/10 flex">
            <button class="flex-1 py-3 rounded-lg" :class="tab==='notice' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='notice'">공지사항</button>
            <button class="flex-1 py-3 rounded-lg relative" :class="tab==='review' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='review'">고객 후기 <span v-if="reviewTotal>0" class="absolute top-1 right-2 text-[10px] font-bold bg-red-500/30 text-red-200 px-2 rounded">{{ reviewTotal }}</span></button>
            <button class="flex-1 py-3 rounded-lg" :class="tab==='inquiry' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='inquiry'">상담 문의</button>
            <button class="flex-1 py-3 rounded-lg" :class="tab==='admin' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='admin'">관리자문의</button>
          </div>

          <div class="mt-4">
            <!-- 공지사항 -->
            <template v-if="tab==='notice'">
              <PagedSection
                :items="notices"
                :page="noticePage"
                :total-pages="noticeTotalPages"
                :loading="isLoadingNotices"
                :error="noticeError"
                empty-text="등록된 공지사항이 없습니다"
                @update:page="val => noticePage = val"
              >
                <template #default="{ items }">
                  <div v-for="n in items" :key="n.notice_id" class="list-item">
                    <div class="list-item-header">
                      <div class="list-item-title flex items-center gap-2">
                        <span v-if="n.is_important" class="px-2 py-0.5 text-[10px] rounded bg-red-500/20 text-red-200 border border-red-400/30">중요</span>
                        {{ n.title }}
                      </div>
                      <div class="list-item-date">{{ formatDate(n.created_at) }}</div>
                    </div>
                    <div class="list-item-content" v-html="n.content"></div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 고객후기 -->
            <template v-else-if="tab==='review'">
              <PagedSection
                :items="reviews"
                :page="reviewPage"
                :total-pages="reviewTotalPages"
                :loading="isLoadingReviews"
                :error="reviewError"
                empty-text="고객 후기가 없습니다"
                @update:page="val => reviewPage = val"
              >
                <template #default="{ items }">
                  <div v-for="r in items" :key="r.review_id" class="list-item">
                    <div class="list-item-header">
                      <div class="list-item-title flex items-center gap-2">
                        <span class="text-yellow-300">★ {{ r.rating }}</span>
                        <span class="text-white/70">{{ r.user_id }}</span>
                        <span v-if="r.is_best" class="px-2 py-0.5 text-[10px] rounded bg-indigo-500/20 text-indigo-200 border border-indigo-400/30">BEST</span>
                      </div>
                      <div class="list-item-date">{{ formatDate(r.created_at) }}</div>
                    </div>
                    <div class="list-item-content">{{ r.content || '내용 없음' }}</div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 상담문의 (사용자→상담사) -->
            <template v-else-if="tab==='inquiry'">
              <PagedSection
                :items="userInquiries"
                :page="userInquiryPage"
                :total-pages="userInquiryTotalPages"
                :loading="isLoadingUserInquiries"
                :error="userInquiryError"
                empty-text="상담문의가 없습니다"
                @update:page="val => userInquiryPage = val"
              >
                <template #default="{ items }">
                  <div v-for="q in items" :key="q.inquiry_id" class="list-item">
                    <div class="list-item-header">
                      <div class="list-item-title flex items-center gap-2">
                        <span v-if="!q.is_read" class="px-2 py-0.5 text-[10px] rounded bg-yellow-500/20 text-yellow-200 border border-yellow-400/30">NEW</span>
                        <span>{{ q.title || q.category || '제목 없음' }}</span>
                      </div>
                      <div class="list-item-date">{{ formatDate(q.created_at) }}</div>
                    </div>
                    <div class="list-item-content flex items-center gap-2">
                      <span class="text-white/70">문의자: {{ q.inquirer_id || '익명' }}</span>
                      <span :class="q.has_reply ? 'text-teal-300' : 'text-white/50'">{{ q.has_reply ? '답변 완료' : '미답변' }}</span>
                    </div>
                  </div>
                </template>
              </PagedSection>
            </template>

            <!-- 관리자문의 (상담사→관리자) -->
            <template v-else>
              <PagedSection
                :items="adminInquiries"
                :page="adminInquiryPage"
                :total-pages="adminInquiryTotalPages"
                :loading="isLoadingAdminInquiries"
                :error="adminInquiryError"
                empty-text="관리자 문의가 없습니다"
                @update:page="val => adminInquiryPage = val"
              >
                <template #default="{ items }">
                  <div v-for="a in items" :key="a.inquiry_id" class="list-item">
                    <div class="list-item-header">
                      <div class="list-item-title flex items-center gap-2">
                        <span v-if="!a.has_reply" class="px-2 py-0.5 text-[10px] rounded bg-purple-500/20 text-purple-200 border border-purple-400/30">답변대기</span>
                        <span>{{ a.title || a.category || '제목 없음' }}</span>
                      </div>
                      <div class="list-item-date">{{ formatDate(a.created_at) }}</div>
                    </div>
                    <div class="list-item-content flex items-center gap-2">
                      <span class="text-white/70">작성자: 나 (상담사)</span>
                      <span :class="a.has_reply ? 'text-teal-300' : 'text-white/50'">{{ a.has_reply ? '답변 완료' : '미답변' }}</span>
                    </div>
                  </div>
                </template>
              </PagedSection>
            </template>
          </div>
        </div>
      </section>
    </main>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'counselor'
})
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import PagedSection from '~/components/common/PagedSection.vue'
import { computed, ref, watchEffect } from 'vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { useNotify } from '~/composables/utils/useNotify'
import { useCdn } from '~/composables/utils/useCdn'

const { requireAuth, isCounselor, currentUser } = useAuth()
const { notifySuccess, notifyConfirm, notifyError } = useNotify()
await requireAuth()

const { 
  useMypage, 
  useMonthlyConsultationStats, 
  useUpdateMypage,
  useNoticeList,
  useCounselorReviews,
  useCounselorUserInquiries,
  useCounselorAdminInquiries
} = useCounselorQueries()
const { data: mypage } = useMypage()

// CDN 베이스를 사용해 프로필 이미지 절대 URL 생성
const { cdnUrl } = useCdn()
const profileImageUrl = computed(() => {
  return cdnUrl('cs', mypage.value?.profile_image_url)
})

const nickname = ref<string | undefined>(undefined)
const shortIntro = ref<string | undefined>(undefined)
const greeting = ref<string | undefined>(undefined)
const career = ref<string | undefined>(undefined)
const workTime = ref<string | undefined>(undefined)

watchEffect(() => {
  if (mypage.value) {
    nickname.value = mypage.value.nickname
    shortIntro.value = mypage.value.introduction_short
    greeting.value = mypage.value.greeting_message
    career.value = mypage.value.career_info
    workTime.value = mypage.value.work_time
  }
})
const status = ref<'ready' | 'away'>('away')
const tab = ref<'notice' | 'review' | 'inquiry' | 'admin'>('notice')

// 월별 상담시간 네비게이션
const currentDate = new Date()
const selectedMonth = ref(new Date(currentDate.getFullYear(), currentDate.getMonth()))

// 선택된 월의 yyyy, mm을 기반으로 통계 쿼리 훅 생성
const yyyy = computed(() => String(selectedMonth.value.getFullYear()))
const mm = computed(() => String(selectedMonth.value.getMonth() + 1).padStart(2, '0'))

// 월간 통계 데이터 쿼리 (선택 월 변경 시 쿼리키가 달라져 자동 refetch)
const { data: monthlyData, isFetching: isFetchingMonthly, isError: isMonthlyError } = useMonthlyConsultationStats(yyyy, mm)

// selectedMonth가 변하면 새 훅을 만들 수 없으므로, watchEffect로 재등록 대신
// computed 키 기반으로 쿼리 훅을 재평가하게 하기 위해 아래와 같이 래핑
// Vue의 script setup에서 조건부 훅 호출을 피하기 위해, 쿼리키에 year, month를 포함하여
// 내부 훅이 자체적으로 반응하도록 구현되어 있음(useMonthlyConsultationStats 내 queryKey).

// 초를 hh:mm:ss 형태로 변환하는 함수
const formatSecondsToTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
}

const currentMonthText = computed(() => {
  const year = selectedMonth.value.getFullYear()
  const month = selectedMonth.value.getMonth() + 1
  return `${year}년 ${month}월`
})

const currentMonthHours = computed(() => {
  const seconds = monthlyData.value?.sum_realchattm || 0
  return formatSecondsToTime(seconds)
})

const currentMonthPoints = computed(() => {
  const points = monthlyData.value?.sum_usepoint || 0
  return points.toLocaleString() // 숫자에 콤마 추가
})

const canGoPrevious = computed(() => {
  // 과거 데이터는 제한 없이 계속 선택 가능
  return true
})

const canGoNext = computed(() => {
  // 현재 월까지만 허용
  return selectedMonth.value.getTime() < new Date(currentDate.getFullYear(), currentDate.getMonth()).getTime()
})

const previousMonth = () => {
  if (canGoPrevious.value) {
    const newDate = new Date(selectedMonth.value)
    newDate.setMonth(newDate.getMonth() - 1)
    selectedMonth.value = newDate
  }
}

const nextMonth = () => {
  if (canGoNext.value) {
    const newDate = new Date(selectedMonth.value)
    newDate.setMonth(newDate.getMonth() + 1)
    selectedMonth.value = newDate
  }
}

const notifySaved = () => notifySuccess('💾 변경 사항이 저장되었습니다.')

// 업데이트 뮤테이션 인스턴스
const { mutateAsync: updateMypage } = useUpdateMypage()

// 초기 상태값 동기화 (백엔드 counselor_status → 프론트 상태 코드)
watchEffect(() => {
  const cs = mypage.value?.counselor_status as string | undefined
  if (cs === 'WAITING') status.value = 'ready'
  else if (cs === 'ABSENT') status.value = 'away'
})

const handleStatusChange = async (newStatus: 'ready' | 'away') => {
  if (status.value === newStatus) return // 동일한 상태면 아무것도 하지 않음
  
  const statusText = newStatus === 'ready' ? '대기' : '부재중'
  const confirmed = await notifyConfirm(`상태를 '${statusText}'로 변경하시겠습니까?`)
  
  if (confirmed) {
    const counselor_status = newStatus === 'ready' ? 'WAITING' : 'ABSENT'
    try {
      await updateMypage({ counselor_status })
      status.value = newStatus
      notifySuccess(`✅ 상태가 '${statusText}'로 변경되었습니다.`)
    } catch (e: any) {
      notifyError(e?.message || '상태 변경에 실패했습니다.')
    }
  }
}

// 각 필드 저장 핸들러
const saveWorkTime = async () => {
  try {
    await updateMypage({ work_time: workTime.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '활동시간 저장에 실패했습니다.')
  }
}

const saveShortIntro = async () => {
  try {
    await updateMypage({ introduction_short: shortIntro.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '짧은 소개글 저장에 실패했습니다.')
  }
}

const saveGreeting = async () => {
  try {
    await updateMypage({ greeting_message: greeting.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '인사말 저장에 실패했습니다.')
  }
}

const saveCareer = async () => {
  try {
    await updateMypage({ career_info: career.value || '' })
    notifySaved()
  } catch (e: any) {
    notifyError(e?.message || '경력사항 저장에 실패했습니다.')
  }
}

// 공지/후기/문의 탭 데이터 로딩
const noticePage = ref(1)
const noticeLimit = ref(10)
const { data: noticeData, isFetching: isNoticeFetching, error: noticeQueryError } = useNoticeList(noticePage, noticeLimit)
const notices = computed(() => noticeData.value?.items ?? [])
const noticeTotalPages = computed(() => noticeData.value?.total_pages ?? 1)
const isLoadingNotices = computed(() => isNoticeFetching.value)
const noticeError = computed(() => (noticeQueryError.value as any)?.message || '')

const reviewPage = ref(1)
const reviewLimit = ref(10)
const { data: reviewData, isFetching: isReviewFetching, error: reviewQueryError } = useCounselorReviews(
  reviewPage,
  reviewLimit,
  true,
  { enabled: computed(() => tab.value === 'review') }
)
const reviews = computed(() => reviewData.value?.items ?? [])
const reviewTotalPages = computed(() => reviewData.value?.total_pages ?? 1)
const reviewTotal = computed(() => reviewData.value?.total ?? 0)
const isLoadingReviews = computed(() => isReviewFetching.value)
const reviewError = computed(() => (reviewQueryError.value as any)?.message || '')

const userInquiryPage = ref(1)
const userInquiryLimit = ref(10)
const { data: userInquiryData, isFetching: isUserInquiryFetching, error: userInquiryQueryError } = useCounselorUserInquiries(
  userInquiryPage,
  userInquiryLimit,
  { enabled: computed(() => tab.value === 'inquiry') }
)
const userInquiries = computed(() => userInquiryData.value?.items ?? [])
const userInquiryTotalPages = computed(() => userInquiryData.value?.total_pages ?? 1)
const isLoadingUserInquiries = computed(() => isUserInquiryFetching.value)
const userInquiryError = computed(() => (userInquiryQueryError.value as any)?.message || '')

const adminInquiryPage = ref(1)
const adminInquiryLimit = ref(10)
const { data: adminInquiryData, isFetching: isAdminInquiryFetching, error: adminInquiryQueryError } = useCounselorAdminInquiries(
  adminInquiryPage,
  adminInquiryLimit,
  { enabled: computed(() => tab.value === 'admin') }
)
const adminInquiries = computed(() => adminInquiryData.value?.items ?? [])
const adminInquiryTotalPages = computed(() => adminInquiryData.value?.total_pages ?? 1)
const isLoadingAdminInquiries = computed(() => isAdminInquiryFetching.value)
const adminInquiryError = computed(() => (adminInquiryQueryError.value as any)?.message || '')

// 공통 날짜 포맷터
const formatDate = (iso: string) => {
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth()+1).padStart(2,'0')
  const day = String(d.getDate()).padStart(2,'0')
  return `${y}.${m}.${day}`
}
</script>

<style scoped>
.list-item{padding:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1);border-radius:12px;margin-bottom:12px}
.list-item-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.list-item-title{font-size:15px;font-weight:600}
.list-item-date{font-size:12px;color:rgba(255,255,255,.5)}
.list-item-content{font-size:14px;color:rgba(255,255,255,.7);line-height:1.5;display:-webkit-box;line-clamp:2;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
</style>


