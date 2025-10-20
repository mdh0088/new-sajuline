<template>
  <div class="apply-container">
    <!-- 헤더 -->
    <div class="apply-header">
      <div class="apply-header-top">
        <button class="apply-back-button" @click="$router.back()">←</button>
        <h1 class="apply-header-title">상담사 신청</h1>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="apply-main-content">
      <form @submit.prevent="submitForm">
        <!-- 분야 선택 -->
        <section class="apply-form-section">
          <div class="apply-form-group">
            <label class="apply-form-label">분야 선택 <span class="apply-form-required">*</span></label>
            <div class="apply-category-grid">
              <label class="apply-category-option">
                <input type="radio" v-model="form.category" value="타로" name="category">
                <span class="apply-category-label">
                  <span class="apply-category-icon">🔮</span>
                  <span class="apply-category-name">타로</span>
                </span>
              </label>
              <label class="apply-category-option">
                <input type="radio" v-model="form.category" value="신점" name="category">
                <span class="apply-category-label">
                  <span class="apply-category-icon">🧿</span>
                  <span class="apply-category-name">신점</span>
                </span>
              </label>
              <label class="apply-category-option">
                <input type="radio" v-model="form.category" value="사주" name="category">
                <span class="apply-category-label">
                  <span class="apply-category-icon">📜</span>
                  <span class="apply-category-name">사주</span>
                </span>
              </label>
            </div>
          </div>
        </section>

        <!-- 신청자 정보 -->
        <section class="apply-form-section">
          <div class="apply-form-group apply-row">
            <div>
              <label class="apply-form-label">닉네임<span class="apply-form-required">*</span></label>
              <input type="text" v-model="form.nickname" class="apply-form-input" placeholder="프로필에 표시될 닉네임" maxlength="20" required>
              <div class="apply-form-help">최대 20자</div>
            </div>
            <div>
              <label class="apply-form-label">이름<span class="apply-form-required">*</span></label>
              <input type="text" v-model="form.name" class="apply-form-input" placeholder="홍길동" required>
            </div>
          </div>

          <div class="apply-form-group apply-row">
            <div>
              <label class="apply-form-label">휴대폰 번호<span class="apply-form-required">*</span></label>
              <input type="tel" v-model="form.phone" class="apply-form-input" placeholder="010-0000-0000" required>
            </div>
            <div>
              <label class="apply-form-label">이메일 주소<span class="apply-form-required">*</span></label>
              <input type="email" v-model="form.email" class="apply-form-input" placeholder="you@example.com" required>
            </div>
          </div>

          <div class="apply-form-group">
            <label class="apply-form-label">나를 소개하는 짧은 한마디(1줄)<span class="apply-form-required">*</span></label>
            <input type="text" v-model="form.tagline" class="apply-form-input" placeholder="예: 따뜻한 통찰로 방향을 제시합니다." maxlength="60" required>
            <div class="apply-counter">{{ form.tagline.length }} / 60</div>
          </div>

          <div class="apply-form-group">
            <label class="apply-form-label">인사말(긴 소개)<span class="apply-form-required">*</span></label>
            <textarea v-model="form.greeting" class="apply-form-input" placeholder="상담 스타일, 철학, 가능 영역 등을 소개해 주세요." maxlength="1000" required></textarea>
            <div class="apply-counter">{{ form.greeting.length }} / 1000</div>
          </div>

          <div class="apply-form-group">
            <label class="apply-form-label">경력사항</label>
            <textarea v-model="form.career" class="apply-form-input" placeholder="예: 타로 상담 5년 / 오프라인 점사 3년 / 관련 자격 등" maxlength="1000"></textarea>
            <div class="apply-counter">{{ form.career.length }} / 1000</div>
          </div>

          <div class="apply-form-group">
            <label class="apply-form-label">주요사항 키워드</label>
            <input type="text" v-model="form.keywords" class="apply-form-input" placeholder="예: 연애, 재회, 커리어, 금전, 시험, 이직">
            <p class="apply-form-help">쉼표(,)로 구분해 입력하세요.</p>
          </div>

          <!-- 동의 체크 -->
          <div class="apply-form-group">
            <label class="apply-form-label">약관 동의<span class="apply-form-required">*</span></label>
            <div class="apply-agreements">
              <!-- 전체 동의 -->
              <label class="apply-agree-row apply-agree-all">
                <input type="checkbox" v-model="agreeAll" @change="toggleAllAgreements">
                <span class="apply-label">모든 약관에 동의합니다.</span>
              </label>

              <!-- 이용약관(필수) -->
              <label class="apply-agree-row">
                <input type="checkbox" v-model="agreements.terms" required>
                <span class="apply-label">이용약관(필수)</span>
                <button type="button" class="apply-open-btn" @click="openModal('terms')">
                  ▾
                </button>
              </label>

              <!-- 개인정보 수집 및 이용(필수) -->
              <label class="apply-agree-row">
                <input type="checkbox" v-model="agreements.privacy" required>
                <span class="apply-label">개인정보 수집 및 이용(필수)</span>
                <button type="button" class="apply-open-btn" @click="openModal('privacy')">
                  ▾
                </button>
              </label>
            </div>
            <p class="apply-form-help">필수 항목 2가지 모두 체크해야 제출할 수 있습니다.</p>
          </div>
        </section>

        <!-- 사진 첨부 -->
        <section class="apply-form-section">
          <div class="apply-form-group">
            <label class="apply-form-label">사진첨부 (상담에 사용하실 사진)<span class="apply-form-required">*</span></label>
            <div class="apply-file-upload" @click="triggerFileInput">
              <span class="apply-file-icon">📎</span>
              <span class="apply-file-text">{{ fileText }}</span>
              <button type="button" class="apply-file-button">파일 선택</button>
            </div>
            <input ref="fileInput" type="file" accept="image/*" multiple hidden @change="handleFileSelect">
            <div class="apply-thumbs" v-if="selectedImages.length">
              <img v-for="(img, index) in selectedImages" :key="index" :src="img" alt="첨부 이미지">
            </div>
            <p class="apply-form-help">*머리 위, 양 어깨가 잘리지 않은 정면사진 · 상반신 전체 노출 권장 · 1~3장 등록 · 각 5MB 이하</p>
          </div>
        </section>
      </form>
    </main>

    <!-- 제출 버튼 -->
    <section class="apply-submit-section">
      <button
        type="button"
        @click="submitForm"
        class="apply-submit-button"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? '신청 중...' : '신청하기' }}
      </button>
    </section>

    <!-- 이용약관 모달 -->
    <div v-if="modals.terms" class="apply-modal-backdrop" @click="closeModal('terms')">
      <div class="apply-modal" @click.stop>
        <div class="apply-modal-header">
          <div class="apply-modal-title">이용약관</div>
          <button class="apply-modal-close" @click="closeModal('terms')">✕</button>
        </div>
        <div class="apply-modal-body">
          <!-- 이용약관 내용 -->
          <pre>제 1 장 총칙

