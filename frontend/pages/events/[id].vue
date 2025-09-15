<template>
  <div class="event-detail-page">
    <!-- 헤더 -->
    <header class="event-header">
      <div class="event-header-top">
        <button class="event-back-button" @click="$router.back()">
          <Icon name="mdi:arrow-left" />
        </button>
        <h1 class="event-header-title">이벤트 상세</h1>
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
      <div v-if="event" class="event-detail">
        <!-- 썸네일 -->
        <div class="event-detail-thumbnail">{{ event.icon }}</div>

        <div class="event-detail-content">
          <!-- 제목 및 메타 정보 -->
          <div class="event-detail-header">
            <span class="event-detail-title">{{ event.title }}</span>
            <div class="event-detail-meta">
              <span class="event-detail-date">{{ event.period }}</span>
              <span :class="['event-detail-status', event.status]">
                {{ event.status === 'ongoing' ? '진행중' : '진행완료' }}
              </span>
            </div>
          </div>

          <!-- 상세 설명 -->
          <div class="event-detail-body">{{ event.content || event.description }}</div>

          <!-- 참여 버튼과 네비게이션 -->
          <div class="event-detail-footer">
            <button
              class="event-detail-button"
              :disabled="event.status === 'completed'"
              @click="handleEventAction"
            >
              {{ event.status === 'ongoing' ? '지금 참여하기' : '종료됨' }}
            </button>
            <div class="event-navigation-links">
              <NuxtLink
                :to="prevEventId ? `/events/${prevEventId}` : '#'"
                :class="['event-nav-button', 'prev', { disabled: !prevEventId }]"
              >
                <Icon name="mdi:arrow-left" />
                <span>이전 이벤트</span>
              </NuxtLink>
              <NuxtLink
                :to="nextEventId ? `/events/${nextEventId}` : '#'"
                :class="['event-nav-button', 'next', { disabled: !nextEventId }]"
              >
                <span>다음 이벤트</span>
                <Icon name="mdi:arrow-right" />
              </NuxtLink>
            </div>
          </div>

          <!-- 댓글 섹션 -->
          <div class="event-comments-section">
            <h2 class="event-comments-title">
              댓글
              <span class="event-comment-count">({{ comments.length }})</span>
            </h2>
            <div v-if="comments.length > 0" class="event-comments-list">
              <div v-for="comment in comments" :key="comment.id" class="event-comment-item">
                <div class="event-comment-header">
                  <div class="event-comment-author">
                    <span>{{ comment.userName }}</span>
                    <span v-if="comment.isAuthor" class="event-author-badge">작성자</span>
                  </div>
                  <div class="event-comment-actions">
                    <button
                      :class="['event-action-button', 'like', { active: comment.isLiked }]"
                      @click="toggleLike(comment)"
                    >
                      <span>{{ comment.isLiked ? '❤️' : '🤍' }}</span>
                      <span class="event-like-count">{{ comment.likeCount }}</span>
                    </button>
                    <span class="event-comment-date">{{ formatDate(comment.createdAt) }}</span>
                    <button v-if="comment.isAuthor" class="event-action-button edit" @click="editComment(comment)">
                      수정
                    </button>
                    <button v-if="comment.isAuthor" class="event-action-button delete" @click="deleteComment(comment)">
                      삭제
                    </button>
                  </div>
                </div>
                <p class="event-comment-text">{{ comment.content }}</p>
                <div :class="['event-comment-edit-form', { active: editingCommentId === comment.id }]">
                  <textarea v-model="editingContent" class="event-comment-edit-input"></textarea>
                  <div class="event-edit-actions">
                    <button class="event-edit-button cancel" @click="cancelEdit">취소</button>
                    <button class="event-edit-button save" @click="saveEdit(comment)">저장</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="event-comment-form">
              <textarea
                v-model="newComment"
                class="event-comment-input"
                placeholder="댓글을 입력하세요..."
              ></textarea>
              <button class="event-comment-submit" @click="submitComment">등록</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 하단 네비게이션 -->
    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { IEvent, IEventComment } from '~/types/event'
import '~/assets/css/event/detail.css'

const route = useRoute()
const eventId = computed(() => parseInt(route.params.id as string))

