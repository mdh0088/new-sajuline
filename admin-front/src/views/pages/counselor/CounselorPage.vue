<template>
  <div class="m-b-20">
    <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  </div>

  <div class="m-b-10">
    <div class="row m-t-10">
      <div class="d-flex justify-content-between">
        <div class="col-2">
          <div class="text-start">
          </div>
        </div>
        <div class="col-10">
          <div class="text-end d-flex justify-content-end">
            <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
              <el-button type="primary" :icon="Delete" @click="counselorOut">
                상담사 탈퇴
              </el-button>
            </el-badge>
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
        <!-- 노출여부 커스텀 슬롯 -->
        <template v-slot:customSlot-is_show="{ data }">
          <CustomSwitch
              v-model:switchValue="data.is_show"
              :rowValue="data"
              :switchEvent="updateShowStatus"
          />
        </template>
        <template v-slot:customSlot-m_state="{ data }">
          <el-tag :type="data.m_state === '1' ? 'success' : data.m_state === '2' ? 'warning' : 'danger'">
            {{ data.m_state === '1' ? '대기중' : data.m_state === '2' ? '상담중' : '부재중' }}
          </el-tag>
        </template>
      </CommonList>
    </el-card>
  </div>

  <CounselorDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />
</template>

<script lang="ts" setup>
import { Delete } from '@element-plus/icons-vue'
import {ref, defineAsyncComponent, onMounted} from "vue"
import {getCounselorsList, updateCounselorShow, updateCounselorInfo} from "@/views/pages/counselor/counselorPage"
import {counselorSearchOptions, counselorHeaders} from "@/views/pages/counselor/counselorConstants"
import * as swal from '@/commonUtils/swal';
import type {CounselorListItem, CounselorDetailUpdate} from '@/types/counselor';
import type {TableOptions, SearchOptionsList} from '@/types/common';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const CounselorDetailDrawer = defineAsyncComponent(() => import("@/views/pages/counselor/components/CounselorDetailDrawer.vue"))

// 테이블 옵션 초기화
const tableOptions = ref<TableOptions<CounselorListItem>>({
  headers: counselorHeaders,
  rowItems: [10, 20, 30, 50],
  currentPage: 1,
  totalCnt: 0,
  rowPage: 10,
  isLoading: false,
  isDrawerActive: false,
  isSelectActive: true,
  isNumberActive: false,
  isPagination: true,
  chooseRow: {},
  selectedItems: [],
  items: []
});

// 검색 옵션 초기화
const searchOptions = ref<SearchOptionsList>({
  optionsList: counselorSearchOptions
});

// 검색 실행
const doSearch = async () => {
  await getCounselorsList(searchOptions, tableOptions);
}

// 페이지 로드 시 초기 검색
onMounted(async () => {
  await doSearch();
})

// 노출 여부 변경
const updateShowStatus = async (rowData: CounselorListItem) => {
  const message = rowData.is_show
    ? '노출 상태로 변경하시겠습니까?'
    : '비노출 상태로 변경하시겠습니까?';

  const result = await swal.swalConfirm(message, 'question');

  if (result.isConfirmed) {
    await updateCounselorShow(
      rowData.counselor_id,
      rowData.is_show,
      doSearch
    );
  } else {
    // 사용자가 취소한 경우 원래 상태로 되돌림
    rowData.is_show = !rowData.is_show;
  }
}

// 상담사 탈퇴
const counselorOut = async () => {
  if (tableOptions.value.selectedItems.length === 0) {
    swal.swalAlert("탈퇴할 상담사를 선택해주세요.", 'warning');
    return;
  }

  const result = await swal.swalConfirm('정말 탈퇴 시키겠습니까?', 'warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      const updateData: CounselorDetailUpdate = {
        is_out: true
      };

      await updateCounselorInfo(
        item.counselor_id,
        updateData,
        undefined
      );
    }

    swal.swalAlert('탈퇴 처리가 완료되었습니다.', 'success');
    await doSearch();
  }
}
</script>
