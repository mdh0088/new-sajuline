<template>
  <div class="m-b-10">
    <div class="row m-t-10">
      <div class="d-flex justify-content-between">
        <div class="col-2">
          <div class="text-start"></div>
        </div>
        <div class="col-10">
          <div class="text-end d-flex justify-content-end">
            <div>
              <el-button class="m-r-10" type="primary" :icon="Edit" @click="createProduct">
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
        <el-tab-pane :label="`상품 목록 (${tableOptions.totalCnt || 0})`" name="product"/>
        <CommonList
          v-model:tableOptions="tableOptions"
          :doSearch="doSearch"
        >
          <template v-slot:customSlot-m_product_img="{ data }">
            <el-image
              v-if="data.m_product_img"
              :src="getCdnImageUrl(data.m_product_img)"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px;"
              :preview-src-list="[getCdnImageUrl(data.m_product_img)]"
            />
            <span v-else style="color: #909399;">-</span>
          </template>

          <template v-slot:customSlot-is_active="{ data }">
            <CustomSwitch
              v-model:switchValue="data.is_active"
              :rowValue="data"
              :switchEvent="handleStatusChange"
            />
          </template>
        </CommonList>
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
import { Edit } from '@element-plus/icons-vue'
import { defineAsyncComponent, onMounted, ref } from "vue";
import { mileageProductHeader } from "@/views/pages/mileage/mileage-product/mileageProductConstants"
import { TableOptionsClass } from "@/models/common"
import * as swal from "@/commonUtils/swal";
import { getMileageProductList, updateMileageProductQuick } from "@/views/pages/mileage/mileage-product/mileageProductPage";
import type { MileageProductItem } from "@/types/mileage";

const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const MileageProductDetailDrawer = defineAsyncComponent(() => import("@/views/pages/mileage/mileage-product/components/MileageProductDetailDrawer.vue"))

const openType = ref("update"); // create or update
const activeTab = ref('product')

const tableOptions = ref<TableOptions<MileageProductItem>>(
  new TableOptionsClass({ headers: mileageProductHeader, isPagination: true, isSelectActive: false })
)

// 테이블 row 클릭 시
tableOptions.value.rowClick = (row: MileageProductItem) => {
  openType.value = "update";
  tableOptions.value.chooseRow = row;
  tableOptions.value.isDrawerActive = true;
}

// 상품 생성용 drawer open
const createProduct = () => {
  openType.value = "create";
  tableOptions.value.chooseRow = {};
  tableOptions.value.isDrawerActive = true;
}

// 활성화 상태 변경 처리
const handleStatusChange = async (product: MileageProductItem) => {
  await updateMileageProductQuick(product, doSearch);
}

// CDN 이미지 URL 생성
const getCdnImageUrl = (m_product_img: string): string => {
  if (!m_product_img) return '';
  if (m_product_img.startsWith('http')) return m_product_img;
  const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
  return `${cdnBase}mileage/${m_product_img}`;
}

// 상품 목록 조회
const doSearch = async () => {
  await getMileageProductList(tableOptions)
}

onMounted(async () => {
  await doSearch();
})
</script>
