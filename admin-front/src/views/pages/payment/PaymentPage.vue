<template>
  <div class="m-b-20">
    <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  </div>

  <div>
    <el-card>
      <CommonList
          v-model:tableOptions="tableOptions"
          :doSearch="doSearch"
      >
        <!-- 결제 상태 커스텀 슬롯 -->
        <template v-slot:customSlot-payment_status="{ data }">
          <el-tag
            :type="paymentStatusOptions[data.payment_status]?.type || 'info'"
          >
            {{ paymentStatusOptions[data.payment_status]?.label || data.payment_status }}
          </el-tag>
        </template>

        <!-- 취소 버튼 커스텀 슬롯 -->
        <template v-slot:customSlot-actions="{ data }">
          <el-button
            v-if="data.payment_status === 'SUCCESS'"
            type="danger"
            size="small"
            @click="handleCancelPayment(data)"
          >
            취소
          </el-button>
        </template>
      </CommonList>
    </el-card>
  </div>

  <PaymentDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      :chooseRow="tableOptions.chooseRow"
  />
</template>

<script lang="ts" setup>
import {ref, defineAsyncComponent, onMounted} from "vue"
import {getPaymentsList, cancelPayment} from "@/views/pages/payment/paymentPage"
import {paymentSearchOptions, paymentHeaders, paymentStatusOptions} from "@/views/pages/payment/paymentConstants"
import type {TableOptions, SearchOptionsList} from '@/types/common';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const PaymentDetailDrawer = defineAsyncComponent(() => import("@/views/pages/payment/components/PaymentDetailDrawer.vue"))

// 테이블 옵션 초기화
const tableOptions = ref<TableOptions<any>>({
  headers: paymentHeaders,
  rowItems: [10, 20, 30, 50],
  currentPage: 1,
  totalCnt: 0,
  rowPage: 10,
  isLoading: false,
  isDrawerActive: false,
  isSelectActive: false,
  isNumberActive: false,
  isPagination: true,
  chooseRow: {},
  selectedItems: [],
  items: []
});

// 검색 옵션 초기화
const searchOptions = ref<SearchOptionsList>({
  optionsList: paymentSearchOptions
});

// 검색 실행
const doSearch = async () => {
  await getPaymentsList(searchOptions, tableOptions);
}

// 결제 취소 처리
const handleCancelPayment = async (data: any) => {
  const payment_id = Number(data.payment_id);
  const success = await cancelPayment(payment_id, doSearch);

  if (success) {
    // 목록은 doSearch로 이미 새로고침됨
    // 필요시 drawer도 닫기
    if (tableOptions.value.isDrawerActive) {
      tableOptions.value.isDrawerActive = false;
    }
  }
}

// 페이지 로드 시 초기 검색
onMounted(async () => {
  await doSearch();
})
</script>
