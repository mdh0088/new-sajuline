<template>
  <el-drawer
      v-model="isDrawerActive"
      :title="openType === 'create' ? '공지사항 등록' : '공지사항 수정'"
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>
      <div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="120px"
            :model="noticeForm"
            status-icon>

          <el-form-item label="제목" prop="title" required>
            <el-input v-model="noticeForm.title" placeholder="공지사항 제목을 입력하세요"/>
          </el-form-item>

          <el-form-item label="내용" prop="content" required>
            <Editor
                v-model="noticeForm.content"
                api-key="e33t8vsld7z7z11ixrdky8uqoq3xn7njdnvist7r010a953m"
                :init="{
                  plugins: 'lists link image table code help wordcount',
                  height: 400,
                  menubar: true,
                  toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link image | code'
                }"
            />
          </el-form-item>

          <el-form-item label="대상" prop="target_audience">
            <el-select v-model="noticeForm.target_audience" placeholder="대상을 선택하세요">
              <el-option
                  v-for="option in targetAudienceOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="공지 타입" prop="notice_type">
            <el-select v-model="noticeForm.notice_type" placeholder="타입을 선택하세요">
              <el-option
                  v-for="option in noticeTypeOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="중요 공지" prop="is_important">
            <el-switch v-model="noticeForm.is_important"/>
          </el-form-item>

        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false">취소</el-button>
        <el-button type="primary" @click="confirmClick" :loading="isLoading">저장</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import Editor from '@tinymce/tinymce-vue'
import {ref, reactive } from 'vue'
import {getNoticeDetail, createNotice, updateNotice} from "@/views/pages/customer-support/notice/noticePage";
import {targetAudienceOptions, noticeTypeOptions} from "@/views/pages/customer-support/notice/noticeConstants";
import type {NoticeCreateRequest, NoticeUpdateRequest} from '@/types/notice';

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const isLoading = ref<boolean>(false);

const noticeForm = reactive<NoticeCreateRequest & NoticeUpdateRequest>({
  notice_id: 0,
  title: '',
  content: '',
  target_audience: 'ALL',
  notice_type: 'GENERAL',
  is_important: false,
});

const confirmClick = async () => {
  // 필수 필드 검증
  if (!noticeForm.title || !noticeForm.title.trim()) {
    await import('element-plus').then(({ ElMessage }) => {
      ElMessage.warning('제목을 입력해주세요.');
    });
    return;
  }

  if (!noticeForm.content || !noticeForm.content.trim()) {
    await import('element-plus').then(({ ElMessage }) => {
      ElMessage.warning('내용을 입력해주세요.');
    });
    return;
  }

  if (openType.value === "update") {
    // 수정
    const requestData: NoticeUpdateRequest = {
      notice_id: noticeForm.notice_id,
      title: noticeForm.title,
      content: noticeForm.content,
      target_audience: noticeForm.target_audience,
      notice_type: noticeForm.notice_type,
      is_important: noticeForm.is_important,
    };
    const success = await updateNotice(requestData, props.doSearch);
    if (success) {
      isDrawerActive.value = false;
    }
  } else {
    // 등록
    const requestData: NoticeCreateRequest = {
      title: noticeForm.title,
      content: noticeForm.content,
      target_audience: noticeForm.target_audience,
      notice_type: noticeForm.notice_type,
      is_important: noticeForm.is_important,
    };
    const success = await createNotice(requestData, props.doSearch);
    if (success) {
      isDrawerActive.value = false;
    }
  }
}

const closeDrawer = () => {
  openType.value = "update";
  resetForm();
}

const resetForm = () => {
  noticeForm.notice_id = 0;
  noticeForm.title = '';
  noticeForm.content = '';
  noticeForm.target_audience = 'ALL';
  noticeForm.notice_type = 'GENERAL';
  noticeForm.is_important = false;
}

const openDrawer = async () => {
  resetForm();

  if (openType.value === "update") {
    const notice_id = props.chooseRow.notice_id;
    if (notice_id) {
      const result = await getNoticeDetail(notice_id, isLoading);
      if (result && result.notice) {
        noticeForm.notice_id = result.notice.notice_id;
        noticeForm.title = result.notice.title;
        noticeForm.content = result.notice.content || '';
        noticeForm.target_audience = result.notice.target_audience;
        noticeForm.notice_type = result.notice.notice_type;
        noticeForm.is_important = result.notice.is_important;
      }
    }
  }
}

</script>
