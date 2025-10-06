<template>
  <div class="m-b-10">
    <div class="row m-t-10">
      <div class="d-flex justify-content-between">
        <div class="col-2">
          <div class="text-start">
          </div>
        </div>
        <div class="col-10">
          <div class="text-end d-flex justify-content-end">
            <div>
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createGradeItem">
                등급 추가
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <CommonList
          v-model:tableOptions="tableOptions"
          :doSearch="doSearch"
      >
        <!-- 포인트 적립률 커스텀 슬롯 -->
        <template v-slot:customSlot-point_earn_rate="{ data }">
          {{ data.point_earn_rate }}%
        </template>

        <!-- 할인율 커스텀 슬롯 -->
        <template v-slot:customSlot-discount_rate="{ data }">
          {{ data.discount_rate }}%
        </template>

        <!-- 활성화 여부 커스텀 슬롯 -->
        <template v-slot:customSlot-is_active="{ data }">
          <el-tag :type="data.is_active ? 'success' : 'danger'">
            {{ data.is_active ? '활성' : '비활성' }}
          </el-tag>
        </template>

        <!-- 액션 커스텀 슬롯 -->
        <template v-slot:customSlot-actions="{ data }">
          <el-button
              type="info"
              size="small"
              @click="openUsersPopup(data.grade_code)">
            유저 목록
          </el-button>
        </template>
      </CommonList>
    </el-card>
  </div>

  <GradeDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

  <GradeUsersPopup
      v-model:isPopActive="isPopActive"
      :targetGradeCode="targetGradeCode"
  />

</template>

<script lang="ts" setup>
import {Edit} from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {gradeHeaders} from "@/views/pages/grade/gradeConstants"
import {getGradesList} from "@/views/pages/grade/gradePage";
import type {GradeItem} from '@/types/grade';
import type {TableOptions} from '@/types/common';

const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const GradeDetailDrawer = defineAsyncComponent(() => import("@/views/pages/grade/components/GradeDetailDrawer.vue"))
const GradeUsersPopup = defineAsyncComponent(() => import("@/views/pages/grade/components/GradeUsersPopup.vue"))

const openType = ref("update"); // create or update

// 테이블 옵션 초기화
const tableOptions = ref<TableOptions<GradeItem>>({
  headers: gradeHeaders,
  rowItems: [10, 20, 30, 50],
  currentPage: 1,
  totalCnt: 0,
  rowPage: 10,
  isLoading: false,
  isDrawerActive: false,
  isSelectActive: false,
  isNumberActive: false,
  isPagination: false,
  chooseRow: {},
  selectedItems: [],
  items: []
});

const isPopActive = ref<boolean>(false);
const targetGradeCode = ref<string>('');

// 등급 생성용 drawer open
const createGradeItem = () => {
  openType.value = "create";
  tableOptions.value.chooseRow = {};
  tableOptions.value.isDrawerActive = true;
}

// 유저 목록 팝업 열기
const openUsersPopup = (grade_code: string) => {
  targetGradeCode.value = grade_code;
  isPopActive.value = true;
}

// 등급 목록 조회
const doSearch = async () => {
  await getGradesList(tableOptions);
}

onMounted(async () => {
  await doSearch();
})

</script>
