<template>
  <el-drawer
      v-model="localIsDrawerActive"
      :title="drawerTitle"
      direction="rtl"
      size="50%"
  >
    <div v-if="inquiryDetail" class="inquiry-detail">
      <!-- 문의자 정보 -->
      <el-card class="m-b-20" shadow="never">
        <template #header>
          <div class="card-header">
            <span>문의자 정보</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item v-if="activeTab === 'counselor'" label="상담사명">
            {{ inquiryDetail.counselor?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'counselor'" label="닉네임">
            {{ inquiryDetail.counselor?.nickname || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'counselor'" label="전화번호">
            {{ inquiryDetail.counselor?.phone || '-' }}
          </el-descriptions-item>

          <el-descriptions-item v-if="activeTab === 'user' || activeTab === 'userToCs'" label="사용자명">
            {{ inquiryDetail.user?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'user' || activeTab === 'userToCs'" label="닉네임">
            {{ inquiryDetail.user?.nickname || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'user' || activeTab === 'userToCs'" label="이메일">
            {{ inquiryDetail.user?.email || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'user' || activeTab === 'userToCs'" label="전화번호">
            {{ inquiryDetail.user?.phone || '-' }}
          </el-descriptions-item>

          <el-descriptions-item v-if="activeTab === 'userToCs' && inquiryDetail.counselor" label="상담사명">
            {{ inquiryDetail.counselor?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="activeTab === 'userToCs' && inquiryDetail.counselor" label="상담사 닉네임">
            {{ inquiryDetail.counselor?.nickname || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 문의 내용 -->
      <el-card class="m-b-20" shadow="never">
        <template #header>
          <div class="card-header">
            <span>문의 내용</span>
          </div>
        </template>
        <el-form :model="inquiryForm" label-width="120px">
          <el-form-item label="카테고리">
            {{ inquiryDetail.inquiry?.category || '-' }}
          </el-form-item>
          <el-form-item v-if="activeTab === 'user'" label="제목">
            <el-input v-model="inquiryForm.title" placeholder="제목을 입력하세요" />
          </el-form-item>
          <el-form-item label="내용">
            <el-input
                v-model="inquiryForm.content"
                type="textarea"
                :rows="6"
                placeholder="내용을 입력하세요"
            />
          </el-form-item>
          <el-form-item label="등록일">
            {{ formatDate(inquiryDetail.inquiry?.created_at) }}
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 답변 내용 -->
      <el-card class="m-b-20" shadow="never">
        <template #header>
          <div class="card-header">
            <span>답변 내용</span>
          </div>
        </template>
        <el-form :model="inquiryForm" label-width="120px">
          <el-form-item label="답변 내용">
            <el-input
                v-model="inquiryForm.reply_content"
                type="textarea"
                :rows="6"
                placeholder="답변 내용을 입력하세요"
            />
          </el-form-item>
          <el-form-item v-if="inquiryDetail.inquiry?.answered_at" label="답변 등록일">
            {{ formatDate(inquiryDetail.inquiry?.answered_at) }}
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 버튼 -->
      <div class="drawer-footer">
        <el-button type="danger" @click="handleDelete">삭제</el-button>
        <div class="button-group-right">
          <el-button @click="handleClose">취소</el-button>
          <el-button type="primary" @click="handleUpdate">저장</el-button>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import * as swal from '@/commonUtils/swal';
import {
  getCounselorInquiryDetail,
  getUserInquiryDetail,
  getUserToCsDetail,
  updateCounselorInquiry,
  updateUserInquiry,
  updateUserToCsInquiry,
  deleteCounselorInquiry,
  deleteUserInquiry,
  deleteUserToCs
} from '@/views/pages/customer-support/inquiry/inquiryPage';
import type { InquiryUpdateRequest } from '@/types/inquiry';

interface Props {
  isDrawerActive: boolean;
  chooseRow: any;
  activeTab: string;
  doSearch: () => void;
}

const props = defineProps<Props>();
const emit = defineEmits(['update:isDrawerActive']);

const localIsDrawerActive = computed({
  get: () => props.isDrawerActive,
  set: (value) => emit('update:isDrawerActive', value)
});

const inquiryDetail = ref<any>(null);
const inquiryForm = ref({
  title: '',
  content: '',
  reply_content: ''
});

const drawerTitle = computed(() => {
  if (props.activeTab === 'counselor') return '상담사 문의 상세';
  if (props.activeTab === 'user') return '1:1 고객센터 문의 상세';
  return '1:1 상담사 문의 상세';
});

const loadInquiryDetail = async () => {
  if (!props.chooseRow?.inquiry?.inquiry_id) return;

  const inquiry_id = props.chooseRow.inquiry.inquiry_id;

  try {
    let detail;
    if (props.activeTab === 'counselor') {
      detail = await getCounselorInquiryDetail(inquiry_id);
    } else if (props.activeTab === 'user') {
      detail = await getUserInquiryDetail(inquiry_id);
    } else {
      detail = await getUserToCsDetail(inquiry_id);
    }

    if (detail) {
      inquiryDetail.value = detail;
      inquiryForm.value.title = detail.inquiry?.title || '';
      inquiryForm.value.content = detail.inquiry?.content || '';
      inquiryForm.value.reply_content = detail.inquiry?.reply_content || '';
    }
  } catch (error) {
    console.error('문의 상세 조회 실패:', error);
  }
};

const handleUpdate = async () => {
  if (!inquiryForm.value.content.trim()) {
    await swal.swalAlert('내용을 입력하세요.', 'warning');
    return;
  }

  // USER_TO_ADMIN인 경우에만 제목 필수 검증
  if (props.activeTab === 'user' && !inquiryForm.value.title.trim()) {
    await swal.swalAlert('제목을 입력하세요.', 'warning');
    return;
  }

  const inquiry_id = inquiryDetail.value?.inquiry?.inquiry_id;
  if (!inquiry_id) return;

  const payload: InquiryUpdateRequest = {
    inquiry_id,
    content: inquiryForm.value.content,
    reply_content: inquiryForm.value.reply_content || undefined
  };

  // USER_TO_ADMIN인 경우에만 제목 추가
  if (props.activeTab === 'user') {
    payload.title = inquiryForm.value.title;
  }

  const result = await swal.swalConfirm('수정 내용을 저장하시겠습니까?', 'question');
  if (!result.isConfirmed) return;

  let success = false;
  if (props.activeTab === 'counselor') {
    success = await updateCounselorInquiry(payload, props.doSearch);
  } else if (props.activeTab === 'user') {
    success = await updateUserInquiry(payload, props.doSearch);
  } else {
    success = await updateUserToCsInquiry(payload, props.doSearch);
  }

  if (success) {
    handleClose();
  }
};

const handleDelete = async () => {
  const inquiry_id = inquiryDetail.value?.inquiry?.inquiry_id;
  if (!inquiry_id) return;

  const result = await swal.swalConfirm('정말 삭제하시겠습니까?', 'warning');
  if (!result.isConfirmed) return;

  let success = false;
  if (props.activeTab === 'counselor') {
    success = await deleteCounselorInquiry(inquiry_id);
  } else if (props.activeTab === 'user') {
    success = await deleteUserInquiry(inquiry_id);
  } else {
    success = await deleteUserToCs(inquiry_id);
  }

  if (success) {
    await props.doSearch();
    handleClose();
  }
};

const handleClose = () => {
  localIsDrawerActive.value = false;
  inquiryDetail.value = null;
  inquiryForm.value.title = '';
  inquiryForm.value.content = '';
  inquiryForm.value.reply_content = '';
};

const formatDate = (dateString: string | null) => {
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

watch(() => props.isDrawerActive, (newValue) => {
  if (newValue) {
    loadInquiryDetail();
  }
});
</script>

<style scoped>
.inquiry-detail {
  padding: 0 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.inquiry-content {
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.drawer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid #eee;
}

.button-group-right {
  display: flex;
  gap: 10px;
}

.m-b-20 {
  margin-bottom: 20px;
}
</style>
