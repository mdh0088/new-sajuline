<template>
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
                상품 추가
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
        <el-tab-pane :label="`상품 목록`" name="grade"/>

        <CommonList
            v-model:tableOptions="tableOptions"
            :doSearch="doSearch"
        />
      </el-tabs>
    </el-card>
  </div>

  <MileageProductDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      v-model:openType="openType"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />

</template>
<script lang="ts" setup>
import {  Edit, Delete } from '@element-plus/icons-vue'
import {defineAsyncComponent, onMounted, ref} from "vue";
import {mileageProductHeader} from "@/views/pages/mileage/mileage-product/mileageProductConstants"
import {TableOptionsClass, SearchOptionsClass} from "@/models/common"
import * as swal from "@/commonUtils/swal";
import {MileageProductClass} from "@/models/mileage";
import {getMileageProductList} from "@/views/pages/mileage/mileage-product/mileageProductPage";

const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const MileageProductDetailDrawer = defineAsyncComponent(() => import("@/views/pages/mileage/mileage-product/components/MileageProductDetailDrawer.vue"))
const openType = ref("update"); // create or update

const activeTab = ref('')

const tableOptions = ref<TableOptions<MileageProductInfo>>(new TableOptionsClass({headers: mileageProductHeader, isPagination:false, isSelectActive:false}))



// 배너 생성요 drawer open
const createBanner = () => {
  openType.value = "create";
  tableOptions.value.isDrawerActive = true;
}

const attachFile = ref([]);

// 배너 목로 조회
const doSearch = async () => {
  await getMileageProductList(tableOptions)
}

onMounted(async () => {
  await doSearch();
})


</script>
