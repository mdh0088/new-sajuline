<template>
  <div class="auth-container">
    <!-- 메인 콘텐츠 -->
    <main class="auth-main">
      <div class="max-w-md mx-auto">
        <!-- 히어로 섹션 -->
        <div class="text-center mb-10">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-3xl font-bold mb-3">아이디 찾기</h2>
          <p class="text-white/70 text-base">
            본인인증을 통해<br />
            가입하신 아이디를 찾아드립니다
          </p>
        </div>

        <!-- 본인인증 안내 -->
        <div class="mb-8 p-6 bg-white/5 border border-white/10 rounded-xl">
          <div class="flex items-start gap-3 mb-4">
            <div class="text-2xl">📱</div>
            <div>
              <h3 class="text-lg font-semibold mb-2">휴대폰 본인인증</h3>
              <p class="text-white/60 text-sm leading-relaxed">
                휴대폰 본인인증을 진행하시면<br />
                해당 번호로 가입된 아이디를 확인하실 수 있습니다
              </p>
            </div>
          </div>

          <!-- 본인인증 버튼 -->
          <button
            type="button"
            class="w-full py-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-98 shadow-lg shadow-purple-500/25"
            @click="handlePhoneVerification"
          >
            휴대폰 본인인증 하기
          </button>
        </div>

        <!-- 결과 표시 영역 (본인인증 후 표시) -->
        <div v-if="foundUserId" class="mb-8 p-6 bg-green-500/10 border border-green-500/30 rounded-xl">
          <div class="text-center">
            <div class="text-3xl mb-3">✅</div>
            <h3 class="text-lg font-semibold mb-3">아이디를 찾았습니다</h3>
            <div class="p-4 bg-white/5 rounded-lg mb-4">
              <p class="text-2xl font-bold text-purple-400">{{ foundUserId }}</p>
            </div>
            <p class="text-white/60 text-sm">
              가입일: {{ foundUserDate }}
            </p>
          </div>
        </div>

        <!-- 하단 링크 -->
        <div class="space-y-4">
          <!-- 로그인 링크 -->
          <div class="text-center">
            <NuxtLink
              to="/login"
              class="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
              </svg>
              로그인하기
            </NuxtLink>
          </div>

          <!-- 비밀번호 찾기 링크 -->
          <div class="text-center pt-4 border-t border-white/10">
            <p class="text-white/60 text-sm">
              비밀번호를 잊으셨나요?
              <NuxtLink to="/user/find-password" class="text-purple-400 hover:text-purple-300 hover:underline font-medium ml-1">
                비밀번호 찾기
              </NuxtLink>
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// 인증 도메인 CSS 로드
import '~/assets/css/common/auth-common.css'

definePageMeta({
  layout: 'default'
})

// SEO 및 메타 데이터 설정
useHead({
  title: '아이디 찾기 - 사주라인',
  meta: [
    { name: 'description', content: '사주라인 아이디 찾기. 휴대폰 본인인증으로 가입하신 아이디를 찾으실 수 있습니다.' },
    { property: 'og:title', content: '아이디 찾기 - 사주라인' },
    { property: 'og:description', content: '사주라인 아이디 찾기. 휴대폰 본인인증으로 가입하신 아이디를 찾으실 수 있습니다.' },
  ],
})

// 상태 관리
const foundUserId = ref('')
const foundUserDate = ref('')

// 본인인증 처리 (추후 구현 예정)
const handlePhoneVerification = () => {
  console.log('본인인증 시작')
  // TODO: KCP 본인인증 연동
  // 성공 시 foundUserId와 foundUserDate 설정
}
</script>