제 1 조 (목적)
이 약관은 주식회사 피플라인(이하 "회사"라고 함)가 인터넷 사이트 (https://www.sajuline.com/, 이하 "홈페이지"라고 합니다.)와 모바일 사이트(https://m.www.sajuline.com/) 및 스마트폰 등 이동통신기기를 통해 제공되는 어플리케이션 "사주라인" 모바일 어플리케이션(이하 "모바일 서비스"라고 합니다.)을 통하여 제공하는 서비스 및 제반 서비스의 이용과 관련하여 회사와 이용고객 간의 권리와 의무, 책임사항 및 이용고객의 서비스 이용절차에 관한 사항을 규정함을 목적으로 합니다.

제 2 조 (약관의 명시, 효력 및 변경)
1. 회사는 이 약관을 서비스를 이용하고자 하는 자와 이용고객이 알 수 있도록 서비스가 제공되는 홈페이지와 모바일 서비스에 게시하며, 회원가입을 위해 회원정보를 제출하거나 회사의 고지와 안내 멘트를 듣고 회사의 서비스를 이용하는 자는 이 약관에 동의하는 것을 의미합니다.
2. 이 약관에 동의하는 것은 정기적으로 홈페이지와 모바일 서비스에 방문하여 약관의 변경 사항을 확인하는 것에 동의하는 것을 의미합니다.
3. 회사는 필요한 경우 이 약관을 변경할 수 있습니다. 회사는 약관이 변경되는 경우에 변경된 약관의 내용과 시행일을 정하여, 그 시행일로부터 7일 전 홈페이지와 모바일 서비스에 게시합니다.</pre>
        </div>
      </div>
    </div>

    <!-- 개인정보처리방침 모달 -->
    <div v-if="modals.privacy" class="apply-modal-backdrop" @click="closeModal('privacy')">
      <div class="apply-modal" @click.stop>
        <div class="apply-modal-header">
          <div class="apply-modal-title">개인정보처리방침</div>
          <button class="apply-modal-close" @click="closeModal('privacy')">✕</button>
        </div>
        <div class="apply-modal-body">
          <!-- 개인정보처리방침 내용 -->
          <pre>피플라인(이하 "회사"는) 고객님의 개인정보를 중요시하며, "정보통신망 이용촉진 및 정보보호"에 관한 법률을 준수하고 있습니다.

회사는 개인정보처리방침을 통하여 고객님께서 제공하시는 개인정보가 어떠한 용도와 방식으로 이용되고 있으며, 개인정보 보호를 위해 어떠한 조치가 취해지고 있는지 알려드립니다.

1. 개인정보의 수집 항목 및 수집 방법
(1) 회사는 회원가입, 원활한 고객상담, 각종 서비스 제공을 위해 최초 회원가입 시 다음과 같은 개인정보를 수집합니다.
수집 항목: 아이디, 비밀번호, 닉네임, 휴대폰번호, 이메일

2. 개인정보의 수집목적 및 이용목적
회사는 수집한 개인정보를 다음의 목적을 위해 활용합니다.</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCounselorApplicationQueries } from '~/composables/api/useCounselorApplicationQueries'
import { useNotify } from '~/composables/utils/useNotify'

