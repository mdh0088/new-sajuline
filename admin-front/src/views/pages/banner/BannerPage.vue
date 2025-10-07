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
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="handleCreateBanner">
                배너 등록
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane :label="`배너 목록 (${tableOptions.totalCnt})`" name="banner"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        >
          <template v-slot:customSlot-display_order="{ data }">
            <el-select
                v-if="data.is_active"
                v-model="data.display_order"
                @change="handleBannerUpdate(data)"
                placeholder="노출 순번"
                style="width: 100px"
            >
              <el-option
                  v-for="item in getBannerOrderOptions(data.banner_type)"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
            <span v-else>-</span>
          </template>

          <template v-slot:customSlot-is_active="{ data }">
            <CustomSwitch
                v-model:switchValue="data.is_active"
                :rowValue="data"
                :switchEvent="handleBannerUpdate"
            />
          </template>

          <template v-slot:customSlot-link_target="{ data }">
            {{ getLinkTargetLabel(data.link_target) }}
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
import { Edit } from '@element-plus/icons-vue'
import { defineAsyncComponent, onMounted, ref, computed } from "vue";
import { bannerHeaders, bannerSearchOptions, linkTargetOptions } from "@/views/pages/banner/bannerConstants"
import { TableOptionsClass, SearchOptionsClassList } from "@/models/common"
import { getBannerList, updateBannerQuick } from "@/views/pages/banner/bannerPage"
import type { BannerItem } from '@/types/banner';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const BannerDetailDrawer = defineAsyncComponent(() => import("@/views/pages/banner/components/BannerDetailDrawer.vue"))

const activeTab = ref('banner')
const openType = ref("update"); // create or update

const tableOptions = ref<TableOptions<BannerItem>>(new TableOptionsClass({headers: bannerHeaders}))
const searchOptions = ref(new SearchOptionsClassList(bannerSearchOptions))

// 배너 타입별 순서 옵션 목록을 반환하는 함수
const getBannerOrderOptions = (banner_type: string) => {
  const activeBannersOfType = tableOptions.value.items.filter(
    item => item.is_active && item.banner_type === banner_type
  );
  return Array.from({ length: activeBannersOfType.length }, (_, i) => ({ value: i + 1, label: (i + 1).toString() }));
};

// 링크 타겟 라벨 조회
const getLinkTargetLabel = (target: string) => {
  const option = linkTargetOptions.find(opt => opt.value === target);
  return option ? option.label : target;
}

// 배너 생성 drawer open
const handleCreateBanner = () => {
  openType.value = "create";
  tableOptions.value.chooseRow = {};
  tableOptions.value.isDrawerActive = true;
}

// 배너 순서 또는 노출여부 변경
const handleBannerUpdate = async (banner: BannerItem) => {
  await updateBannerQuick(banner, doSearch);
}

// 배너 목록 조회
const doSearch = async () => {
  await getBannerList(searchOptions, tableOptions)
}

// 테이블 row 클릭 시
tableOptions.value.rowClick = (row: BannerItem) => {
  openType.value = "update";
  tableOptions.value.chooseRow = row;
  tableOptions.value.isDrawerActive = true;
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
</style>
