<template>
  <el-drawer
      v-model="isDrawerActive"
      title="더미 후기 생성"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>
      <!-- 사용자 정보 -->
      <div>
        <div class="m-b-20">
          <h4>사용자 정보</h4>
        </div>

        <el-form
            label-position="left"
            label-width="120px"
            status-icon
        >
          <el-form-item label="사용자 ID" required>
            <el-input
              v-model="formData.user_id"
              placeholder="사용자 ID를 입력하세요"
            />
          </el-form-item>

          <el-form-item label="사용자 닉네임" required>
            <el-input
              v-model="formData.user_nickname"
              placeholder="표시될 닉네임을 입력하세요"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 상담사 선택 -->
      <div>
        <div class="m-b-20">
          <h4>상담사 정보</h4>
        </div>

        <el-form
            label-position="left"
            label-width="120px"
            status-icon
        >
          <el-form-item label="상담사" required>
            <el-select
              v-model="formData.counselor_id"
              placeholder="상담사를 선택하세요"
              filterable
              style="width: 100%"
              :loading="isLoadingCounselors"
            >
              <el-option
                v-for="counselor in counselorList"
                :key="counselor.counselor_id"
                :label="`${counselor.nickname} (${counselor.counselor_id})`"
                :value="counselor.counselor_id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 후기 내용 -->
      <div>
        <div class="m-b-20">
          <h4>후기 내용</h4>
        </div>

        <el-form
            label-position="left"
            label-width="120px"
            status-icon
        >
          <el-form-item label="별점" required>
            <el-rate
                v-model="formData.rating"
                show-score
                text-color="#ff9900"
                score-template="{value}점"
            />
          </el-form-item>

          <el-form-item label="후기 내용">
            <el-input
                :autosize="{ minRows: 5, maxRows: 10 }"
                type="textarea"
                v-model="formData.content"
                placeholder="후기 내용을 입력하세요"
            />
          </el-form-item>

          <el-form-item label="후기 태그">
            <el-checkbox-group v-model="formData.review_tags">
              <el-checkbox
                v-for="tag in REVIEW_TAG_OPTIONS"
                :key="tag.value"
                :label="tag.value"
                :value="tag.value"
              >
                {{ tag.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="상담사 답변">
            <el-input
                :autosize="{ minRows: 5, maxRows: 10 }"
                type="textarea"
                v-model="formData.counselor_reply"
                placeholder="상담사 답변을 입력하세요 (선택)"
            />
          </el-form-item>

          <el-form-item label="노출 여부">
            <el-switch v-model="formData.is_visible"/>
          </el-form-item>

          <el-form-item label="베스트 여부">
            <el-switch v-model="formData.is_best"/>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <div style="float: right">
          <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
          <el-button type="primary" @click="handleSave" :loading="isSaving" :disabled="isSaving">
            {{ isSaving ? '생성 중...' : '생성' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import * as swal from '@/commonUtils/swal';
import {
  createDummyReview,
  getCounselorList
} from '@/views/pages/review/cs-review/csReviewPage';
import { REVIEW_TAG_OPTIONS } from '@/views/pages/review/cs-review/csReviewConstants';

const props = defineProps({
  doSearch: { type: Function, default: null }
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", { default: false });

// 상담사 목록
const counselorList = ref<Array<{ counselor_id: string; nickname: string }>>([]);
const isLoadingCounselors = ref<boolean>(false);

// 폼 데이터
const formData = reactive<{
  user_id: string;
  user_nickname: string;
  counselor_id: string;
  rating: number;
  content: string;
  counselor_reply: string;
  review_tags: string[];
  is_visible: boolean;
  is_best: boolean;
}>({
  user_id: '',
  user_nickname: '',
  counselor_id: '',
  rating: 5,
  content: '',
  counselor_reply: '',
  review_tags: [],
  is_visible: true,
  is_best: false,
});

const isSaving = ref<boolean>(false);

// 상담사 목록 로드
const loadCounselors = async () => {
  isLoadingCounselors.value = true;
  try {
    counselorList.value = await getCounselorList();
  } finally {
    isLoadingCounselors.value = false;
  }
};

// 저장 처리
const handleSave = async () => {
  // 유효성 검사
  if (!formData.user_id.trim()) {
    await swal.swalAlert('사용자 ID를 입력하세요.', 'warning');
    return;
  }
  if (!formData.user_nickname.trim()) {
    await swal.swalAlert('사용자 닉네임을 입력하세요.', 'warning');
    return;
  }
  if (!formData.counselor_id) {
    await swal.swalAlert('상담사를 선택하세요.', 'warning');
    return;
  }
  if (formData.rating < 1 || formData.rating > 5) {
    await swal.swalAlert('별점을 선택하세요.', 'warning');
    return;
  }

  const result = await swal.swalConfirm('더미 후기를 생성하시겠습니까?', 'question');
  if (!result.isConfirmed) return;

  try {
    isSaving.value = true;

    const payload = {
      user_id: formData.user_id.trim(),
      user_nickname: formData.user_nickname.trim(),
      counselor_id: formData.counselor_id,
      rating: formData.rating,
      content: formData.content.trim() || undefined,
      counselor_reply: formData.counselor_reply.trim() || undefined,
      review_tags: formData.review_tags.length > 0 ? JSON.stringify(formData.review_tags) : undefined,
      is_visible: formData.is_visible,
      is_best: formData.is_best,
    };

    const success = await createDummyReview(payload, props.doSearch);

    if (success) {
      isDrawerActive.value = false;
    }
  } finally {
    isSaving.value = false;
  }
};

// Drawer 열릴 때
const openDrawer = async () => {
  // 상담사 목록이 없으면 로드
  if (counselorList.value.length === 0) {
    await loadCounselors();
  }
};

// Drawer 닫힐 때
const closeDrawer = () => {
  // 폼 초기화
  formData.user_id = '';
  formData.user_nickname = '';
  formData.counselor_id = '';
  formData.rating = 5;
  formData.content = '';
  formData.counselor_reply = '';
  formData.review_tags = [];
  formData.is_visible = true;
  formData.is_best = false;
};
</script>

<style scoped>
.m-b-20 {
  margin-bottom: 20px;
}
</style>
