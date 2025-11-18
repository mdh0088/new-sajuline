<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <main class="pt-[60px] pb-24">
      <div class="px-5 py-6">
        <!-- 즐겨찾기 상담사 리스트 -->
        <div v-if="items.length > 0" class="favorite-list">
          <div
            v-for="c in items"
            :key="c.counselor_id"
            class="favorite-item"
          >
            <!-- 즐겨찾기 해제 버튼 (요구: class 그대로 유지) -->
            <button
              class="unfavorite-button"
              @click.stop="onUnfavorite(c)"
              aria-label="즐겨찾기 해제"
            >
              ×
            </button>

            <CounselorCardCompact :counselor="c" />
          </div>
        </div>

        <!-- 빈 상태 -->
        <div v-else class="empty-state">
          <div class="empty-icon">📭</div>
          <div class="empty-title">즐겨찾기한 상담사가 없습니다</div>
          <div class="empty-desc">마음에 드는 상담사를 찾아 즐겨찾기에 추가해보세요!</div>
          <NuxtLink
            to="/categories"
            class="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-xl font-semibold"
          >
            상담사 찾아보기
          </NuxtLink>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CounselorCardCompact from '~/components/counselor/CounselorCardCompact.vue'
import { useBookmarkQueries } from '~/composables/api/useBookmarkQueries'
import type { CounselorSearchItem } from '~/types/counselor/search'
import { useNotify } from '~/composables/utils/useNotify'

definePageMeta({
  middleware: ['auth'],
  requiresAuth: true,
  requireRole: 'user'
})

// SEO 메타 데이터 설정
useHead({
  title: '찜한 상담사 - 사주라인',
  meta: [
    { name: 'robots', content: 'noindex,nofollow' }
  ]
})

const { useBookmarkList, useRemoveBookmark } = useBookmarkQueries()
const page = ref(1)
const limit = ref(20)
const { data } = useBookmarkList({ page: page.value, limit: limit.value })
const items = computed<CounselorSearchItem[]>(() => data?.value?.items ?? [])

const { mutate: removeBookmark, isPending: removing } = useRemoveBookmark({})
const { notifyConfirm, notifySuccess, notifyError } = useNotify()
const onUnfavorite = async (c: CounselorSearchItem) => {
  if (!c?.counselor_id || removing.value) return
  const confirmed = await notifyConfirm(`'${c.nickname}' 상담사를 즐겨찾기에서 해제하시겠습니까?`)
  if (!confirmed) return
  try {
    removeBookmark(c.counselor_id)
    notifySuccess('즐겨찾기에서 해제되었습니다.')
  } catch (e: any) {
    notifyError(e?.message || '해제에 실패했습니다.')
  }
}

// 모달/전화상담 관련 기존 UI 제거 (요구사항 범위 밖)
</script>

<style>
@import '~/assets/css/user/favorite.css';
</style>