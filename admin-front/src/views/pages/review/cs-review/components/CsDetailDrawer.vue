<template>
  <el-drawer
      v-model="isDrawerActive"
      title="후기 상세"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div v-if="reviewData">
      <!-- 사용자 후기 정보 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>사용자 후기</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{ formatDate(reviewData.created_at) }}
              </span>
            </el-col>
          </el-row>
        </div>

        <el-form
            label-position="left"
            label-width="120px"
            status-icon
        >
          <el-form-item label="후기 ID">
            <el-input v-model="reviewData.review_id" :disabled="true"/>
          </el-form-item>

          <el-form-item label="세션 ID">
            <el-input v-model="reviewData.session_id" :disabled="true"/>
          </el-form-item>

          <el-form-item label="사용자 ID">
            <el-input v-model="reviewData.user_id" :disabled="true"/>
          </el-form-item>

          <el-form-item label="사용자 닉네임">
            <el-input v-model="reviewData.user_nickname" :disabled="true"/>
          </el-form-item>

          <el-form-item label="별점">
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
                placeholder="후기 내용"
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

          <el-form-item label="베스트 여부">
            <el-switch v-model="reviewData.is_best" :disabled="true"/>
          </el-form-item>

          <el-form-item label="노출 여부">
            <el-switch v-model="reviewData.is_visible" :disabled="true"/>
          </el-form-item>

          <el-form-item label="좋아요 수">
            <el-input-number v-model="reviewData.like_count" :disabled="true" />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 상담사 답변 정보 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>상담사 답변</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12" v-if="reviewData.counselor_replied_at">
                답변일 : {{ formatDate(reviewData.counselor_replied_at) }}
              </span>
              <span class="f-12" v-else style="color: #909399;">
                미답변
              </span>
            </el-col>
          </el-row>
        </div>

        <el-form
            label-position="left"
            label-width="120px"
            status-icon
        >
          <el-form-item label="상담사 ID">
            <el-input v-model="reviewData.counselor_id" :disabled="true"/>
          </el-form-item>

          <el-form-item label="상담사 닉네임">
            <el-input v-model="reviewData.counselor_nickname" :disabled="true"/>
          </el-form-item>

          <el-form-item label="답변 내용">
            <el-input
                :autosize="{ minRows: 5, maxRows: 10 }"
                type="textarea"
                v-model="formData.counselor_reply"
                placeholder="상담사 답변 내용"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 수정 이력 -->
      <div v-if="reviewData.updated_at">
        <div class="m-b-20">
          <h4>수정 이력</h4>
        </div>
        <el-form label-position="left" label-width="120px">
          <el-form-item label="최종 수정일">
            <el-input :value="formatDate(reviewData.updated_at)" :disabled="true"/>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <div style="float: right">
          <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
          <el-button type="primary" @click="handleSave" :loading="isSaving" :disabled="isSaving">
            {{ isSaving ? '저장 중...' : '저장' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import * as swal from '@/commonUtils/swal';
import {
  getReviewDetail,
  updateReview
} from '@/views/pages/review/cs-review/csReviewPage';
import { REVIEW_TAG_OPTIONS } from '@/views/pages/review/cs-review/csReviewConstants';
import type { ConsultationReviewItem } from '@/types/consultation_review';

const props = defineProps({
  chooseRow: { type: Object, default: {} },
  doSearch: { type: Function, default: null }
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", { default: false });
const openType = defineModel<string>("openType", { default: "update" });

// 백엔드에서 받아온 원본 데이터
const reviewData = ref<ConsultationReviewItem | null>(null);

// 수정용 폼 데이터 (수정 가능한 필드만)
const formData = reactive<{
  content: string | null;
  counselor_reply: string | null;
  rating: number;
  review_tags: string[];
}>({
  content: null,
  counselor_reply: null,
  rating: 0,
  review_tags: []
});

const isSaving = ref<boolean>(false);

// 저장 처리
const handleSave = async () => {
  if (!reviewData.value?.review_id) return;

  const result = await swal.swalConfirm('저장하시겠습니까?', 'question');
  if (!result.isConfirmed) return;

  try {
    isSaving.value = true;

    const payload = {
      content: formData.content || undefined,
      counselor_reply: formData.counselor_reply || undefined,
      rating: formData.rating,
      review_tags: formData.review_tags.length > 0 ? JSON.stringify(formData.review_tags) : undefined
    };

    const success = await updateReview(reviewData.value.review_id, payload, props.doSearch);

    if (success) {
      isDrawerActive.value = false;
    }
  } finally {
    isSaving.value = false;
  }
};

// Drawer 열릴 때
const openDrawer = async () => {
  const review_id = props.chooseRow?.review_id;
  if (!review_id) return;

  const detail = await getReviewDetail(review_id);

  if (detail) {
    reviewData.value = detail;

    // 폼 데이터 초기화 (수정 가능한 필드만)
    formData.content = detail.content || '';
    formData.counselor_reply = detail.counselor_reply || '';
    formData.rating = detail.rating || 0;

    // review_tags JSON 문자열을 배열로 파싱
    if (detail.review_tags) {
      try {
        const parsed = JSON.parse(detail.review_tags);
        formData.review_tags = Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        formData.review_tags = [];
      }
    } else {
      formData.review_tags = [];
    }
  }
};

// Drawer 닫힐 때
const closeDrawer = () => {
  openType.value = "update";
  reviewData.value = null;
  formData.content = null;
  formData.counselor_reply = null;
  formData.rating = 0;
  formData.review_tags = [];
};

// 날짜 포맷팅
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};
</script>

<style scoped>
.m-b-20 {
  margin-bottom: 20px;
}

.f-12 {
  font-size: 12px;
}
</style>
