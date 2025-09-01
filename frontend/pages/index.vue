<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 성공 메시지 토스트 -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="transform translate-y-[-100%] opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-[-100%] opacity-0"
    >
      <div 
        v-if="successMessage" 
        class="fixed top-20 right-4 z-[100] bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ successMessage }}
          </div>
          <button 
            @click="successMessage = ''"
            class="ml-4 text-white hover:text-green-200 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 헤더 -->
    <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
      <div class="flex justify-between items-center px-5 py-4 h-[60px]">
        <div class="flex items-center">
          <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 via-purple-300 to-purple-500 bg-clip-text text-transparent">
            사주라인
          </h1>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- 알림 버튼 -->
          <button 
            class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95"
            @click="handleNotificationClick"
          >
            🔔
          </button>
          
          <!-- 메뉴 버튼 -->
          <button 
            class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95"
            @click="handleMenuClick"
          >
            ☰
          </button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-20">
      <!-- 히어로 섹션 -->
      <section class="relative px-5 py-8 overflow-hidden">
        <!-- 배경 애니메이션 -->
        <div class="absolute inset-0 bg-gradient-to-b from-purple-600/30 via-transparent to-transparent"></div>
        <div class="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
          <div class="absolute top-10 right-10 text-8xl animate-pulse">✨</div>
          <div class="absolute bottom-20 left-10 text-6xl animate-bounce">🌟</div>
        </div>
        
        <div class="relative z-10 text-center">
          <!-- 서비스 배지 -->
          <div class="inline-flex items-center gap-1.5 px-4 py-1.5 bg-purple-600/10 border border-purple-600/30 rounded-full text-xs text-purple-300 mb-4 font-medium">
            <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            AI × 전문가 하이브리드 상담
          </div>
          
          <!-- 메인 타이틀 -->
          <h1 class="text-3xl sm:text-4xl font-bold mb-3 leading-tight bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">
            당신의 운명을<br />밝히는 빛
          </h1>
          
          <!-- 서브 타이틀 -->
          <p class="text-base text-white/70 mb-6 leading-relaxed max-w-md mx-auto">
            AI 기술과 전문가의 지혜가 만나<br />새로운 사주 상담 경험을 제공합니다
          </p>
          
          <!-- CTA 버튼 -->
          <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto">
            <button
              @click="requestAIFortune"
              class="relative px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-full font-bold text-base shadow-lg shadow-purple-600/40 hover:shadow-purple-600/60 transition-all duration-300 active:scale-98 overflow-hidden group"
            >
              <span class="relative z-10">AI 운세 보기</span>
              <div class="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-active:opacity-100 transition-opacity duration-300"></div>
            </button>
            <button
              @click="requestExpertConsult"
              class="relative px-8 py-4 bg-white/10 border border-white/20 rounded-full font-bold text-base hover:bg-white/15 transition-all duration-300 active:scale-98"
            >
              전문가 상담 받기
            </button>
          </div>
        </div>
      </section>

      <!-- 실시간 지표 -->
      <section class="px-5 py-5 bg-white/2 border-y border-white/10">
        <div class="flex justify-around max-w-md mx-auto">
          <div 
            v-for="(stat, index) in liveStats" 
            :key="index"
            class="text-center"
          >
            <div class="text-2xl font-bold text-purple-300 mb-1">{{ stat.number }}</div>
            <div class="text-xs text-white/60">{{ stat.label }}</div>
          </div>
        </div>
      </section>

      <!-- 오늘의 운세 카드 -->
      <section class="px-5 py-6">
        <div class="relative p-5 bg-gradient-to-br from-purple-600/10 to-purple-700/5 border border-purple-600/20 rounded-2xl overflow-hidden max-w-md mx-auto">
          <div class="absolute top-0 right-0 text-8xl opacity-10 pointer-events-none">✨</div>
          
          <div class="relative z-10">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-bold flex items-center gap-2">
                <span>🔮</span>
                오늘의 운세
              </h2>
              <span class="text-sm text-white/60">{{ formattedToday }}</span>
            </div>
            
            <p class="text-sm text-white/80 leading-relaxed mb-4">
              {{ todayFortune.content }}
            </p>
            
            <div class="grid grid-cols-3 gap-4">
              <div 
                v-for="(meter, index) in todayFortune.meters" 
                :key="index"
                class="text-center"
              >
                <div class="text-xs text-white/60 mb-2">{{ meter.label }}</div>
                <div class="h-1 bg-white/10 rounded-full overflow-hidden mb-1">
                  <div 
                    class="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-1000"
                    :style="{ width: `${meter.value}%` }"
                  ></div>
                </div>
                <div class="text-sm font-semibold text-purple-300">{{ meter.value }}%</div>
              </div>
            </div>
            
            <!-- AI 상세 분석 버튼 -->
            <div class="mt-4 pt-4 border-t border-white/10">
              <button
                @click="requestAIFortune"
                class="w-full py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-600/30 rounded-xl font-medium text-sm transition-all duration-300"
              >
                AI 상세 분석 받기 🤖
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 빠른 상담 카테고리 -->
      <section class="px-5 py-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">빠른 상담</h2>
          <NuxtLink to="/categories" class="text-sm text-purple-300 flex items-center gap-1 hover:text-purple-200 transition-colors">
            전체보기 →
          </NuxtLink>
        </div>
        
        <div class="grid grid-cols-3 gap-3 max-w-md mx-auto">
          <NuxtLink
            v-for="(category, index) in quickCategories"
            :key="index"
            :to="category.path"
            class="relative p-5 bg-white/3 border border-white/10 rounded-2xl text-center cursor-pointer transition-all duration-300 hover:bg-white/5 active:scale-98 group overflow-hidden"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            <div class="relative z-10">
              <div class="w-14 h-14 mx-auto mb-3 bg-gradient-to-br from-purple-600/20 to-purple-700/10 rounded-2xl flex items-center justify-center text-2xl border border-purple-600/20">
                {{ category.icon }}
              </div>
              <div class="text-sm font-semibold text-white/90">{{ category.name }}</div>
            </div>
          </NuxtLink>
        </div>
      </section>

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

    <!-- 하단 네비게이션 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl border-t border-white/10 px-5 py-3">
      <div class="flex justify-around max-w-md mx-auto">
        <button 
          class="flex flex-col items-center gap-1 text-purple-400 transition-colors"
          @click="handleNavClick('home')"
        >
          <span class="text-xl">🏠</span>
          <span class="text-xs font-medium">홈</span>
        </button>
        <NuxtLink to="/fortune" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
          <span class="text-xl">🔮</span>
          <span class="text-xs font-medium">운세</span>
        </NuxtLink>
        <NuxtLink to="/chat" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
          <span class="text-xl">💬</span>
          <span class="text-xs font-medium">상담</span>
        </NuxtLink>
        <NuxtLink to="/profile" class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
          <span class="text-xl">👤</span>
          <span class="text-xs font-medium">마이페이지</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>


