<template>
  <el-drawer
      v-model="isDrawerActive"
      title="기획전 등록"
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
              <el-switch v-model="isActiveSwitch" />
            </div>
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

          <el-form-item label="기획전 명">
            <el-input v-model="exhibitionInfo.exhibitionNm"></el-input>
          </el-form-item>

          <el-form-item label="설명">
            <el-input
              v-model="exhibitionInfo.description"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 6 }"
              placeholder="기획전 설명을 입력하세요"
            ></el-input>
          </el-form-item>

          <el-form-item label="약관" v-if="exhibitionInfo.terms !== null && exhibitionInfo.terms !== undefined">
            <el-input
              v-model="exhibitionInfo.terms"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 6 }"
              placeholder="약관 내용을 입력하세요"
            ></el-input>
          </el-form-item>

          <el-form-item label="이벤트 타입">
            <el-select v-model="exhibitionInfo.event_type" placeholder="이벤트 타입 선택">
              <el-option label="회원가입" value="SIGNUP"></el-option>
              <el-option label="로그인" value="LOGIN"></el-option>
              <el-option label="상담" value="CONSULTATION"></el-option>
              <el-option label="포인트" value="POINT"></el-option>
              <el-option label="프로모션" value="PROMOTION"></el-option>
              <el-option label="시즌" value="SEASONAL"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="보상 타입">
            <el-select v-model="exhibitionInfo.reward_type" placeholder="보상 타입 선택">
              <el-option label="포인트" value="POINT"></el-option>
              <el-option label="마일리지" value="MILEAGE"></el-option>
              <el-option label="쿠폰" value="COUPON"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="보상 값">
            <el-input-number v-model="exhibitionInfo.reward_value" :min="0"></el-input-number>
          </el-form-item>

          <el-form-item label="최대 참여자수" v-if="exhibitionInfo.max_participants !== null && exhibitionInfo.max_participants !== undefined">
            <el-input-number v-model="exhibitionInfo.max_participants" :min="1"></el-input-number>
          </el-form-item>

          <el-form-item label="표시 타입">
            <el-select v-model="displayType" placeholder="이벤트 표시 타입 선택">
              <el-option label="일반 텍스트" value="text"></el-option>
              <el-option label="랜덤카드" value="random_card"></el-option>
            </el-select>
          </el-form-item>

          <!-- 랜덤카드 설정 (display_type이 random_card일 때만 표시) -->
          <template v-if="displayType === 'random_card'">
            <el-divider>랜덤카드 설정</el-divider>

            <el-form-item label="보상 포인트">
              <el-input
                v-model="randomCardRewards"
                placeholder="예: 5,10,50,100,500,1000,5000,10000"
              >
                <template #prepend>쉼표로 구분</template>
              </el-input>
            </el-form-item>

            <el-form-item label="확률 가중치">
              <el-input
                v-model="randomCardWeights"
                placeholder="예: 30,25,20,15,7,2,0.9,0.1"
              >
                <template #prepend>쉼표로 구분</template>
              </el-input>
            </el-form-item>

            <el-form-item label="최소 상담 시간 (분)">
              <el-input-number v-model="minConsultationMinutes" :min="1"></el-input-number>
            </el-form-item>

            <el-form-item label="기회 유효기간 (일)">
              <el-input-number v-model="chanceExpiryDays" :min="1"></el-input-number>
            </el-form-item>

            <el-form-item label="보상 유효기간 (일)">
              <el-input-number v-model="rewardExpiryDays" :min="1"></el-input-number>
            </el-form-item>
          </template>

          <el-form-item label="기획전 이미지">
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
          <template v-if="exhibitionInfo.replayList.length > 0">
            <el-form-item label="기획전 유저 댓글">
              <el-timeline>
                <el-timeline-item
                    v-for="item in exhibitionInfo.replayList"
                    :key="item.reply_idx"
                    :timestamp="formatDate(item.registDate,'yyyy-MM-dd')" placement="top">
                  <el-card style="width: 700px">
                    <template #header>
                      <div class="card-header">
                        <el-row :gutter="20">
                          <el-col :span="16">
                            <strong>등록자 :</strong>
                            <el-tag class="m-l-5">
                              {{item.userNickName}}
                            </el-tag>
                          </el-col>
                          <el-col :span="3" :offset="5">
                            <el-button type="danger" @click="deleteReply(item)">
                              삭제
                            </el-button>
                          </el-col>
                        </el-row>

                      </div>
                    </template>
                    <el-input
                        :autosize="{ minRows: 10 }"
                        maxlength="200"
                        type="textarea" v-model="item.userCont" :disabled="false"/>
                    <p>{{formatDate(item.registDate,'yyyy-MM-dd HH:mm:ss')}}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-form-item>
          </template>

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
import {ref, defineAsyncComponent, computed } from 'vue'
import {getExhibitionInfo, updateExhibition, createExhibition, deleteExhibitionReply } from "@/views/pages/exhibition/exhibitionPage"
import {formatDate} from "@/commonUtils/dateUtils"
import {ExhibitionClass} from "@/models/exhibition"
import {UploadProps, UploadUserFile} from "element-plus";
import * as swal from "@/commonUtils/swal";