const router = useRouter()
const { useCreateApplication } = useCounselorApplicationQueries()
const { notifySuccess, notifyError } = useNotify()

// API 뮤테이션
const { mutate: createApplication, isPending: isSubmitting } = useCreateApplication({
  onSuccess: () => {
    notifySuccess('상담사 신청이 완료되었습니다. 검토 후 연락드리겠습니다.')
    router.push('/')
  },
  onError: (error: any) => {
    const errorMessage = error?.statusMessage || error?.message || error?.data?.message || '상담사 신청 중 오류가 발생했습니다.'
    notifyError(errorMessage)
  }
})

// Form data
const form = ref({
  category: '',
  nickname: '',
  name: '',
  phone: '',
  email: '',
  tagline: '',
  greeting: '',
  career: '',
  keywords: ''
})

// Agreements
const agreements = ref({
  terms: false,
  privacy: false
})

// File handling
const fileInput = ref<HTMLInputElement>()
const selectedFiles = ref<File[]>([])
const selectedImages = ref<string[]>([])

// Modals
const modals = ref({
  terms: false,
  privacy: false
})

// Computed
const agreeAll = computed({
  get: () => agreements.value.terms && agreements.value.privacy,
  set: (value: boolean) => {
    agreements.value.terms = value
    agreements.value.privacy = value
  }
})

const fileText = computed(() => {
  if (selectedFiles.value.length === 0) return '사진 1~3장을 첨부하려면 클릭하세요'
  return `${selectedFiles.value.length}개 파일 선택됨`
})

