<template>
    <el-drawer
        v-model="isDrawerActive"
        title="상담사 정보"
        size="50%"
        @open="openDrawer"
        @close="closeDrawer"
    >
      <div>
        <template v-if="props.activeTab=='counselor'">
          <div>
            <div class="m-b-20">
              <h4>상태정보</h4>
            </div>
          </div>
          <el-divider />
        </template>
  
        <div>
          <div class="m-b-20">
            <el-row :gutter="20">
              <el-col :span="6">
                <h4>기본정보</h4>
              </el-col>
              <el-col :span="6" :offset="12">
                <span class="f-12">
                  신청일 : {{counselorInfo.recruitDate}}
                </span>
              </el-col>
            </el-row>
  
          </div>
          <el-form
              ref="ruleFormRef"
              label-position="left"
              label-width="auto"
              :model="counselorInfo"
              :rules="rules"
              status-icon>
            <el-form-item label="이름" prop="name">
              <el-input v-model="counselorInfo.name"/>
            </el-form-item>
  
            <el-form-item label="닉네임" prop="nickName">
              <el-input v-model="counselorInfo.nickName"/>
            </el-form-item>
  
            <el-form-item label="이메일" prop="email">
              <el-input v-model="counselorInfo.email"/>
            </el-form-item>
  
            <el-form-item label="휴대폰 번호" prop="phone">
              <el-input v-model="counselorInfo.phone"/>
            </el-form-item>
  
            <el-form-item label="비밀번호" prop="password">
              <el-input
                  class="m-b-10"
                  placeholder="비밀번호 입력"
                  v-model="counselorInfo.password"/>
            </el-form-item>
            <el-form-item label="비밀번호 확인">
              <el-input
                  class="m-b-10"
                  placeholder="비밀번호 확인"
                  v-model="counselorInfo.password"/>
            </el-form-item>
          </el-form>
        </div>
  
        <el-divider />
  
        <div>
          <div class="m-b-20">
            <h4>상세정보</h4>
          </div>
          <el-form
              ref="ruleFormRef"
              label-position="left"
              label-width="auto"
              :model="counselorInfo"
              :rules="rules"
              status-icon>
            <template v-if="props.activeTab!='applicant'">
              <el-form-item label="타입">
                <el-radio-group v-model="counselorInfo.type">
                  <el-radio value="1">타로</el-radio>
                  <el-radio value="2">신점</el-radio>
                  <el-radio value="3">역학</el-radio>
                  <el-radio value="4">사주/운세</el-radio>
                </el-radio-group>
              </el-form-item>
  
              <el-form-item label="상담사 코드">
                <el-input v-model="counselorInfo.code"/>
              </el-form-item>
  
              <el-form-item label="상담사 등급">
                <el-select v-model="counselorInfo.grade" placeholder="Select" style="width: 240px">
                  <el-option
                      v-for="item in csGradeOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                  />
                </el-select>
              </el-form-item>
  
              <el-form-item label="선불금액">
                <el-input-number v-model="counselorInfo.afterAmount"/>
              </el-form-item>
  
              <el-form-item label="활동시간(24시)">
                <el-input v-model="counselorInfo.workTime"/>
              </el-form-item>
  
              <el-form-item label="신규여부">
                <CustomSwitch v-model:switchValue="counselorInfo.newYn"/>
              </el-form-item>
            </template>
            <template v-else>
              <el-form-item label="타입">
                <el-radio-group v-model="counselorInfo.taroYn" :disabled="true">
                  <el-radio value="Y">타로</el-radio>
                </el-radio-group>
                <el-radio-group class="m-l-10" v-model="counselorInfo.fortuneYn" :disabled="true">
                  <el-radio value="Y">신점</el-radio>
                </el-radio-group>
                <el-radio-group class="m-l-10" v-model="counselorInfo.easyYn" :disabled="true">
                  <el-radio value="Y">역학</el-radio>
                </el-radio-group>
                <el-radio-group class="m-l-10" v-model="counselorInfo.luckYn" :disabled="true">
                  <el-radio value="Y">사주/운세</el-radio>
                </el-radio-group>
              </el-form-item>
            </template>
  
  
          </el-form>
        </div>
  
        <el-divider />
  
        <div>
          <div class="m-b-20">
            <h4>소개정보</h4>
          </div>
          <el-form
              ref="ruleFormRef"
              label-position="left"
              label-width="auto"
              :model="counselorInfo"
              :rules="rules"
              status-icon>
            <el-form-item label="짧은 한줄">
              <el-input v-model="counselorInfo.shortInfo"/>
            </el-form-item>
  
            <el-form-item label="공지사항">
              <el-input
                  v-model="counselorInfo.notice"
                  :autosize="{ minRows: 10, maxRows: 100 }"
                  type="textarea"
              />
            </el-form-item>
  
            <el-form-item label="인사말">
              <el-input
                  v-model="counselorInfo.greeting"
                  :autosize="{ minRows: 10, maxRows: 100 }"
                  type="textarea"
              />
            </el-form-item>
  
            <el-form-item label="커리어">
              <el-input
                  v-model="counselorInfo.career"
                  :autosize="{ minRows: 5, maxRows: 100 }"
                  type="textarea"
              />
            </el-form-item>
  
            <el-form-item label="키워드">
              <div class="flex gap-2">
                <el-tag
                    v-for="tag in keyword"
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
  
            <template v-if="props.activeTab!='applicant'">
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
            </template>
  
  
            <template v-else>
              <el-form-item label="확인용 이미지">
                <el-upload
                    v-model:file-list="subfiles"
                    :show-file-list="true"
                    :auto-upload="false"
                    class="upload-subfiles w-100"
                    :on-preview="handlePreview"
                    :on-remove="handleRemove"
                    list-type="picture"
                    multiple
                    drag
                >
                </el-upload>
              </el-form-item>
            </template>
  
          </el-form>
        </div>
  
      </div>
  
      <template #footer>
        <div style="flex: auto">
  
          <template v-if="props.activeTab!='applicant'">
            <el-button @click="isDrawerActive = false">취소</el-button>
            <el-button type="primary" @click="confirmClick(ruleFormRef)">저장</el-button>
          </template>
          <template v-else>
            <el-button @click="isDrawerActive = false">거절</el-button>
            <el-button type="primary" @click="confirmClick(ruleFormRef)">승인</el-button>
          </template>
  
        </div>
      </template>
    </el-drawer>
  </template>
  <script lang="ts" setup>
  import {ref, reactive, defineAsyncComponent, nextTick, computed} from 'vue'
  import type {  FormInstance, FormRules, InputInstance, UploadProps, UploadUserFile } from 'element-plus'
  import * as swal from '@/commonUtils/swal';
  import {getCounselorInfo, modifyCounselorInfo} from "@/views/pages/counselor/counselorPage"
  import {csGradeOptions, csTypeList} from "@/views/pages/counselor/counselorConstants"
  import {CounselorClass} from "@/models/counselor"
  
  const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
  
  const props = defineProps({
    chooseRow: { Type: Object, default: {} },
    doSearch: { Type: Function, default: null },
    activeTab: { Type: String, default: null },
  });
  
  const counselorInfo = reactive<CounselorInfo>(new CounselorClass());
  
  const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
  
  const ruleFormRef = ref<FormInstance>()
  const passwordChk = ref<string>('');
  
  const inputValue = ref<string>('')
  const inputVisible = ref<boolean>(false)
  const InputRef = ref<InputInstance>()
  
  const keyword = computed(()=>counselorInfo.csKeyword.split(','));
  const csTypeYn = ref<string>('');
  
  const mainfile = ref<UploadUserFile[]>([])
  const subfiles = ref<UploadUserFile[]>([])
  
  const rules = reactive<FormRules>({
    name: [{ required: true, message: '이름을 입력해주세요', trigger: 'blur' }],
    nickName: [{ required: true, message: '닉네임을 입력해주세요', trigger: 'blur' }],
    email: [{ required: true, message: '이메일을 입력해주세요', trigger: 'blur' }],
    phone: [{ required: true, message: '핸드폰 번호를 입력해주세요', trigger: 'blur' }],
    password: [
      {
        validator: (rule, value, callback) => {
          const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{10,16}$/;
  
          if (!value) {
            callback(new Error('비밀번호를 입력해주세요'));
          } else if (!passwordRegex.test(value)) {
            callback(new Error('비밀번호는 영문대문자/영문소문자/숫자/특수문자 중 2개 이상 포함하고, 10~16자리여야 합니다.'));
          } else if (value !== passwordChk.value) {
            callback(new Error('비밀번호 확인과 일치하지 않습니다.'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
  })
  
  
  const confirmClick = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
      if (valid) {
        console.log('submit!')
        console.log('chk last info >>',counselorInfo)
  
        if (props.activeTab == 'applicant') {
          counselorInfo.approvalYn = 'Y'
        }
  
        modifyCounselorInfo(counselorInfo, mainfile, subfiles, props.doSearch)
  
      } else {
        console.log('error submit!', fields)
      }
    })
  }
  
  
  
  const showInput = () => {
    inputVisible.value = true
    nextTick(() => {
      InputRef.value!.input!.focus()
    })
  }
  
  const handleClose = (tag: string) => {
    let keywordArray = counselorInfo.csKeyword.split(',');
    keywordArray = keywordArray.filter((item) => item !== tag);
    counselorInfo.csKeyword = keywordArray.join(',');
  };
  
  const handleInputConfirm = () => {
    if (inputValue.value) {
      let keywordArray = counselorInfo.csKeyword.split(',');
  
      if (keywordArray.includes(inputValue.value)) {
        swal.swalAlert('이미 존재하는 키워드입니다.', 'warning');
      } else {
        keywordArray.push(inputValue.value);
  
        counselorInfo.csKeyword = keywordArray.join(',');
      }
    }
    inputVisible.value = false;
    inputValue.value = '';
  };
  
  
  const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
    console.log(uploadFile, uploadFiles)
    counselorInfo.img = "";
    mainfile.value = [];
  }
  
  const handlePreview: UploadProps['onPreview'] = (file) => {
    console.log(file)
  }
  
  const openDrawer = async () => {
    const counselorIdx = props.chooseRow.idx;
    counselorInfo.idx= counselorIdx;
    await getCounselorInfo(counselorInfo, mainfile, subfiles)
  
    csTypeList.forEach(item => {
      if (counselorInfo[item] == 'Y') {
        csTypeYn.value = item;
      }
    })
  }
  
  const closeDrawer = async () => {
    isDrawerActive.value = false;
    mainfile.value = [];
    subfiles.value = [];
  }
  
  const chooseCsType = () => {
    csTypeList.forEach(item => {
      counselorInfo[item] = 'N';
    })
    counselorInfo[csTypeYn.value] = 'Y';
  }
  
  
  const uploadImgs = async (target) => {
  
    let file = target.raw;  // 'raw' 속성에서 실제 File 객체를 접근
    console.log('chk file .>>',file)
    const validExtensions = ['png', 'jpg', 'jpeg'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
  
    if (!validExtensions.includes(fileExtension)) {
      await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
      mainfile.value = [];
      return;
    }
  
    // 이미지 width, height 계산
    const getImageSize = (file) => {
      return new Promise((resolve, reject) => {
        const imageUrl = URL.createObjectURL(file);  // 임시 url 생성
        const img = new Image();
        img.onload = () => {
          resolve({ width: img.width, height: img.height, imageUrl:imageUrl });
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
        const { width, height, imageUrl } = await getImageSize(target.raw);
        target.imgWidth = width;
        target.imgHeight = height;
        target.imageUrl = imageUrl;
  
        // 중복 이미지 업로드 방지처리
        if (!mainfile.value.some(file => file.name === target.name)) {
          counselorInfo.img = "";
          mainfile.value.push(target);
        }
  
      } catch (error) {
        console.error("Error loading image size:", error);
      }
    } else {
      console.error("No file found in target.raw");
    }
  }
  </script>
  <style>
  .upload-subfiles .el-upload {
    display: none;
  }
  </style>
  