// 임시 이벤트 데이터
const events: IEvent[] = [
  {
    id: 1,
    icon: '🎉',
    title: '첫 충전 2배 보너스',
    period: '2025.06.01 ~ 2025.06.30',
    status: 'ongoing',
    description: '신규 회원님께 첫 포인트 충전 시 보너스 포인트 100% 증정! 최대 50,000P까지 적용됩니다.',
    buttonText: '참여하기',
    content: `안녕하세요, 사주라인 회원님!

🎁 신규 회원님을 위한 특별 혜택!
오늘 첫 포인트 충전 시 보너스 포인트 100% 증정 이벤트를 진행 중입니다.
예를 들어, 10,000P를 충전하시면 10,000P 추가 적립되어 총 20,000P를 받으실 수 있습니다.

📌 주요 내용
・ 이벤트 기간: 2025년 6월 1일(월) 오전 00:00 ~ 6월 30일(화) 오후 23:59
・ 대상: 사주라인 신규 회원 한정
・ 보너스 한도: 최대 50,000P

💡 참여 방법
1. 사주라인 앱 혹은 웹에서 회원가입 후 로그인
2. '포인트 충전' 메뉴에서 첫 충전 금액 입력
3. 결제 완료 시 자동으로 보너스 포인트 적립

⚠️ 유의 사항
・ 이미 포인트를 충전한 기록이 있는 경우 본 이벤트 참여가 제한될 수 있습니다.
・ 이벤트 종료 후에는 자동 보너스 지급이 중단됩니다.
・ 부정한 방법으로 참여 시 적립된 보너스는 회수될 수 있습니다.

궁금하신 점은 고객센터(1:1 문의)를 통해 문의해주시기 바랍니다.
많은 참여 부탁드립니다!`
  },
  {
    id: 2,
    icon: '🔮',
    title: '타로 무료 뽑기',
    period: '상시 진행 중',
    status: 'ongoing',
    description: '매일 한 번! 무료 타로 카드 뽑기를 통해 당신의 오늘 운세를 확인해보세요.',
    buttonText: '뽑기 하러 가기',
    content: `타로 무료 뽑기 이벤트 상세 내용...`
  },
  {
    id: 3,
    icon: '🎁',
    title: '리뷰 작성시 포인트 적립',
    period: '2025.05.15 ~ 2025.07.15',
    status: 'ongoing',
    description: '상담 후 리뷰를 작성하면 500P를 즉시 적립해드립니다.',
    buttonText: '리뷰 작성하기',
    content: `리뷰 작성 이벤트 상세 내용...`
  }
]

const event = computed(() => events.find(e => e.id === eventId.value))
const prevEventId = computed(() => {
  const currentIndex = events.findIndex(e => e.id === eventId.value)
  return currentIndex > 0 ? events[currentIndex - 1]?.id ?? null : null
})
const nextEventId = computed(() => {
  const currentIndex = events.findIndex(e => e.id === eventId.value)
  return currentIndex < events.length - 1 ? events[currentIndex + 1]?.id ?? null : null
})

// 댓글 관련
const comments = ref<IEventComment[]>([
  {
    id: 1,
    eventId: 1,
    userId: 1,
    userName: '사용자1',
    content: '이벤트 기대됩니다! 포인트 충전하고 싶네요.',
    likeCount: 3,
    isLiked: true,
    isAuthor: true,
    createdAt: '2025-06-05T00:00:00Z'
  },
  {
    id: 2,
    eventId: 1,
    userId: 2,
    userName: '사용자2',
    content: '최대 50,000P까지라니 정말 좋은 혜택이네요!',
    likeCount: 1,
    isLiked: false,
    isAuthor: false,
    createdAt: '2025-06-04T00:00:00Z'
  },
  {
    id: 3,
    eventId: 1,
    userId: 3,
    userName: '사용자3',
    content: '이벤트 기간이 한 달이나 되니까 여유롭게 참여할 수 있겠네요.',
    likeCount: 0,
    isLiked: false,
    isAuthor: false,
    createdAt: '2025-06-03T00:00:00Z'
  }
])

const newComment = ref('')
const editingCommentId = ref<number | null>(null)
const editingContent = ref('')

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const toggleLike = (comment: IEventComment) => {
  if (comment.isLiked) {
    comment.likeCount--
    comment.isLiked = false
  } else {
    comment.likeCount++
    comment.isLiked = true
  }
}

const editComment = (comment: IEventComment) => {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
}

const cancelEdit = () => {
  editingCommentId.value = null
  editingContent.value = ''
}

const saveEdit = (comment: IEventComment) => {
  comment.content = editingContent.value
  cancelEdit()
}

const deleteComment = (comment: IEventComment) => {
  if (confirm('댓글을 삭제하시겠습니까?')) {
    const index = comments.value.findIndex(c => c.id === comment.id)
    if (index > -1) {
      comments.value.splice(index, 1)
    }
  }
}

const submitComment = () => {
  if (!newComment.value.trim()) return

  const newCommentObj: IEventComment = {
    id: comments.value.length + 1,
    eventId: eventId.value,
    userId: 999,
    userName: '현재 사용자',
    content: newComment.value,
    likeCount: 0,
    isLiked: false,
    isAuthor: true,
    createdAt: new Date().toISOString()
  }

  comments.value.push(newCommentObj)
  newComment.value = ''
}

const handleEventAction = () => {
  if (event.value?.status === 'completed') return

  // TODO: 이벤트 참여 처리
  console.log('Event action:', event.value?.id)
}
</script>