// Methods
const toggleAllAgreements = () => {
  const allChecked = agreeAll.value
  agreements.value.terms = allChecked
  agreements.value.privacy = allChecked
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])

  if (files.length === 0) {
    selectedFiles.value = []
    selectedImages.value = []
    return
  }

  if (files.length > 3) {
    notifyError('사진은 최대 3장까지 첨부 가능합니다.')
    target.value = ''
    return
  }

  // Validate files
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      notifyError('이미지 파일만 첨부 가능합니다.')
      target.value = ''
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      notifyError('각 파일 크기는 5MB를 초과할 수 없습니다.')
      target.value = ''
      return
    }
  }

  selectedFiles.value = files

  // Create image previews
  selectedImages.value = []
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      selectedImages.value.push(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  })
}

const openModal = (type: 'terms' | 'privacy') => {
  modals.value[type] = true
  document.body.style.overflow = 'hidden'
}

const closeModal = (type: 'terms' | 'privacy') => {
  modals.value[type] = false
  document.body.style.overflow = 'auto'
}

const validateForm = () => {
  if (!form.value.category || form.value.category.trim() === '') {
    notifyError('분야를 선택해주세요.')
    return false
  }

  if (!form.value.nickname.trim()) {
    notifyError('닉네임을 입력해주세요.')
    return false
  }

  if (!form.value.name.trim()) {
    notifyError('이름을 입력해주세요.')
    return false
  }

  if (!form.value.phone.trim()) {
    notifyError('휴대폰 번호를 입력해주세요.')
    return false
  }

  const phoneRegex = /^01[0-9]{8,9}$/
  const phoneNumber = form.value.phone.replace(/-/g, '')
  if (!phoneRegex.test(phoneNumber)) {
    notifyError('휴대폰 번호 형식을 확인해주세요.')
    return false
  }

  if (!form.value.email.trim()) {
    notifyError('이메일 주소를 입력해주세요.')
    return false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email.trim())) {
    notifyError('이메일 형식을 확인해주세요.')
    return false
  }

  if (!form.value.tagline.trim()) {
    notifyError('짧은 한마디를 입력해주세요.')
    return false
  }

  if (!form.value.greeting.trim()) {
    notifyError('인사말(긴 소개)을 입력해주세요.')
    return false
  }

  if (!agreements.value.terms || !agreements.value.privacy) {
    notifyError('이용약관과 개인정보 수집 및 이용에 모두 동의해 주세요.')
    return false
  }

  if (selectedFiles.value.length < 1 || selectedFiles.value.length > 3) {
    notifyError('사진을 1~3장 첨부해주세요.')
    return false
  }

  return true
}

const submitForm = () => {
  if (!validateForm()) return
  if (isSubmitting.value) return

  // specialty_types 매핑 (category -> 대문자)
  const specialtyTypesMap: Record<string, string> = {
    '타로': 'TARO',
    '사주': 'SAJU',
    '신점': 'FORTUNE'
  }

  // API 요청 데이터 준비
  const requestData = {
    name: form.value.name.trim(),
    nickname: form.value.nickname.trim(),
    email: form.value.email.trim(),
    phone: form.value.phone.replace(/-/g, '').trim(),
    address: undefined,
    specialty_types: [specialtyTypesMap[form.value.category] || 'TARO'],
    keywords: form.value.keywords.trim() || undefined,
    introduction: `${form.value.tagline.trim()}\n\n${form.value.greeting.trim()}${form.value.career.trim() ? '\n\n[경력]\n' + form.value.career.trim() : ''}`,
    photos: selectedFiles.value
  }

  // API 호출
  createApplication(requestData)
}

// URL params check for pre-selected category
onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const selectedCategory = urlParams.get('category')
  if (selectedCategory) {
    form.value.category = selectedCategory
  }
})
</script>

<style>
@import '~/assets/css/apply.css';
</style>