<template>
  <el-drawer
      v-model="isDrawerActive"
      title="상담사 정보"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div v-if="counselorData">
      <!-- 상태정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상태정보</h4>
        </div>
        <el-form label-position="left" label-width="auto" style="max-width: 600px">
          <el-form-item label="노출여부">
            <CustomSwitch v-model:switchValue="formData.is_show"/>
          </el-form-item>

          <el-form-item label="상태" v-if="counselorData.member">
            <el-radio-group v-model="memberState">
              <el-radio value="1">대기중</el-radio>
              <el-radio value="2">상담중</el-radio>
              <el-radio value="3">부재중</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      <el-divider />

      <!-- 기본정보 섹션 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>기본정보</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{ formatDate(counselorData.counselor.created_at) }}
              </span>
            </el-col>
          </el-row>
        </div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            :model="formData"
            :rules="rules"
            status-icon>
          <el-form-item label="이름" prop="name">
            <el-input v-model="formData.name"/>
          </el-form-item>

          <el-form-item label="닉네임" prop="nickname">
            <el-input v-model="formData.nickname"/>
          </el-form-item>

          <el-form-item label="휴대폰 번호" prop="phone">
            <el-input v-model="formData.phone"/>
          </el-form-item>

          <el-form-item label="비밀번호" prop="password">
            <el-input
                type="password"
                placeholder="비밀번호 입력 (변경시에만)"
                v-model="formData.password"/>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 상세정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상세정보</h4>
        </div>
        <el-form
            label-position="left"
            label-width="auto"
            :model="formData"
            status-icon>
          <el-form-item label="전문분야">
            <el-checkbox-group v-model="specialties">
              <el-checkbox value="TARO">타로</el-checkbox>
              <el-checkbox value="SAJU">사주/운세</el-checkbox>
              <el-checkbox value="YEOKAK">역학</el-checkbox>
              <el-checkbox value="SINJEOM">신점</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="상담사 코드">
            <el-input v-model="formData.counselor_code" :disabled="true"/>
          </el-form-item>

          <el-form-item label="상담사 등급">
            <el-select v-model="formData.grade" placeholder="Select" style="width: 240px">
              <el-option
                  v-for="item in csGradeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="선불금액">
            <el-input-number v-model="formData.after_amount"/>
          </el-form-item>

          <el-form-item label="활동시간(24시)">
            <el-input v-model="formData.work_time" placeholder="예: 09:00-18:00"/>
          </el-form-item>

          <el-form-item label="신규여부">
            <CustomSwitch v-model:switchValue="formData.is_new"/>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 소개정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>소개정보</h4>
        </div>
        <el-form
            label-position="left"
            label-width="auto"
            :model="formData"
            status-icon>
          <el-form-item label="짧은 한줄">
            <el-input v-model="formData.introduction_short"/>
          </el-form-item>

          <el-form-item label="인사말">
            <el-input
                v-model="formData.greeting_message"
                :autosize="{ minRows: 10, maxRows: 100 }"
                type="textarea"
            />
          </el-form-item>

          <el-form-item label="커리어">
            <el-input
                v-model="formData.career_info"
                :autosize="{ minRows: 5, maxRows: 100 }"
                type="textarea"
            />
          </el-form-item>

          <el-form-item label="키워드">
            <div class="flex gap-2">
              <el-tag
                  v-for="tag in keywordList"
                  :key="tag"
                  closable
                  class="m-r-5"
                  :disable-transitions="false"
                  @close="handleClose(tag)"
              >
                {{ tag }}
              </el-tag>
              <el-input
                  v-if="inputVisible"
                  ref="InputRef"
                  v-model="inputValue"
                  class="w-20"
                  size="small"
                  @keyup.enter="handleInputConfirm"
                  @blur="handleInputConfirm"
              />
              <el-button v-else class="button-new-tag" size="small" @click="showInput">
                + 키워드 추가
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="상담사 메인 이미지">
            <el-upload
                v-model:file-list="mainfile"
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
        <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
        <el-button type="primary" @click="confirmClick(ruleFormRef)" :loading="isSaving" :disabled="isSaving">
          {{ isSaving ? '저장 중...' : '저장' }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, reactive, defineAsyncComponent, nextTick, computed, watch} from 'vue'
