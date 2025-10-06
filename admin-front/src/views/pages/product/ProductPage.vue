<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <div class="row m-t-10">
          <div class="d-flex justify-content-between">
            <div class="col-2">
              <div class="text-start">
                <span>결제정보</span>
              </div>
            </div>
            <div class="col-10">
              <div class="text-end d-flex justify-content-end">
                <el-button :icon="Edit" :loading="isLoading" type="primary" @click="saveProducts">
                  저장
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    <el-skeleton :count="2" :loading="isLoading" animated >
      <template #default>

        <VueDraggableNext
            :list="productList"
            ghost-class="ghost"
            chosen-class="chosenClass"
            :sort="true"
            v-bind="dragOptions"
            @change="tempChange">

          <el-form class="cursor-pointer" :inline="false" label-width="auto" v-for="(element, index) in productList" :key="element.product_id || `new-${index}`">
            <el-row class="cursor-pointer">
              <el-form-item :label="(index+1)+'번'" :label-position="'top'" >
                <el-icon class="m-5 f-20 cursor-pointer"><Grid/></el-icon>
              </el-form-item>
              <el-form-item class="m-r-10" label="상품명" :label-position="'top'">
                <el-input  v-model="element.product_name" />
              </el-form-item>
              <el-form-item class="m-r-10" label="정상가" :label-position="'top'">
                <el-input-number :controls="false" v-model="element.price" />
              </el-form-item>
              <el-form-item class="m-r-10" label="할인" :label-position="'top'">
                <el-input-number :controls="false" v-model="element.discount_rate"/>%
              </el-form-item>
              <el-form-item class="m-r-10" label="할인가" :label-position="'top'">
                <el-input :disabled="true" :value="getDiscountValue(element.price, element.discount_rate)" />
              </el-form-item>
              <el-form-item class="m-r-10" label="적립" :label-position="'top'">
                <el-input-number :controls="false" v-model="element.bonus_point"/>%
              </el-form-item>
              <el-form-item class="m-r-10" label="충전포인트" :label-position="'top'">
                <el-input :disabled="true" :value="getSaveValue(element.price, element.bonus_point)"  />
              </el-form-item>
              <el-form-item class="m-r-10" label="이벤트기간" :label-position="'top'">
                <el-config-provider :locale="kor">
                  <el-date-picker
                      v-model="getRange(element).value"
                      type="datetimerange"
                      range-separator="To"
                      start-placeholder="Start date"
                      end-placeholder="End date"
                  />
                </el-config-provider>
              </el-form-item>
              <el-form-item class="m-r-10"  label="활성화" :label-position="'top'">
                <CustomSwitch v-model:switchValue="element.is_active"/>
              </el-form-item>
              <el-form-item label="삭제" :label-position="'top'">
                <el-icon class="f-20 cursor-pointer" @click="deleteProduct(element, index)"><Delete /></el-icon>
              </el-form-item>
            </el-row>
          </el-form>
        </VueDraggableNext>
        <el-row :gutter="20">
          <el-col :span="4" :offset="10">
            <el-button type="primary" :loading="isLoading" :icon="Plus" style="width: 300px" @click="addProduct">
              상품추가
            </el-button>
          </el-col>
        </el-row>
      </template>
    </el-skeleton>
  </el-card>

</template>
<script lang="ts" setup>
import kor from 'element-plus/dist/locale/ko.mjs';
import { VueDraggableNext } from 'vue-draggable-next'
import {defineAsyncComponent, ref, computed, onMounted} from "vue";
import {getProductList, createProduct, updateProduct, deleteProductById} from "@/views/pages/product/productPage"
import type { PointProductItem } from '@/types/product';
import {Plus, Edit } from '@element-plus/icons-vue'
import * as swal from '@/commonUtils/swal';
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))

const isLoading = ref<boolean>(false);
const productList = ref<PointProductItem[]>([]);

const tempChange = (target) => {
  console.log('chk target >>>',target);
}

const dragOptions = computed(() => ({
  animation: 0,
  group: 'description',
  disabled: false,
  ghostClass: 'ghost'
}))

// 상품 추가
const addProduct = ()=> {
  if (isLoading.value){
    swal.swalAlert("작업 처리중입니다.", "warning");
    return false;
  }

  // 새 상품 객체 생성 (임시 ID는 0, 백엔드에서 자동 생성)
  const newProduct: any = {
    product_id: 0,
    product_code: '',
    product_name: '',
    point_amount: 0,
    price: 0,
    bonus_point: 0,
    discount_rate: 0,
    display_order: productList.value.length,
    is_active: false,
    valid_from: null,
    valid_until: null,
    created_at: '',
    updated_at: null,
  };

  productList.value.push(newProduct);
}

