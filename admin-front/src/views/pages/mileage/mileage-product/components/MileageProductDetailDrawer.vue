<template>
  <el-drawer
      v-model="isDrawerActive"
      title="등급정보"
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>
      <div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>

          <el-form-item label="노출여부">
            <div>
              <CustomSwitch v-model:switchValue="mileageProductInfo.is_use"/>
            </div>
          </el-form-item>

          <el-form-item label="상품 명">
            <el-input v-model="mileageProductInfo.m_product_name"></el-input>
          </el-form-item>

          <el-form-item label="상품 금액">
            <el-input-number v-model="mileageProductInfo.m_product_value"/>
          </el-form-item>

          <el-form-item label="충전 포인트">
            <el-input-number v-model="mileageProductInfo.charge_point"/>
          </el-form-item>

          <el-form-item label="시작일/종료일">
            <el-config-provider :locale="kor">
              <el-date-picker
                  v-model="dateTimeValue"
                  type="datetimerange"
                  range-separator="To"
                  start-placeholder="Start date"
                  end-placeholder="End date"
              />
            </el-config-provider>
          </el-form-item>
          <el-form-item label="상품 설명">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="mileageProductInfo.description" :disabled="false"/>
          </el-form-item>

          <el-form-item label="상품 이미지">
            <el-upload
                v-model:file-list="attachFile"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="uploadImgs"
                :on-preview="handlePreview"
                :on-remove="handleRemove"
                :limit="1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                이미지를 드래그 하거나 <em>클릭 해주세요.</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  500kb이하의 jpg/png파일만 업로드 가능합니다.
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false">취소</el-button>
        <el-button type="primary" :loading="isLoading" @click="confirmClick()">저장</el-button>
      </div>
    </template>
  </el-drawer>



  <!--  -->
</template>
<script lang="ts" setup>
import kor from 'element-plus/dist/locale/ko.mjs';
import {defineAsyncComponent, ref} from 'vue'
import {getMileageProductInfo, updateMileageProduct, createMileageProduct } from "@/views/pages/mileage/mileage-product/mileageProductPage"
import {MileageProductClass} from "@/models/mileage"
import {UploadProps, UploadUserFile} from "element-plus";
import * as swal from "@/commonUtils/swal";
import {targetType} from "@/views/pages/banner/bannerContants"
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const attachFile = ref<UploadUserFile[]>([])
const dateTimeValue = ref<[Date, Date]>([]);

const mileageProductInfo = ref<MileageProductInfo>(new MileageProductClass());

const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const isLoading = ref<boolean>(false)

const confirmClick = async () => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {

    if (!dateTimeValue.value[0]) {
      swal.swalAlert("시작일 / 종료일을 설정해주세요.","warning")
      return
    }

    mileageProductInfo.value.start_dt = dateTimeValue.value[0];
    mileageProductInfo.value.end_dt = dateTimeValue.value[1];

    isLoading.value = true;
    try {
      if (openType.value == "update") {
        await updateMileageProduct(mileageProductInfo, attachFile, props.doSearch as Function)
      } else {

        await createMileageProduct(mileageProductInfo, attachFile, props.doSearch as Function)
      }
    } finally {
      isLoading.value = false;
    }

  }
}

const closeDrawer = () => {
  openType.value = "update"
}

const openDrawer = async () => {
  mileageProductInfo.value = new MileageProductClass();
  attachFile.value = [];

  if (openType.value == "update") {
    console.log('chk props >>>',props.chooseRow)
    mileageProductInfo.value.m_product_idx = props.chooseRow.m_product_idx;
    console.log('chk mileageProductInfo >>>',mileageProductInfo.value)

    await getMileageProductInfo(mileageProductInfo, attachFile)
    dateTimeValue.value[0] = mileageProductInfo.value.start_dt
    dateTimeValue.value[1] = mileageProductInfo.value.end_dt
  } else {

    // 생성 drawer라면 신규 추가
    const mileageProduct = new MileageProductClass();
  }
}

const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  mileageProductInfo.value.m_product_img = "";
  mileageProductInfo.value.file_nm = "";
  attachFile.value = [];
}

const handlePreview: UploadProps['onPreview'] = (file) => {
  console.log(file)
}

const uploadImgs = async (target) => {

  let file = target.raw;  // 'raw' 속성에서 실제 File 객체를 접근
  console.log('chk file .>>',file)
  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    attachFile.value = [];
    return;
  }

  // 이미지 width, height 계산
  const getImageSize = (file) => {
    return new Promise((resolve, reject) => {
      const imageUrl = URL.createObjectURL(file);  // 임시 url 생성
      const img = new Image();
      img.onload = () => {
        resolve({ width: img.width, height: img.height, name: file.name,imageUrl:imageUrl });
        URL.revokeObjectURL(img.src); // width, height 구하고 임시 url 제거
      };
      img.onerror = () => {
        URL.revokeObjectURL(imageUrl);
        reject(new Error("Failed to load image"));
      };
      img.src = imageUrl;
    });
  }

  if (target.raw && target.raw instanceof File) {
    try {
      // 이미지 사이즈를 가져오기 위한 비동기 처리
      const { width, height, imageUrl, name } = await getImageSize(target.raw);
      target.imgWidth = width;
      target.imgHeight = height;
      target.imageUrl = imageUrl;
      mileageProductInfo.value.file_nm = name;
      // 중복 이미지 업로드 방지처리
      if (!attachFile.value.some(file => file.name === target.name)) {
        mileageProductInfo.value.m_product_img = "";
        mileageProductInfo.value.file_nm = "";
        attachFile.value.push(target);
      }

    } catch (error) {
      console.error("Error loading image size:", error);
    }
  } else {
    console.error("No file found in target.raw");
  }
}

</script>
