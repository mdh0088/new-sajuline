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
            <div>
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createNotice">
                공지사항 등록
              </el-button>
            </div>
            <div>
              <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deleteNotices">
                  공지사항 삭제
                </el-button>
              </el-badge>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane :label="`공지사항 리스트(${tableOptions.totalCnt})`" name="notice"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template #target_audience="{ row }">
            <el-tag v-if="row.target_audience === 'ALL'" type="success">전체 공개</el-tag>
            <el-tag v-else-if="row.target_audience === 'USER'" type="info">사용자</el-tag>
            <el-tag v-else-if="row.target_audience === 'COUNSELOR'" type="warning">상담사</el-tag>
            <el-tag v-else>{{ row.target_audience }}</el-tag>
          </template>

          <template #is_important="{ row }">
            <el-tag v-if="row.is_important" type="danger">중요</el-tag>
            <el-tag v-else type="info">일반</el-tag>
          </template>

          <template #customSlot-is_important="{ data }">
            <el-tag v-if="data.is_important" type="danger">중요</el-tag>
            <el-tag v-else type="info">일반</el-tag>
          </template>
          <template #customSlot-is_active="{ data }">
            <CustomSwitch
                v-model:switchValue="data.is_active"
                :rowValue="data"
                :switchEvent="updateActiveStatus"
            />
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

  <NoticeDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import { Edit, Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import { noticeHeaders, noticeSearchOptions} from "@/views/pages/customer-support/notice/noticeConstants"
import {getNoticesList, deleteNotice, updateNoticeActiveStatus} from "@/views/pages/customer-support/notice/noticePage"
import * as swal from "@/commonUtils/swal";
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common";
import type { NoticeListItem } from '@/types/notice';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const NoticeDetailDrawer = defineAsyncComponent(() => import("@/views/pages/customer-support/notice/components/NoticeDetailDrawer.vue"))

const openType = ref<string>("update"); // create or update

const activeTab = ref<string>('notice')
const tableOptions = ref<TableOptions<NoticeListItem>>(new TableOptionsClass({headers: noticeHeaders}))
const searchOptions = ref(new SearchOptionsClassList(noticeSearchOptions))

const createNotice = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

const deleteNotices = async () => {
  if (tableOptions.value.selectedItems.length === 0) {
    await swal.swalAlert('삭제할 공지사항을 선택해주세요.', 'warning');
    return;
  }

  const result = await swal.swalConfirm('선택한 공지사항을 삭제하시겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      await deleteNotice(item.notice_id, undefined);
    }
    await doSearch();
  }
}

const updateActiveStatus = async (rowData: NoticeListItem) => {
  const message = rowData.is_active
    ? '활성 상태로 변경하시겠습니까?'
    : '비활성 상태로 변경하시겠습니까?';

  const result = await swal.swalConfirm(message, 'question');

  if (result.isConfirmed) {
    const success = await updateNoticeActiveStatus(
      Number(rowData.notice_id),
      rowData.is_active,
      doSearch
    );

    // API 호출 실패 시 원래 상태로 되돌림
    if (!success) {
      rowData.is_active = !rowData.is_active;
    }
  } else {
    // 사용자가 취소한 경우 원래 상태로 되돌림
    rowData.is_active = !rowData.is_active;
  }
}

const doSearch = async () => {
  await getNoticesList(searchOptions, tableOptions)
}

onMounted(async () => {
  await doSearch();
})
</script>