<script setup lang="ts">
// Vue 및 Nuxt imports
import { ref, onMounted, computed } from 'vue'
import { useHead, useRoute, navigateTo } from 'nuxt/app'

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

// 성공 메시지 처리
const route = useRoute()
const successMessage = ref('')

// 페이지 로드 시 쿼리 파라미터 확인
onMounted(() => {
  if (route.query.message === 'login_success') {
    successMessage.value = '로그인되었습니다! 환영합니다.'
  } else if (route.query.message === 'social_login_success') {
    successMessage.value = '소셜 로그인이 완료되었습니다!'
  }
  
  // 성공 메시지 자동 숨김 (3초 후)
  if (successMessage.value) {
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
})

// 오늘 날짜 포맷
const formattedToday = computed(() => {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
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

// 버튼 클릭 핸들러들
const handleNotificationClick = () => {
  console.log('알림 버튼 클릭')
}

const handleMenuClick = () => {
  console.log('메뉴 버튼 클릭')
}

const handleQuickConsult = (type: string) => {
  console.log(`빠른 상담 요청: ${type}`)
  successMessage.value = `${type} 상담을 준비 중입니다...`
  setTimeout(() => {
    successMessage.value = ''
  }, 2000)
}

const handleAIConsult = () => {
  console.log('AI 상담 시작')
  successMessage.value = 'AI 상담을 시작합니다...'
}

const handleExpertConsult = () => {
  console.log('전문가 상담 예약')
  successMessage.value = '전문가 상담 예약 페이지로 이동합니다...'
}

const handleCTAClick = () => {
  console.log('상담 시작하기 클릭')
  successMessage.value = '상담을 시작합니다!'
}

// 템플릿에서 사용하는 호출명과 연결
const requestAIFortune = () => handleAIConsult()
const requestExpertConsult = () => handleExpertConsult()

// 하단 네비게이션 클릭 처리
const handleNavClick = (tab: 'home' | 'fortune' | 'chat' | 'profile') => {
  if (tab === 'home') return
  if (tab === 'fortune') return navigateTo('/fortune')
  if (tab === 'chat') return navigateTo('/chat')
  if (tab === 'profile') return navigateTo('/profile')
}
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
