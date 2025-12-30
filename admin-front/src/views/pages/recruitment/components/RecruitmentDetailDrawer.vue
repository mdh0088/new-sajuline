<template>
  <el-drawer
      v-model="isDrawerActive"
      title="상담사 신청 상세"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="text-center p-20">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p class="m-t-10">데이터를 불러오는 중...</p>
    </div>

    <!-- 데이터 표시 -->
    <div v-else-if="applicationData">
      <!-- 상태정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상태정보</h4>
        </div>
        <el-form
            ref="statusFormRef"
            label-position="left"
            label-width="auto"
            :model="formData"
            style="max-width: 600px"
            status-icon>
          <el-form-item label="신청 상태" prop="application_status">
            <el-radio-group v-model="formData.application_status">
              <el-radio value="PENDING">대기중</el-radio>
              <el-radio value="APPROVED">승인됨</el-radio>
              <el-radio value="REJECTED">거절됨</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="관리자 메모" prop="admin_note">
            <el-input
                v-model="formData.admin_note"
                type="textarea"
                :rows="4"
                placeholder="관리자 메모를 입력하세요"
            />
          </el-form-item>
        </el-form>
      </div>
      <el-divider />

      <!-- 신청자 기본정보 섹션 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>신청자 기본정보</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                신청일 : {{ formatDate(applicationData?.created_at) }}
              </span>
            </el-col>
          </el-row>
        </div>
        <el-form
            ref="basicFormRef"
            label-position="left"
            label-width="auto"
            :model="formData"
            style="max-width: 600px"
            status-icon>
          <el-form-item label="신청ID">
            <el-input v-model="applicationData.application_id" disabled/>
          </el-form-item>

          <el-form-item label="이름" prop="name">
            <el-input v-model="formData.name" placeholder="이름을 입력하세요"/>
          </el-form-item>

          <el-form-item label="닉네임" prop="nickname">
            <el-input v-model="formData.nickname" placeholder="닉네임을 입력하세요"/>
          </el-form-item>

          <el-form-item label="이메일" prop="email">
            <el-input v-model="formData.email" placeholder="이메일을 입력하세요"/>
          </el-form-item>

          <el-form-item label="휴대폰" prop="phone">
            <el-input v-model="formData.phone" placeholder="휴대폰 번호를 입력하세요"/>
          </el-form-item>

          <el-form-item label="생년월일" prop="birth_date">
            <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="생년월일을 선택하세요"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="성별" prop="gender">
            <el-radio-group v-model="formData.gender">
              <el-radio value="M">남성</el-radio>
              <el-radio value="F">여성</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      <el-divider />

      <!-- 상담사 정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상담사 정보</h4>
        </div>
        <el-form
            ref="counselorFormRef"
            label-position="left"
            label-width="auto"
            :model="formData"
            style="max-width: 600px"
            status-icon>
          <el-form-item label="전문분야" prop="specialty_types">
            <el-checkbox-group v-model="formData.specialty_types">
              <el-checkbox value="TARO">타로</el-checkbox>
              <el-checkbox value="SAJU">사주</el-checkbox>
              <el-checkbox value="FORTUNE">운세</el-checkbox>
              <el-checkbox value="EASY">쉬운상담</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="경력" prop="experience_years">
            <el-input-number v-model="formData.experience_years" :min="0" :max="50" style="width: 150px"/>
            <span class="m-l-5">년</span>
          </el-form-item>

          <el-form-item label="자기소개" prop="introduction">
            <el-input
                v-model="formData.introduction"
                type="textarea"
                :autosize="{ minRows: 5, maxRows: 15 }"
                placeholder="자기소개를 입력하세요"
            />
          </el-form-item>
        </el-form>
      </div>
      <el-divider />

      <!-- 첨부 이미지 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>첨부 이미지</h4>
        </div>
        <el-form label-position="left" label-width="auto" style="max-width: 600px">
          <el-form-item label="대표 이미지">
            <el-upload
                v-model:file-list="selectedImageFile"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="uploadSelectedImage"
                :on-preview="handlePreview"
                :on-remove="handleRemoveSelectedImage"
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

          <el-form-item label="추가 이미지 1">
            <el-upload
                v-model:file-list="uploadImage1File"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="uploadImage1"
                :on-preview="handlePreview"
                :on-remove="handleRemoveImage1"
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

          <el-form-item label="추가 이미지 2">
            <el-upload
                v-model:file-list="uploadImage2File"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="uploadImage2"
                :on-preview="handlePreview"
                :on-remove="handleRemoveImage2"
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

          <el-form-item label="추가 이미지 3">
            <el-upload
                v-model:file-list="uploadImage3File"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="uploadImage3"
                :on-preview="handlePreview"
                :on-remove="handleRemoveImage3"
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
      <el-divider />

      <!-- 검토 정보 섹션 -->
      <div v-if="applicationData?.reviewed_at">
        <div class="m-b-20">
          <h4>검토 정보</h4>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="검토자">
            {{ applicationData?.reviewed_by || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="검토일시">
            {{ formatDate(applicationData?.reviewed_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
        <el-button type="primary" @click="confirmClick" :loading="isSaving" :disabled="isSaving">
          {{ isSaving ? '전환 중...' : '전환' }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, reactive} from 'vue'
import type {FormInstance, FormRules, UploadProps, UploadUserFile} from 'element-plus'
import {Loading, UploadFilled} from '@element-plus/icons-vue'
import * as swal from '@/commonUtils/swal';
import {getCounselorApplicationDetail, updateApplicationStatus, updateApplicationInfo, convertToCounselor} from "@/views/pages/recruitment/recruitmentPage"
import type {CounselorApplicationResponse} from '@/types/counselor_application';

const props = defineProps({
  chooseRow: {Type: Object, default: {}},
  doSearch: {Type: Function, default: null},
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", {default: false});

// 백엔드에서 받아온 원본 데이터
const applicationData = ref<CounselorApplicationResponse | null>(null);

// 수정용 폼 데이터
const formData = reactive({
  application_status: '',
  admin_note: '',
  name: '',
  nickname: '',
  email: '',
  phone: '',
  birth_date: '',
  gender: '',
  specialty_types: [] as string[],
  experience_years: 0,
  introduction: ''
});

// Form ref and loading state
const statusFormRef = ref<FormInstance>()
const basicFormRef = ref<FormInstance>()
const counselorFormRef = ref<FormInstance>()
const isSaving = ref<boolean>(false);
const isLoading = ref<boolean>(false);

// 이미지 업로드 관련
const selectedImageFile = ref<UploadUserFile[]>([])
const uploadImage1File = ref<UploadUserFile[]>([])
const uploadImage2File = ref<UploadUserFile[]>([])
const uploadImage3File = ref<UploadUserFile[]>([])

const selectedImageNewFile = ref<File | null>(null);
const uploadImage1NewFile = ref<File | null>(null);
const uploadImage2NewFile = ref<File | null>(null);
const uploadImage3NewFile = ref<File | null>(null);

/**
 * Drawer 열릴 때 데이터 로드
 */
const openDrawer = async () => {
  if (!props.chooseRow?.application_id) return;

  try {
    isLoading.value = true;
    // 이미지 파일 ref를 API 함수에 전달
    const response = await getCounselorApplicationDetail(
      props.chooseRow.application_id,
      selectedImageFile,
      uploadImage1File,
      uploadImage2File,
      uploadImage3File
    );

    if (response.success && response.data) {
      applicationData.value = response.data;

      // 폼 데이터 초기화
      formData.application_status = response.data.application_status;
      formData.admin_note = response.data.admin_note || '';
      formData.name = response.data.name || '';
      formData.nickname = response.data.nickname || '';
      formData.email = response.data.email || '';
      formData.phone = response.data.phone || '';
      formData.birth_date = response.data.birth_date || '';
      formData.gender = response.data.gender || '';
      formData.experience_years = response.data.experience_years || 0;
      formData.introduction = response.data.introduction || '';

      // 전문분야 파싱
      if (response.data.specialty_types) {
        if (typeof response.data.specialty_types === 'string') {
          try {
            formData.specialty_types = JSON.parse(response.data.specialty_types);
          } catch {
            formData.specialty_types = response.data.specialty_types.split(',').map(s => s.trim()).filter(s => s);
          }
        } else if (Array.isArray(response.data.specialty_types)) {
          formData.specialty_types = response.data.specialty_types;
        }
      } else {
        formData.specialty_types = [];
      }

      // 이미지 파일은 getCounselorApplicationDetail에서 이미 처리됨
    } else {
      await swal.swalAlert(response.message || '신청 정보를 불러오는데 실패했습니다.', 'error');
    }
  } catch (error) {
    console.error('신청 상세 조회 실패:', error);
    await swal.swalAlert('신청 정보를 불러오는데 실패했습니다.', 'error');
  } finally {
    isLoading.value = false;
  }
};

/**
 * Drawer 닫힐 때 데이터 초기화
 */
const closeDrawer = () => {
  applicationData.value = null;
  formData.application_status = '';
  formData.admin_note = '';
  formData.name = '';
  formData.nickname = '';
  formData.email = '';
  formData.phone = '';
  formData.birth_date = '';
  formData.gender = '';
  formData.specialty_types = [];
  formData.experience_years = 0;
  formData.introduction = '';

  // 이미지 파일 초기화
  selectedImageFile.value = [];
  uploadImage1File.value = [];
  uploadImage2File.value = [];
  uploadImage3File.value = [];
  selectedImageNewFile.value = null;
  uploadImage1NewFile.value = null;
  uploadImage2NewFile.value = null;
  uploadImage3NewFile.value = null;

  isLoading.value = false;
  isSaving.value = false;
};

/**
 * 전환 버튼 클릭
 */
const confirmClick = async () => {
  if (!props.chooseRow?.application_id) return;
  if (!applicationData.value) return;

  const result = await swal.swalConfirm('정말 전환 하시겠습니까?', 'question');
  if (!result.isConfirmed) return;

  // counselor_code 입력 받기
  const Swal = (await import('sweetalert2')).default;
  const inputResult = await Swal.fire({
    title: '상담사 코드 입력',
    input: 'text',
    inputLabel: '상담사 코드를 입력하세요',
    inputPlaceholder: '예: CS001',
    showCancelButton: true,
    confirmButtonText: '확인',
    cancelButtonText: '취소',
    inputValidator: (value) => {
      if (!value) {
        return '상담사 코드를 입력해주세요';
      }
      return null;
    }
  });

  if (!inputResult.isConfirmed || !inputResult.value) return;

  try {
    isSaving.value = true;

    // 상담사 전환 API 호출
    const response = await convertToCounselor(
      inputResult.value,
      applicationData.value
    );

    if (response.success) {
      await swal.swalAlert('상담사로 전환되었습니다.', 'success');
      isDrawerActive.value = false;
      if (props.doSearch) {
        props.doSearch();
      }
    } else {
      await swal.swalAlert(response.message || '전환에 실패했습니다.', 'error');
    }
  } catch (error) {
    console.error('전환 실패:', error);
    await swal.swalAlert('전환 중 오류가 발생했습니다.', 'error');
  } finally {
    isSaving.value = false;
  }
};

/**
 * 성별 라벨 반환
 */
const getGenderLabel = (gender: string | undefined) => {
  if (!gender) return '-';

  const genderMap: Record<string, string> = {
    M: '남성',
    F: '여성'
  };
  return genderMap[gender] || '-';
};

/**
 * 전문분야 라벨 반환
 */
const getSpecialtiesLabel = (specialties: string[] | string | undefined) => {
  if (!specialties) return '-';

  // 문자열인 경우 JSON 파싱 시도
  let specialtyArray: string[] = [];

  if (typeof specialties === 'string') {
    try {
      specialtyArray = JSON.parse(specialties);
      if (!Array.isArray(specialtyArray)) {
        specialtyArray = [specialties];
      }
    } catch {
      // JSON 파싱 실패시 쉼표로 분리 시도
      specialtyArray = specialties.split(',').map(s => s.trim()).filter(s => s);
    }
  } else if (Array.isArray(specialties)) {
    specialtyArray = specialties;
  }

  if (specialtyArray.length === 0) return '-';

  const labelMap: Record<string, string> = {
    TARO: '타로',
    SAJU: '사주',
    FORTUNE: '운세',
    EASY: '쉬운상담'
  };

  return specialtyArray.map(s => labelMap[s] || s).join(', ');
};

/**
 * 날짜 포맷팅
 */
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '-';

  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '-';

    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return '-';
  }
};

/**
 * 이미지 업로드 핸들러 - 대표 이미지
 */
const uploadSelectedImage = async (target: any) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    selectedImageFile.value = [];
    return;
  }

  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    selectedImageFile.value = [];
    return;
  }

  selectedImageNewFile.value = file;
};

/**
 * 이미지 업로드 핸들러 - 추가 이미지 1
 */
const uploadImage1 = async (target: any) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    uploadImage1File.value = [];
    return;
  }

  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    uploadImage1File.value = [];
    return;
  }

  uploadImage1NewFile.value = file;
};