import type {FormInstance, FormRules, InputInstance, UploadProps, UploadUserFile} from 'element-plus'
import * as swal from '@/commonUtils/swal';
import {getCounselorDetail, updateCounselorInfo, updateCounselorState} from "@/views/pages/counselor/counselorPage"
import {csGradeOptions} from "@/views/pages/counselor/counselorConstants"
import type {
  CounselorFullDetailResponse,
  CounselorDetailUpdate,
  CounselorStateUpdateRequest
} from '@/types/counselor';

const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))

const props = defineProps({
  chooseRow: {Type: Object, default: {}},
  doSearch: {Type: Function, default: null},
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", {default: false});

// 백엔드에서 받아온 원본 데이터
const counselorData = ref<CounselorFullDetailResponse | null>(null);

// 수정용 폼 데이터
const formData = reactive<CounselorDetailUpdate>({
  is_show: undefined,
  name: undefined,
  nickname: undefined,
  phone: undefined,
  password: undefined,
  specialties: undefined,
  counselor_code: undefined,
  grade: undefined,
  after_amount: undefined,
  before_amount: undefined,
  work_time: undefined,
  is_new: undefined,
  introduction_short: undefined,
  greeting_message: undefined,
  career_info: undefined,
  keywords: undefined,
});

// 상담사 상태 (m_state) - member 데이터
const memberState = ref<"1" | "2" | "3">("1");

// 전문분야 체크박스 배열
const specialties = ref<string[]>([]);

// 키워드 관리
const keywordList = computed(() => {
  if (!formData.keywords) return [];
  return formData.keywords.split(',').filter(k => k.trim());
});

const ruleFormRef = ref<FormInstance>()
const inputValue = ref<string>('')
const inputVisible = ref<boolean>(false)
const InputRef = ref<InputInstance>()

const mainfile = ref<UploadUserFile[]>([])
const profileImageFile = ref<File | null>(null);
const isSaving = ref<boolean>(false);

const rules = reactive<FormRules>({
  name: [{required: true, message: '이름을 입력해주세요', trigger: 'blur'}],
  nickname: [{required: true, message: '닉네임을 입력해주세요', trigger: 'blur'}],
  phone: [{required: true, message: '핸드폰 번호를 입력해주세요', trigger: 'blur'}],

  // password: [
  //   {
  //     validator: (rule, value, callback) => {
  //       if (!value) {
  //         // 비밀번호 변경하지 않을 때는 패스
  //         callback();
  //         return;
  //       }

  //       // const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{10,16}$/;
  //       // if (!passwordRegex.test(value)) {
  //       //   callback(new Error('비밀번호는 영문대문자/영문소문자/숫자/특수문자 중 2개 이상 포함하고, 10~16자리여야 합니다.'));
  //       // } else {
  //       //   callback();
  //       // }
  //     },
  //     trigger: 'blur'
  //   }
  // ],
})

// 저장 버튼 클릭
const confirmClick = async (formEl: FormInstance | undefined) => {
  if (!formEl || !counselorData.value) return

  await formEl.validate(async (valid, fields) => {
    if (valid) {
      try {
        isSaving.value = true;

        // formData를 기반으로 payload 구성
        const updatePayload: CounselorDetailUpdate = {
          is_show: formData.is_show,
          name: formData.name,
          nickname: formData.nickname,
          phone: formData.phone,
          counselor_code: formData.counselor_code,
          grade: formData.grade,
          after_amount: formData.after_amount,
          before_amount: formData.before_amount,
          work_time: formData.work_time,
          is_new: formData.is_new,
          introduction_short: formData.introduction_short,
          greeting_message: formData.greeting_message,
          career_info: formData.career_info,
          keywords: formData.keywords,
        };

        // 비밀번호 (입력된 경우에만)
        if (formData.password && formData.password.trim() !== '') {
          updatePayload.password = formData.password;
        }

        // 전문분야 (JSON 문자열로 변환)
        if (specialties.value && specialties.value.length > 0) {
          updatePayload.specialties = JSON.stringify(specialties.value);
        }

        console.log('confirmClick - updatePayload:', updatePayload);

        // 상담사 정보 업데이트
        const updateSuccess = await updateCounselorInfo(
            counselorData.value.counselor.counselor_id,
            updatePayload,
            profileImageFile.value,
            props.doSearch
        );

        // 상담사 상태 업데이트 (member 데이터가 있고 상태가 변경된 경우)
        if (updateSuccess && counselorData.value.member && memberState.value !== counselorData.value.member.m_state) {
          const statePayload: CounselorStateUpdateRequest = {
            counselor_id: counselorData.value.counselor.counselor_id,
            counselor_code: counselorData.value.counselor.counselor_code,
            m_state: memberState.value
          };

          await updateCounselorState(statePayload, props.doSearch);
        }

        if (updateSuccess) {
          isDrawerActive.value = false;
        }
      } finally {
        isSaving.value = false;
      }
    } else {
      console.log('error submit!', fields)
    }
  })
}

// 키워드 관리 함수
const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}

const handleClose = (tag: string) => {
  const keywords = keywordList.value.filter((item) => item !== tag);
  formData.keywords = keywords.join(',');
};

const handleInputConfirm = () => {
  if (inputValue.value) {
    const keywords = keywordList.value;

    if (keywords.includes(inputValue.value)) {
      swal.swalAlert('이미 존재하는 키워드입니다.', 'warning');
    } else {
      keywords.push(inputValue.value);
      formData.keywords = keywords.join(',');
    }
  }
  inputVisible.value = false;
  inputValue.value = '';
};

// 이미지 업로드 관리
const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  mainfile.value = [];
  profileImageFile.value = null;
}

