<template>
  <el-drawer
      v-model="isDrawerActive"
      :title="isCreateMode ? '등급 추가' : '등급 정보'"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div v-if="gradeData || isCreateMode">
      <!-- 기본정보 섹션 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>기본정보</h4>
            </el-col>
            <el-col :span="6" :offset="12" v-if="!isCreateMode && gradeData">
              <span class="f-12">
                등록일 : {{ formatDate(gradeData.created_at) }}
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
          <el-form-item label="등급 코드" prop="grade_code">
            <el-input
                v-model="formData.grade_code"
                :disabled="!isCreateMode"
                placeholder="예: GOLD, SILVER"/>
          </el-form-item>

          <el-form-item label="등급명" prop="grade_name">
            <el-input v-model="formData.grade_name" placeholder="예: 골드 등급"/>
          </el-form-item>

          <el-form-item label="등급 레벨" prop="grade_level">
            <el-input-number v-model="formData.grade_level" :min="0" :max="100"/>
            <span class="m-l-10 f-12 text-muted">숫자가 높을수록 높은 등급</span>
          </el-form-item>

          <el-form-item label="최소 구매 금액" prop="min_purchase_amount">
            <el-input-number v-model="formData.min_purchase_amount" :min="0" :step="1000"/>
            <span class="m-l-10">원</span>
          </el-form-item>

          <el-form-item label="포인트 적립률" prop="point_earn_rate">
            <el-input-number v-model="formData.point_earn_rate" :min="0" :max="100" :precision="1" :step="0.1"/>
            <span class="m-l-10">%</span>
          </el-form-item>

          <el-form-item label="할인율" prop="discount_rate">
            <el-input-number v-model="formData.discount_rate" :min="0" :max="100" :precision="1" :step="0.1"/>
            <span class="m-l-10">%</span>
          </el-form-item>

          <el-form-item label="활성화 여부" prop="is_active">
            <el-switch v-model="formData.is_active"/>
          </el-form-item>

          <el-form-item label="등급 이미지">
            <el-upload
                v-model:file-list="gradeImageFile"
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

          <el-form-item label="등급 설명">
            <el-input
                v-model="formData.description"
                :autosize="{ minRows: 5, maxRows: 10 }"
                type="textarea"
                placeholder="등급에 대한 설명을 입력하세요"/>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
        <el-button
            type="primary"
            @click="confirmClick(ruleFormRef)"
            :loading="isSaving"
            :disabled="isSaving">
          {{ isSaving ? '저장 중...' : '저장' }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, reactive, computed} from 'vue'
import type {FormInstance, FormRules, UploadProps, UploadUserFile} from 'element-plus'
import * as swal from '@/commonUtils/swal';
import {getGradeDetail, createGrade, updateGrade} from "@/views/pages/grade/gradePage"
import type {GradeItem, GradeCreateRequest, GradeUpdateRequest} from '@/types/grade';

