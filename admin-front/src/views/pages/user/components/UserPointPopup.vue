<template>
  <el-dialog
      v-model="isPointPopActive"
      title="마일리지 적립 내역 및 포인트 관리"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="!isAdjusting"
      @open="openDialog"
      @close="closeDialog"
  >
    <div v-if="isPointPopActive && userData">
      <!-- 사용자 기본 정보 -->
      <div class="m-b-20">
        <el-row :gutter="20">
          <el-col :span="8">
            <strong>아이디:</strong> {{ userData.user_id }}
          </el-col>
          <el-col :span="8">
            <strong>닉네임:</strong> {{ userData.nickname }}
          </el-col>
          <el-col :span="8">
            <strong>보유 마일리지:</strong> {{ numberComma(userData.mileage_point) }} P
          </el-col>
        </el-row>
      </div>

      <el-divider />

      <!-- 포인트 지급/차감 섹션 -->
      <div class="m-b-20">
        <h4>포인트 지급/차감</h4>
        <el-form :model="pointAdjustForm" label-width="120px" inline class="m-t-10">
          <el-form-item label="조정 타입">
            <el-radio-group v-model="pointAdjustForm.type">
              <el-radio value="plus">지급</el-radio>
              <el-radio value="minus">차감</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="금액">
            <el-input-number v-model="pointAdjustForm.amount" :min="1" :step="1000" style="width: 200px"/>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="adjustPoints" :loading="isAdjusting">
              {{ pointAdjustForm.type === 'plus' ? '지급' : '차감' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 마일리지 적립 내역 테이블 -->
      <div>
        <h4 class="m-b-10">마일리지 적립 내역</h4>
        <el-scrollbar :max-height="'400px'" :min-size="1">
          <CommonList
              v-model:tableOptions="tableOptions"
              :doSearch="loadEarnLogs"
          >
            <template v-slot:customSlot-amount="{ data }">
              {{ numberComma(data.amount) }}
            </template>
            <template v-slot:customSlot-balance_after="{ data }">
              {{ numberComma(data.balance_after) }}
            </template>
          </CommonList>
        </el-scrollbar>
      </div>
    </div>

    <template #footer>
      <el-button @click="closeDialog">닫기</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import {ref, defineAsyncComponent} from 'vue';
import {getMileageEarnLogs, adjustUserPoints} from "@/views/pages/user/userPage";
import {pointTransactionHeaders} from "@/views/pages/user/userConstants";
import {numberComma} from "@/commonUtils/utils";
import * as swal from '@/commonUtils/swal';
import type {
  UserListItemResponse,
  PointTransactionItem,
  UserPointAdjustRequest
} from '@/types/user';
import type {TableOptions} from '@/types/common';

const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"));

// Props
const props = defineProps<{
  userData: UserListItemResponse | null;
  doRefresh?: () => void;
}>();

// Model
const isPointPopActive = defineModel<boolean>("isPointPopActive", { default: false });

// Data
const isAdjusting = ref(false);

// 포인트 조정 폼
const pointAdjustForm = ref<UserPointAdjustRequest>({
  user_id: '',
  amount: 1000,
  type: 'plus'
});

// 테이블 옵션
const tableOptions = ref<TableOptions<PointTransactionItem>>({
  headers: pointTransactionHeaders,
  rowItems: [10, 20, 30, 50],
  currentPage: 1,
  totalCnt: 0,
  rowPage: 10,
  isLoading: false,
  isDrawerActive: false,
  isSelectActive: false,
  isNumberActive: true,
  isPagination: false,
  chooseRow: {},
  selectedItems: [],
  items: []
});

// Methods
const openDialog = async () => {
  if (!props.userData) {
    return;
  }

  // 포인트 조정 폼 초기화
  pointAdjustForm.value = {
    user_id: props.userData.user_id,
    amount: 1000,
    type: 'plus'
  };

  // 마일리지 적립 내역 로드
  await loadEarnLogs();
};

const closeDialog = () => {
  isPointPopActive.value = false;
  tableOptions.value.items = [];
};

const loadEarnLogs = async () => {
  if (!props.userData) {
    return;
  }

  await getMileageEarnLogs(props.userData.user_id, tableOptions);
};

const adjustPoints = async () => {
  const result = await swal.swalConfirm(
      `${pointAdjustForm.value.type === 'plus' ? '지급' : '차감'} 하시겠습니까?`,
      'question'
  );

  if (result.isConfirmed) {
    isAdjusting.value = true;

    const success = await adjustUserPoints(pointAdjustForm.value, async () => {
      // 성공 시 적립 내역 새로고침
      await loadEarnLogs();
      // 상위 컴포넌트 새로고침
      if (props.doRefresh) {
        props.doRefresh();
      }
    });

    if (success) {
      // 폼 초기화
      pointAdjustForm.value.amount = 1000;
      pointAdjustForm.value.type = 'plus';
    }

    isAdjusting.value = false;
  }
};
</script>

<style scoped>
.m-b-10 {
  margin-bottom: 10px;
}

.m-b-20 {
  margin-bottom: 20px;
}

.m-t-10 {
  margin-top: 10px;
}
</style>
