<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <!-- 메인 콘텐츠 -->
    <main class="pb-24">
      <section class="px-5 py-6">
        <!-- 문의 작성 폼 -->
        <div class="inquiry-write-container">
          <form @submit.prevent="handleSubmit">
            <!-- 문의 유형 선택 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">
                문의 유형<span class="required">*</span>
              </label>
              <select v-model="formData.inquiry_type" class="inquiry-form-select" required>
                <option value="">문의 유형을 선택하세요</option>
                <option value="PAY">결제문의</option>
                <option value="ACCOUNT">계정문의</option>
                <option value="CS">상담문의</option>
                <option value="EVENT">이벤트문의</option>
                <option value="ETC">기타문의</option>
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


            <!-- 제출 버튼 -->
            <div class="inquiry-submit-container">
              <button type="submit" class="inquiry-submit-button" :disabled="!isFormValid || isSubmitting">
                {{ isSubmitting ? '제출 중...' : '문의하기' }}
              </button>
              <button type="button" class="inquiry-cancel-button" @click="handleCancel">
                취소
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInquiryQueries } from '~/composables/api/useInquiryQueries'
import { useNotify } from '~/composables/utils/useNotify'
import type { InquiryType } from '~/types/inquiry'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const router = useRouter()
const { notifySuccess, notifyError } = useNotify()

// 문의 API
const { useCreateInquiry } = useInquiryQueries()

// 폼 데이터
const formData = ref<{
  inquiry_type: InquiryType | ''
  title: string
  content: string
}>({
  inquiry_type: '',
  title: '',
  content: ''
})

// 제출 중 상태
const isSubmitting = ref(false)

// 폼 유효성 검사
const isFormValid = computed(() => {
  return (
    formData.value.inquiry_type !== '' &&
    formData.value.title.trim() !== '' &&
    formData.value.content.trim() !== ''
  )
})

// 문의 작성 mutation
const { mutateAsync: createInquiry } = useCreateInquiry({
  onSuccess: () => {
    notifySuccess('문의가 등록되었습니다.')
    router.push('/cs')
  },
  onError: (error) => {
    notifyError(error.message || '문의 등록에 실패했습니다.')
  }
})

// 폼 제출
const handleSubmit = async () => {
  if (!isFormValid.value || isSubmitting.value) return

  try {
    isSubmitting.value = true
    await createInquiry({
      inquiry_type: formData.value.inquiry_type as InquiryType,
      title: formData.value.title.trim(),
      content: formData.value.content.trim()
    })
  } finally {
    isSubmitting.value = false
  }
}

// 취소
const handleCancel = () => {
  router.push('/cs')
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';
</style>
