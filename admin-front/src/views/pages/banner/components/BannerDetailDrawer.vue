<template>
  <el-drawer
      v-model="isDrawerActive"
      :title="drawerTitle"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>
      <!-- 배너 기본 정보 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>배너 기본 정보</h4>
            </el-col>
            <el-col :span="6" :offset="12" v-if="bannerData && bannerData.created_at">
              <span class="f-12">
                등록일 : {{ formatDate(bannerData.created_at) }}
              </span>
            </el-col>
          </el-row>
        </div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="120px"
            :model="formData"
            :rules="rules"
            status-icon
        >
          <el-form-item label="배너명" prop="banner_name">
            <el-input v-model="formData.banner_name" placeholder="배너명을 입력하세요" />
          </el-form-item>

          <el-form-item label="배너 타입" prop="banner_type">
            <el-select v-model="formData.banner_type" placeholder="배너 타입을 선택하세요" style="width: 100%">
              <el-option
                  v-for="item in bannerTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="노출 순서">
            <el-input-number v-model="formData.display_order" :min="1" :max="999" :disabled="true" />
            <span class="f-12 m-l-10" style="color: #909399;">활성화 시 자동으로 마지막 순서로 배치됩니다</span>
          </el-form-item>

          <el-form-item label="활성 여부">
            <el-switch v-model="formData.is_active" />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 링크 설정 -->
      <div>
        <div class="m-b-20">
          <h4>링크 설정</h4>
        </div>
        <el-form label-position="left" label-width="120px" :model="formData">
          <el-form-item label="링크 URL">
            <el-input v-model="formData.link_url" placeholder="https://example.com" />
          </el-form-item>

          <el-form-item label="링크 타겟">
            <el-select v-model="formData.link_target" placeholder="링크 타겟을 선택하세요" style="width: 100%">
              <el-option
                  v-for="item in linkTargetOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 게시 기간 -->
      <div>
        <div class="m-b-20">
          <h4>게시 기간</h4>
        </div>
        <el-form
            label-position="left"
            label-width="120px"
            :model="formData"
            :rules="rules"
        >
          <el-form-item label="시작일" prop="valid_from">
            <el-date-picker
                v-model="formData.valid_from"
                type="datetime"
                placeholder="시작일을 선택하세요"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="종료일" prop="valid_until">
            <el-date-picker
                v-model="formData.valid_until"
                type="datetime"
                placeholder="종료일을 선택하세요"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 이미지 업로드 -->
      <div>
        <div class="m-b-20">
          <h4>배너 이미지</h4>
        </div>
        <el-form label-position="left" label-width="120px" :model="formData">
          <el-form-item label="이미지 파일">
            <el-upload
                v-model:file-list="attachFile"
                list-type="picture"
                class="upload-demo w-100"
                drag
                :show-file-list="true"
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :limit="1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                이미지를 드래그 하거나 <em>클릭 해주세요.</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  1MB이하의 jpg/png파일만 업로드 가능합니다.
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item v-if="currentImageUrl" label="현재 이미지">
            <el-image
                :src="currentImageUrl"
                fit="contain"
                style="width: 200px; height: 150px"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button v-if="!isCreateMode" type="danger" @click="handleDelete" :disabled="isSaving">
          삭제
        </el-button>
        <div style="float: right">
          <el-button @click="isDrawerActive = false" :disabled="isSaving">취소</el-button>
          <el-button type="primary" @click="handleSave(ruleFormRef)" :loading="isSaving" :disabled="isSaving">
            {{ isSaving ? '저장 중...' : '저장' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref, reactive, computed} from 'vue'
import type {FormInstance, FormRules, UploadUserFile} from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue';
import * as swal from '@/commonUtils/swal';
import {
  getBannerDetail,
  createBanner,
  updateBanner,
  deleteBanner
} from '@/views/pages/banner/bannerPage';
import { linkTargetOptions, bannerTypeOptions } from '@/views/pages/banner/bannerConstants';
import type { BannerItem, BannerCreateRequest, BannerUpdateRequest } from '@/types/banner';

const props = defineProps({
  chooseRow: {Type: Object, default: {}},
  doSearch: {Type: Function, default: null},
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", {default: false});
const openType = defineModel<string>("openType", {default: "update"});

// 백엔드에서 받아온 원본 데이터
const bannerData = ref<BannerItem | null>(null);

// 수정용 폼 데이터
const formData = reactive<Partial<BannerItem>>({
  banner_name: undefined,
  banner_type: undefined,
  link_url: undefined,
  link_target: undefined,
  display_order: undefined,
  is_active: undefined,
  valid_from: undefined,
  valid_until: undefined,
  image_url: undefined
});

const attachFile = ref<UploadUserFile[]>([]);
const currentImageUrl = ref<string>('');
const imageFile = ref<File | null>(null);
const isSaving = ref<boolean>(false);
const ruleFormRef = ref<FormInstance>();

const isCreateMode = computed(() => openType.value === "create");

const drawerTitle = computed(() => {
  return isCreateMode.value ? '배너 추가' : '배너 정보';
});

const rules = reactive<FormRules>({
  banner_name: [{required: true, message: '배너명을 입력해주세요', trigger: 'blur'}],
  banner_type: [{required: true, message: '배너 타입을 선택해주세요', trigger: 'change'}],
  valid_from: [{required: true, message: '시작일을 선택해주세요', trigger: 'change'}],
  valid_until: [{required: true, message: '종료일을 선택해주세요', trigger: 'change'}],
});

const handleFileChange = async (file: any) => {
  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop()?.toLowerCase();

  if (!validExtensions.includes(fileExtension || '')) {
    await swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
    attachFile.value = [];
    return;
  }

  // 파일 크기 체크 (1MB)
  if (file.raw && file.raw.size > 1024 * 1024) {
    await swal.swalAlert('1MB 이하의 이미지만 업로드 가능합니다.', 'warning');
    attachFile.value = [];
    return;
  }

  imageFile.value = file.raw;
};

const handleFileRemove = () => {
  imageFile.value = null;
  attachFile.value = [];
};

const handleSave = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;

  await formEl.validate(async (valid) => {
    if (valid) {
      const result = await swal.swalConfirm('저장하시겠습니까?', 'question');
      if (!result.isConfirmed) return;

      try {
        isSaving.value = true;
        let success = false;

        if (!isCreateMode.value && bannerData.value?.banner_id) {
          // 수정 모드
          const payload: BannerUpdateRequest = {
            banner_id: bannerData.value.banner_id,
            banner_name: formData.banner_name,
            banner_type: formData.banner_type,
            link_url: formData.link_url || undefined,
            link_target: formData.link_target,
            display_order: formData.display_order,
            is_active: formData.is_active,
            valid_from: formData.valid_from,
            valid_until: formData.valid_until,
            image: imageFile.value || undefined
          };
          success = await updateBanner(payload, props.doSearch);
        } else {
          // 생성 모드
          const payload: BannerCreateRequest = {
            banner_name: formData.banner_name!,
            banner_type: formData.banner_type!,
            link_url: formData.link_url,
            link_target: formData.link_target,
            display_order: formData.display_order,
            is_active: formData.is_active,
            valid_from: formData.valid_from!,
            valid_until: formData.valid_until!,
            image: imageFile.value || undefined
          };
          success = await createBanner(payload, props.doSearch);
        }

        if (success) {
          isDrawerActive.value = false;
        }
      } finally {
        isSaving.value = false;
      }
    }
  });
};

const handleDelete = async () => {
  if (!bannerData.value?.banner_id) return;

  const result = await swal.swalConfirm('정말 삭제하시겠습니까?', 'warning');
  if (!result.isConfirmed) return;

  try {
    isSaving.value = true;
    const success = await deleteBanner(bannerData.value.banner_id);
    if (success) {
      await props.doSearch();
      isDrawerActive.value = false;
    }
  } finally {
    isSaving.value = false;
  }
};

// Drawer 열릴 때
const openDrawer = async () => {
  if (isCreateMode.value) {
    // 생성 모드: 폼 데이터 초기화
    bannerData.value = null;
    formData.banner_name = '';
    formData.banner_type = 'MAIN';
    formData.link_url = '';
    formData.link_target = 'SELF';
    formData.display_order = 1;
    formData.is_active = true;
    formData.valid_from = '';
    formData.valid_until = '';
    formData.image_url = '';
    currentImageUrl.value = '';
    attachFile.value = [];
    imageFile.value = null;
    return;
  }

  // 수정 모드: 배너 상세 정보 조회
  const banner_id = props.chooseRow?.banner_id;
  if (!banner_id) return;

  const detail = await getBannerDetail(banner_id, attachFile);

  if (detail) {
    bannerData.value = detail;

    // 폼 데이터 초기화
    formData.banner_name = detail.banner_name;
    formData.banner_type = detail.banner_type;
    formData.link_url = detail.link_url || '';
    formData.link_target = detail.link_target;
    formData.display_order = detail.display_order || 1;
    formData.is_active = detail.is_active;
    formData.valid_from = detail.valid_from;
    formData.valid_until = detail.valid_until;
    formData.image_url = detail.image_url;

    // 이미지 URL 설정 (attachFile에 이미 설정되어 있음)
    if (detail.image_url) {
      const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
      currentImageUrl.value = detail.image_url.startsWith('http')
        ? detail.image_url
        : `${cdnBase}banner/${detail.image_url}`;
    } else {
      currentImageUrl.value = '';
    }

    imageFile.value = null;
  }
};

// Drawer 닫힐 때
const closeDrawer = () => {
  openType.value = "update";
  isDrawerActive.value = false;
  bannerData.value = null;
  attachFile.value = [];
  imageFile.value = null;

  // 폼 데이터 초기화
  Object.keys(formData).forEach(key => {
    formData[key as keyof typeof formData] = undefined;
  });
};

// 날짜 포맷팅
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('ko-KR');
};
</script>

<style scoped>
.m-b-20 {
  margin-bottom: 20px;
}

.m-l-10 {
  margin-left: 10px;
}

.f-12 {
  font-size: 12px;
}

.w-100 {
  width: 100%;
}
</style>
