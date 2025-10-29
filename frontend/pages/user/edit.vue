<template>
  <div class="min-h-screen bg-slate-950 text-white">

    <!-- 메인 콘텐츠 -->
    <main class="pb-24">
      <section class="px-5 py-6">
        <!-- 헤더 섹션 -->
        <div class="edit-header">
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

        <!-- 위험 영역 (계정 관리) -->
        <div class="danger-zone">
          <div class="danger-zone-header">
            <h3 class="danger-zone-title">계정 관리</h3>
            <p class="danger-zone-description">계정 삭제 시 모든 데이터가 영구적으로 삭제됩니다</p>
          </div>
          <button class="withdrawal-button" @click="openWithdrawalModal">
            회원탈퇴
          </button>
        </div>
      </section>
    </main>

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

    <!-- 1단계: 회원탈퇴 비밀번호 입력 및 유의사항 모달 -->
    <div v-if="showWithdrawalModal" class="modal-backdrop" @click="closeWithdrawalModal">
      <div class="modal-content withdrawal-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">회원탈퇴</h3>
          <button class="modal-close" @click="closeWithdrawalModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-subtitle">비밀번호와 유의사항을 확인해주세요.</p>

          <!-- 비밀번호 입력 -->
          <div class="form-group">
            <label class="form-label">비밀번호 확인<span class="required">*</span></label>
            <div class="password-input-wrapper">
              <input
                v-model="withdrawalPassword"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="비밀번호를 입력하세요"
              >
              <button
                type="button"
                class="password-toggle-btn"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <!-- 유의사항 -->
          <div class="withdrawal-warnings">
            <h4 class="warnings-title">⚠️ 탈퇴 시 유의사항</h4>

            <div class="warning-item">
              <div class="warning-icon">🗑️</div>
              <div class="warning-content">
                <h5 class="warning-title">회원정보/서비스 이용기록 삭제</h5>
                <p class="warning-text">
                  회원등급, 포인트, 즐겨찾기 상담사, 마일리지 등의 데이터가 영구히 삭제되며 복구가 불가합니다.
                </p>
              </div>
            </div>

            <div class="warning-item">
              <div class="warning-icon">🚫</div>
              <div class="warning-content">
                <h5 class="warning-title">회원 탈퇴 후 재가입</h5>
                <p class="warning-text">
                  탈퇴 시 1개월간 재가입이 불가합니다.
                </p>
              </div>
            </div>
          </div>

          <!-- 동의 체크박스 -->
          <div class="agreement-check">
            <label class="checkbox-label">
              <input
                v-model="agreedToTerms"
                type="checkbox"
                class="checkbox-input"
              >
              <span class="checkbox-text">위 유의사항을 모두 확인했으며 회원탈퇴에 동의합니다.</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-cancel-btn" @click="closeWithdrawalModal">취소</button>
          <button
            class="modal-danger-btn"
            :disabled="!withdrawalPassword || !agreedToTerms"
            @click="openFinalConfirmModal"
          >
            다음
          </button>
        </div>
      </div>
    </div>

    <!-- 2단계: 최종 확인 모달 -->
    <div v-if="showFinalConfirmModal" class="modal-backdrop" @click="closeFinalConfirmModal">
      <div class="modal-content final-confirm-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">최종 확인</h3>
          <button class="modal-close" @click="closeFinalConfirmModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="final-confirm-icon">⚠️</div>
          <p class="final-confirm-text">
            정말 탈퇴하시겠습니까?
          </p>
          <p class="final-confirm-subtext">
            이 작업은 되돌릴 수 없습니다.
          </p>
        </div>
        <div class="modal-footer">
          <button class="modal-cancel-btn" @click="closeFinalConfirmModal">취소</button>
          <button class="modal-danger-btn" @click="handleWithdrawal">탈퇴하기</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/auth/useAuth'

const router = useRouter()
const { logout } = useAuth()

// 모달 상태
const showPasswordModal = ref(false)
const showWithdrawalModal = ref(false)
const showFinalConfirmModal = ref(false)

// 회원탈퇴 관련 상태
const withdrawalPassword = ref('')
const agreedToTerms = ref(false)
const showPassword = ref(false)

// 비밀번호 변경 모달
const openPasswordModal = () => {
  showPasswordModal.value = true
  document.body.style.overflow = 'hidden'
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  document.body.style.overflow = 'auto'
}

// 1단계: 회원탈퇴 모달 (비밀번호 입력 + 유의사항)
const openWithdrawalModal = () => {
  showWithdrawalModal.value = true
  document.body.style.overflow = 'hidden'
  // 초기화
  withdrawalPassword.value = ''
  agreedToTerms.value = false
  showPassword.value = false
}

const closeWithdrawalModal = () => {
  showWithdrawalModal.value = false
  document.body.style.overflow = 'auto'
  // 초기화
  withdrawalPassword.value = ''
  agreedToTerms.value = false
  showPassword.value = false
}

// 2단계: 최종 확인 모달
const openFinalConfirmModal = () => {
  // 1단계 모달 닫기
  showWithdrawalModal.value = false
  // 2단계 모달 열기
  showFinalConfirmModal.value = true
}

const closeFinalConfirmModal = () => {
  showFinalConfirmModal.value = false
  document.body.style.overflow = 'auto'
  // 1단계로 돌아가기
  showWithdrawalModal.value = true
}

// 회원탈퇴 실행
const handleWithdrawal = async () => {
  try {
    // TODO: 실제 API 호출
    // await withdrawalAPI(withdrawalPassword.value)

    // 임시: 콘솔 로그
    console.log('회원탈퇴 처리:', {
      password: withdrawalPassword.value,
      agreed: agreedToTerms.value
    })

    // 모달 닫기
    showFinalConfirmModal.value = false
    document.body.style.overflow = 'auto'

    // 로그아웃 처리
    await logout()

    // 로그인 페이지로 이동
    router.push('/login')

    // 성공 알림 (선택사항)
    alert('회원탈퇴가 완료되었습니다.')
  } catch (error) {
    console.error('회원탈퇴 실패:', error)
    alert('회원탈퇴 처리 중 오류가 발생했습니다.')
  }
}
</script>

<style>
@import '~/assets/css/edit.css';
</style>