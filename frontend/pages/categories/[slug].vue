<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 헤더 -->
    <header class="category-header">
      <button @click="goBack" class="back-button">←</button>
      <h1 class="header-title">{{ categoryInfo.label }}</h1>
      <div class="header-spacer"></div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 카테고리 설명 -->
      <div class="category-description" v-if="categoryInfo.description">
        <p class="description-text">{{ categoryInfo.description }}</p>
      </div>

      <!-- 검색 결과 정보 -->
      <div class="search-info">
        <span class="result-count">총 <strong>{{ totalCount }}명</strong>의 상담사</span>
      </div>

      <!-- 상담사 리스트 -->
      <div class="counselor-grid-container">
        <div
          class="counselor-card-compact"
          v-for="counselor in filteredCounselors"
          :key="counselor.id"
          @click="goToCounselorDetail(counselor.counselorCode)"
        >
          <div class="counselor-avatar-small" :class="{ online: counselor.isOnline }">
            <img :src="counselor.image" :alt="counselor.name" v-if="counselor.image">
            <span v-else>{{ counselor.avatar }}</span>
          </div>
          <div class="counselor-info-compact">
            <div class="counselor-main-info">
              <div class="counselor-left-info">
                <div class="counselor-name-row">
                  <span class="counselor-name-small">{{ counselor.name }}</span>
                  <span class="counselor-code">{{ counselor.counselorCode }}</span>
                </div>
                <div class="counselor-specialty-small">{{ counselor.specialty }}</div>
                <div class="counselor-tags-small">
                  <span
                    class="tag-small"
                    v-for="tag in counselor.tags"
                    :key="tag"
                  >
                    {{ tag }}
                  </span>
                </div>
                <div class="counselor-desc-small">
                  {{ counselor.description }}
                </div>
              </div>
              <div class="counselor-right-info">
                <div class="counselor-price-small">{{ counselor.price }}P/30초</div>
                <div class="counselor-rating-small">
                  <span class="rating-stars-small">⭐⭐⭐⭐⭐</span>
                  <span class="rating-score">{{ counselor.rating }}</span>
                </div>
                <div class="counselor-experience">{{ counselor.experience }} · 리뷰 {{ counselor.reviewCount }}</div>
                <button class="consult-button" @click.stop="openConsultModal(counselor)">
                  상담하기
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div class="empty-state" v-if="filteredCounselors.length === 0 && !isLoading">
        <div class="empty-icon">😔</div>
        <div class="empty-title">{{ categoryInfo.label }} 상담사가 없습니다</div>
        <div class="empty-desc">다른 카테고리를 선택해보세요</div>
      </div>

      <!-- 로딩 상태 -->
      <div class="loading-state" v-if="isLoading">
        <div class="loading-spinner"></div>
        <div class="empty-title">불러오는 중...</div>
      </div>
    </main>

    <!-- 전화 상담 모달 (로그인 유저용) -->
    <PhoneConsultModal
      v-if="isUser && modalCounselorData"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      :user-points="userPoints"
      @close="closePhoneModal"
      @start-point-consult="handlePointConsult"
      @start060-consult="handle060Consult"
      @go-to-charge="goToCharge"
    />

    <!-- 전화 상담 모달 (비로그인 유저용) -->
    <GuestPhoneConsultModal
      v-if="!isUser && modalCounselorData"
      :counselor="modalCounselorData"
      :is-visible="showPhoneModal"
      @close="closePhoneModal"
      @start060-consult="handle060Consult"
      @go-to-register-login="goToRegisterLogin"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '~/composables/auth/useAuth'
import { useUserPoints } from '~/composables/user/useUserPoints'

definePageMeta({
  requiresAuth: false
})

const router = useRouter()
const route = useRoute()
const { isUser } = useAuth()
const { points: storePoints } = useUserPoints()

// 상태 관리
const isLoading = ref(false)
const slug = computed(() => String(route.params.slug || ''))

// 전화 상담 모달 관련
const showPhoneModal = ref(false)
const selectedCounselor = ref<any>(null)
const userPoints = computed(() => storePoints.value)

// 카테고리 정보 매핑
const categoryMap: Record<string, { label: string; icon: string; description: string; value: string }> = {
  'tarot': { label: '타로', icon: '🔮', description: '타로 카드를 통해 당신의 미래와 운명을 읽어드립니다.', value: 'tarot' },
  'saju': { label: '사주', icon: '📜', description: '정통 사주명리학으로 인생의 큰 그림을 그려드립니다.', value: 'saju' },
  'divine': { label: '신점', icon: '✨', description: '신통력과 영감으로 정확한 신점을 봐드립니다.', value: 'divine' },
  'love': { label: '연애운', icon: '💕', description: '연애와 인연에 대한 깊은 통찰력을 제공합니다.', value: 'love' },
  'money': { label: '재물운', icon: '💰', description: '재물운과 사업운을 전문으로 상담해드립니다.', value: 'money' },
  'career': { label: '직장운', icon: '💼', description: '직장과 취업, 커리어에 대한 조언을 드립니다.', value: 'work' }
}