// 이벤트 기간 배열 반환 함수
const getRange = (element) => {
  return computed({
    get: () => {
      if (element.valid_from && element.valid_until) {
        return [new Date(element.valid_from), new Date(element.valid_until)];
      }
      return null;
    },
    set: (newRange) => {
      if (newRange && Array.isArray(newRange)) {
        element.valid_from = newRange[0]?.toISOString() || null;
        element.valid_until = newRange[1]?.toISOString() || null;
      } else {
        element.valid_from = null;
        element.valid_until = null;
      }
    },
  });
};

// 할인가 계산
const getDiscountValue = (price: number, discountRate: number) => {
  if (discountRate <= 0 || price <= 0) {
    return price;
  }

  return Math.round(price * (1 - discountRate / 100));
}

// 충전 포인트 계산
const getSaveValue = (price: number, bonusPoint: number) => {
  if (bonusPoint <= 0 && price <= 0) {
    return 0;
  } else if (price > 0 && bonusPoint <= 0) {
    return price;
  } else {
    const rate = bonusPoint / 100;
    return Math.round((price * rate) + price);
  }
}

// 저장: 모든 상품 일괄 저장 (생성/수정 API 반복 호출)
const saveProducts = async () => {
  // 검증
  const isAllValid = productList.value.every(productItem => {
    if (!productItem.product_name) {
      swal.swalAlert("상품명은 필수 입니다", "warning");
      return false;
    }
    if (!productItem.price || productItem.price <= 0) {
      swal.swalAlert("정상가를 입력해주세요", "warning");
      return false;
    }
    return true;
  });

  if (!isAllValid) {
    return;
  }

  isLoading.value = true;

  try {
    for (const [index, productItem] of productList.value.entries()) {
      // display_order 업데이트 (드래그앤드롭 순서 반영)
      productItem.display_order = index;

      if (productItem.product_id === 0 || !productItem.product_id) {
        // 신규 상품 생성
        const createPayload = {
          product_name: productItem.product_name,
          point_amount: productItem.point_amount || 0,
          price: productItem.price,
          bonus_point: productItem.bonus_point || 0,
          discount_rate: productItem.discount_rate || 0,
          display_order: productItem.display_order,
          is_active: productItem.is_active,
          valid_from: productItem.valid_from || null,
          valid_until: productItem.valid_until || null,
        };

        await createProduct(createPayload, isLoading);
      } else {
        // 기존 상품 수정
        const updatePayload = {
          product_id: productItem.product_id,
          product_name: productItem.product_name,
          point_amount: productItem.point_amount,
          price: productItem.price,
          bonus_point: productItem.bonus_point,
          discount_rate: productItem.discount_rate,
          display_order: productItem.display_order,
          is_active: productItem.is_active,
          valid_from: productItem.valid_from,
          valid_until: productItem.valid_until,
        };

        await updateProduct(updatePayload, isLoading);
      }
    }

    // 저장 완료 후 목록 다시 조회
    await getProductList(productList, isLoading);
    swal.swalAlert('저장되었습니다.', 'success');
  } catch (error) {
    console.error('저장 실패:', error);
    swal.swalAlert('저장에 실패했습니다.', 'error');
  } finally {
    isLoading.value = false;
  }
};

// 상품 삭제
const deleteProduct = async (element: PointProductItem, index: number) => {
  // 신규 상품 (아직 저장 안된 것)은 목록에서만 제거
  if (element.product_id === 0 || !element.product_id) {
    productList.value.splice(index, 1);
    return;
  }

  // 기존 상품은 비활성화 확인 후 API 호출
  const msg = '정말 삭제하시겠습니까?';
  const swalResult = await swal.swalConfirm(msg, 'warning');

  if (swalResult.isConfirmed) {
    const success = await deleteProductById(element.product_id, isLoading);
    if (success) {
      await getProductList(productList, isLoading);
      swal.swalAlert('삭제되었습니다.', 'success');
    }
  }
}

onMounted(async () => {
  await getProductList(productList, isLoading)
})
</script>
<style>
.ghost {
  border: dashed 1px rgb(19, 41, 239) !important;
}

.chosenClass {
  opacity: 1;
  border: solid 1px red;
}

.fallbackClass {
  background-color: aquamarine;
}

</style>
