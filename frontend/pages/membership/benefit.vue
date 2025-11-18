<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <main class="pt-[60px] pb-24">
      <!-- 인트로 섹션 -->
      <section class="intro-section">
        <h2 class="intro-title">사주라인 회원을 위한 특별 혜택 안내</h2>
        <p class="intro-description">
          전월 결제 금액을 바탕으로 매월 1일 새로운 멤버십 등급이 결정됩니다.
        </p>
      </section>

      <!-- 등급 시각화 -->
      <section class="tier-visualization">
        <div class="tier-steps">
          <div class="tier-step">
            <div class="tier-step-icon white">⚪</div>
            <div class="tier-step-label">WHITE</div>
            <div class="tier-step-amount">10만원 미만</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon bronze">🥉</div>
            <div class="tier-step-label">BRONZE</div>
            <div class="tier-step-amount">~30만원</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon silver">🥈</div>
            <div class="tier-step-label">SILVER</div>
            <div class="tier-step-amount">~50만원</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon gold">🥇</div>
            <div class="tier-step-label">GOLD</div>
            <div class="tier-step-amount">~100만원</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon vip">👑</div>
            <div class="tier-step-label">VIP</div>
            <div class="tier-step-amount">~300만원</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon vip-plus">👑</div>
            <div class="tier-step-label">VIP+</div>
            <div class="tier-step-amount">~700만원</div>
          </div>
          <div class="tier-step">
            <div class="tier-step-icon vvip">💎</div>
            <div class="tier-step-label">VVIP</div>
            <div class="tier-step-amount">700만원↑</div>
          </div>
        </div>
      </section>

      <!-- 등급 상세 카드 -->
      <section class="tier-cards">
        <!-- WHITE -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon white">⚪</div>
            WHITE
          </div>
          <div class="tier-range">전월 결제금액 10만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 0%</div>
        </div>

        <!-- BRONZE -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon bronze">🥉</div>
            BRONZE
          </div>
          <div class="tier-range">전월 결제금액 10만원 이상 ~ 30만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 1%</div>
        </div>

        <!-- SILVER -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon silver">🥈</div>
            SILVER
          </div>
          <div class="tier-range">전월 결제금액 30만원 이상 ~ 50만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 2%</div>
        </div>

        <!-- GOLD -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon gold">🥇</div>
            GOLD
          </div>
          <div class="tier-range">전월 결제금액 50만원 이상 ~ 100만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 3%</div>
        </div>

        <!-- VIP -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon vip">👑</div>
            VIP
          </div>
          <div class="tier-range">전월 결제금액 100만원 이상 ~ 300만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 4%</div>
        </div>

        <!-- VIP+ -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon vip-plus">👑</div>
            VIP+
          </div>
          <div class="tier-range">전월 결제금액 300만원 이상 ~ 700만원 미만</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 5%</div>
        </div>

        <!-- VVIP -->
        <div class="tier-card">
          <div class="tier-name">
            <div class="tier-icon vvip">💎</div>
            VVIP
          </div>
          <div class="tier-range">전월 결제금액 700만원 이상</div>
          <div class="tier-benefit">등급 혜택: 마일리지 적립 7%</div>
        </div>
      </section>

      <!-- 마일리지 안내 -->
      <section class="mileage-info">
        <div class="mileage-header">
          <span class="mileage-icon">💡</span>
          <h3 class="mileage-title">마일리지 안내</h3>
        </div>
        <ul class="mileage-list">
          <li class="mileage-item">
            마일리지는 마일리지샵에서 상담 포인트를 구매할 수 있는 재화입니다.
          </li>
          <li class="mileage-item">
            멤버십 혜택은 해당 멤버십 기간 동안 무제한으로 적립됩니다.
          </li>
          <li class="mileage-item">
            마일리지로 구매한 포인트는 환불 및 양도가 불가합니다.
          </li>
          <li class="mileage-item">
            회원 탈퇴 시 미사용된 마일리지는 자동 소멸됩니다.
          </li>
          <li class="mileage-item">
            마일리지는 포인트 상담 금액만 해당되며, 060 상담 금액은 포함되지 않습니다.
          </li>
          <li class="mileage-item">
            1 마일리지는 1 포인트로 환산됩니다.
          </li>
          <li class="mileage-item">
            마일리지는 익일 01시에 전일 사용 금액만큼 적립됩니다.
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
// SEO 메타 데이터 설정
useSeoMeta({
  title: '멤버십 혜택 - 사주라인',
  description: '사주라인 멤버십 등급별 혜택과 마일리지 적립 안내입니다. 일반, VIP, VVIP 등급에 따른 포인트 적립률, 할인 혜택, 전용 서비스를 확인하세요.',
  keywords: '사주라인, 멤버십, 혜택, 마일리지, 등급, VIP, VVIP, 포인트 적립, 회원 혜택',
  ogTitle: '멤버십 혜택 - 사주라인',
  ogDescription: '사주라인 멤버십 등급별 혜택. 일반, VIP, VVIP 등급의 특별한 혜택을 확인하세요.',
  ogImage: 'https://sajuline.com/images/og-membership.jpg',
  ogUrl: 'https://sajuline.com/membership/benefit',
  ogType: 'website',
  twitterCard: 'summary_large_image',
  twitterTitle: '멤버십 혜택 - 사주라인',
  twitterDescription: '사주라인 멤버십 등급별 혜택 안내',
  twitterImage: 'https://sajuline.com/images/og-membership.jpg',
  robots: 'index,follow'
})

useHead({
  link: [{ rel: 'canonical', href: 'https://sajuline.com/membership/benefit' }]
})
</script>

<style scoped>
@import '~/assets/css/membership/benefit.css';
</style>