const props = defineProps({
  chooseRow: {Type: Object, default: {}},
  doSearch: {Type: Function, default: null},
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", {default: false});
const openType = defineModel<string>("openType", {default: "update"});

const isCreateMode = computed(() => openType.value === "create");

// 백엔드에서 받아온 원본 데이터
const gradeData = ref<GradeItem | null>(null);

// 수정용 폼 데이터
const formData = reactive<GradeCreateRequest & GradeUpdateRequest>({
  grade_code: '',
  grade_name: '',
  grade_level: 0,
  min_purchase_amount: 0,
  point_earn_rate: 0,
  discount_rate: 0,
  benefits: null,
  description: '',
  is_active: true,
});

const ruleFormRef = ref<FormInstance>()
const gradeImageFile = ref<UploadUserFile[]>([])
const imageFile = ref<File | null>(null);
const isSaving = ref<boolean>(false);

const rules = reactive<FormRules>({
  grade_code: [{required: true, message: '등급 코드를 입력해주세요', trigger: 'blur'}],
  grade_name: [{required: true, message: '등급명을 입력해주세요', trigger: 'blur'}],
  grade_level: [{required: true, message: '등급 레벨을 입력해주세요', trigger: 'blur'}],
  min_purchase_amount: [{required: true, message: '최소 구매 금액을 입력해주세요', trigger: 'blur'}],
  point_earn_rate: [{required: true, message: '포인트 적립률을 입력해주세요', trigger: 'blur'}],
  discount_rate: [{required: true, message: '할인율을 입력해주세요', trigger: 'blur'}],
})

// 저장 버튼 클릭
const confirmClick = async (formEl: FormInstance | undefined) => {
  if (!formEl) return

  await formEl.validate(async (valid, fields) => {
    if (valid) {
      try {
        isSaving.value = true;

        if (isCreateMode.value) {
          // 등급 생성
          const createPayload: GradeCreateRequest = {
            grade_code: formData.grade_code,
            grade_name: formData.grade_name,
            grade_level: formData.grade_level,
            min_purchase_amount: formData.min_purchase_amount,
            point_earn_rate: formData.point_earn_rate,
            discount_rate: formData.discount_rate,
            benefits: formData.benefits,
            description: formData.description || null,
            is_active: formData.is_active,
          };

          const success = await createGrade(
              createPayload,
              imageFile.value,
              props.doSearch
          );

          if (success) {
            isDrawerActive.value = false;
          }
        } else {
          // 등급 수정
          if (!gradeData.value) return;

          const updatePayload: GradeUpdateRequest = {
            grade_code: gradeData.value.grade_code,
            grade_name: formData.grade_name,
            grade_level: formData.grade_level,
            min_purchase_amount: formData.min_purchase_amount,
            point_earn_rate: formData.point_earn_rate,
            discount_rate: formData.discount_rate,
            benefits: formData.benefits,
            description: formData.description,
            is_active: formData.is_active,
          };

          const success = await updateGrade(
              gradeData.value.grade_code,
              updatePayload,
              imageFile.value,
              props.doSearch
          );

          if (success) {
            isDrawerActive.value = false;
          }
        }
      } finally {
        isSaving.value = false;
      }
    } else {
      console.log('error submit!', fields)
    }
  })
}

// 이미지 업로드 관리
const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  gradeImageFile.value = [];
  imageFile.value = null;
}

const handlePreview: UploadProps['onPreview'] = (file) => {
  console.log(file)
}

const uploadImgs = async (target) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    gradeImageFile.value = [];
    return;
  }

  // 파일 크기 체크 (500KB)
  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    gradeImageFile.value = [];
    return;
  }

  imageFile.value = file;
}

// Drawer 열릴 때
const openDrawer = async () => {
  if (isCreateMode.value) {
    // 생성 모드: 폼 데이터 초기화
    formData.grade_code = '';
    formData.grade_name = '';
    formData.grade_level = 0;
    formData.min_purchase_amount = 0;
    formData.point_earn_rate = 0;
    formData.discount_rate = 0;
    formData.benefits = null;
    formData.description = '';
    formData.is_active = true;
    gradeData.value = null;
  } else {
    // 수정 모드: 등급 상세 정보 조회
    const grade_code = props.chooseRow.grade_code;
    if (!grade_code) {
      swal.swalAlert('등급 코드가 없습니다.', 'error');
      return;
    }

    const data = await getGradeDetail(grade_code, gradeImageFile);

    if (data) {
      gradeData.value = data;

      // 폼 데이터 초기화
      formData.grade_code = data.grade_code;
      formData.grade_name = data.grade_name;
      formData.grade_level = data.grade_level;
      formData.min_purchase_amount = data.min_purchase_amount;
      formData.point_earn_rate = data.point_earn_rate;
      formData.discount_rate = data.discount_rate;
      formData.benefits = data.benefits;
      formData.description = data.description || '';
      formData.is_active = data.is_active;
    }
  }
}

// Drawer 닫힐 때
const closeDrawer = async () => {
  isDrawerActive.value = false;
  gradeImageFile.value = [];
  imageFile.value = null;
  gradeData.value = null;

  // 폼 데이터 초기화
  formData.grade_code = '';
  formData.grade_name = '';
  formData.grade_level = 0;
  formData.min_purchase_amount = 0;
  formData.point_earn_rate = 0;
  formData.discount_rate = 0;
  formData.benefits = null;
  formData.description = '';
  formData.is_active = true;
  openType.value = "update";
}

// 날짜 포맷팅
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('ko-KR');
}
</script>
