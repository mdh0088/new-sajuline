<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <main class="pt-[60px] pb-24">
      <div class="px-5 py-6">
        <!-- 상담 내역 리스트 -->
        <div v-if="consultHistory.length > 0" class="space-y-4">
          <div
            v-for="item in consultHistory"
            :key="item.id"
            class="history-item"
          >
            <!-- 상담사 정보 및 메타 -->
            <div class="flex justify-between items-start gap-4 mb-4">
              <div class="flex items-center gap-4">
                <div class="counselor-thumb">
                  {{ item.counselor.emoji || '👩‍🦰' }}
                </div>
                <div class="flex flex-col gap-1">
                  <span class="counselor-name">
                    {{ item.counselor.name }}
                  </span>
                  <span class="counselor-type">
                    {{ item.counselor.specialty }}
                  </span>
                </div>
              </div>
              <div class="flex flex-col gap-1 items-end">
                <span class="session-date">
                  {{ formatDate(item.createdAt) }}
                </span>
                <span
                  class="session-status"
                  :class="getStatusClass(item.status)"
                >
                  {{ getStatusText(item.status) }}
                </span>
              </div>
            </div>

            <!-- 상담 내용 -->
            <div class="consultation-content">
              <strong>상담 주제</strong>
              <p>{{ item.topic }}</p>

              <strong>상세 내용</strong>
              <p>{{ item.content }}</p>

              <div class="session-info">
                <div class="session-time">
                  상담 시간: {{ item.duration }}분
                </div>
              </div>
            </div>

            <!-- 액션 버튼 -->
            <div
              v-if="item.status === 'completed' && !item.reviewSubmitted"
              class="flex justify-end mt-4"
            >
              <button
                @click="openReviewModal(item)"
                class="review-button"
              >
                후기 작성
              </button>
            </div>
          </div>
        </div>

        <!-- 빈 상태 -->
        <div v-else class="empty-state">
          <div class="empty-icon">📭</div>
          <div class="empty-title">상담 내역이 없습니다</div>
          <div class="empty-desc">상담을 통해 적립된 내역이 표시됩니다.</div>
        </div>
      </div>
    </main>


    <!-- 후기 작성 모달 -->
    <div
      v-if="showReviewModal"
      class="modal-overlay"
      @click="closeReviewModal"
    >
      <div
        class="modal-content"
        @click.stop
      >
        <div class="modal-header">
          <h3 class="modal-title">후기 작성</h3>
          <button
            @click="closeReviewModal"
            class="modal-close"
          >
            ×
          </button>
        </div>

        <form @submit.prevent="submitReview" class="review-form">
          <!-- 별점 입력 -->
          <div class="rating-input">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              @click="setRating(n)"
              class="rating-star"
              :class="{ active: n <= reviewForm.rating }"
            >
              ⭐
            </button>
          </div>

          <!-- 후기 내용 -->
          <textarea
            v-model="reviewForm.content"
            placeholder="상담에 대한 후기를 작성해주세요."
            class="review-textarea"
          ></textarea>

          <!-- 버튼 -->
          <div class="modal-footer">
            <button
              type="button"
              @click="closeReviewModal"
              class="modal-button cancel-button"
            >
              취소
            </button>
            <button
              type="submit"
              class="modal-button submit-button"
            >
              작성완료
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

definePageMeta({
  middleware: ['auth'],
  requiresAuth: true,
  requireRole: 'user'
})

// 상담 내역 데이터 (임시 - 실제로는 API에서 가져옴)
const consultHistory = ref([
  {
    id: 1,
    counselor: {
      name: '김지은 상담사',
      specialty: '사주 전문가',
      emoji: '👩‍🦰'
    },
    topic: '2025년 하반기 사업 운세',
    content: '사업 확장 시기 및 투자 방향에 대해 상담했습니다. 특히 올해 하반기에 예상되는 시장 변화와 그에 따른 대응 방안에 대해 자세히 논의했습니다.',
    duration: 30,
    status: 'completed',
    reviewSubmitted: false,
    createdAt: '2025-06-05T14:30:00Z'
  },
  {
    id: 2,
    counselor: {
      name: '박준현 상담사',
      specialty: '타로 전문가',
      emoji: '👨‍💼'
    },
    topic: '연애 문제 해결 방안',
    content: '이성 관계에서의 갈등 해소 및 소통 방법에 대해 상담했습니다. 현재 상황에서의 감정적 어려움과 앞으로의 관계 발전 방향에 대해 심도 있게 논의했습니다.',
    duration: 45,
    status: 'completed',
    reviewSubmitted: false,
    createdAt: '2025-05-20T10:00:00Z'
  },
  {
    id: 3,
    counselor: {
      name: '이소민 상담사',
      specialty: '사주·타로 통합',
      emoji: '🧑'
    },
    topic: '건강운 상담',
    content: '갑작스러운 일정 변경으로 인해 취소되었습니다.',
    duration: 30,
    status: 'cancelled',
    reviewSubmitted: false,
    createdAt: '2025-05-10T16:45:00Z'
  }
])

// 후기 모달 관련
const showReviewModal = ref(false)
const selectedConsultation = ref<any>(null)
const reviewForm = ref({
  rating: 0,
  content: ''
})

// 날짜 포맷팅
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\./g, '.').replace(/ /g, ' ')
}

// 상태 텍스트
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '완료'
    case 'cancelled': return '취소'
    case 'pending': return '대기'
    default: return '알 수 없음'
  }
}

// 상태 스타일 클래스
const getStatusClass = (status: string) => {
  switch (status) {
    case 'completed': return 'status-completed'
    case 'cancelled': return 'status-cancelled'
    case 'pending': return 'status-pending'
    default: return ''
  }
}

// 후기 모달 열기
const openReviewModal = (consultation: any) => {
  selectedConsultation.value = consultation
  showReviewModal.value = true
  reviewForm.value = { rating: 0, content: '' }
}

// 후기 모달 닫기
const closeReviewModal = () => {
  showReviewModal.value = false
  selectedConsultation.value = null
  reviewForm.value = { rating: 0, content: '' }
}

// 별점 설정
const setRating = (rating: number) => {
  reviewForm.value.rating = rating
}

// 후기 제출
const submitReview = () => {
  if (reviewForm.value.rating === 0) {
    alert('별점을 선택해주세요.')
    return
  }

  if (!reviewForm.value.content.trim()) {
    alert('후기 내용을 입력해주세요.')
    return
  }

  // TODO: API 호출하여 후기 제출
  console.log('후기 제출:', {
    consultationId: selectedConsultation.value?.id,
    rating: reviewForm.value.rating,
    content: reviewForm.value.content
  })

  // 제출 완료 후 상태 업데이트
  if (selectedConsultation.value) {
    selectedConsultation.value.reviewSubmitted = true
  }

  closeReviewModal()
  alert('후기가 성공적으로 작성되었습니다.')
}
</script>

<style>
@import '~/assets/css/user/cslog.css';
</style>