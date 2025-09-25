<template>
  <footer class="app-footer">
    <!-- 메인 링크 섹션 -->
    <div class="footer-links">
      <div class="footer-link" @click="goProvision">이용약관</div>
      <div class="footer-link" @click="goPrivacy">개인정보처리방침</div>
      <div class="footer-link" @click="goCs">고객센터</div>
      <div class="footer-link" @click="goApply">상담사 신청</div>
    </div>

    <!-- 책임 고지 -->
    <div class="footer-disclaimer">
      <p>
        피플라인은 통신판매중개시스템의 제공자로서 통신판매의 당사자가 아닙니다.
        상품의 판매, 상담 내용을 포함하여 거래에 대한 책임은 각 판매자(상담사)에게 있으며,
        또한 피플라인 본 플랫폼 외부에서 이루어진 상담 등으로 인하여 발생한 문제에 대해서도
        마찬가지로 책임을 지지 않습니다.
      </p>
      <p>
        당 사이트의 모든 저작물의 저작권은 피플라인에 있으며, 무단 복제나 도용은 금지되어 있습니다.
      </p>
    </div>

    <!-- 회사 정보 -->
    <div class="footer-company-info">
      <div class="company-info-grid">
        <div class="company-info-item">
          <span class="info-label">상호명</span>
          <span class="info-value">피플라인</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">주소</span>
          <span class="info-value">서울시 광진구 광나루로 486</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">사업자등록번호</span>
          <span class="info-value">647-34-01142</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">대표</span>
          <span class="info-value">김진형</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">통신판매번호</span>
          <span class="info-value">제2023-서울광진-0178호</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">고객센터</span>
          <span class="info-value">02-6212-0465</span>
        </div>
        <div class="company-info-item">
          <span class="info-label">이메일</span>
          <a href="mailto:help@sajutarot.com" class="info-email">help@sajutarot.com</a>
        </div>
      </div>
    </div>

    <!-- 저작권 -->
    <div class="footer-copyright">
      <p>&copy; {{ new Date().getFullYear() }} 피플라인. All rights reserved.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 마이페이지와 동일한 라우터 push 방식 사용
const goCs = () => router.push('/cs')
const goProvision = () => router.push('/provision')
const goPrivacy = () => router.push('/privacy')
const goApply = () => router.push('/apply')
</script>

<style scoped>
/* 컴포넌트별 스코프 스타일이 필요한 경우 여기에 추가 */
</style>