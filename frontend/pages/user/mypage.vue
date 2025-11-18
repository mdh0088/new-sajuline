<template>
  <div class="min-h-screen text-white" style="background: linear-gradient(180deg, rgb(134 0 255 / 15%) 0%, transparent 100%);">

    <main class="pb-24">
      <!-- 유저 마이페이지: 프로토타입 반영 -->
      <section class="px-5 py-6">

        <!-- 프로필 헤더 + 등급 진행도 통합 -->
        <div class="mb-5">
          <!-- 이름 / 설정 -->
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-xl font-bold">
              <template v-if="isLoading">
                <div class="bg-white/20 animate-pulse rounded h-7 w-32"></div>
              </template>
              <template v-else>{{ userNickname }}님</template>
            </h2>
            <button class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/15 transition-colors text-sm flex-shrink-0" @click="goEdit">
              <span>⚙️</span>
              <span>설정</span>
            </button>
          </div>

          <!-- 멤버십 혜택 -->
          <div class="flex items-center gap-2 mb-3 text-sm">
            <template v-if="isLoading">
              <div class="bg-white/20 animate-pulse rounded h-5 w-40"></div>
            </template>
            <template v-else>
              <span class="text-base">👑</span>
              <span class="font-semibold text-purple-300">{{ currentGrade }}</span>
              <span class="text-white/40">|</span>
              <NuxtLink to="/membership/benefit" class="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-semibold text-white/80 hover:bg-white/10 transition-colors">
                {{ pointEarnRate }} 적립
              </NuxtLink>
            </template>
          </div>

          <!-- 등급 진행도 바 -->
          <div class="mb-3">
            <div class="flex items-center justify-between mb-1.5 px-0.5">
              <span class="text-xs text-white/60 flex items-center gap-1">
                🎯 <span>다음 등급까지</span>
              </span>
              <span class="text-xs text-white/50">
                <template v-if="isLoading">
                  <span class="bg-white/20 animate-pulse rounded h-3 w-16 inline-block"></span>
                </template>
                <template v-else-if="error">-</template>
                <template v-else>{{ gradeRemaining }}</template>
              </span>
            </div>
            <div class="relative w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-500" :style="{ width: progressWidth }"></div>
            </div>
            <div class="flex items-center justify-between mt-1 px-0.5">
              <span class="text-xs text-purple-300 font-medium">
                <template v-if="isLoading">
                  <span class="bg-purple-300/20 animate-pulse rounded h-2.5 w-10 inline-block"></span>
                </template>
                <template v-else-if="error">-</template>
                <template v-else>{{ currentGrade }}</template>
              </span>
              <span class="text-xs text-white/40">
                <template v-if="isLoading">
                  <span class="bg-white/20 animate-pulse rounded h-2.5 w-10 inline-block"></span>
                </template>
                <template v-else-if="error">-</template>
                <template v-else>{{ nextGrade }}</template>
              </span>
            </div>
          </div>

          <div class="h-px bg-gradient-to-r from-white/20 via-white/10 to-transparent mt-4"></div>
        </div>

        <!-- 포인트 카드 - 강조 -->
        <div class="rounded-2xl border border-yellow-400/30 bg-gradient-to-br from-yellow-400/10 to-yellow-400/5 p-5 mb-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xl">💰</span>
            <h3 class="text-sm font-semibold text-white/70">보유 포인트</h3>
          </div>
          <div class="text-2xl font-bold text-yellow-300 mb-4">
            <template v-if="isLoading">
              <div class="bg-yellow-300/20 animate-pulse rounded h-8 w-40"></div>
            </template>
            <template v-else-if="error">
              <span class="text-red-300 text-sm">로딩 실패</span>
            </template>
            <template v-else>
              {{ points.toLocaleString() }} P
            </template>
          </div>
          <div class="flex gap-3">
            <NuxtLink to="/point" class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-yellow-400 to-amber-400 text-slate-950 font-semibold text-sm text-center active:scale-95">충전하기</NuxtLink>
            <NuxtLink to="/user/pointlog" class="flex-1 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 font-semibold text-sm text-center active:scale-95">포인트 내역</NuxtLink>
          </div>
        </div>

        <!-- 마일리지 카드 -->
        <div class="rounded-xl border border-blue-500/30 bg-blue-500/5 p-5 mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="text-xl">💎</span>
              <h3 class="text-sm font-semibold text-white/70">마일리지</h3>
            </div>
            <div class="flex gap-2">
              <NuxtLink to="/mileageshop" class="px-8 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs font-semibold text-center active:scale-95">사용</NuxtLink>
              <NuxtLink to="/user/mileagelog" class="px-8 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs font-semibold text-center active:scale-95">내역</NuxtLink>
            </div>
          </div>
          <div class="text-2xl font-bold">
            <template v-if="isLoading">
              <div class="bg-white/20 animate-pulse rounded h-8 w-40"></div>
            </template>
            <template v-else>
              {{ mileagePoints }}M
            </template>
          </div>
        </div>

        <!-- 메뉴 그룹 -->
        <div class="space-y-6">
          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">상담 관리</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <!-- <NuxtLink to="/user/cslog" class="menu-item"><div class="menu-left"><div class="menu-icon">💬</div><div><div class="menu-title">상담 내역</div><div class="menu-desc">지난 상담 기록 확인</div></div></div><div class="menu-right">›</div></NuxtLink> -->
              <NuxtLink to="/user/favorite" class="menu-item"><div class="menu-left"><div class="menu-icon">⭐</div><div><div class="menu-title">즐겨찾기 상담사</div><div class="menu-desc">자주 찾는 상담사 관리</div></div></div><div class="menu-right">›</div></NuxtLink>
              <NuxtLink to="/user/reviews" class="menu-item"><div class="menu-left"><div class="menu-icon">📝</div><div><div class="menu-title">상담 후기</div><div class="menu-desc">내가 작성한 후기 보기</div></div></div><div class="menu-right">›</div></NuxtLink>
            </div>
          </div>
          <!-- 혜택 영역 숨김처리
          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">혜택</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🎁</div><div><div class="menu-title">쿠폰함</div><div class="menu-desc">사용 가능한 쿠폰 확인</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🎯</div><div><div class="menu-title">출석 체크</div><div class="menu-desc">매일 포인트 받기</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🤝</div><div><div class="menu-title">친구 초대</div><div class="menu-desc">초대하고 5,000P 받기</div></div></div><div class="menu-right">›</div></div>
            </div>
          </div> -->

          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">멤버십</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <NuxtLink to="/membership/benefit" class="menu-item"><div class="menu-left"><div class="menu-icon">👑</div><div><div class="menu-title">멤버십 혜택</div><div class="menu-desc">등급별 할인 및 적립 혜택</div></div></div><div class="menu-right">›</div></NuxtLink>
            </div>
          </div>

          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">이벤트</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <NuxtLink to="/events" class="menu-item"><div class="menu-left"><div class="menu-icon">🎁</div><div><div class="menu-title">진행중인 이벤트</div><div class="menu-desc">다양한 혜택을 확인하세요</div></div></div><div class="menu-right">›</div></NuxtLink>
            </div>
          </div>

          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">기타</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <div class="menu-item" @click="goNotice"><div class="menu-left"><div class="menu-icon">📢</div><div><div class="menu-title">공지사항</div><div class="menu-desc">서비스 소식 확인</div></div></div><div class="menu-right">NEW</div></div>
              <!-- 알림 설정 메뉴 숨김처리
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🔔</div><div><div class="menu-title">알림 설정</div><div class="menu-desc">푸시 알림 관리</div></div></div><div class="menu-right">›</div></div>
               -->
              <div class="menu-item" @click="goCs"><div class="menu-left"><div class="menu-icon">❓</div><div><div class="menu-title">고객센터</div><div class="menu-desc">1:1 문의 및 FAQ</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item" @click="goProvision"><div class="menu-left"><div class="menu-icon">📜</div><div><div class="menu-title">이용약관</div><div class="menu-desc">서비스 이용 약관</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item" @click="goPrivacy"><div class="menu-left"><div class="menu-icon">🔒</div><div><div class="menu-title">개인정보처리방침</div><div class="menu-desc">개인정보 보호 정책</div></div></div><div class="menu-right">›</div></div>
            </div>
          </div>
        </div>
      </section>
    </main>

  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserQueries } from '~/composables/api/useUserQueries'
definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})

// SEO 메타 데이터 설정
useHead({
  title: '마이페이지 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const { useUserMypage } = useUserQueries()
const { data: mypage, isLoading, error } = useUserMypage()

// 사용자 정보
const userNickname = computed(() => mypage.value?.user_info.nickname ?? '사용자')

// 마일리지 포인트
const mileagePoints = computed(() => {
  const points = mypage.value?.user_info.mileage_point ?? 0
  return points.toLocaleString()
})

// 포인트 (tm60_users)
const points = computed(() => Number(mypage.value?.current_points ?? 0))

// 요약 통계
const stats = computed(() => ({
  consults: mypage.value?.total_consultation_count ?? 0,
  favorites: mypage.value?.total_bookmark_count ?? 0,
  reviews: mypage.value?.total_review_count ?? 0
}))

// 등급 정보
const currentGrade = computed(() => mypage.value?.grade_info.current_grade.grade_name ?? '-')
const nextGrade = computed(() => mypage.value?.grade_info.next_grade?.grade_name ?? '최고등급')

// 멤버십 혜택 - 적립률
const pointEarnRate = computed(() => {
  const gradeInfo = mypage.value?.grade_info.current_grade
  if (!gradeInfo) return '0%'
  const earnRate = Number(gradeInfo.point_earn_rate ?? 0)
  return earnRate > 0 ? `${earnRate}%` : '0%'
})

// 멤버십 혜택 - 할인율
const discountRate = computed(() => {
  const gradeInfo = mypage.value?.grade_info.current_grade
  if (!gradeInfo) return '0%'
  const discount = Number(gradeInfo.discount_rate ?? 0)
  return discount > 0 ? `${discount}%` : '0%'
})

// 진행도 계산: (이번 달 결제 총액) / (다음 등급까지 필요한 금액) * 100
const requiredAmount = computed(() => {
  const req = mypage.value?.grade_info.required_amount
  return typeof req === 'number' ? req : (req ? Number(req) : 0)
})

const monthlyPaid = computed(() => {
  const v = mypage.value?.monthly_payment_total as any
  const n = typeof v === 'string' ? Number(v) : Number(v ?? 0)
  return isNaN(n) ? 0 : n
})

const remainingAmount = computed(() => {
  const req = requiredAmount.value
  if (!req || req <= 0) return 0
  const remain = req - monthlyPaid.value
  return remain > 0 ? remain : 0
})

const progressPercent = computed(() => {
  const req = requiredAmount.value
  if (!req || req <= 0) return 100
  const percent = (monthlyPaid.value / req) * 100
  return Math.max(0, Math.min(100, Math.floor(percent)))
})

const progressWidth = computed(() => `${progressPercent.value}%`)

// 우측 상단 표기: "NNN,NNN원 남음" 또는 최고등급/충분
const gradeRemaining = computed(() => {
  if (!mypage.value?.grade_info.next_grade || (requiredAmount.value ?? 0) <= 0) {
    return '최고 등급입니다'
  }
  const remain = remainingAmount.value
  if (remain <= 0) return '다음 등급 달성'
  return `${remain.toLocaleString()}원 남음`
})

const router = useRouter()
const goNotice = () => router.push('/notices')
const goCs = () => router.push('/cs')
const goProvision = () => router.push('/provision')
const goPrivacy = () => router.push('/privacy')
const goEdit = () => router.push('/user/edit')
</script>

<style scoped>
.menu-item{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;cursor:pointer;transition:all .3s;border-bottom:1px solid rgba(255,255,255,.05)}
.menu-item:last-child{border-bottom:none}
.menu-left{display:flex;align-items:center;gap:16px}
.menu-icon{width:40px;height:40px;background:rgba(147,51,234,.1);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.menu-title{font-size:14px;font-weight:500;margin-bottom:2px}
.menu-desc{font-size:13px;color:rgba(255,255,255,.6)}
.menu-right{color:rgba(255,255,255,.3);font-size:14px}
.point-card{background:linear-gradient(135deg, rgba(147,51,234,.1) 0%, rgba(124,58,237,.05) 100%);border:1px solid rgba(147,51,234,.2);border-radius:20px;padding:16px;text-decoration:none;color:inherit}
.point-card:active{transform:scale(.98)}

/* profile-info-container 그리드 레이아웃 */
.profile-info-container {
  display: grid !important;
  grid-template-columns: 1fr !important;
  grid-template-rows: auto auto auto !important;
  gap: 12px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.profile-section-item:nth-child(1) {
  grid-column: 1 / 2 !important;
  grid-row: 1 / 2 !important;
}

.profile-section-item:nth-child(2) {
  grid-column: 1 / 2 !important;
  grid-row: 2 / 3 !important;
}

.profile-section-item:nth-child(3) {
  grid-column: 1 / 2 !important;
  grid-row: 3 / 4 !important;
}

/* 더 큰 화면에서는 2열 레이아웃 (500px 이상) */
@media (min-width: 500px) {
  .profile-info-container {
    grid-template-columns: 1fr 1fr !important;
    grid-template-rows: auto auto !important;
    gap: 16px !important;
  }

  .profile-section-item:nth-child(1) {
    grid-column: 1 / 2 !important;
    grid-row: 1 / 2 !important;
  }

  .profile-section-item:nth-child(2) {
    grid-column: 2 / 3 !important;
    grid-row: 1 / 2 !important;
  }

  .profile-section-item:nth-child(3) {
    grid-column: 1 / 3 !important;
    grid-row: 2 / 3 !important;
  }
}
</style>


