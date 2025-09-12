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
              <div class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-2xl shadow-[0_4px_12px_rgba(255,215,0,0.3)]">🔮</div>
              <div>
                <div class="text-lg font-bold">{{ nickname }}</div>
              </div>
            </div>
            <NuxtLink to="/counselor/price" class="px-3 py-2 text-sm rounded-lg border border-white/10 bg-white/5 hover:bg-white/10">상담료 안내</NuxtLink>
          </div>

          <div class="flex items-center gap-3">
            <div class="inline-flex p-1 rounded-full border border-white/10 bg-white/5">
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='ready' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="status='ready'">대기</button>
              <button :class="['px-4 py-1 rounded-full text-sm font-semibold', status==='away' ? 'bg-purple-600/40 text-purple-100' : 'text-white/70']" @click="status='away'">부재중</button>
            </div>
            <button class="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="saveStatus">변경저장</button>
          </div>

          <!-- 상담사간 카드 -->
          <div class="mt-5 p-5 rounded-2xl bg-gradient-to-br from-blue-900/70 to-blue-800/60 relative overflow-hidden">
            <div class="absolute -top-1/2 -right-1/2 w-[200%] h-[200%] rounded-full bg-white/10 opacity-20"></div>
            <div class="relative">
              <div class="text-base font-bold mb-3">상담사간</div>
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm text-white/80">7월</div>
                  <div class="text-xl font-extrabold">00:00:00</div>
                </div>
                <div>
                  <div class="text-sm text-white/80">8월</div>
                  <div class="text-xl font-extrabold">00:00:00</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 활동시간 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">활동시간</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="notifySaved">변경하기</button>
          </div>
          <input type="text" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" placeholder="매일 04:00~밤 새벽 1:00" v-model="workTime" />
        </div>

        <!-- 짧은 소개글 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">짧은 소개글</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="notifySaved">변경하기</button>
          </div>
          <textarea rows="3" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="shortIntro" placeholder="간단한 소개글을 입력해주세요" />
        </div>

        <!-- 인사말 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">인사말</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="notifySaved">변경하기</button>
          </div>
          <textarea rows="4" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="greeting" placeholder="고객에게 전할 인사말을 입력해주세요" />
        </div>

        <!-- 경력사항 -->
        <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold">경력사항</h3>
            <button class="px-3 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-sm font-semibold active:scale-95" @click="notifySaved">변경하기</button>
          </div>
          <textarea rows="5" class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10" v-model="career" placeholder="상담 경력 및 전문 분야를 입력해주세요" />
        </div>

        <!-- 탭 섹션 -->
        <div class="mt-5">
          <div class="p-1 rounded-xl bg-white/5 border border-white/10 flex">
            <button class="flex-1 py-3 rounded-lg" :class="tab==='notice' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='notice'">공지사항</button>
            <button class="flex-1 py-3 rounded-lg relative" :class="tab==='review' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='review'">고객 후기 <span class="absolute top-1 right-2 text-[10px] font-bold bg-red-500/30 text-red-200 px-2 rounded">26</span></button>
            <button class="flex-1 py-3 rounded-lg" :class="tab==='inquiry' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='inquiry'">상담 문의</button>
            <button class="flex-1 py-3 rounded-lg" :class="tab==='admin' ? 'bg-gradient-to-r from-purple-600 to-purple-700' : ''" @click="tab='admin'">관리자문의</button>
          </div>

          <div class="mt-4">
            <div v-if="tab==='notice'">
              <div class="list-item"><div class="list-item-header"><div class="list-item-title">23.07.31)네이버_엑스퍼트_모집</div><div class="list-item-date">2023.07.31</div></div><div class="list-item-content">네이버 엑스퍼트 상담사 모집 중입니다. 관심 있으신 분들은 지원해주세요.</div></div>
              <div class="list-item"><div class="list-item-header"><div class="list-item-title">6/5)화계팅_상담료 관련</div><div class="list-item-date">2023.06.05</div></div><div class="list-item-content">화계팅 상담료 관련 공지사항입니다. 자세한 내용은 클릭하여 확인해주세요.</div></div>
            </div>
            <div v-else-if="tab==='review'">
              <div class="list-item"><div class="list-item-header"><div class="list-item-title">정말 잘 맞아요!</div><div class="list-item-date">2024.01.15</div></div><div class="list-item-content">선생님 상담 받고 마음이 편해졌어요. 앞으로도 잘 부탁드립니다.</div></div>
              <div class="list-item"><div class="list-item-header"><div class="list-item-title">감사합니다</div><div class="list-item-date">2024.01.14</div></div><div class="list-item-content">친절하고 자세한 상담 감사합니다. 많은 도움이 되었어요.</div></div>
            </div>
            <div v-else>
              <div class="empty-state text-center py-10 text-white/40">
                <div class="text-5xl mb-3">📭</div>
                <div class="text-sm">새로운 항목이 없습니다</div>
              </div>
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

definePageMeta({
  middleware: [auth],
  requiresAuth: true,
  requireRole: 'counselor'
})
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'
import { computed, ref, watchEffect } from 'vue'
import { useCounselorQueries } from '~/composables/api/useCounselorQueries'
import { useAuth } from '~/composables/auth/useAuth'
import { useNotify } from '~/composables/utils/useNotify'

const { requireAuth, isCounselor, currentUser } = useAuth()
const { notifySuccess } = useNotify()
await requireAuth()

const { useMypage } = useCounselorQueries()
const { data: mypage } = useMypage()

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

const notifySaved = () => notifySuccess('💾 변경 사항이 저장되었습니다.')
const saveStatus = () => notifySuccess(`✅ 상태가 '${status.value === 'ready' ? '대기' : '부재중'}'로 변경되었습니다.`)
</script>

<style scoped>
.list-item{padding:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1);border-radius:12px;margin-bottom:12px}
.list-item-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.list-item-title{font-size:15px;font-weight:600}
.list-item-date{font-size:12px;color:rgba(255,255,255,.5)}
.list-item-content{font-size:14px;color:rgba(255,255,255,.7);line-height:1.5;display:-webkit-box;line-clamp:2;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
</style>


