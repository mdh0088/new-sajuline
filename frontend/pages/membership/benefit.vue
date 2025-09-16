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
            v-for="g in grades"
            :key="g.grade_code"
            class="tier-step"
          >
            <div class="tier-step-icon">
              <img
                v-if="g.grade_image_url"
                :src="cdnUrl('grade', g.grade_image_url)"
                alt="grade image"
                class="tier-icon-img"
                loading="lazy"
              />
              <span v-else class="tier-icon-fallback">⭐</span>
            </div>
            <div class="tier-step-info">
              <div class="tier-step-label">{{ g.grade_code }}</div>
              <div class="tier-step-amount">
                {{ shortAmountRange(g.min_purchase_amount) }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 등급 상세 카드 -->
      <section class="tier-cards">
        <div
          v-for="g in grades"
          :key="g.grade_code"
          class="tier-card"
        >
          <div class="tier-card-header">
            <div class="tier-icon">
              <img
                v-if="g.grade_image_url"
                :src="cdnUrl('grade', g.grade_image_url)"
                alt="grade image"
                class="tier-icon-img"
                loading="lazy"
              />
              <span v-else class="tier-icon-fallback">⭐</span>
            </div>
            <h3 class="tier-name">{{ g.grade_code }}</h3>
          </div>
          <div class="tier-range">
            {{ fullAmountRange(g.min_purchase_amount, nextMin(g)) }}
          </div>
          <div v-if="numberVal(g.point_earn_rate) >= 1" class="tier-benefit">
            적립 혜택: 마일리지 적립 {{ numberVal(g.point_earn_rate) }}%
          </div>
          <div v-if="numberVal(g.discount_rate) >= 1" class="tier-benefit">
            할인 혜택 : 상품 할인 {{ numberVal(g.discount_rate) }}%
          </div>
          <div v-if="g.description" class="tier-desc">{{ g.description }}</div>
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
import { computed } from 'vue';
import '~/assets/css/membership/benefit.css';
import { useGradeApi } from '~/composables/api/useGrade'
import { useCdn } from '~/composables/utils/useCdn'

const { usePublicGrades } = useGradeApi()
const { data } = usePublicGrades()
const grades = computed(() => (data.value ?? []).sort((a, b) => a.grade_level - b.grade_level))
const { cdnUrl } = useCdn()

const shortAmountRange = (min: number) => {
  if (!min || min === 0) return '10만원 미만'
  return `~${(min / 10000).toLocaleString()}만원`
}

const fullAmountRange = (min: number, nextMin?: number | null) => {
  const fmt = (v: number) => v >= 10000 ? `${(v/10000).toLocaleString()}만원` : `${v.toLocaleString()}원`
  if (!min || min === 0) return '전월 결제금액 10만원 미만'
  if (!nextMin || nextMin <= min) return `전월 결제금액 ${fmt(min)} 이상`
  return `전월 결제금액 ${fmt(min)} 이상 ~ ${fmt(nextMin)} 미만`
}

const numberVal = (v: number | string | undefined) => Number(v ?? 0)

const nextMin = (g: any) => {
  const arr = grades.value
  const idx = arr.findIndex(it => it.grade_code === g.grade_code)
  const next = idx >= 0 && idx + 1 < arr.length ? arr[idx + 1] : undefined
  return next?.min_purchase_amount ?? null
}

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
.tier-icon-img{width:36px;height:36px;object-fit:contain;border-radius:8px;border:1px solid rgba(0,0,0,.06);background:#fff}
.tier-icon-fallback{font-size:20px}
</style>