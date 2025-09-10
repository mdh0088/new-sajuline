<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <!-- 헤더 컴포넌트 -->
    <AppHeader />

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-20">
      <!-- 히어로 섹션 컴포넌트 -->
      <HeroSection 
        @ai-fortune-request="handleAIFortuneRequest"
        @expert-consult-request="handleExpertConsultRequest"
      />

      <!-- 실시간 지표 컴포넌트 -->
      <LiveStats :stats="liveStats" />

      <!-- 오늘의 운세 컴포넌트 -->
      <TodayFortune 
        :fortune="todayFortune"
        @ai-analysis-request="handleAIFortuneRequest"
      />

      <!-- 빠른 상담 컴포넌트 -->
      <QuickConsult :categories="quickCategories" />

      <!-- AI vs 전문가 비교 섹션 -->
      <section class="px-5 py-6">
        <h2 class="text-xl font-bold mb-4 text-center">상담 방식 선택</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
          <!-- AI 상담 카드 -->
          <div class="relative p-6 bg-gradient-to-br from-blue-600/10 to-cyan-700/5 border border-blue-600/20 rounded-2xl overflow-hidden">
            <div class="absolute top-2 right-2 text-4xl opacity-20 pointer-events-none">🤖</div>
            
            <div class="relative z-10">
              <h3 class="text-lg font-bold mb-2 flex items-center gap-2">
                <span>🤖</span>
                AI 운세 상담
              </h3>
              
              <div class="text-sm text-white/70 mb-4 space-y-1">
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-blue-400 rounded-full"></span>
                  24시간 언제나 이용 가능
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-blue-400 rounded-full"></span>
                  빠른 결과 (3초 이내)
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-blue-400 rounded-full"></span>
                  합리적인 가격
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-blue-400 rounded-full"></span>
                  객관적인 분석
                </div>
              </div>
              
              <button
                @click="requestAIFortune"
                class="w-full py-3 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-600/30 rounded-xl font-medium text-sm transition-all duration-300"
              >
                AI 상담 시작하기
              </button>
            </div>
          </div>
          
          <!-- 전문가 상담 카드 -->
          <div class="relative p-6 bg-gradient-to-br from-amber-600/10 to-orange-700/5 border border-amber-600/20 rounded-2xl overflow-hidden">
            <div class="absolute top-2 right-2 text-4xl opacity-20 pointer-events-none">👨‍🏫</div>
            
            <div class="relative z-10">
              <h3 class="text-lg font-bold mb-2 flex items-center gap-2">
                <span>👨‍🏫</span>
                전문가 상담
              </h3>
              
              <div class="text-sm text-white/70 mb-4 space-y-1">
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-amber-400 rounded-full"></span>
                  경험 많은 전문 상담사
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-amber-400 rounded-full"></span>
                  1:1 맞춤형 상담
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-amber-400 rounded-full"></span>
                  깊이 있는 해석
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-1 h-1 bg-amber-400 rounded-full"></span>
                  실시간 질의응답
                </div>
              </div>
              
              <button
                @click="requestExpertConsult"
                class="w-full py-3 bg-amber-600/20 hover:bg-amber-600/30 border border-amber-600/30 rounded-xl font-medium text-sm transition-all duration-300"
              >
                전문가 예약하기
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA 섹션 -->
      <section class="px-5 py-8 mt-6">
        <div class="text-center p-6 bg-gradient-to-br from-purple-600/20 to-purple-700/10 border border-purple-600/30 rounded-2xl max-w-md mx-auto">
          <h2 class="text-2xl font-bold mb-2">사주라인과 함께 시작하세요</h2>
          <p class="text-sm text-white/70 mb-6">
            AI와 전문가의 하이브리드 상담으로<br />더 정확하고 깊이 있는 사주 분석을 받아보세요
          </p>
          <NuxtLink
            to="/signup"
            class="inline-block w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl font-bold text-lg shadow-lg shadow-purple-600/40 hover:shadow-purple-600/60 transition-all duration-300 active:scale-98 text-center"
          >
            회원가입하고 시작하기
          </NuxtLink>
        </div>
      </section>
    </main>

    <!-- 하단 네비게이션 컴포넌트 -->
    <AppBottomNavi />
  </div>
</template>


<script setup lang="ts">
// Vue 및 Nuxt imports
import { ref, onMounted } from 'vue'
import { useHead, useRoute, navigateTo } from 'nuxt/app'
import { useNotify } from '~/composables/utils/useNotify'

const { notifySuccess, notifyInfo } = useNotify()

// SEO 및 메타 데이터 설정
useHead({
  title: '사주라인 - AI와 전문가의 하이브리드 사주 상담',
  meta: [
    { name: 'description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:title', content: '사주라인 - AI와 전문가의 하이브리드 사주 상담' },
    { property: 'og:description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:image', content: '/images/og-image.jpg' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
})

// 반응형 상태 관리
const liveStats = ref([
  { number: '15,234', label: '누적 상담' },
  { number: '4.9', label: '평균 평점' },
  { number: '89', label: '실시간 접속자' }
])

// 라우트 처리
const route = useRoute()

// 페이지 로드 시 쿼리 파라미터 확인 - Notivue로 환영 메시지 표시
onMounted(() => {
  if (route.query.message === 'login_success') {
    notifySuccess('🎉 사주라인에 오신 것을 환영합니다!')
  } else if (route.query.message === 'social_login_success') {
    notifySuccess('🚀 간편하게 로그인되었습니다!')
  }
})


// 오늘의 운세 상태 (템플릿 구조에 맞게 content/meters 제공)
const todayFortune = ref({
  content: '오늘은 중요한 결정을 내리기에 좋은 날입니다. 자신감을 갖고 한 걸음 나아가 보세요.',
  meters: [
    { label: '종합', value: 85 },
    { label: '연애', value: 72 },
    { label: '재물', value: 91 }
  ]
})

// 빠른 상담 카테고리 (빈 화면 방지용 기본 값)
const quickCategories = ref([
  { name: '연애', path: '/categories/love', icon: '❤️' },
  { name: '직장', path: '/categories/work', icon: '💼' },
  { name: '재물', path: '/categories/money', icon: '💰' }
])

// 컴포넌트 이벤트 핸들러들
function handleAIFortuneRequest() {
  console.log('AI 운세 요청')
  notifyInfo('🤖 AI 운세를 준비 중입니다...')
}

function handleExpertConsultRequest() {
  console.log('전문가 상담 요청')
  notifyInfo('👨‍🏫 전문가 상담 예약 페이지로 이동합니다...')
}

// 기존 호환성을 위한 별칭
const requestAIFortune = handleAIFortuneRequest
const requestExpertConsult = handleExpertConsultRequest
</script>

<style scoped>
/* 컴포넌트 고유 애니메이션 */
.active\:scale-98:active {
  transform: scale(0.98);
}

.active\:scale-95:active {
  transform: scale(0.95);
}
</style>
