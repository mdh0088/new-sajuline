<template>
  <div class="m-b-20">
    <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  </div>

  <div class="m-b-10">
    <div class="row m-t-10">
      <div class="d-flex justify-content-between">
        <div class="col-6">
          <div class="text-start d-flex align-items-center">
            <el-button type="warning" :icon="Refresh" @click="handleDryRun" :loading="isExecuting">
              등급 업데이트 테스트
            </el-button>
            <el-button class="m-l-10" type="danger" :icon="Setting" @click="handleExecute" :loading="isExecuting">
              등급 업데이트 실행
            </el-button>
            <span class="m-l-10 text-muted" style="font-size: 12px;">
              * 선택한 연월 기준으로 등급을 업데이트합니다
            </span>
          </div>
        </div>
        <div class="col-6">
          <div class="text-end">
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane :label="`등급 변경 이력 (${tableOptions.totalCnt})`" name="gradeHistory"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template v-slot:customSlot-change_reason="{ data }">
            <el-tag :type="getChangeReasonType(data.change_reason)">
              {{ getChangeReasonLabel(data.change_reason) }}
            </el-tag>
          </template>

          <template v-slot:customSlot-purchase_amount="{ data }">
            {{ formatNumber(data.purchase_amount) }}원
          </template>

          <template v-slot:customSlot-grade_change="{ data }">
            <span>{{ data.grade_before }}</span>
            <el-icon class="m-l-5 m-r-5"><Right /></el-icon>
            <span :class="getGradeChangeClass(data.grade_before, data.grade_after)">
              {{ data.grade_after }}
            </span>
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

</template>

<script lang="ts" setup>
import { Refresh, Setting, Right } from '@element-plus/icons-vue'
import { defineAsyncComponent, onMounted, ref } from "vue";
import { gradeHistoryHeaders, gradeHistorySearchOptions, changeReasonOptions } from "@/views/pages/grade-history/gradeHistoryConstants"
import { TableOptionsClass, SearchOptionsClassList } from "@/models/common"
import { getGradeChangeLogsList, executeMonthlyGradeUpdate } from "@/views/pages/grade-history/gradeHistory"
import type { GradeChangeLogItem } from "@/views/pages/grade-history/gradeHistory"

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))

const activeTab = ref('gradeHistory')
const isExecuting = ref(false)

const tableOptions = ref<TableOptions<GradeChangeLogItem>>(new TableOptionsClass({headers: gradeHistoryHeaders}))
const searchOptions = ref(new SearchOptionsClassList(gradeHistorySearchOptions))

// 변경 사유 라벨 조회
const getChangeReasonLabel = (reason: string) => {
  const option = changeReasonOptions.find(opt => opt.value === reason);
  return option ? option.label : reason;
}

// 변경 사유 태그 타입
const getChangeReasonType = (reason: string) => {
  if (reason === 'AUTO_BATCH') return 'primary';
  if (reason === 'MANUAL') return 'warning';
  return 'info';
}

// 숫자 포맷팅
const formatNumber = (num: number) => {
  return num?.toLocaleString('ko-KR') || '0';
}

// 등급 변경 클래스 (상승/하락 표시)
const getGradeChangeClass = (before: string, after: string) => {
  // 등급 레벨 비교는 실제 데이터에 따라 조정 필요
  return '';
}

// 등급 업데이트 테스트 (dry_run)
const handleDryRun = async () => {
  const year = searchOptions.value.getOptionByKey('year')?.value;
  const month = searchOptions.value.getOptionByKey('month')?.value;

  if (!year) {
    return;
  }

  // 월이 선택되지 않은 경우 현재 월 사용
  const targetMonth = month || new Date().getMonth() + 1;

  isExecuting.value = true;
  try {
    await executeMonthlyGradeUpdate(year, targetMonth, true, doSearch);
  } finally {
    isExecuting.value = false;
  }
}

// 등급 업데이트 실행
const handleExecute = async () => {
  const year = searchOptions.value.getOptionByKey('year')?.value;
  const month = searchOptions.value.getOptionByKey('month')?.value;

  if (!year) {
    return;
  }

  // 월이 선택되지 않은 경우 현재 월 사용
  const targetMonth = month || new Date().getMonth() + 1;

  isExecuting.value = true;
  try {
    await executeMonthlyGradeUpdate(year, targetMonth, false, doSearch);
  } finally {
    isExecuting.value = false;
  }
}

// 등급 변경 로그 목록 조회
const doSearch = async () => {
  await getGradeChangeLogsList(searchOptions, tableOptions)
}

onMounted(async () => {
  await doSearch();
})

</script>

<style scoped>
.m-b-20 {
  margin-bottom: 20px;
}

.m-b-10 {
  margin-bottom: 10px;
}

.m-t-10 {
  margin-top: 10px;
}

.m-l-5 {
  margin-left: 5px;
}

.m-r-5 {
  margin-right: 5px;
}

.m-l-10 {
  margin-left: 10px;
}

.text-muted {
  color: #909399;
}
</style>
