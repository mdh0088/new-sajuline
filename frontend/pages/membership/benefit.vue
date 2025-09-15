<template>
  <div class="membership-page">
    <!-- 헤더 -->
    <AppHeader title="멤버십 혜택" :show-back="true" />

    <!-- 메인 콘텐츠 -->
    <main class="membership-content">
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
          <div
            v-for="tier in tiers"
            :key="tier.id"
            class="tier-step"
          >
            <div :class="['tier-step-icon', tier.id]">
              {{ tier.icon }}
            </div>
            <div class="tier-step-info">
              <div class="tier-step-label">{{ tier.name }}</div>
              <div class="tier-step-amount">
                {{ formatAmountRange(tier) }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 등급 상세 카드 -->
      <section class="tier-cards">
        <div
          v-for="tier in tiers"
          :key="tier.id"
          class="tier-card"
        >
          <div class="tier-card-header">
            <div :class="['tier-icon', tier.id]">
              {{ tier.icon }}
            </div>
            <h3 class="tier-name">{{ tier.name }}</h3>
          </div>
          <div class="tier-range">
            {{ getFullAmountRange(tier) }}
          </div>
          <div class="tier-benefit">
            등급 혜택: 마일리지 적립 {{ tier.mileageRate }}%
          </div>
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

    <!-- 하단 네비게이션 -->
    <AppBottomNavi />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { IMembershipTier } from '~/types/membership';
import '~/assets/css/membership/benefit.css';

// 멤버십 등급 데이터
const tiers = ref<IMembershipTier[]>([
  {
    id: 'white',
    name: 'WHITE',
    icon: '⚪',
    minAmount: 0,
    maxAmount: 100000,
    mileageRate: 0,
    displayOrder: 1,
  },
  {
    id: 'bronze',
    name: 'BRONZE',
    icon: '🥉',
    minAmount: 100000,
    maxAmount: 300000,
    mileageRate: 1,
    displayOrder: 2,
  },
  {
    id: 'silver',
    name: 'SILVER',
    icon: '🥈',
    minAmount: 300000,
    maxAmount: 500000,
    mileageRate: 2,
    displayOrder: 3,
  },
  {
    id: 'gold',
    name: 'GOLD',
    icon: '🥇',
    minAmount: 500000,
    maxAmount: 1000000,
    mileageRate: 3,
    displayOrder: 4,
  },
  {
    id: 'vip',
    name: 'VIP',
    icon: '👑',
    minAmount: 1000000,
    maxAmount: 3000000,
    mileageRate: 4,
    displayOrder: 5,
  },
  {
    id: 'vip-plus',
    name: 'VIP+',
    icon: '👑',
    minAmount: 3000000,
    maxAmount: 7000000,
    mileageRate: 5,
    displayOrder: 6,
  },
  {
    id: 'vvip',
    name: 'VVIP',
    icon: '💎',
    minAmount: 7000000,
    mileageRate: 7,
    displayOrder: 7,
  },
]);

// 금액 포맷팅 (간략 버전)
const formatAmountRange = (tier: IMembershipTier): string => {
  if (tier.id === 'white') {
    return '~10만원';
  }
  if (tier.id === 'vvip') {
    return '700만원↑';
  }

  const max = tier.maxAmount! / 10000;
  return `~${max}만원`;
};

// 금액 포맷팅 (상세 버전)
const getFullAmountRange = (tier: IMembershipTier): string => {
  const formatAmount = (amount: number): string => {
    if (amount >= 10000) {
      return `${(amount / 10000).toLocaleString()}만원`;
    }
    return `${amount.toLocaleString()}원`;
  };

  if (tier.id === 'white') {
    return '전월 결제금액 10만원 미만';
  }

  if (tier.id === 'vvip') {
    return '전월 결제금액 700만원 이상';
  }

  const min = formatAmount(tier.minAmount);
  const max = formatAmount(tier.maxAmount!);

  return `전월 결제금액 ${min} 이상 ~ ${max} 미만`;
};

// SEO 설정
useHead({
  title: '멤버십 혜택 - 사주라인',
  meta: [
    {
      name: 'description',
      content: '사주라인 멤버십 등급별 혜택과 마일리지 적립 안내',
    },
    {
      name: 'keywords',
      content: '사주라인, 멤버십, 혜택, 마일리지, 등급, VIP, VVIP',
    },
  ],
});
</script>

<style scoped>
/* 모바일에서 tier-step 내부 정보 그룹핑 */
@media (max-width: 768px) {
  .tier-step-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }
}
</style>