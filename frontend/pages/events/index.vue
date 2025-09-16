<template>
  <div class="event-page">
    <!-- 헤더 -->
    <header class="event-header">
      <div class="event-header-top">
        <button class="event-back-button" @click="$router.back()">
          <Icon name="mdi:arrow-left" />
        </button>
        <h1 class="event-header-title">이벤트</h1>
        <div class="event-header-actions">
          <button class="event-icon-btn">
            <Icon name="mdi:magnify" />
          </button>
          <button class="event-icon-btn" @click="$router.push('/user/mypage')">
            <Icon name="mdi:account" />
          </button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="event-main-content">
      <!-- 이벤트 리스트 -->
      <div v-if="items.length > 0" class="event-list">
        <NuxtLink
          v-for="event in items"
          :key="event.id"
          :to="`/events/${event.id}`"
          :class="['event-item', { completed: event.status === 'completed' }]"
        >
          <div class="event-item-header">
            <div class="event-info">
              <span class="event-title">{{ event.title }}</span>
              <div class="event-meta">
                <span class="event-date">{{ event.period }}</span>
                <span :class="['event-status', event.status]">
                  {{ event.status === 'ongoing' ? '진행중' : (event.status === 'upcoming' ? '진행예정' : '진행완료') }}
                </span>
              </div>
            </div>
          </div>
          <div class="event-body line-clamp-2">{{ event.description }}</div>
          <div class="event-footer">
            <button
              class="event-button"
              @click.prevent
            >
              확인하기
            </button>
          </div>
        </NuxtLink>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="event-empty-state">
        <div class="event-empty-icon">📭</div>
        <div class="event-empty-title">진행 중인 이벤트가 없습니다</div>
        <div class="event-empty-desc">새로운 이벤트가 등록되는 대로 알려드릴게요!</div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="event-pagination">
        <button
          :class="['event-page-button', { disabled: currentPage === 1 }]"
          @click="changePage(currentPage - 1)"
        >
          <Icon name="mdi:chevron-left" />
        </button>

        <template v-for="page in displayPages" :key="page">
          <button
            v-if="page !== '...'"
            :class="['event-page-button', { active: page === currentPage }]"
            @click="changePage(page as number)"
          >
            {{ page }}
          </button>
          <span v-else class="event-page-ellipsis">...</span>
        </template>

        <button
          :class="['event-page-button', { disabled: currentPage === totalPages }]"
          @click="changePage(currentPage + 1)"
        >
          <Icon name="mdi:chevron-right" />
        </button>
      </div>
    </main>

    <!-- 하단 네비게이션 -->
    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEventApi } from '~/composables/api/useEvent'
import '~/assets/css/event/list.css'

const { useEventList } = useEventApi()
const { data } = useEventList()

const currentPage = ref(1)
const itemsPerPage = 10
const items = computed(() => data.value ?? [])
const totalPages = computed(() => Math.ceil(items.value.length / itemsPerPage))

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return items.value.slice(start, end)
})

const displayPages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }

  return pages
})

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 버튼은 상세 링크로 대체되므로 추가 액션 없음
</script>