const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const attachFile = ref<UploadUserFile[]>([])
const dateTimeValue = ref<[Date, Date]>([]);

const exhibitionInfo = ref<ExhibitionInfo>(new ExhibitionClass());

const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const isLoading = ref<boolean>(false)

// showYn (Y/N) <-> is_active (boolean) 변환
const isActiveSwitch = computed({
  get: () => exhibitionInfo.value.showYn === 'Y',
  set: (val: boolean) => {
    exhibitionInfo.value.showYn = val ? 'Y' : 'N'
  }
})

// 랜덤카드 설정 관련
const displayType = ref<'text' | 'random_card'>('text')
const randomCardRewards = ref('5,10,50,100,500,1000,5000,10000')
const randomCardWeights = ref('30,25,20,15,7,2,0.9,0.1')
const minConsultationMinutes = ref(15)
const chanceExpiryDays = ref(30)
const rewardExpiryDays = ref(90)

const confirmClick = async () => {
  const msg = '정말 저장하시겠습니까?.';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    exhibitionInfo.value.startDate = dateTimeValue.value[0];
    exhibitionInfo.value.endDate = dateTimeValue.value[1];

    // metadata 구성
    if (displayType.value === 'random_card') {
      exhibitionInfo.value.metadata_json = {
        display_type: 'random_card',
        card_config: {
          rewards: randomCardRewards.value.split(',').map(v => parseInt(v.trim())),
          weights: randomCardWeights.value.split(',').map(v => parseFloat(v.trim())),
          min_consultation_minutes: minConsultationMinutes.value,
          chance_expiry_days: chanceExpiryDays.value,
          reward_expiry_days: rewardExpiryDays.value
        }
      };
    } else {
      exhibitionInfo.value.metadata_json = null;
    }

    isLoading.value = true;
    try {
      if (openType.value == "update") {
        await updateExhibition(exhibitionInfo, attachFile, props.doSearch as Function)
      } else {
        await createExhibition(exhibitionInfo, attachFile, props.doSearch as Function)
      }
    } finally {
      isLoading.value = false;
    }
  }
}

const closeDrawer = () => {
  openType.value = "update"
}

const deleteReply = async (item:ExhibitionReplyInfo) => {
  const msg = '정말 삭제 하시겠습니가?';
  const swalResult = await swal.swalConfirm(msg, 'warning');
  if (swalResult.isConfirmed) {
    await deleteExhibitionReply(item, exhibitionInfo);
  }
}

const openDrawer = async () => {
  exhibitionInfo.value = new ExhibitionClass();
  dateTimeValue.value = [];
  attachFile.value = [];

  if (openType.value == "update") {
    console.log('chk props >>>',props.chooseRow)
    exhibitionInfo.value.exhibition_idx = props.chooseRow.exhibition_idx;
    console.log('chk bannerInfo >>>',exhibitionInfo.value)

    await getExhibitionInfo(exhibitionInfo, attachFile)
    dateTimeValue.value[0] = exhibitionInfo.value.startDate
    dateTimeValue.value[1] = exhibitionInfo.value.endDate

    // metadata 파싱
    if (exhibitionInfo.value.metadata_json) {
      const metadata = exhibitionInfo.value.metadata_json;
      if (metadata.display_type === 'random_card') {
        displayType.value = 'random_card';
        const config = metadata.card_config || {};
        randomCardRewards.value = (config.rewards || []).join(',');
        randomCardWeights.value = (config.weights || []).join(',');
        minConsultationMinutes.value = config.min_consultation_minutes || 15;
        chanceExpiryDays.value = config.chance_expiry_days || 30;
        rewardExpiryDays.value = config.reward_expiry_days || 90;
      } else {
        displayType.value = 'text';
      }
    } else {
      displayType.value = 'text';
    }
  } else {
    // 새로 생성할 때 기본값 설정
    displayType.value = 'text';
    randomCardRewards.value = '5,10,50,100,500,1000,5000,10000';
    randomCardWeights.value = '30,25,20,15,7,2,0.9,0.1';
    minConsultationMinutes.value = 15;
    chanceExpiryDays.value = 30;
    rewardExpiryDays.value = 90;
  }
}

const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  exhibitionInfo.value.bannerImg = "";
  exhibitionInfo.value.fileNm = "";
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
      exhibitionInfo.value.fileNm = name;
      // 중복 이미지 업로드 방지처리
      if (!attachFile.value.some(file => file.name === target.name)) {
        exhibitionInfo.value.bannerImg = "";
        exhibitionInfo.value.fileNm = "";
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
