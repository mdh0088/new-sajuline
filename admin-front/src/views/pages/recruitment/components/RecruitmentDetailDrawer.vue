<template>
  <el-drawer
      v-model="isDrawerActive"
      title="상담사 신청 상세"
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div v-if="applicationData">
      <!-- 상태정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상태정보</h4>
        </div>
        <el-form label-position="left" label-width="auto" style="max-width: 600px">
          <el-form-item label="신청 상태">
            <el-radio-group v-model="formData.application_status">
              <el-radio value="PENDING">대기중</el-radio>
              <el-radio value="APPROVED">승인됨</el-radio>
              <el-radio value="REJECTED">거절됨</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="관리자 메모">
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
                신청일 : {{ formatDate(applicationData.created_at) }}
              </span>
            </el-col>
          </el-row>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="신청ID">
            {{ applicationData.application_id }}
          </el-descriptions-item>
          <el-descriptions-item label="이름">
            {{ applicationData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="닉네임">
            {{ applicationData.nickname }}
          </el-descriptions-item>
          <el-descriptions-item label="이메일">
            {{ applicationData.email }}
          </el-descriptions-item>
          <el-descriptions-item label="휴대폰">
            {{ applicationData.phone }}
          </el-descriptions-item>
          <el-descriptions-item label="생년월일">
            {{ applicationData.birth_date || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="성별">
            {{ getGenderLabel(applicationData.gender) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-divider />

      <!-- 상담사 정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>상담사 정보</h4>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="전문분야">
            {{ getSpecialtiesLabel(applicationData.specialty_types) }}
          </el-descriptions-item>
          <el-descriptions-item label="경력">
            {{ applicationData.experience_years }}년
          </el-descriptions-item>
          <el-descriptions-item label="자기소개">
            <div style="white-space: pre-wrap;">{{ applicationData.introduction || '-' }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-divider />

      <!-- 첨부 이미지 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>첨부 이미지</h4>
        </div>
        <el-row :gutter="16">
          <el-col :span="12" v-if="applicationData.selected_image_url">
            <div class="image-item m-b-20">
              <p class="image-label m-b-10">대표 이미지</p>
              <el-image
                  :src="applicationData.selected_image_url"
                  :preview-src-list="[applicationData.selected_image_url]"
                  fit="cover"
                  style="width: 100%; height: 200px; border-radius: 4px;"
              />
            </div>
          </el-col>
          <el-col :span="12" v-if="applicationData.upload_image1_url">
            <div class="image-item m-b-20">
              <p class="image-label m-b-10">추가 이미지 1</p>
              <el-image
                  :src="applicationData.upload_image1_url"
                  :preview-src-list="[applicationData.upload_image1_url]"
                  fit="cover"
                  style="width: 100%; height: 200px; border-radius: 4px;"
              />
            </div>
          </el-col>
          <el-col :span="12" v-if="applicationData.upload_image2_url">
            <div class="image-item m-b-20">
              <p class="image-label m-b-10">추가 이미지 2</p>
              <el-image
                  :src="applicationData.upload_image2_url"
                  :preview-src-list="[applicationData.upload_image2_url]"
                  fit="cover"
                  style="width: 100%; height: 200px; border-radius: 4px;"
              />
            </div>
          </el-col>
          <el-col :span="12" v-if="applicationData.upload_image3_url">
            <div class="image-item m-b-20">
              <p class="image-label m-b-10">추가 이미지 3</p>
              <el-image
                  :src="applicationData.upload_image3_url"
                  :preview-src-list="[applicationData.upload_image3_url]"
                  fit="cover"
                  style="width: 100%; height: 200px; border-radius: 4px;"
              />
            </div>
          </el-col>
        </el-row>
      </div>
      <el-divider />

      <!-- 검토 정보 섹션 -->
      <div v-if="applicationData.reviewed_at">
        <div class="m-b-20">
          <h4>검토 정보</h4>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="검토자">
            {{ applicationData.reviewed_by || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="검토일시">
            {{ formatDate(applicationData.reviewed_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false">취소</el-button>
        <el-button type="primary" @click="confirmClick">저장</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, reactive} from 'vue'
import * as swal from '@/commonUtils/swal';
import {getCounselorApplicationDetail, updateApplicationStatus} from "@/views/pages/recruitment/recruitmentPage"
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
  admin_note: ''
});

/**
 * Drawer 열릴 때 데이터 로드
 */
const openDrawer = async () => {
  if (!props.chooseRow?.application_id) return;

  try {
    const response = await getCounselorApplicationDetail(props.chooseRow.application_id);

    if (response.success && response.data) {
      applicationData.value = response.data;

      // 폼 데이터 초기화
      formData.application_status = response.data.application_status;
      formData.admin_note = response.data.admin_note || '';
    } else {
      swal.swalAlert(response.message || '신청 정보를 불러오는데 실패했습니다.', 'error');
    }
  } catch (error) {
    console.error('신청 상세 조회 실패:', error);
    swal.swalAlert('신청 정보를 불러오는데 실패했습니다.', 'error');
  }
};

/**
 * Drawer 닫힐 때 데이터 초기화
 */
const closeDrawer = () => {
  applicationData.value = null;
  formData.application_status = '';
  formData.admin_note = '';
};

/**
 * 저장 버튼 클릭
 */
const confirmClick = async () => {
  if (!props.chooseRow?.application_id) return;

  const result = await swal.swalConfirm('저장하시겠습니까?', 'question');
  if (result.isConfirmed) {
    const response = await updateApplicationStatus(
        props.chooseRow.application_id,
        formData.application_status,
        formData.admin_note
    );

    if (response.success) {
      swal.swalAlert('저장되었습니다.', 'success');
      isDrawerActive.value = false;
      if (props.doSearch) {
        props.doSearch();
      }
    }
  }
};

/**
 * 성별 라벨 반환
 */
const getGenderLabel = (gender: string) => {
  const genderMap: Record<string, string> = {
    M: '남성',
    F: '여성'
  };
  return genderMap[gender] || gender;
};

/**
 * 전문분야 라벨 반환
 */
const getSpecialtiesLabel = (specialties: string[]) => {
  if (!specialties || specialties.length === 0) return '-';

  const labelMap: Record<string, string> = {
    TARO: '타로',
    SAJU: '사주',
    FORTUNE: '운세',
    EASY: '쉬운상담'
  };

  return specialties.map(s => labelMap[s] || s).join(', ');
};

/**
 * 날짜 포맷팅
 */
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>
