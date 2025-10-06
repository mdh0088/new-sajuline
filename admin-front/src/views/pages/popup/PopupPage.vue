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
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createPopup">
                팝업 등록
              </el-button>
            </div>
            <div>
              <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deletePopupByIdx">
                  팝업 삭제
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
        <el-tab-pane :label="`팝업 목록 (${tableOptions.totalCnt})`" name="counselor"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template v-slot:customSlot-ord="{ data }">
            <el-select
                v-if="data.showYn == 'Y'"
                class="m-r-10"
                v-model="data.ord"
                @change="updatePopupInfo(data)"
                placeholder="노출 순번"
                style="width: 100px"
            >
              <el-option
                  v-for="item in popupOrdList"
                  :key="item.ord"
                  :label="item.ord"
                  :value="item.ord"
              />
            </el-select>
          </template>

          <template v-slot:customSlot-showYn="{ data }">
            <CustomSwitch
                v-model:switchValue="data.showYn"
                :rowValue="data"
                :switchEvent="updatePopupInfo"
            />
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

  <PopupDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import {  Edit, Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {popupHeader, popupSearchOption} from "@/views/pages/popup/popupConstants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
import {getPopupList, getPopupOrderNo ,deletePopup, updatePopup} from "@/views/pages/popup/popupPage"
import * as swal from "@/commonUtils/swal";
import {PopupClass} from "@/models/popup";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const PopupDetailDrawer = defineAsyncComponent(() => import("@/views/pages/popup/components/PopupDetailDrawer.vue"))
const openType = ref("update"); // create or update


const activeTab = ref('')

const tableOptions = ref<TableOptions<PopupInfo>>(new TableOptionsClass({headers: popupHeader}))
const searchOptions = ref(new SearchOptionsClassList(popupSearchOption))

// 팝업 생성요 drawer open
const createPopup = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

// 팝업 삭제
const deletePopupByIdx = async () => {
  const result = await swal.swalConfirm('정말 삭제 시키겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      await deletePopup(item);
    }
    await doSearch();
  }
}

const popupOrdList = ref<Array<PopupInfo>>([]);
const popupInfo = ref<PopupInfo>(new PopupClass());
const attachFile = ref([]);

// 팝업 노출 여부 수정
const updatePopupInfo = async (info:PopupInfo) => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    popupInfo.value = new PopupClass(info)

    if (popupInfo.value.ord == null) {
      popupInfo.value.ord = popupOrdList.value.length + 1;
    }

    await updatePopup(popupInfo, attachFile, doSearch)
  } else {
    await doSearch()
  }

  await getPopupOrderNo(popupOrdList);
}

const targetSort = ref<string>('asc');
const targetSortKey = ref<string>('');
// 팝업 목로 조회
const doSearch = async (sort:string='asc', sortKey:string='') => {
  targetSort.value = typeof sort === 'number' ? 'asc' : sort;
  targetSortKey.value = sortKey;

  const startDt = searchOptions.value.getOptionByKey('dateValue').value[0]
  const endDt = searchOptions.value.getOptionByKey('dateValue').value[1]

  const queryParams:PopupRequest = {
    searchName: searchOptions.value.getOptionByKey('searchName').value,
    type: searchOptions.value.getOptionByKey('type').value,
    startDt:startDt,
    endDt:endDt,
    showYn:searchOptions.value.getOptionByKey('showYn').value,
    page: tableOptions.value.currentPage ?? 1,
    pageSize: tableOptions.value.rowPage ?? 10,
    sort:targetSort.value,
    sortKey:targetSortKey.value
  };

  await getPopupList(queryParams, tableOptions)
}

onMounted(async () => {
  await doSearch();
  await getPopupOrderNo(popupOrdList);
})

</script>
