<template>
  <el-drawer
      v-model="isDrawerActive"
      title="팝업 등록"
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
              <CustomSwitch v-model:switchValue="popupInfo.showYn"/>
            </div>

            <div class="m-l-10" v-if="popupInfo.showYn == 'Y'">
              <el-select
                  class="m-r-10"
                  v-model="popupInfo.ord"
                  placeholder="Select"
                  style="width: 500px"
              >
                <el-option
                    v-for="item in popupOrdList"
                    :key="item.ord"
                    :label="item.ord+' - '+item.popupNm"
                    :value="item.ord"
                />
              </el-select>
            </div>


          </el-form-item>

          <el-form-item label="클릭 가능 여부">
            <CustomSwitch v-model:switchValue="popupInfo.clickable"/>
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
          <el-form-item label="팝업 명">
            <el-input v-model="popupInfo.popupNm"></el-input>
          </el-form-item>
          <el-form-item label="랜딩 URL">
            <el-input v-model="popupInfo.randingUrl"></el-input>
          </el-form-item>
          <el-form-item label="팝업 이미지">

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
                  1MB이하의 jpg/png파일만 업로드 가능합니다.
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item label="팝업 설명" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="popupInfo.description" :disabled="false"/>
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
import {getPopupInfo, updatePopup, createPopup, getPopupOrderNo } from "@/views/pages/popup/popupPage"
import {PopupClass} from "@/models/popup"
import {UploadProps, UploadUserFile} from "element-plus";
import * as swal from "@/commonUtils/swal";

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const attachFile = ref<UploadUserFile[]>([])
const dateTimeValue = ref<[Date, Date]>([]);

const popupInfo = ref<PopupInfo>(new PopupClass());
const popupOrdList = ref<Array<PopupInfo>>([]); // 빈 배열로 초기화

const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const isLoading = ref<boolean>(false)

const confirmClick = async () => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    popupInfo.value.startDate = dateTimeValue.value[0];
    popupInfo.value.endDate = dateTimeValue.value[1];

    isLoading.value = true;
    try {
      if (openType.value == "update") {
        await updatePopup(popupInfo, attachFile, props.doSearch as Function)
      } else {

        await createPopup(popupInfo, attachFile, props.doSearch as Function)
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
  popupInfo.value = new PopupClass();
  dateTimeValue.value = [];
  attachFile.value = [];
  // 팝업 순번 리스트 조회
  await getPopupOrderNo(popupOrdList);

  if (openType.value == "update") {
    console.log('chk props >>>',props.chooseRow)
    popupInfo.value.popup_idx = props.chooseRow.popup_idx;
    console.log('chk popupInfo >>>',popupInfo.value)

    await getPopupInfo(popupInfo, attachFile)
    dateTimeValue.value[0] = popupInfo.value.startDate
    dateTimeValue.value[1] = popupInfo.value.endDate
  } else {

    // 생성 drawer라면 신규 추가
    const popup = new PopupClass();
    popup.ord = popupOrdList.value.length+1
    popup.popupNm = "신규"
    popupOrdList.value.push(popup)
  }
}

const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  popupInfo.value.popupImg = "";
  popupInfo.value.fileNm = "";
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

  // 파일 크기 체크 (1MB)
  if (file.size > 1024 * 1024) {
    await swal.swalAlert('1MB 이하의 이미지만 업로드 가능합니다.', 'warning');
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
      popupInfo.value.fileNm = name;
      // 중복 이미지 업로드 방지처리
      if (!attachFile.value.some(file => file.name === target.name)) {
        popupInfo.value.popupImg = "";
        popupInfo.value.fileNm = "";
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