/**
 * 이미지 업로드 핸들러 - 추가 이미지 2
 */
const uploadImage2 = async (target: any) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    uploadImage2File.value = [];
    return;
  }

  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    uploadImage2File.value = [];
    return;
  }

  uploadImage2NewFile.value = file;
};

/**
 * 이미지 업로드 핸들러 - 추가 이미지 3
 */
const uploadImage3 = async (target: any) => {
  let file = target.raw;

  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExtension)) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    uploadImage3File.value = [];
    return;
  }

  if (file.size > 500 * 1024) {
    await swal.swalAlert('500KB 이하의 이미지만 업로드 가능합니다.', 'warning');
    uploadImage3File.value = [];
    return;
  }

  uploadImage3NewFile.value = file;
};

/**
 * 이미지 삭제 핸들러
 */
const handleRemoveSelectedImage: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  selectedImageFile.value = [];
  selectedImageNewFile.value = null;
};

const handleRemoveImage1: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  uploadImage1File.value = [];
  uploadImage1NewFile.value = null;
};

const handleRemoveImage2: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  uploadImage2File.value = [];
  uploadImage2NewFile.value = null;
};

const handleRemoveImage3: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  uploadImage3File.value = [];
  uploadImage3NewFile.value = null;
};

/**
 * 이미지 클릭 시 다운로드
 */
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
};
</script>

<style scoped>
.text-center {
  text-align: center;
}

.text-gray {
  color: #909399;
}

.p-20 {
  padding: 20px;
}

.m-t-10 {
  margin-top: 10px;
}

.m-b-10 {
  margin-bottom: 10px;
}

.m-b-20 {
  margin-bottom: 20px;
}

.m-r-5 {
  margin-right: 5px;
}

.f-12 {
  font-size: 12px;
}

.image-label {
  font-weight: 500;
  color: #606266;
}

.m-l-5 {
  margin-left: 5px;
}

.w-100 {
  width: 100%;
}

.upload-demo .el-upload {
  width: 100%;
}
</style>
