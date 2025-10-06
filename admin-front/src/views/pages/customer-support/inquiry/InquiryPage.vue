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
                  삭제
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
      <el-tabs v-model="activeTab" class="demo-tabs" @tab-click="handleClick">
        <el-tab-pane :label="`상담사 문의 리스트`" name="csAdminFaq"/>
        <el-tab-pane :label="`1:1고객센터 문의 리스트`" name="adminFaq"/>
        <el-tab-pane :label="`1:1상담사 문의 리스트`" name="csFaq"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        />

      </el-tabs>
    </el-card>
  </div>

  <template v-if="activeTab == 'csAdminFaq'">
    <CsAdminFaqDrawer
        v-model:isDrawerActive="tableOptions.isDrawerActive"
        :chooseRow="tableOptions.chooseRow"
        :doSearch="doSearch"
    />
  </template>
  <template v-else-if="activeTab == 'adminFaq'">
    <AdminFaqDrawer
        v-model:isDrawerActive="tableOptions.isDrawerActive"
        :chooseRow="tableOptions.chooseRow"
        :doSearch="doSearch"
    />
  </template>
  <template v-else>
    <CsFaqDrawer
        v-model:isDrawerActive="tableOptions.isDrawerActive"
        :chooseRow="tableOptions.chooseRow"
        :doSearch="doSearch"
    />
  </template>


</template>
<script lang="ts" setup>
import { Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref, computed, watch, nextTick} from "vue";
import {
  csAdminFaqHeader,
  adminFaqHeader,
  csFaqHeader,
  csAdminFaqSearchOptions,
  csFaqSearchOptions,
  adminFaqSearchOptions} from "@/views/pages/customer-support/inquiry/inquiryConstants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
import {
  getCsAdminFaqList,
  getAdminFaqList,
  getCsFaqList,
  deleteCsAdminFaq,
  deleteAdminFaq,
  deleteCsFaq
} from "@/views/pages/customer-support/inquiry/inquiryPage"
import * as swal from "@/commonUtils/swal";
import {TabsPaneContext} from "element-plus";
import {userHeaders} from "@/views/pages/user/userConstants";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CsAdminFaqDrawer = defineAsyncComponent(() => import("@/views/pages/customer-support/inquiry/components/CsAdminFaqDrawer.vue"))
const AdminFaqDrawer = defineAsyncComponent(() => import("@/views/pages/customer-support/inquiry/components/AdminFaqDrawer.vue"))
const CsFaqDrawer = defineAsyncComponent(() => import("@/views/pages/customer-support/inquiry/components/CsFaqDrawer.vue"))

const activeTab = ref('csAdminFaq')
const tableOptions = ref<TableOptions<any>>(new TableOptionsClass({headers: userHeaders}))
const searchOptions = ref(new SearchOptionsClassList(csAdminFaqSearchOptions))

const deleteNotice = async () => {
  const result = await swal.swalConfirm('정말 삭제 시키겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      if (activeTab.value == "csAdminFaq") {
        await deleteCsAdminFaq(item)
      } else if (activeTab.value == "adminFaq") {
        await deleteAdminFaq(item)
      } else {
        await deleteCsFaq(item)
      }
    }
    await doSearch();
  }
}

const handleClick = async (tab: TabsPaneContext, event: Event) => {
  await nextTick();
  await doSearch()
}

const targetSort = ref<string>('asc');
const targetSortKey = ref<string>('');
const doSearch = async (sort:string='asc', sortKey:string='') => {
  targetSort.value = typeof sort === 'number' ? 'asc' : sort;
  targetSortKey.value = sortKey;

  const queryParams = {
    startDt:null,
    endDt:null,
    page:1,
    newYn:'total',
    pageSize:10,
    sort:targetSort.value,
    sortKey:targetSortKey.value
  };

  const dateValue = searchOptions.value.getOptionByKey('dateValue');
  if (dateValue) {
    queryParams.startDt = dateValue.value[0];
    queryParams.endDt = dateValue.value[1];
  }

  searchOptions.value.optionsList.forEach(item => {
    if (item.key !== 'dateValue') {
      queryParams[item.key] = item.value;
    }
  });

  queryParams.page = tableOptions.value.currentPage;
  queryParams.pageSize = tableOptions.value.rowPage;

  if (activeTab.value == "csAdminFaq") {
    await getCsAdminFaqList(queryParams, tableOptions)
  } else if (activeTab.value == "adminFaq") {
    await getAdminFaqList(queryParams, tableOptions)
  } else {
    await getCsFaqList(queryParams, tableOptions)
  }
}

watch(
    () => activeTab.value,
    (newValue) => {
      if (newValue == 'csAdminFaq'){
        tableOptions.value.headers = csAdminFaqHeader;
        searchOptions.value = new SearchOptionsClassList(csAdminFaqSearchOptions);
      } else if (newValue == 'adminFaq') {
        tableOptions.value.headers = adminFaqHeader;
        searchOptions.value = new SearchOptionsClassList(csFaqSearchOptions);
      } else {
        tableOptions.value.headers = csFaqHeader;
        searchOptions.value = new SearchOptionsClassList(adminFaqSearchOptions);
      }
    },
    { immediate: true }
);

onMounted(async () => {
  activeTab.value = 'csAdminFaq'
  await doSearch();
})

</script>
