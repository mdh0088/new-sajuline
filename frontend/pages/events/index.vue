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
      <div v-if="events.length > 0" class="event-list">
        <NuxtLink
          v-for="event in paginatedEvents"
          :key="event.id"
          :to="`/events/${event.id}`"
          :class="['event-item', { completed: event.status === 'completed' }]"
        >
          <div class="event-item-header">
            <div class="event-thumbnail">{{ event.icon }}</div>
            <div class="event-info">
              <span class="event-title">{{ event.title }}</span>
              <div class="event-meta">
                <span class="event-date">{{ event.period }}</span>
                <span :class="['event-status', event.status]">
                  {{ event.status === 'ongoing' ? '진행중' : '진행완료' }}
                </span>
              </div>
            </div>
          </div>
          <div class="event-body">{{ event.description }}</div>
          <div class="event-footer">
            <button
              class="event-button"
              :disabled="event.status === 'completed'"
              @click.prevent="handleEventAction(event)"
            >
              {{ event.status === 'ongoing' ? event.buttonText : '종료됨' }}
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
import type { IEvent } from '~/types/event'
import '~/assets/css/event/list.css'

// 임시 데이터
const events = ref<IEvent[]>([
  {
    id: 1,
    icon: '🎉',
    title: '첫 충전 2배 보너스',
    period: '2025.06.01 ~ 2025.06.30',
    status: 'ongoing',
    description: '신규 회원님께 첫 포인트 충전 시 보너스 포인트 100% 증정! 최대 50,000P까지 적용됩니다.',
    buttonText: '참여하기'
  },
  {
    id: 2,
    icon: '🔮',
    title: '타로 무료 뽑기',
    period: '상시 진행 중',
    status: 'ongoing',
    description: '매일 한 번! 무료 타로 카드 뽑기를 통해 당신의 오늘 운세를 확인해보세요. 결과 공유 시 추가 포인트 지급.',
    buttonText: '뽑기 하러 가기'
  },
  {
    id: 3,
    icon: '🎁',
    title: '리뷰 작성시 포인트 적립',
    period: '2025.05.15 ~ 2025.07.15',
    status: 'ongoing',
    description: '상담 후 리뷰를 작성하면 500P를 즉시 적립해드립니다. 솔직한 후기만 남겨주세요!',
    buttonText: '리뷰 작성하기'
  },
  {
    id: 4,
    icon: '🎁',
    title: '지난 달 이벤트 예시',
    period: '2025.04.01 ~ 2025.04.30',
    status: 'completed',
    description: '지난 달에 진행된 특별 이벤트로, 모든 회원님께 감사드립니다.',
    buttonText: '종료됨'
  }
])

const currentPage = ref(1)
const itemsPerPage = 10
const totalPages = computed(() => Math.ceil(events.value.length / itemsPerPage))

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return events.value.slice(start, end)
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

const handleEventAction = (event: IEvent) => {
  if (event.status === 'completed') return

  // TODO: 이벤트별 액션 처리
  console.log('Event action:', event.id)
}
</script>