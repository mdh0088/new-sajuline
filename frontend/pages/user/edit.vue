<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />

    <!-- 메인 콘텐츠 -->
    <main class="pt-[60px] pb-24">
      <section class="px-5 py-6">
        <!-- 헤더 섹션 -->
        <div class="edit-header">
          <button class="back-button" @click="$router.back()">
            <span class="back-icon">←</span>
          </button>
          <h1 class="edit-title">회원정보 수정</h1>
        </div>

        <!-- 회원정보 폼 -->
        <div class="edit-form-container">
          <form @submit.prevent="">

            <!-- 아이디 (변경 불가) -->
            <div class="form-group">
              <label class="form-label">
                아이디<span class="required">*</span>
              </label>
              <div class="form-input-readonly">
                <input
                  type="text"
                  value="user123@example.com"
                  readonly
                  class="readonly-input"
                >
                <span class="readonly-badge">변경 불가</span>
              </div>
            </div>

            <!-- 비밀번호 (수정 버튼) -->
            <div class="form-group">
              <label class="form-label">
                비밀번호<span class="required">*</span>
              </label>
              <div class="form-input-with-button">
                <input
                  type="password"
                  value="••••••••"
                  readonly
                  class="password-input"
                >
                <button
                  type="button"
                  class="change-password-btn"
                  @click="openPasswordModal"
                >
                  비밀번호 수정
                </button>
              </div>
            </div>

            <!-- 닉네임 (변경 가능) -->
            <div class="form-group">
              <label class="form-label">닉네임</label>
              <input
                type="text"
                value="김사주"
                class="form-input"
                placeholder="닉네임을 입력하세요"
                maxlength="20"
              >
              <div class="form-help">최대 20자</div>
            </div>

            <!-- 휴대폰 번호 (변경 불가) -->
            <div class="form-group">
              <label class="form-label">
                휴대폰 번호<span class="required">*</span>
              </label>
              <div class="form-input-readonly">
                <input
                  type="tel"
                  value="010-1234-5678"
                  readonly
                  class="readonly-input"
                >
                <span class="readonly-badge">변경 불가</span>
              </div>
            </div>

            <!-- 저장 버튼 -->
            <div class="save-button-container">
              <button type="submit" class="save-button">
                저장
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- 회원탈퇴 버튼 (우측 하단 고정) -->
    <div class="withdrawal-container">
      <button class="withdrawal-button" @click="openWithdrawalModal">
        회원탈퇴
      </button>
    </div>

    <!-- 비밀번호 변경 모달 -->
    <div v-if="showPasswordModal" class="modal-backdrop" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">비밀번호 변경</h3>
          <button class="modal-close" @click="closePasswordModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">현재 비밀번호</label>
            <input
              type="password"
              class="form-input"
              placeholder="현재 비밀번호를 입력하세요"
            >
          </div>
          <div class="form-group">
            <label class="form-label">새 비밀번호</label>
            <input
              type="password"
              class="form-input"
              placeholder="새 비밀번호를 입력하세요"
            >
          </div>
          <div class="form-group">
            <label class="form-label">새 비밀번호 확인</label>
            <input
              type="password"
              class="form-input"
              placeholder="새 비밀번호를 다시 입력하세요"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-cancel-btn" @click="closePasswordModal">취소</button>
          <button class="modal-save-btn">변경</button>
        </div>
      </div>
    </div>

    <!-- 회원탈퇴 확인 모달 -->
    <div v-if="showWithdrawalModal" class="modal-backdrop" @click="closeWithdrawalModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">회원탈퇴</h3>
          <button class="modal-close" @click="closeWithdrawalModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="withdrawal-warning">
            정말로 탈퇴하시겠습니까?
          </p>
          <p class="withdrawal-notice">
            탈퇴 시 모든 데이터가 삭제되며, 복구할 수 없습니다.
          </p>
        </div>
        <div class="modal-footer">
          <button class="modal-cancel-btn" @click="closeWithdrawalModal">취소</button>
          <button class="modal-danger-btn">탈퇴</button>
        </div>
      </div>
    </div>

    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '~/components/common/AppHeader.vue'
import AppBottomNavi from '~/components/common/AppBottomNavi.vue'

// 모달 상태 (UI만)
const showPasswordModal = ref(false)
const showWithdrawalModal = ref(false)

// 모달 열기/닫기 (UI만)
const openPasswordModal = () => {
  showPasswordModal.value = true
  document.body.style.overflow = 'hidden'
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  document.body.style.overflow = 'auto'
}

const openWithdrawalModal = () => {
  showWithdrawalModal.value = true
  document.body.style.overflow = 'hidden'
}

const closeWithdrawalModal = () => {
  showWithdrawalModal.value = false
  document.body.style.overflow = 'auto'
}
</script>

<style>
@import '~/assets/css/edit.css';
</style>