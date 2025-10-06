<template>
  <el-drawer
      v-model="isDrawerActive"
      title="결제 상세 정보"
      size="50%"
      @open="openDrawer"
  >
    <!-- 헤더 우측 버튼 영역 -->
    <template #header>
      <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
        <span>결제 상세 정보</span>
        <el-button
          v-if="paymentData && paymentData.payment.payment_status === 'SUCCESS'"
          type="danger"
          size="default"
          @click="handleCancelPayment"
        >
          결제 취소
        </el-button>
      </div>
    </template>

    <div v-loading="isLoading">
      <div v-if="paymentData">
        <!-- 결제 정보 섹션 -->
        <div>
          <div class="m-b-20">
            <h4>결제 정보</h4>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="결제 ID">
              {{ paymentData.payment.payment_id }}
            </el-descriptions-item>
            <el-descriptions-item label="주문번호">
              {{ paymentData.payment.order_no }}
            </el-descriptions-item>
            <el-descriptions-item label="결제 금액">
              {{ formatNumber(paymentData.payment.amount) }} 원
            </el-descriptions-item>
            <el-descriptions-item label="결제 수단">
              <el-tag>{{ paymentMethodLabels[paymentData.payment.payment_method] || paymentData.payment.payment_method }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="결제 상태">
              <el-tag :type="paymentStatusOptions[paymentData.payment.payment_status]?.type || 'info'">
                {{ paymentStatusOptions[paymentData.payment.payment_status]?.label || paymentData.payment.payment_status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="결제 완료일">
              {{ formatDateTime(paymentData.payment.paid_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="생성일">
              {{ formatDateTime(paymentData.payment.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="PG사 거래번호" v-if="paymentData.payment.pg_transaction_id">
              {{ paymentData.payment.pg_transaction_id }}
            </el-descriptions-item>
            <el-descriptions-item label="PG사 응답코드" v-if="paymentData.payment.pg_response_code">
              {{ paymentData.payment.pg_response_code }}
            </el-descriptions-item>
            <el-descriptions-item label="PG사 응답메시지" v-if="paymentData.payment.pg_response_message">
              {{ paymentData.payment.pg_response_message }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <!-- 회원 정보 섹션 -->
        <div>
          <div class="m-b-20">
            <h4>회원 정보</h4>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="회원 ID">
              {{ paymentData.user.user_id }}
            </el-descriptions-item>
            <el-descriptions-item label="닉네임" v-if="paymentData.user.nickname">
              {{ paymentData.user.nickname }}
            </el-descriptions-item>
            <el-descriptions-item label="이메일" v-if="paymentData.user.email">
              {{ paymentData.user.email }}
            </el-descriptions-item>
            <el-descriptions-item label="휴대폰 번호" v-if="paymentData.user.phone">
              {{ paymentData.user.phone }}
            </el-descriptions-item>
            <el-descriptions-item label="회원 등급" v-if="paymentData.user.grade_code">
              {{ paymentData.user.grade_code }}
            </el-descriptions-item>
            <el-descriptions-item label="포인트 잔액" v-if="paymentData.user.point_balance !== undefined">
              {{ formatNumber(paymentData.user.point_balance) }} P
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <!-- 상품 정보 섹션 (있는 경우) -->
        <div v-if="paymentData.payment.product_id">
          <div class="m-b-20">
            <h4>상품 정보</h4>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="상품 ID">
              {{ paymentData.payment.product_id }}
            </el-descriptions-item>
            <el-descriptions-item label="상품명" v-if="paymentData.payment.product_name">
              {{ paymentData.payment.product_name }}
            </el-descriptions-item>
            <el-descriptions-item label="포인트 금액" v-if="paymentData.payment.point_amount">
              {{ formatNumber(paymentData.payment.point_amount) }} P
            </el-descriptions-item>
            <el-descriptions-item label="보너스 포인트" v-if="paymentData.payment.bonus_point">
              {{ formatNumber(paymentData.payment.bonus_point) }} P
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, computed, watch} from 'vue';
import {getPaymentDetail, cancelPayment} from "@/views/pages/payment/paymentPage"
import {paymentStatusOptions, paymentMethodLabels} from "@/views/pages/payment/paymentConstants"
import type {PaymentDetailResponse, PaymentWithUserItem} from '@/types/payment';

interface Props {
  isDrawerActive: boolean;
  chooseRow: any;
}

const props = defineProps<Props>();
const emit = defineEmits(['update:isDrawerActive']);

const isDrawerActive = computed({
  get: () => props.isDrawerActive,
  set: (value) => emit('update:isDrawerActive', value)
});

const isLoading = ref(false);
const paymentData = ref<PaymentDetailResponse | null>(null);

const openDrawer = async () => {
  if (props.chooseRow && props.chooseRow.payment_id) {
    const payment_id = props.chooseRow.payment_id;
    if (payment_id) {
      paymentData.value = await getPaymentDetail(payment_id, isLoading);
    }
  }
};

// 결제 취소 처리
const handleCancelPayment = async () => {
  if (!paymentData.value) return;

  const payment_id = paymentData.value.payment.payment_id;
  const success = await cancelPayment(payment_id);

  if (success) {
    // Drawer 닫기
    isDrawerActive.value = false;
    // 상세 정보 다시 로드
    await openDrawer();
  }
};

// 날짜 포맷팅 (날짜만)
const formatDate = (dateString: string | null): string => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR');
};

// 날짜 포맷팅 (날짜 + 시간)
const formatDateTime = (dateString: string | null): string => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR');
};

// 숫자 포맷팅
const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '0';
  return value.toLocaleString('ko-KR');
};
</script>

<style scoped>
.el-descriptions {
  margin-top: 20px;
}
</style>
