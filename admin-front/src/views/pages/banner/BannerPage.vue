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
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createBanner">
                배너 등록
              </el-button>
            </div>
            <div>
              <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deleteNotice">
                  배너 삭제
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
        <el-tab-pane :label="`배너 목록 (${tableOptions.totalCnt})`" name="counselor"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template v-slot:customSlot-target="{ data }">
            {{getTypeNm[data.target]}}
          </template>
          <template v-slot:customSlot-ord="{ data }">
            <el-select
                v-if="data.showYn == 'Y'"
                class="m-r-10"
                v-model="data.ord"
                @change="updateBannerInfo(data)"
                placeholder="노출 순번"
                style="width: 100px"
            >
              <el-option
                  v-for="item in bannerOrdList"
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
                :switchEvent="updateBannerInfo"
            />
          </template>
        </CommonList>

      </el-tabs>
    </el-card>
  </div>

  <BannerDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import {  Edit, Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {bannerHeader, bannerSearchOptions} from "@/views/pages/banner/bannerContants"
import {TableOptionsClass, SearchOptionsClassList} from "@/models/common"
import {getBannerList, getBannerOrderNo ,deleteBanner, updateBanner} from "@/views/pages/banner/bannerPage"
import * as swal from "@/commonUtils/swal";
import {BannerClass} from "@/models/banner";

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const BannerDetailDrawer = defineAsyncComponent(() => import("@/views/pages/banner/components/BannerDetailDrawer.vue"))
const openType = ref("update"); // create or update


const activeTab = ref('')

const tableOptions = ref<TableOptions<BannerInfo>>(new TableOptionsClass({headers: bannerHeader}))
 const searchOptions = ref(new SearchOptionsClassList(bannerSearchOptions))


// 배너 생성요 drawer open
const createBanner = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

// 배너 삭제
const deleteNotice = async () => {
  const result = await swal.swalConfirm('정말 삭제 시키겠습니까?','warning');
  if (result.isConfirmed) {
    for (const item of tableOptions.value.selectedItems) {
      await deleteBanner(item);
    }
    await doSearch();
  }
}
const getTypeNm = {
  BLANK:'새창',
  SELF:"현재창"
}
const bannerOrdList = ref<Array<BannerInfo>>([]);
const bannerInfo = ref<BannerInfo>(new BannerClass());
const attachFile = ref([]);

// 배너 노출 여부 수정
const updateBannerInfo = async (info:BannerInfo) => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    bannerInfo.value = new BannerClass(info)

    if (bannerInfo.value.ord == null) {
      bannerInfo.value.ord = bannerOrdList.value.length + 1;
    }

    await updateBanner(bannerInfo, attachFile, doSearch)
  } else {
    await doSearch()
  }

  await getBannerOrderNo(bannerOrdList);
}


const targetSort = ref<string>('asc');
const targetSortKey = ref<string>('');
// 배너 목로 조회
const doSearch = async (sort:string='asc', sortKey:string='') => {
  targetSort.value = typeof sort === 'number' ? 'asc' : sort;
  targetSortKey.value = sortKey;

  const startDt = searchOptions.value.getOptionByKey('dateValue').value[0]
  const endDt = searchOptions.value.getOptionByKey('dateValue').value[1]

  const queryParams:BannerRequest = {
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

  await getBannerList(queryParams, tableOptions)
}

onMounted(async () => {
  await doSearch();
  await getBannerOrderNo(bannerOrdList);
})

</script>
