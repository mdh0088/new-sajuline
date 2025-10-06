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
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createExhibition">
                기획전 등록
              </el-button>
            </div>
            <div>
              <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deleteExhibitionByIdx">
                  기획전 삭제
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
        <el-tab-pane :label="`기획전 목록 (${tableOptions.totalCnt})`" name="counselor"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template v-slot:customSlot-showYn="{ data }">
            <CustomSwitch
                v-model:switchValue="data.showYn"
                :rowValue="data"
                :switchEvent="updateExhibitionInfo"
            />
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

  <ExhibitionDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import {  Edit, Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {exhibitionHeader, exhibitionSearchOptions} from "@/views/pages/exhibition/exhibitionContants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
import {getExhibitionList, deleteExhibition, updateExhibition} from "@/views/pages/exhibition/exhibitionPage"
import * as swal from "@/commonUtils/swal";
import {ExhibitionClass} from "@/models/exhibition";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const ExhibitionDetailDrawer = defineAsyncComponent(() => import("@/views/pages/exhibition/components/ExhibitionDetailDrawer.vue"))
const openType = ref("update"); // create or update


const activeTab = ref('')

const tableOptions = ref<TableOptions<ExhibitionInfo>>(new TableOptionsClass({headers: exhibitionHeader}))
const searchOptions = ref(new SearchOptionsClassList(exhibitionSearchOptions))

// 기획전 생성요 drawer open
const createExhibition = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

// 기획전 삭제
const deleteExhibitionByIdx = async () => {
  const result = await swal.swalConfirm('정말 삭제 시키겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      await deleteExhibition(item);
    }
    await doSearch();
  }
}
const getTypeNm = {
  BLANK:'새창',
  SELF:"현재창"
}
const exhibitionInfo = ref<ExhibitionInfo>(new ExhibitionClass());
const attachFile = ref([]);

// 기획전 노출 여부 수정
const updateExhibitionInfo = async (info:ExhibitionInfo) => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    exhibitionInfo.value = new ExhibitionClass(info)
    await updateExhibition(exhibitionInfo, attachFile, doSearch)
  } else {
    await doSearch()
  }
}

// 기획전 목로 조회
const doSearch = async (sort:string='asc', sortKey:string='') => {
  const startDt = searchOptions.value.getOptionByKey('dateValue').value[0]
  const endDt = searchOptions.value.getOptionByKey('dateValue').value[1]

  const queryParams:ExhibitionRequest = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    type: searchOptions.value.getOptionByKey('type').value,
    startDt:startDt,
    endDt:endDt,
    showYn:searchOptions.value.getOptionByKey('showYn').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage ?? 10,
    sort:sort,
    sortKey:sortKey
  };

  await getExhibitionList(queryParams, tableOptions)
}

onMounted(async () => {
  await doSearch();
})

</script>
