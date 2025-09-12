<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <main class="pt-[60px] pb-24">
      <!-- 유저 마이페이지: 프로토타입 반영 -->
      <section class="px-5 py-6">
        <div class="text-center mb-6">
          <div class="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-purple-600/30 to-purple-700/20 flex items-center justify-center text-5xl shadow-[0_8px_32px_rgba(147,51,234,0.3)] relative">
            👤
            <button class="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-purple-600 border-4 border-slate-950 text-sm">✏️</button>
          </div>
          <h2 class="text-2xl font-bold mt-4">{{ nickname }}</h2>
          <p class="text-white/60 text-sm">{{ email }}</p>
        </div>

        <!-- 포인트 카드 -->
        <div class="rounded-2xl border border-yellow-400/30 bg-gradient-to-br from-yellow-400/10 to-yellow-400/5 p-5 mb-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold flex items-center gap-2">💰 <span>내 포인트</span></h3>
          </div>
          <div class="text-3xl font-extrabold text-yellow-300 mb-4">{{ points.toLocaleString() }} P</div>
          <div class="flex gap-3">
            <NuxtLink to="/point" class="flex-1 py-3 rounded-xl bg-gradient-to-r from-yellow-400 to-amber-400 text-slate-950 font-semibold text-center active:scale-95">충전하기</NuxtLink>
            <NuxtLink to="/point/log" class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/15 font-semibold text-center active:scale-95">사용내역</NuxtLink>
          </div>
        </div>

        <!-- 등급 진행도 -->
        <div class="rounded-2xl border border-purple-500/30 bg-purple-500/5 p-5 mb-5">
          <div class="flex items-center justify-between mb-3">
            <div class="text-purple-200 font-semibold flex items-center gap-2">🎯 <span>다음 등급까지</span></div>
            <div class="text-sm text-white/80">{{ gradeRemaining }}</div>
          </div>
          <div class="w-full h-2 rounded-lg bg-white/10 overflow-hidden">
            <div class="h-full bg-gradient-to-r from-purple-600 to-purple-300 rounded-lg" :style="{ width: progressWidth }"></div>
          </div>
          <div class="flex items-center justify-between mt-2 text-xs text-white/60">
            <div class="flex items-center gap-1">🥉 <span class="text-purple-200 font-medium">{{ currentGrade }}</span></div>
            <div class="flex items-center gap-1">👑 <span class="text-white/80 font-medium">{{ nextGrade }}</span></div>
          </div>
        </div>

        <!-- 요약 카드들 -->
        <div class="grid grid-cols-3 gap-3 mb-6">
          <NuxtLink to="/consults" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.consults }}</div>
            <div class="text-xs text-white/60">총 상담</div>
          </NuxtLink>
          <NuxtLink to="/favorites" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.favorites }}</div>
            <div class="text-xs text-white/60">즐겨찾기</div>
          </NuxtLink>
          <NuxtLink to="/reviews" class="point-card">
            <div class="text-2xl font-bold text-purple-200">{{ stats.reviews }}</div>
            <div class="text-xs text-white/60">후기작성</div>
          </NuxtLink>
        </div>

        <!-- 메뉴 그룹 -->
        <div class="space-y-6">
          <div>
            <h4 class="text-sm text-white/60 mb-2 px-1">상담 관리</h4>
            <div class="rounded-2xl overflow-hidden border border-white/10">
              <NuxtLink to="/consults" class="menu-item"><div class="menu-left"><div class="menu-icon">💬</div><div><div class="menu-title">상담 내역</div><div class="menu-desc">지난 상담 기록 확인</div></div></div><div class="menu-right">›</div></NuxtLink>
              <NuxtLink to="/favorites" class="menu-item"><div class="menu-left"><div class="menu-icon">⭐</div><div><div class="menu-title">즐겨찾기 상담사</div><div class="menu-desc">자주 찾는 상담사 관리</div></div></div><div class="menu-right">›</div></NuxtLink>
              <NuxtLink to="/reviews" class="menu-item"><div class="menu-left"><div class="menu-icon">📝</div><div><div class="menu-title">상담 후기</div><div class="menu-desc">내가 작성한 후기 보기</div></div></div><div class="menu-right">›</div></NuxtLink>
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
definePageMeta({
  middleware: ['auth'],
  requiresAuth: true,
  requireRole: 'user'
})
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { computed } from 'vue'
import { useAuth } from '~/composables/auth/useAuth'

const { currentUser, requireAuth } = useAuth()
await requireAuth()

const nickname = computed(() => currentUser.value?.nickname ?? '사용자')
const email = computed(() => currentUser.value?.email ?? '')
const points = 1200
const stats = { consults: 156, favorites: 12, reviews: 89 }
const gradeRemaining = '300,000원 남음'
const currentGrade = 'SILVER'
const nextGrade = 'VIP'
const progressWidth = '35%'

const goNotice = () => navigateTo('/notice')
const goCs = () => navigateTo('/cs')
const goTerms = () => navigateTo('/terms')
const goPrivacy = () => navigateTo('/privacy')
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


