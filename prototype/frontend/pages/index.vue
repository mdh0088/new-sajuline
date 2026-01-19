<script setup lang="ts">
// SEO 및 메타 데이터 설정 (MVP: AI 관련 설명 제거)
useHead({
  title: '사주라인 - 당신의 운명을 밝히는 빛',
  meta: [
    { name: 'description', content: '전통 사주 상담 서비스. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:title', content: '사주라인 - 당신의 운명을 밝히는 빛' },
    { property: 'og:description', content: '전통 사주 상담 서비스. 언제 어디서나 신뢰할 수 있는 사주 상담을 받아보세요.' },
    { property: 'og:image', content: '/images/og-image.jpg' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
})

// 반응형 상태 관리
const liveStats = ref([
  { number: '12,847', label: '누적 상담' },
  { number: '4.8', label: '평균 평점' },
  { number: '156', label: '전문 상담사' }
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
  } else if (route.query.message === 'social_signup_success') {
    successMessage.value = '소셜 회원가입이 완료되었습니다! 환영합니다.'
  }
  
  // 5초 후 메시지 자동 숨김
  if (successMessage.value) {
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  }
})

const quickCategories = ref([
  { name: '연애운', icon: '💕', path: '/fortune/love' },
  { name: '금전운', icon: '💰', path: '/fortune/money' },
  { name: '사업운', icon: '📈', path: '/fortune/business' },
  { name: '건강운', icon: '🏥', path: '/fortune/health' },
  { name: '학업운', icon: '📚', path: '/fortune/study' },
  { name: '가족운', icon: '👨‍👩‍👧‍👦', path: '/fortune/family' }
])

const todayFortune = ref({
  content: "오늘은 새로운 기회가 찾아올 수 있는 날입니다. 특히 오후 시간대에 중요한 소식이나 만남이 있을 수 있으니 준비하세요.",
  meters: [
    { label: '애정운', value: 85 },
    { label: '금전운', value: 72 },
    { label: '건강운', value: 90 }
  ]
})

// 메서드
// MVP: AI 운세와 전문가 상담 기능 제거
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 성공 메시지 토스트 -->
    <div v-if="successMessage" class="fixed top-20 right-4 z-[100] bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg animate-fade-in">
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
    <!-- 헤더 -->
    <header class="fixed top-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl z-50 border-b border-white/10">
      <div class="flex justify-between items-center px-5 py-4 h-15">
        <div class="flex items-center">
          <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 via-purple-300 to-purple-500 bg-clip-text text-transparent">
            사주라인
          </h1>
        </div>
        
        <div class="flex items-center gap-2">
          
          <!-- 알림 버튼 -->
          <button class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95">
            🔔
          </button>
          
          <!-- 메뉴 버튼 -->
          <button class="w-9 h-9 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl flex items-center justify-center text-lg transition-all duration-300 active:scale-95">
            ☰
          </button>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="pt-15 pb-20">
      <!-- 히어로 섹션 -->
      <section class="relative px-5 py-8 overflow-hidden">
        <!-- 배경 애니메이션 -->
        <div class="absolute inset-0 bg-gradient-to-b from-purple-600/30 via-transparent to-transparent"></div>
        <div class="absolute top-0 left-0 w-full h-full opacity-5">
          <div class="absolute top-10 right-10 text-8xl animate-pulse">✨</div>
          <div class="absolute bottom-20 left-10 text-6xl animate-bounce">🌟</div>
        </div>
        
        <div class="relative z-10 text-center">
          <!-- MVP: 서비스 배지 단순화 -->
          <div class="inline-flex items-center gap-1.5 px-4 py-1.5 bg-purple-600/10 border border-purple-600/30 rounded-full text-xs text-purple-300 mb-4 font-medium">
            <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            사주라인 서비스 LIVE
          </div>
          
          <!-- 메인 타이틀 -->
          <h1 class="text-3xl sm:text-4xl font-bold mb-3 leading-tight bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">
            당신의 운명을<br />밝히는 빛
          </h1>
          
          <!-- 서브 타이틀 -->
          <p class="text-base text-white/70 mb-6 leading-relaxed">
            전통과 현대가 만나는<br />새로운 사주 서비스
          </p>
          
          <!-- MVP: 기본 CTA 버튼 -->
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <NuxtLink
              to="/login"
              class="relative px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-full font-bold text-base shadow-lg shadow-purple-600/40 hover:shadow-purple-600/60 transition-all duration-300 active:scale-98 overflow-hidden group"
            >
              <span class="relative z-10">지금 시작하기</span>
              <div class="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-active:opacity-100 transition-opacity duration-300"></div>
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- 실시간 지표 -->
      <section class="px-5 py-5 bg-white/2 border-y border-white/10">
        <div class="flex justify-around">
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
        <div class="relative p-5 bg-gradient-to-br from-purple-600/10 to-purple-700/5 border border-purple-600/20 rounded-2xl overflow-hidden">
          <div class="absolute top-0 right-0 text-8xl opacity-10">✨</div>
          
          <div class="relative z-10">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-bold flex items-center gap-2">
                <span>🔮</span>
                오늘의 운세
              </h2>
              <span class="text-sm text-white/60">{{ new Date().toLocaleDateString('ko-KR') }}</span>
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
          </div>
        </div>
      </section>

      <!-- 빠른 상담 카테고리 -->
      <section class="px-5 py-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">빠른 상담</h2>
          <NuxtLink to="/categories" class="text-sm text-purple-300 flex items-center gap-1">
            전체보기 →
          </NuxtLink>
        </div>
        
        <div class="grid grid-cols-3 gap-3">
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

      <!-- MVP: 상담사 추천 섹션 제거 -->

      <!-- MVP: CTA 섹션 단순화 -->
      <section class="px-5 py-8 mt-6">
        <div class="text-center p-6 bg-gradient-to-br from-purple-600/20 to-purple-700/10 border border-purple-600/30 rounded-2xl">
          <h2 class="text-2xl font-bold mb-2">사주라인과 함께 시작하세요</h2>
          <p class="text-sm text-white/70 mb-6">
            전통 사주 상담을<br />간편하게 받아보실 수 있습니다
          </p>
          <NuxtLink
            to="/login"
            class="inline-block w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl font-bold text-lg shadow-lg shadow-purple-600/40 hover:shadow-purple-600/60 transition-all duration-300 active:scale-98 text-center"
          >
            지금 시작하기
          </NuxtLink>
        </div>
      </section>
    </main>

    <!-- MVP: 하단 네비게이션 단순화 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-slate-950/95 backdrop-blur-xl border-t border-white/10 px-5 py-3">
      <div class="flex justify-around">
        <button class="flex flex-col items-center gap-1 text-purple-400">
          <span class="text-xl">🏠</span>
          <span class="text-xs font-medium">홈</span>
        </button>
        <button class="flex flex-col items-center gap-1 text-white/60 hover:text-white/80 transition-colors">
          <span class="text-xl">👤</span>
          <span class="text-xs font-medium">마이페이지</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.active\:scale-98:active {
  transform: scale(0.98);
}

.active\:scale-99:active {
  transform: scale(0.99);
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 