const categoryInfo = computed(() => {
  return categoryMap[slug.value] || { label: '카테고리', icon: '🌟', description: '', value: 'all' }
})

// 목업 상담사 데이터
const counselors = ref([
  {
    id: 1,
    counselorCode: '001',
    name: '명월 선생님',
    avatar: '🌙',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '타로 마스터',
    experience: '20년 경력',
    category: 'tarot',
    tags: ['🔮 타로', '💕 연애', '🔄 재회'],
    description: '모든 인연에는 의미가 있습니다. 20년간 수만건의 상담을 통해 쌓은 통찰력으로 당신의 마음을 읽어드립니다.',
    rating: 4.9,
    reviewCount: 3456,
    price: 3900
  },
  {
    id: 2,
    counselorCode: '002',
    name: '천기누설 선생님',
    avatar: '🔥',
    image: '/images/cs_2.png',
    isOnline: true,
    specialty: '사주/신점 전문',
    experience: '30년 경력',
    category: 'saju',
    tags: ['📅 사주', '✨ 신점', '💼 취업'],
    description: '정통 사주명리학과 신점을 통해 인생의 큰 그림을 그려드립니다.',
    rating: 4.8,
    reviewCount: 2892,
    price: 4500
  },
  {
    id: 3,
    counselorCode: '003',
    name: '별빛 선생님',
    avatar: '💫',
    image: '/images/cs_2.png',
    isOnline: false,
    specialty: '신통력',
    experience: '15년 경력',
    category: 'money',
    tags: ['🌟 신통력', '💰 재물', '🍀 행운'],
    description: '타고난 영감과 신통력으로 막힌 운을 뚫어드립니다.',
    rating: 5.0,
    reviewCount: 1234,
    price: 5900
  },
  {
    id: 4,
    counselorCode: '004',
    name: '운명사랑 선생님',
    avatar: '💖',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '연애 전문',
    experience: '18년 경력',
    category: 'love',
    tags: ['💔 재회', '💕 연애', '💑 궁합'],
    description: '끊어진 인연도 다시 이어드립니다. 사랑의 길을 함께 찾아갑니다.',
    rating: 4.7,
    reviewCount: 2156,
    price: 3500
  },
  {
    id: 5,
    counselorCode: '005',
    name: '건강행복 선생님',
    avatar: '🌿',
    image: '/images/cs_2.png',
    isOnline: true,
    specialty: '가족/건강',
    experience: '25년 경력',
    category: 'work',
    tags: ['👨‍👩‍👧‍👦 가족', '🏥 건강', '🍀 행운'],
    description: '가족의 평안과 건강을 기원하며 따뜻한 상담을 제공합니다.',
    rating: 4.9,
    reviewCount: 1897,
    price: 4200
  },
  {
    id: 6,
    counselorCode: '006',
    name: '신비 선생님',
    avatar: '✨',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '신점 전문',
    experience: '22년 경력',
    category: 'divine',
    tags: ['✨ 신점', '🔮 영감', '🌟 직감'],
    description: '타고난 직감력과 영감으로 정확한 신점을 봐드립니다.',
    rating: 4.8,
    reviewCount: 2341,
    price: 4800
  },
  {
    id: 7,
    counselorCode: '007',
    name: '미래 선생님',
    avatar: '🔮',
    image: '/images/cs_2.png',
    isOnline: true,
    specialty: '타로/사주',
    experience: '25년 경력',
    category: 'tarot',
    tags: ['🔮 타로', '📅 사주', '🔮 미래'],
    description: '타로와 사주를 결합한 독특한 방식으로 미래를 읽어드립니다.',
    rating: 4.9,
    reviewCount: 3234,
    price: 3800
  },
  {
    id: 8,
    counselorCode: '008',
    name: '금성 선생님',
    avatar: '🌸',
    image: '/images/cs_1.png',
    isOnline: true,
    specialty: '연애운 전문',
    experience: '12년 경력',
    category: 'love',
    tags: ['💕 연애', '💘 인연', '💍 결혼'],
    description: '연애와 인연에 대한 깊은 통찰력을 바탕으로 진정한 사랑을 찾아드립니다.',
    rating: 4.7,
    reviewCount: 2156,
    price: 3200
  }
])

// 필터링된 상담사
const filteredCounselors = computed(() => {
  const categoryValue = categoryInfo.value.value
  if (!categoryValue || categoryValue === 'all') {
    return counselors.value
  }
  return counselors.value.filter(c => c.category === categoryValue)
})

