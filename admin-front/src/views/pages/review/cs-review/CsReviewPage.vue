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
              <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deleteNotice">
                  후기 삭제
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
        <el-tab-pane :label="`후기 리스트(${tableOptions.totalCnt})`" name="counselor"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        />

      </el-tabs>
    </el-card>
  </div>

  <CsDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import {  Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {csReviewHeader, csReviewSearchOptions} from "@/views/pages/review/cs-review/csReviewConstants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
import {getCsReviewList, deleteCsReview} from "@/views/pages/review/cs-review/csReviewPage"
import * as swal from "@/commonUtils/swal";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CsDetailDrawer = defineAsyncComponent(() => import("@/views/pages/review/cs-review/components/CsDetailDrawer.vue"))

const openType = ref("update"); // create or update

const activeTab = ref('')

const tableOptions = ref<TableOptions<CsReviewInfo>>(new TableOptionsClass({headers: csReviewHeader}))
const searchOptions = ref(new SearchOptionsClassList(csReviewSearchOptions))

const createNotice = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

const deleteNotice = async () => {
  const result = await swal.swalConfirm('정말 삭제 시키겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      await deleteCsReview(item);
    }
    await doSearch();
  }
}

const targetSort = ref<string>('asc');
const targetSortKey = ref<string>('');

const doSearch = async (sort:string='asc', sortKey:string='') => {
  targetSort.value = typeof sort === 'number' ? 'asc' : sort;
  targetSortKey.value = sortKey;

  const startDt = searchOptions.value.getOptionByKey('dateValue').value[0]
  const endDt = searchOptions.value.getOptionByKey('dateValue').value[1]

  const queryParams:ReviewRequest = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    type: searchOptions.value.getOptionByKey('type').value,
    startDt: startDt,
    endDt: endDt,
    bestYn: searchOptions.value.getOptionByKey('bestYn').value,
    //showYn: searchOptions.value.getOptionByKey('showYn').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage  ?? 10,
    sort:targetSort.value,
    sortKey:targetSortKey.value
  };

  await getCsReviewList(queryParams, tableOptions)
}



onMounted(async () => {
  await doSearch();
})
</script>
