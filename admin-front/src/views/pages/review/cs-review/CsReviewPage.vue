<template>
  <div class="m-b-20">
    <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  </div>

  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">상담 후기 관리</span>
          <el-button type="primary" @click="openDummyReviewDrawer">
            더미 후기 생성
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane :label="`후기 목록 (${tableOptions.totalCnt || 0})`" name="review"/>

        <CommonList
          v-model:tableOptions="tableOptions"
          :doSearch="doSearch"
        >
          <template v-slot:customSlot-is_best="{ data }">
            <CustomSwitch
              v-model:switchValue="data.is_best"
              :rowValue="data"
              :switchEvent="handleBestChange"
            />
          </template>

          <template v-slot:customSlot-is_visible="{ data }">
            <CustomSwitch
              v-model:switchValue="data.is_visible"
              :rowValue="data"
              :switchEvent="handleVisibleChange"
            />
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

  <CsDetailDrawer
    v-model:isDrawerActive="tableOptions.isDrawerActive"
    v-model:openType="openType"
    :chooseRow="tableOptions.chooseRow"
    :doSearch="doSearch"
  />

  <CsDummyReviewDrawer
    v-model:isDrawerActive="isDummyDrawerActive"
    :doSearch="doSearch"
  />

</template>

<script lang="ts" setup>
import { defineAsyncComponent, onMounted, ref } from "vue";
import { csReviewHeader, csReviewSearchOptions } from "@/views/pages/review/cs-review/csReviewConstants"
import { TableOptionsClass, SearchOptionsClassList } from "@/models/common"
import { getReviewList, updateReviewQuick } from "@/views/pages/review/cs-review/csReviewPage"
import type { ConsultationReviewItem } from "@/types/consultation_review";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const CsDetailDrawer = defineAsyncComponent(() => import("@/views/pages/review/cs-review/components/CsDetailDrawer.vue"))
const CsDummyReviewDrawer = defineAsyncComponent(() => import("@/views/pages/review/cs-review/components/CsDummyReviewDrawer.vue"))

const openType = ref("update"); // update only (no create for reviews)
const activeTab = ref('review')
const isDummyDrawerActive = ref(false)

const tableOptions = ref<TableOptions<ConsultationReviewItem>>(
  new TableOptionsClass({ headers: csReviewHeader, isPagination: true, isSelectActive: false })
)
const searchOptions = ref(new SearchOptionsClassList(csReviewSearchOptions))

// 테이블 row 클릭 시
tableOptions.value.rowClick = (row: ConsultationReviewItem) => {
  openType.value = "update";
  tableOptions.value.chooseRow = row;
  tableOptions.value.isDrawerActive = true;
}

// 상담 후기 목록 조회
const doSearch = async () => {
  await getReviewList(searchOptions, tableOptions)
}

// 베스트 여부 변경 처리
const handleBestChange = async (review: ConsultationReviewItem) => {
  await updateReviewQuick(review, doSearch, 'is_best');
}

// 노출 상태 변경 처리
const handleVisibleChange = async (review: ConsultationReviewItem) => {
  await updateReviewQuick(review, doSearch, 'is_visible');
}

// 더미 후기 생성 Drawer 열기
const openDummyReviewDrawer = () => {
  isDummyDrawerActive.value = true;
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

.m-r-10 {
  margin-right: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}
</style>