const totalCount = computed(() => filteredCounselors.value.length)

// 메서드
const goBack = () => {
  router.back()
}

const goToCounselorDetail = (counselorCode: string) => {
  navigateTo(`/counselor/${counselorCode}`)
}

// 전화 상담 모달 관련 메서드
const openConsultModal = (counselor: any) => {
  selectedCounselor.value = counselor
  showPhoneModal.value = true
}

const closePhoneModal = () => {
  showPhoneModal.value = false
  selectedCounselor.value = null
}

const modalCounselorData = computed(() => {
  if (!selectedCounselor.value) return null
  return {
    code: selectedCounselor.value.counselorCode,
    nickname: selectedCounselor.value.name,
    profile_image_url: selectedCounselor.value.image,
    specialties: [selectedCounselor.value.specialty],
    afterAmount: selectedCounselor.value.price ?? null,
    beforeAmount: null
  }
})

const handlePointConsult = (counselorId: string) => {
  console.log('포인트 상담 시작:', counselorId)
  // TODO: 포인트 상담 시작 API 호출
}

const handle060Consult = (counselorId: string) => {
  console.log('060 상담 시작:', counselorId)
  // TODO: 060 상담 연결 로직
}

const goToCharge = () => {
  navigateTo('/point')
}

const goToRegisterLogin = () => {
  navigateTo('/login')
}

// SEO 설정
useHead({
  title: `${categoryInfo.value.label} 상담사 - 사주라인`,
  meta: [
    { name: 'description', content: `사주라인 ${categoryInfo.value.label} 전문 상담사. ${categoryInfo.value.description}` }
  ]
})
</script>

<style scoped>
/* 헤더 스타일 */
.category-header {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(2, 6, 23, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-button {
  font-size: 24px;
  color: #fff;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  transition: transform 0.2s ease;
}

.back-button:hover {
  transform: translateX(-4px);
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.header-spacer {
  width: 32px;
}

/* 카테고리 설명 */
.category-description {
  padding: 20px;
  margin-bottom: 8px;
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(124, 58, 237, 0.05));
  border: 1px solid rgba(147, 51, 234, 0.2);
  border-radius: 16px;
  margin: 20px 20px 0;
}

.description-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  text-align: center;
}

/* 메인 콘텐츠 */
.main-content {
  padding: 20px;
}

.search-info {
  margin-bottom: 20px;
  padding: 0 4px;
}

.result-count {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
}

.result-count strong {
  color: #B794F6;
  font-weight: 700;
}

/* 상담사 카드 그리드 */
.counselor-grid-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.counselor-card-compact {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.counselor-card-compact:hover {
  background: rgba(147, 51, 234, 0.08);
  border-color: rgba(147, 51, 234, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(147, 51, 234, 0.2);
}

.counselor-avatar-small {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.2), rgba(124, 58, 237, 0.1));
  border: 2px solid rgba(147, 51, 234, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  flex-shrink: 0;
  overflow: hidden;
}

.counselor-avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.counselor-avatar-small.online::after {
  content: '';
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  background: #10B981;
  border: 2px solid #020617;
  border-radius: 50%;
}

.counselor-info-compact {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.counselor-main-info {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.counselor-left-info {
  flex: 1;
  min-width: 0;
}

.counselor-right-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.counselor-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.counselor-name-small {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.counselor-code {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  background: linear-gradient(135deg, #9264e6 0%, #8244ff 50%, #6b30f2 100%);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.5px;
}

.counselor-specialty-small {
  font-size: 13px;
  color: #B794F6;
  margin-bottom: 8px;
}

.counselor-tags-small {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-small {
  padding: 3px 8px;
  background: rgba(147, 51, 234, 0.1);
  border: 1px solid rgba(147, 51, 234, 0.2);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  color: #B794F6;
  line-height: 1.2;
}

.counselor-price-small {
  font-size: 14px;
  font-weight: 700;
  color: #B794F6;
  line-height: 1.3;
}

.counselor-rating-small {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.rating-stars-small {
  font-size: 10px;
  color: #FBBF24;
}

.rating-score {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.counselor-experience {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.counselor-desc-small {
  margin-top: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.consult-button {
  width: 80px;
  height: 32px;
  padding: 0;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #9333EA 0%, #7C3AED 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.consult-button:hover {
  background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
  box-shadow: 0 4px 12px rgba(147, 51, 234, 0.4);
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* 로딩 상태 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 24px;
  border: 4px solid rgba(147, 51, 234, 0.2);
  border-top-color: #9333EA;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 모바일 최적화 */
@media (max-width: 480px) {
  .counselor-card-compact {
    padding: 16px;
    gap: 12px;
  }

  .counselor-avatar-small {
    width: 80px;
    height: 85px;
    font-size: 24px;
  }
}
</style>
