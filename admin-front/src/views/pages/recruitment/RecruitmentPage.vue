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
        <!-- 신청상태 커스텀 슬롯 -->
        <template v-slot:customSlot-application_status="{ data }">
          <el-tag :type="data.application_status === 'PENDING' ? 'warning' : data.application_status === 'APPROVED' ? 'success' : 'danger'">
            {{ data.application_status === 'PENDING' ? '대기중' : data.application_status === 'APPROVED' ? '승인됨' : '거절됨' }}
          </el-tag>
        </template>
      </CommonList>
    </el-card>
  </div>

  <RecruitmentDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />
</template>

<script lang="ts" setup>
import {ref, defineAsyncComponent, onMounted} from "vue"
import {getCounselorApplicationsList} from "@/views/pages/recruitment/recruitmentPage"
import {recruitmentSearchOptions, recruitmentHeaders} from "@/views/pages/recruitment/constants"
import type {CounselorApplicationListItem} from '@/types/counselor_application';
import type {TableOptions, SearchOptionsList} from '@/types/common';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const RecruitmentDetailDrawer = defineAsyncComponent(() => import("@/views/pages/recruitment/components/RecruitmentDetailDrawer.vue"))

// 테이블 옵션 초기화
const tableOptions = ref<TableOptions<CounselorApplicationListItem>>({
  headers: recruitmentHeaders,
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
  optionsList: recruitmentSearchOptions
});

// 검색 실행
const doSearch = async () => {
  await getCounselorApplicationsList(searchOptions, tableOptions);
}

// 페이지 로드 시 초기 검색
onMounted(async () => {
  await doSearch();
})
</script>
