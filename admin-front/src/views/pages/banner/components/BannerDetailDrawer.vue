<template>
  <el-drawer
      v-model="isDrawerActive"
      title="배너 등록"
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
              <CustomSwitch v-model:switchValue="bannerInfo.showYn"/>
            </div>

            <div class="m-l-10" v-if="bannerInfo.showYn == 'Y'">
              <el-select
                  class="m-r-10"
                  v-model="bannerInfo.ord"
                  placeholder="Select"
                  style="width: 500px"
              >
                <el-option
                    v-for="item in bannerOrdList"
                    :key="item.ord"
                    :label="item.ord+' - '+item.bannerNm"
                    :value="item.ord"
                />
              </el-select>
            </div>


          </el-form-item>

          <el-form-item label="클릭 가능 여부">
            <CustomSwitch v-model:switchValue="bannerInfo.clickable"/>
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
          <el-form-item label="배너명">
            <el-input v-model="bannerInfo.bannerNm"></el-input>
          </el-form-item>
          <el-form-item label="랜딩 URL">
            <el-input v-model="bannerInfo.randingUrl"></el-input>
          </el-form-item>
          <el-form-item label="노출 형태">
            <el-select
                class="m-r-10"
                v-model="bannerInfo.target"
                placeholder="Select"
                style="width: 80px"
            >
              <el-option
                  v-for="item in targetType"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="배너 이미지">

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
                  500kb이하의 jpg/png파일만 업로드 간으합니다.
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item label="배너 설명" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="bannerInfo.description" :disabled="false"/>
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
import {ref, defineAsyncComponent } from 'vue'
const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
import {getBannerInfo, updateBanner, createBanner, getBannerOrderNo } from "@/views/pages/banner/bannerPage"
import {BannerClass} from "@/models/banner"
import {UploadProps, UploadUserFile} from "element-plus";
import * as swal from "@/commonUtils/swal";
import {targetType} from "@/views/pages/banner/bannerContants"

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const attachFile = ref<UploadUserFile[]>([])
const dateTimeValue = ref<[Date, Date]>([]);

const bannerInfo = ref<BannerInfo>(new BannerClass());
const bannerOrdList = ref<Array<BannerInfo>>([]); // 빈 배열로 초기화

const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const isLoading = ref<boolean>(false)

const confirmClick = async () => {
    const msg = '정말 저장하시겠습니까?.';
    const swalResult = await swal.swalConfirm(msg, 'warning');
    if (swalResult.isConfirmed) {
      bannerInfo.value.startDate = dateTimeValue.value[0];
      bannerInfo.value.endDate = dateTimeValue.value[1];

      isLoading.value = true;
      try {
        if (openType.value == "update") {
          await updateBanner(bannerInfo, attachFile, props.doSearch as Function)
        } else {

          await createBanner(bannerInfo, attachFile, props.doSearch as Function)
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
  bannerInfo.value = new BannerClass();
  dateTimeValue.value = [];
  attachFile.value = [];
  // 배너 순번 리스트 조회
  await getBannerOrderNo(bannerOrdList);

  if (openType.value == "update") {
    console.log('chk props >>>',props.chooseRow)
    bannerInfo.value.banner_idx = props.chooseRow.banner_idx;
    console.log('chk bannerInfo >>>',bannerInfo.value)

    await getBannerInfo(bannerInfo, attachFile)
    dateTimeValue.value[0] = bannerInfo.value.startDate
    dateTimeValue.value[1] = bannerInfo.value.endDate
  } else {

    // 생성 drawer라면 신규 추가
    const banner = new BannerClass();
    banner.ord = bannerOrdList.value.length+1
    banner.bannerNm = "신규"
    bannerOrdList.value.push(banner)
  }
}

const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  bannerInfo.value.bannerImg = "";
  bannerInfo.value.fileNm = "";
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
      bannerInfo.value.fileNm = name;
      // 중복 이미지 업로드 방지처리
      if (!attachFile.value.some(file => file.name === target.name)) {
        bannerInfo.value.bannerImg = "";
        bannerInfo.value.fileNm = "";
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
