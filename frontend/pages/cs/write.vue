<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 문의 작성 폼 -->
        <div class="inquiry-write-container">
          <form @submit.prevent="handleSubmit">
            <!-- 문의 유형 선택 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">
                문의 유형<span class="required">*</span>
              </label>
              <select v-model="formData.category" class="inquiry-form-select">
                <option value="">문의 유형을 선택하세요</option>
                <option value="결제/환불">결제/환불</option>
                <option value="계정 문의">계정 문의</option>
                <option value="상담 문의">상담 문의</option>
                <option value="이벤트/혜택">이벤트/혜택</option>
                <option value="기타">기타</option>
              </select>
            </div>

            <!-- 제목 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">
                제목<span class="required">*</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                class="inquiry-form-input"
                placeholder="문의 제목을 입력하세요"
                maxlength="100"
              >
              <div class="inquiry-form-help">최대 100자</div>
            </div>

            <!-- 문의 내용 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">
                문의 내용<span class="required">*</span>
              </label>
              <textarea
                v-model="formData.content"
                class="inquiry-form-textarea"
                placeholder="문의하실 내용을 자세히 작성해 주세요."
                maxlength="1000"
                rows="8"
              ></textarea>
              <div class="inquiry-form-help">최대 1000자</div>
            </div>

            <!-- 연락처 정보 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">답변 받을 연락처</label>
              <input
                v-model="formData.email"
                type="email"
                class="inquiry-form-input"
                placeholder="이메일 주소 (선택사항)"
              >
              <div class="inquiry-form-help">답변을 이메일로도 받고 싶은 경우 입력하세요</div>
            </div>

            <!-- 개인정보 수집 동의 -->
            <div class="inquiry-agreement-section">
              <label class="inquiry-agreement-item">
                <input v-model="formData.agreed" type="checkbox" class="inquiry-checkbox" required>
                <span class="inquiry-agreement-text">
                  개인정보 수집 및 이용에 동의합니다.
                </span>
              </label>
              <div class="inquiry-form-help">문의 답변을 위해 개인정보가 수집됩니다.</div>
            </div>

            <!-- 제출 버튼 -->
            <div class="inquiry-submit-container">
              <button type="submit" class="inquiry-submit-button" :disabled="!isFormValid">
                문의하기
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

definePageMeta({
  layout: 'default'
  // TODO: 실제 구현 시 middleware: 'auth' 추가 (로그인 필수)
})

// 라우트에서 카테고리 가져오기
const route = useRoute()
const categoryFromQuery = route.query.category as string | undefined

// 폼 데이터
const formData = ref({
  category: '',
  title: '',
  content: '',
  email: '',
  agreed: false
})

// 쿼리에서 카테고리가 있으면 자동 선택
onMounted(() => {
  if (categoryFromQuery) {
    formData.value.category = decodeURIComponent(categoryFromQuery)
  }
})

// 폼 유효성 검사
const isFormValid = computed(() => {
  return (
    formData.value.category !== '' &&
    formData.value.title.trim() !== '' &&
    formData.value.content.trim() !== '' &&
    formData.value.agreed
  )
})

// 폼 제출
const handleSubmit = () => {
  if (!isFormValid.value) return

  console.log('문의 제출:', formData.value)
  // TODO: API 연동
  alert('문의가 제출되었습니다.')
  navigateTo('/cs')
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';
</style>