const handlePreview: UploadProps['onPreview'] = async (file) => {
  if (!file.url) {
    await swal.swalAlert('다운로드할 이미지가 없습니다.', 'warning');
    return;
  }

  try {
    // 이미지 다운로드
    const response = await fetch(file.url);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name || 'image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('이미지 다운로드 실패:', error);
    await swal.swalAlert('이미지 다운로드에 실패했습니다.', 'error');
  }
}

const uploadImgs = async (target) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    mainfile.value = [];
    return;
  }

  // 파일 크기 체크 (500KB)
  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    mainfile.value = [];
    return;
  }

  profileImageFile.value = file;
}

// Drawer 열릴 때
const openDrawer = async () => {
  const counselor_id = props.chooseRow.counselor_id;
  if (!counselor_id) {
    swal.swalAlert('상담사 ID가 없습니다.', 'error');
    return;
  }

  // 상담사 상세 정보 조회
  const data = await getCounselorDetail(counselor_id, mainfile);

  if (data) {
    counselorData.value = data;

    // 폼 데이터 초기화
    formData.is_show = data.counselor.is_show;
    formData.name = data.counselor.name;
    formData.nickname = data.counselor.nickname;
    formData.phone = data.counselor.phone;
    formData.counselor_code = data.counselor.counselor_code;
    formData.grade = data.counselor.grade || undefined;
    formData.after_amount = data.counselor.after_amount || undefined;
    formData.before_amount = data.counselor.before_amount || undefined;
    formData.work_time = data.counselor.work_time || undefined;
    formData.is_new = data.counselor.is_new || false;
    formData.introduction_short = data.counselor.introduction_short || undefined;
    formData.greeting_message = data.counselor.greeting_message || undefined;
    formData.career_info = data.counselor.career_info || undefined;
    formData.keywords = data.counselor.keywords || '';

    // 전문분야 파싱
    try {
      if (data.counselor.specialty_types) {
        if (typeof data.counselor.specialty_types === 'string') {
          specialties.value = JSON.parse(data.counselor.specialty_types);
        } else if (Array.isArray(data.counselor.specialty_types)) {
          specialties.value = data.counselor.specialty_types;
        }
      } else {
        specialties.value = [];
      }
    } catch (e) {
      specialties.value = [];
    }

    // 상담사 상태 초기화
    if (data.member && data.member.m_state) {
      memberState.value = data.member.m_state as "1" | "2" | "3";
    }
  }
}

// Drawer 닫힐 때
const closeDrawer = async () => {
  isDrawerActive.value = false;
  mainfile.value = [];
  profileImageFile.value = null;
  counselorData.value = null;

  // 폼 데이터 초기화
  Object.keys(formData).forEach(key => {
    formData[key as keyof CounselorDetailUpdate] = undefined;
  });
  specialties.value = [];
}

// 날짜 포맷팅
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('ko-KR');
}
</script>

<style scoped>
.upload-subfiles .el-upload {
  display: none;
}
</style>
