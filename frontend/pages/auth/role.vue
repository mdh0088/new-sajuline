<template>
  <div class="min-h-screen bg-slate-950 text-white p-6">
    <main class="pt-[60px] max-w-lg mx-auto">
      <h1 class="text-2xl font-bold mb-4">권한 조회</h1>
      <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div class="flex items-center justify-between">
          <div class="text-white/70">현재 로그인 상태</div>
          <div class="text-right">
            <div class="text-lg font-bold" :class="isAuthenticated ? 'text-green-300' : 'text-red-300'">
              {{ isAuthenticated ? '로그인됨' : '로그인 안 됨' }}
            </div>
            <div v-if="isAuthenticated" class="mt-1 text-sm text-white/70">{{ currentUser?.email }}</div>
          </div>
        </div>

        <div class="mt-5 flex items-center justify-between">
          <div class="text-white/70">역할(Role)</div>
          <div>
            <span v-if="role" class="px-3 py-1 rounded-full text-xs font-semibold border"
                  :class="role==='counselor' ? 'bg-purple-600/20 border-purple-500/40 text-purple-200' : 'bg-teal-600/20 border-teal-500/40 text-teal-200'">
              {{ role==='counselor' ? '상담사' : '유저' }}
            </span>
            <span v-else class="text-white/50">-</span>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/15 active:scale-95" @click="sync">서버에서 새로고침</button>
          <button class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/15 active:scale-95" @click="goMypage">마이페이지 열기</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/common/AppHeader.vue'
import { useAuth } from '~/composables/auth/useAuth'
import { useAuthQueries } from '~/composables/api/useAuthQueries'

// SEO 메타 데이터 설정
useHead({
  title: '권한 조회 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const { isAuthenticated, currentUser, role, isCounselor, setRole } = useAuth()
const { useWhoAmI } = useAuthQueries()
const { refetch } = useWhoAmI()

const sync = async () => {
  const result = await refetch()
  if (result.data) setRole(result.data.role)
}

const goMypage = () => {
  const targetUrl = isCounselor.value ? '/counselor/mypage' : '/user/mypage'
  window.location.href = targetUrl
}
</script>


