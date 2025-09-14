<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <main class="pt-[60px] pb-24">
      <!-- 유저 마이페이지: 프로토타입 반영 -->
      <section class="px-5 py-6">
        

        <!-- 포인트 카드 -->
        <div class="rounded-2xl border border-yellow-400/30 bg-gradient-to-br from-yellow-400/10 to-yellow-400/5 p-5 mb-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold flex items-center gap-2">💰 <span>내 포인트</span></h3>
          </div>
          <div class="text-3xl font-extrabold text-yellow-300 mb-4">
            <template v-if="isLoading">
              <div class="bg-yellow-300/20 animate-pulse rounded h-10 w-32"></div>
            </template>
            <template v-else-if="error">
              <span class="text-red-300 text-sm">로딩 실패</span>
            </template>
            <template v-else>
              {{ points.toLocaleString() }} P
            </template>
          </div>
          <div class="flex gap-3">
            <NuxtLink to="/point" class="flex-1 py-3 rounded-xl bg-gradient-to-r from-yellow-400 to-amber-400 text-slate-950 font-semibold text-center active:scale-95">충전하기</NuxtLink>
            <NuxtLink to="/user/pointlog" class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/15 font-semibold text-center active:scale-95">포인트 내역</NuxtLink>
          </div>
        </div>

        <!-- 등급 진행도 -->
        <div class="rounded-2xl border border-purple-500/30 bg-purple-500/5 p-5 mb-5">
          <div class="flex items-center justify-between mb-3">
            <div class="text-purple-200 font-semibold flex items-center gap-2">🎯 <span>다음 등급까지</span></div>
            <div class="text-sm text-white/80">
              <template v-if="isLoading">
                <div class="bg-white/20 animate-pulse rounded h-4 w-16"></div>
              </template>
              <template v-else-if="error">
                <span class="text-red-300">-</span>
              </template>
              <template v-else>
                {{ gradeRemaining }}
              </template>
            </div>
          </div>
          <div class="w-full h-2 rounded-lg bg-white/10 overflow-hidden">
            <div class="h-full bg-gradient-to-r from-purple-600 to-purple-300 rounded-lg" :style="{ width: progressWidth }"></div>
          </div>
          <div class="flex items-center justify-between mt-2 text-xs text-white/60">
            <div class="flex items-center gap-1">
              🥉
              <span class="text-purple-200 font-medium">
                <template v-if="isLoading">
                  <div class="bg-purple-200/20 animate-pulse rounded h-3 w-12 inline-block"></div>
                </template>
                <template v-else-if="error">-</template>
                <template v-else>{{ currentGrade }}</template>
              </span>
            </div>
            <div class="flex items-center gap-1">
              👑
              <span class="text-white/80 font-medium">
                <template v-if="isLoading">
                  <div class="bg-white/20 animate-pulse rounded h-3 w-12 inline-block"></div>
                </template>
                <template v-else-if="error">-</template>
                <template v-else>{{ nextGrade }}</template>
              </span>
            </div>
          </div>
        </div>

        <!-- 요약 카드들 -->
        <div class="grid grid-cols-3 gap-3 mb-6">
          <NuxtLink to="/user/cslog" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.consults }}</div>
            <div class="text-xs text-white/60">총 상담</div>
          </NuxtLink>
          <NuxtLink to="/user/favorite" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.favorites }}</div>
            <div class="text-xs text-white/60">즐겨찾기</div>
          </NuxtLink>
          <NuxtLink to="/user/reviews" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.reviews }}</div>
            <div class="text-xs text-white/60">후기작성</div>
          </NuxtLink>
        </div>

        <!-- 메뉴 그룹 -->
        <div class="space-y-6">
          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">상담 관리</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <NuxtLink to="/user/cslog" class="menu-item"><div class="menu-left"><div class="menu-icon">💬</div><div><div class="menu-title">상담 내역</div><div class="menu-desc">지난 상담 기록 확인</div></div></div><div class="menu-right">›</div></NuxtLink>
              <NuxtLink to="/user/favorite" class="menu-item"><div class="menu-left"><div class="menu-icon">⭐</div><div><div class="menu-title">즐겨찾기 상담사</div><div class="menu-desc">자주 찾는 상담사 관리</div></div></div><div class="menu-right">›</div></NuxtLink>
              <NuxtLink to="/user/reviews" class="menu-item"><div class="menu-left"><div class="menu-icon">📝</div><div><div class="menu-title">상담 후기</div><div class="menu-desc">내가 작성한 후기 보기</div></div></div><div class="menu-right">›</div></NuxtLink>
            </div>
          </div>

          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">혜택</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🎁</div><div><div class="menu-title">쿠폰함</div><div class="menu-desc">사용 가능한 쿠폰 확인</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🎯</div><div><div class="menu-title">출석 체크</div><div class="menu-desc">매일 포인트 받기</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🤝</div><div><div class="menu-title">친구 초대</div><div class="menu-desc">초대하고 5,000P 받기</div></div></div><div class="menu-right">›</div></div>
            </div>
          </div>

          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">기타</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <div class="menu-item" @click="goNotice"><div class="menu-left"><div class="menu-icon">📢</div><div><div class="menu-title">공지사항</div><div class="menu-desc">서비스 소식 확인</div></div></div><div class="menu-right">NEW</div></div>
              <div class="menu-item"><div class="menu-left"><div class="menu-icon">🔔</div><div><div class="menu-title">알림 설정</div><div class="menu-desc">푸시 알림 관리</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item" @click="goCs"><div class="menu-left"><div class="menu-icon">❓</div><div><div class="menu-title">고객센터</div><div class="menu-desc">1:1 문의 및 FAQ</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item" @click="goTerms"><div class="menu-left"><div class="menu-icon">📜</div><div><div class="menu-title">이용약관</div><div class="menu-desc">서비스 이용 약관</div></div></div><div class="menu-right">›</div></div>
              <div class="menu-item" @click="goPrivacy"><div class="menu-left"><div class="menu-icon">🔒</div><div><div class="menu-title">개인정보처리방침</div><div class="menu-desc">개인정보 보호 정책</div></div></div><div class="menu-right">›</div></div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import auth from '~/middleware/auth'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserQueries } from '~/composables/api/useUserQueries'
definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'user'
})


const { useUserMypage } = useUserQueries()
const { data: mypage, isLoading, error } = useUserMypage()

// 포인트
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
const goNotice = () => router.push('/notice')
const goCs = () => router.push('/cs')
const goTerms = () => router.push('/terms')
const goPrivacy = () => router.push('/privacy')
</script>

<style scoped>
.menu-item{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;cursor:pointer;transition:all .3s;border-bottom:1px solid rgba(255,255,255,.05)}
.menu-item:last-child{border-bottom:none}
.menu-left{display:flex;align-items:center;gap:16px}
.menu-icon{width:40px;height:40px;background:rgba(147,51,234,.1);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.menu-title{font-size:16px;font-weight:500;margin-bottom:2px}
.menu-desc{font-size:13px;color:rgba(255,255,255,.6)}
.menu-right{color:rgba(255,255,255,.3);font-size:14px}
.point-card{background:linear-gradient(135deg, rgba(147,51,234,.1) 0%, rgba(124,58,237,.05) 100%);border:1px solid rgba(147,51,234,.2);border-radius:20px;padding:16px;text-decoration:none;color:inherit}
.point-card:active{transform:scale(.98)}
</style>


