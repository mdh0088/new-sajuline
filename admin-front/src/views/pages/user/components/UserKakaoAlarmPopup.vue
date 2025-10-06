<template>
  <el-dialog
      v-model="isAlarmPopActive"
      title="알림톡 로그 목록"
      width="80%"
      :close-on-click-modal="false"
      @open="openDialog"
      @close="closeDialog"
  >
    <div v-if="isAlarmPopActive && userData">
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
            <strong>이메일:</strong> {{ userData.email }}
          </el-col>
        </el-row>
      </div>

      <el-divider />

      <!-- 알림톡 로그 테이블 -->
      <div>
        <h4 class="m-b-10">알림톡 발송 내역</h4>
        <el-scrollbar :max-height="'500px'" :min-size="1">
          <CommonList
              v-model:tableOptions="tableOptions"
              :doSearch="loadNotificationLogs"
          />
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
import {getUserNotificationLogs} from "@/views/pages/user/userPage";
import {notificationLogHeaders} from "@/views/pages/user/userConstants";
import type {
  UserListItemResponse,
  NotificationLogItem
} from '@/types/user';
import type {TableOptions} from '@/types/common';

const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"));

// Props
const props = defineProps<{
  userData: UserListItemResponse | null;
}>();

// Model
const isAlarmPopActive = defineModel<boolean>("isAlarmPopActive", { default: false });

// 테이블 옵션
const tableOptions = ref<TableOptions<NotificationLogItem>>({
  headers: notificationLogHeaders,
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

  // 알림톡 로그 로드
  await loadNotificationLogs();
};

const closeDialog = () => {
  isAlarmPopActive.value = false;
  tableOptions.value.items = [];
};

const loadNotificationLogs = async () => {
  if (!props.userData) {
    return;
  }

  await getUserNotificationLogs(props.userData.user_id, tableOptions);
};
</script>

<style scoped>
.m-b-10 {
  margin-bottom: 10px;
}

.m-b-20 {
  margin-bottom: 20px;
}
</style>
