<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 로딩 상태 -->
    <div v-if="counselorStore.loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">로딩 중...</p>
      </div>
    </div>

    <!-- 인증되지 않은 상태 -->
    <div v-else-if="!counselorStore.isAuthenticated" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">로그인이 필요합니다</h2>
        <p class="text-gray-600 mb-6">상담사 마이페이지에 접근하려면 로그인해주세요.</p>
        <NuxtLink
          to="/counselor/login"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          로그인하기
        </NuxtLink>
      </div>
    </div>

    <!-- 인증된 상담사 마이페이지 -->
    <div v-else class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- 헤더 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- 프로필 이미지 -->
              <div class="flex-shrink-0">
                <img
                  v-if="counselor?.profile_image_url"
                  :src="counselor.profile_image_url"
                  :alt="counselor.name"
                  class="h-16 w-16 rounded-full object-cover"
                />
                <div v-else class="h-16 w-16 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-gray-600 font-medium text-lg">
                    {{ counselor?.name?.charAt(0) || 'C' }}
                  </span>
                </div>
              </div>
              
              <!-- 상담사 정보 -->
              <div>
                <h1 class="text-2xl font-bold text-gray-900">
                  {{ counselor?.name }} 상담사
                </h1>
                <p class="text-sm text-gray-600">
                  {{ counselor?.counselor_nickname }} ({{ counselor?.counselor_code }})
                </p>
                <div class="flex items-center space-x-4 mt-2">
                  <!-- 온라인 상태 -->
                  <span class="flex items-center">
                    <span
                      :class="[
                        'w-2 h-2 rounded-full mr-2',
                        counselor?.is_online ? 'bg-green-400' : 'bg-gray-400'
                      ]"
                    ></span>
                    {{ counselor?.is_online ? '온라인' : '오프라인' }}
                  </span>
                  
                  <!-- 상담사 상태 -->
                  <span class="text-sm text-gray-600">
                    상태: {{ counselor?.counselor_status_text }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 로그아웃 버튼 -->
            <button
              @click="handleLogout"
              :disabled="counselorStore.loading"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              로그아웃
            </button>
          </div>
        </div>
      </div>

      <!-- 상담사 통계 카드 -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <!-- 평점 -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="text-yellow-400">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">평점</dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ counselor?.rating_avg.toFixed(1) }} / 5.0
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- 리뷰 수 -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="text-blue-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">리뷰</dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ counselor?.rating_count }}개
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- 분당 가격 -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="text-green-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">분당 가격</dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ counselor?.price_per_minute.toLocaleString() }}원
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- 승인 상태 -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div :class="counselor?.is_authorized ? 'text-green-400' : 'text-red-400'">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">승인 상태</dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ counselor?.is_authorized ? '승인됨' : '승인 대기' }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 전문 분야 -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">전문 분야</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="specialty in counselor?.specialties"
              :key="specialty.specialty_id"
              class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
            >
              {{ specialty.specialty_name }}
            </span>
            <span v-if="!counselor?.specialties?.length" class="text-gray-500">
              등록된 전문 분야가 없습니다.
            </span>
          </div>
        </div>
      </div>

      <!-- 상담사 소개 -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">상담사 소개</h3>
          <p class="text-gray-700 whitespace-pre-line">
            {{ counselor?.introduction || '소개 내용이 없습니다.' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCounselorStore } from '~/stores/counselor'

// SEO 설정
useHead({
  title: '상담사 마이페이지 - 사주라인',
  meta: [
    {
      name: 'description', 
      content: '사주라인 상담사 마이페이지입니다. 프로필과 상담 현황을 확인할 수 있습니다.'
    }
  ]
})

// Pinia 스토어
const counselorStore = useCounselorStore()
const router = useRouter()

// 상담사 정보
const counselor = computed(() => counselorStore.counselor)

// 로그아웃 처리
async function handleLogout() {
  try {
    await counselorStore.logout()
    await router.push('/counselor/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// 페이지 진입 시 인증 확인
onMounted(async () => {
  if (!counselorStore.isAuthenticated) {
    // 세션 복원 시도
    const restored = await counselorStore.restoreSession()
    if (!restored) {
      // 복원 실패 시 로그인 페이지로 리다이렉트
      await router.push('/counselor/login')
    }
  }
})
</script>