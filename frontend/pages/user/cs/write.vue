<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 헤더 섹션 -->
        <div class="inquiry-write-header">
          <button class="back-button" @click="$router.back()">
            <span class="back-icon">←</span>
          </button>
          <h1 class="inquiry-write-title">문의하기</h1>
        </div>

        <!-- 문의 작성 폼 -->
        <div class="inquiry-write-container">
          <form @submit.prevent="">

            <!-- 문의 유형 선택 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">
                문의 유형<span class="required">*</span>
              </label>
              <select class="inquiry-form-select">
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
                class="inquiry-form-textarea"
                placeholder="문의하실 내용을 자세히 작성해 주세요."
                maxlength="1000"
                rows="8"
              ></textarea>
              <div class="inquiry-form-help">최대 1000자</div>
            </div>

            <!-- 첨부파일 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">첨부파일</label>
              <div class="inquiry-file-upload" @click="triggerFileInput">
                <span class="inquiry-file-icon">📎</span>
                <span class="inquiry-file-text">파일을 선택하세요 (최대 3개, 각 5MB 이하)</span>
                <button type="button" class="inquiry-file-button">파일 선택</button>
              </div>
              <input ref="fileInput" type="file" accept="image/*,.pdf,.doc,.docx,.txt" multiple hidden>
              <div class="inquiry-file-list">
                <!-- 선택된 파일들이 여기에 표시 (UI만) -->
                <div class="inquiry-file-item">
                  <span class="inquiry-file-name">예시파일.png</span>
                  <button type="button" class="inquiry-file-remove">✕</button>
                </div>
              </div>
              <div class="inquiry-form-help">이미지, PDF, 문서 파일만 첨부 가능</div>
            </div>

            <!-- 연락처 정보 -->
            <div class="inquiry-form-group">
              <label class="inquiry-form-label">답변 받을 연락처</label>
              <input
                type="email"
                class="inquiry-form-input"
                placeholder="이메일 주소 (선택사항)"
              >
              <div class="inquiry-form-help">답변을 이메일로도 받고 싶은 경우 입력하세요</div>
            </div>

            <!-- 개인정보 수집 동의 -->
            <div class="inquiry-agreement-section">
              <label class="inquiry-agreement-item">
                <input type="checkbox" class="inquiry-checkbox" required>
                <span class="inquiry-agreement-text">
                  개인정보 수집 및 이용에 동의합니다. <button type="button" class="inquiry-agreement-link" @click="showPrivacyModal = true">(상세보기)</button>
                </span>
              </label>
              <div class="inquiry-form-help">문의 답변을 위해 개인정보가 수집됩니다.</div>
            </div>

            <!-- 제출 버튼 -->
            <div class="inquiry-submit-container">
              <button type="submit" class="inquiry-submit-button">
                문의하기
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- 개인정보 처리방침 모달 -->
    <div v-if="showPrivacyModal" class="modal-backdrop" @click="showPrivacyModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">개인정보 수집 및 이용</h3>
          <button class="modal-close" @click="showPrivacyModal = false">✕</button>
        </div>
        <div class="modal-body">
          <h4>수집하는 개인정보 항목</h4>
          <p>- 이름, 이메일 주소, 문의 내용</p>

          <h4>개인정보 수집 및 이용 목적</h4>
          <p>- 고객 문의 접수 및 답변 제공</p>
          <p>- 서비스 개선을 위한 통계 분석</p>

          <h4>개인정보 보유 및 이용 기간</h4>
          <p>- 문의 처리 완료 후 1년간 보관</p>
          <p>- 관련 법령에 따른 보관 의무가 있는 경우 해당 기간까지 보관</p>
        </div>
        <div class="modal-footer">
          <button class="modal-close-btn" @click="showPrivacyModal = false">확인</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

// 모달 상태 (UI만)
const showPrivacyModal = ref(false)

// 파일 선택 (UI만)
const fileInput = ref<HTMLInputElement>()

const triggerFileInput = () => {
  fileInput.value?.click()
}
</script>

<style>
@import '~/assets/css/cs.css';
@import '~/assets/css/inquiry.css';
</style>