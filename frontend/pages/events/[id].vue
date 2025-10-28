<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div v-if="event" class="event-detail">
        <!-- 배너 이미지 (있을 때만) -->
        <div v-if="event.banner_image_url" class="event-detail-thumbnail">
          <img :src="cdnUrl('events', event.banner_image_url)" alt="이벤트 배너" style="width:100%;height:100%;object-fit:cover;border-radius:12px" />
        </div>

        <div class="event-detail-content">
          <!-- 제목 및 메타 정보 -->
          <div class="event-detail-header">
            <span class="event-detail-title">{{ event.event_name }}</span>
            <div class="event-detail-meta">
              <span class="event-detail-date">{{ event.period }}</span>
              <span :class="['event-detail-status', event.status]">
                {{ event.status === 'ongoing' ? '진행중' : (event.status === 'upcoming' ? '진행예정' : '진행완료') }}
              </span>
            </div>
          </div>

          <!-- 랜덤카드 이벤트인 경우 -->
          <RandomCardGame
            v-if="event.event_metadata?.display_type === 'random_card'"
            :config="event.event_metadata?.card_config"
          />

          <!-- 일반 텍스트 이벤트 -->
          <div v-else class="event-detail-body">{{ event.description }}</div>

          <!-- 참여 버튼과 네비게이션 -->
          <div class="event-detail-footer">
            <!-- <button class="event-detail-button" :disabled="event.status === 'completed'">지금 참여하기</button> -->
            <div class="event-navigation-links">
              <NuxtLink
                :to="event.before_event_id ? `/events/${event.before_event_id}` : '#'"
                :class="['event-nav-button', 'prev', { disabled: !event.before_event_id }]"
              >
                <Icon name="mdi:arrow-left" />
                <span>이전 이벤트</span>
              </NuxtLink>
              <NuxtLink
                :to="event.after_event_id ? `/events/${event.after_event_id}` : '#'"
                :class="['event-nav-button', 'next', { disabled: !event.after_event_id }]"
              >
                <span>다음 이벤트</span>
                <Icon name="mdi:arrow-right" />
              </NuxtLink>
            </div>
          </div>

          <!-- 댓글 섹션 주석 처리 -->
          <!-- 댓글 영역 비활성화 -->
        </div>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useEventApi } from '~/composables/api/useEvent'
import { useCdn } from '~/composables/utils/useCdn'
import '~/assets/css/main-page.css'
import '~/assets/css/event/detail.css'

const route = useRoute()
const eventId = computed(() => parseInt(route.params.id as string))
const { useEventDetail } = useEventApi()
const { cdnUrl } = useCdn()

const { data: event } = useEventDetail(eventId)
</script>

<style scoped>
.main-content {
  padding: 20px;
}
</style>