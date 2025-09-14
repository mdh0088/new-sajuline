<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader title="즐겨찾기한 상담사" />

    <main class="pt-[60px] pb-24">
      <div class="px-5 py-6">
        <!-- 즐겨찾기 상담사 리스트 -->
        <div v-if="favoriteCounselors.length > 0" class="favorite-list">
          <div
            v-for="counselor in favoriteCounselors"
            :key="counselor.id"
            class="favorite-item"
            @click="goToCounselorProfile(counselor.id)"
          >
            <!-- 즐겨찾기 해제 버튼 -->
            <button
              @click.stop="confirmUnfavorite(counselor)"
              class="unfavorite-button"
            >
              ×
            </button>

            <!-- 상담사 헤더 -->
            <div class="counselor-header">
              <div
                class="item-thumbnail"
                :class="{ online: counselor.isOnline }"
              >
                <span>{{ counselor.emoji }}</span>
              </div>
              <div class="item-info">
                <div class="item-header">
                  <div class="item-name-wrapper">
                    <div class="item-name">{{ counselor.name }}</div>
                    <div class="item-number">#{{ counselor.number }}</div>
                  </div>
                  <div class="item-tier">{{ counselor.tier }}</div>
                </div>

                <!-- 상태 인디케이터 -->
                <div class="status-indicator">
                  <div
                    class="status-dot"
                    :class="counselor.isOnline ? 'status-online' : 'status-offline'"
                  ></div>
                  <span :class="counselor.isOnline ? 'text-green-400' : 'text-white/50'">
                    {{ counselor.isOnline ? '상담 가능' : '상담 중' }}
                  </span>
                </div>

                <!-- 전문 분야 -->
                <div class="item-details">
                  <span
                    v-for="specialty in counselor.specialties"
                    :key="specialty"
                    class="detail-chip"
                  >
                    {{ specialty }}
                  </span>
                </div>

                <!-- 상담사 소개 -->
                <div class="item-description">
                  {{ counselor.description }}
                </div>

                <!-- 액션 영역 -->
                <div class="item-actions">
                  <div class="rating">
                    <div class="rating-stars">
                      <span
                        v-for="n in 5"
                        :key="n"
                        class="star"
                        :style="{ opacity: n <= counselor.rating ? 1 : 0.3 }"
                      >
                        ★
                      </span>
                    </div>
                    <span class="rating-info">
                      {{ counselor.rating }} ({{ counselor.reviewCount }})
                    </span>
                  </div>

                  <!-- 상담 유형 버튼 -->
                  <div class="consult-types">
                    <button
                      v-if="counselor.consultTypes.includes('phone')"
                      @click.stop="startConsult(counselor.id, 'phone')"
                      class="consult-type-btn primary"
                      :disabled="!counselor.isOnline"
                    >
                      전화상담
                    </button>
                    <button
                      v-if="counselor.consultTypes.includes('chat')"
                      @click.stop="startConsult(counselor.id, 'chat')"
                      class="consult-type-btn"
                      :disabled="!counselor.isOnline"
                    >
                      채팅상담
                    </button>
                  </div>
                </div>
              </div>
            </div>
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

    <AppBottomNavi />

    <!-- 즐겨찾기 해제 확인 모달 -->
    <div
      v-if="showConfirmModal"
      class="confirm-modal"
      @click="closeConfirmModal"
    >
      <div
        class="confirm-content"
        @click.stop
      >
        <div class="confirm-title">즐겨찾기 해제</div>
        <div class="confirm-message">
          {{ selectedCounselor?.name }} 상담사를<br>
          즐겨찾기에서 해제하시겠습니까?
        </div>
        <div class="confirm-buttons">
          <button
            @click="closeConfirmModal"
            class="confirm-btn confirm-cancel"
          >
            취소
          </button>
          <button
            @click="removeFavorite"
            class="confirm-btn confirm-delete"
          >
            해제
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

definePageMeta({
  middleware: ['auth'],
  requiresAuth: true,
  requireRole: 'user'
})

const router = useRouter()

// 즐겨찾기 상담사 데이터 (임시 - 실제로는 API에서 가져옴)
const favoriteCounselors = ref([
  {
    id: 1234,
    name: '김철수',
    number: '1234',
    tier: '프리미엄 상담사',
    emoji: '👨‍💼',
    isOnline: true,
    specialties: ['사주명리', '궁합', '운세'],
    description: '20년 경력의 사주명리 전문가입니다. 정확한 사주 분석과 따뜻한 상담으로 많은 분들의 신뢰를 받고 있습니다.',
    rating: 4.9,
    reviewCount: 128,
    consultTypes: ['phone', 'chat']
  },
  {
    id: 1235,
    name: '이지은',
    number: '1235',
    tier: '골드 상담사',
    emoji: '👩‍💼',
    isOnline: false,
    specialties: ['타로', '연애운', '직업운'],
    description: '섬세한 타로 리딩으로 연애와 직업에 대한 정확한 조언을 제공합니다. 따뜻한 상담으로 유명합니다.',
    rating: 4.8,
    reviewCount: 95,
    consultTypes: ['phone', 'chat']
  },
  {
    id: 1236,
    name: '박민수',
    number: '1236',
    tier: '실버 상담사',
    emoji: '🧑‍💼',
    isOnline: true,
    specialties: ['사주', '타로', '꿈해몽'],
    description: '다양한 분야의 전문 지식을 바탕으로 종합적인 상담을 제공합니다. 친근하고 이해하기 쉬운 설명이 특징입니다.',
    rating: 4.7,
    reviewCount: 67,
    consultTypes: ['phone']
  }
])

// 모달 관련
const showConfirmModal = ref(false)
const selectedCounselor = ref<any>(null)

// 즐겨찾기 해제 확인
const confirmUnfavorite = (counselor: any) => {
  selectedCounselor.value = counselor
  showConfirmModal.value = true
}

// 모달 닫기
const closeConfirmModal = () => {
  showConfirmModal.value = false
  selectedCounselor.value = null
}

// 즐겨찾기 해제
const removeFavorite = () => {
  if (selectedCounselor.value) {
    const index = favoriteCounselors.value.findIndex(
      c => c.id === selectedCounselor.value.id
    )
    if (index > -1) {
      favoriteCounselors.value.splice(index, 1)
    }

    // TODO: API 호출하여 즐겨찾기 해제
    console.log('즐겨찾기 해제:', selectedCounselor.value.id)
  }
  closeConfirmModal()
}

// 상담사 프로필로 이동
const goToCounselorProfile = (counselorId: number) => {
  router.push(`/counselor/${counselorId}`)
}

// 상담 시작
const startConsult = (counselorId: number, type: string) => {
  if (type === 'phone') {
    router.push(`/chat/${counselorId}?type=phone`)
  } else if (type === 'chat') {
    router.push(`/chat/${counselorId}?type=chat`)
  }
}
</script>

<style>
@import '~/assets/css/user/favorite.css';
</style>