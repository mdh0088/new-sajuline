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
      <!-- 상품 기본 정보 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>상품 기본 정보</h4>
            </el-col>
            <el-col :span="6" :offset="12" v-if="productData && productData.created_at">
              <span class="f-12">
                등록일 : {{ formatDate(productData.created_at) }}
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
          <el-form-item label="상품명" prop="m_product_name">
            <el-input v-model="formData.m_product_name" placeholder="상품명을 입력하세요" />
          </el-form-item>

          <el-form-item label="상품 금액" prop="m_product_value">
            <el-input-number
              v-model="formData.m_product_value"
              :min="0"
              :step="1000"
              :controls="true"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="충전 포인트" prop="charge_point">
            <el-input-number
              v-model="formData.charge_point"
              :min="0"
              :step="100"
              :controls="true"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="노출 순서">
            <el-input-number v-model="formData.ord" :min="0" :max="999" />
            <span class="f-12 m-l-10" style="color: #909399;">순서가 낮을수록 먼저 노출됩니다</span>
          </el-form-item>

          <el-form-item label="활성 여부">
            <el-switch v-model="formData.is_active" />
          </el-form-item>

          <el-form-item label="상품 설명">
            <el-input
                v-model="formData.description"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                maxlength="500"
                show-word-limit
                placeholder="상품 설명을 입력하세요"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 판매 기간 -->
      <div>
        <div class="m-b-20">
          <h4>판매 기간</h4>
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
          <h4>상품 이미지</h4>
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
                  jpg/png 파일만 업로드 가능합니다.
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
import { ref, reactive, computed } from 'vue'
import type { FormInstance, FormRules, UploadUserFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue';
import * as swal from '@/commonUtils/swal';
import {
  getMileageProductDetail,
  createMileageProduct,
  updateMileageProduct,
  deleteMileageProduct
} from '@/views/pages/mileage/mileage-product/mileageProductPage';
import type { MileageProductItem, MileageProductCreateRequest, MileageProductUpdateRequest } from '@/types/mileage';

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: { Type: Function, default: null },
});

const isDrawerActive = defineModel<boolean>("isDrawerActive", { default: false });
const openType = defineModel<string>("openType", { default: "update" });

// 백엔드에서 받아온 원본 데이터
const productData = ref<MileageProductItem | null>(null);

// 수정용 폼 데이터
const formData = reactive<Partial<MileageProductItem>>({
  m_product_name: '',
  m_product_value: 0,
  charge_point: 0,
  valid_from: '',
  valid_until: '',
  ord: 0,
  description: '',
  is_active: true,
});

const attachFile = ref<UploadUserFile[]>([]);
const currentImageUrl = ref<string>('');
const imageFile = ref<File | null>(null);
const isSaving = ref<boolean>(false);
const ruleFormRef = ref<FormInstance>();

const isCreateMode = computed(() => openType.value === "create");

const drawerTitle = computed(() => {
  return isCreateMode.value ? '마일리지 상품 추가' : '마일리지 상품 정보';
});

const rules = reactive<FormRules>({
  m_product_name: [{ required: true, message: '상품명을 입력해주세요', trigger: 'blur' }],
  m_product_value: [{ required: true, message: '상품 금액을 입력해주세요', trigger: 'blur' }],
  charge_point: [{ required: true, message: '충전 포인트를 입력해주세요', trigger: 'blur' }],
  valid_from: [{ required: true, message: '시작일을 선택해주세요', trigger: 'change' }],
  valid_until: [{ required: true, message: '종료일을 선택해주세요', trigger: 'change' }],
});

const handleFileChange = (file: any) => {
  const validExtensions = ['png', 'jpg', 'jpeg'];
  const fileExtension = file.name.split('.').pop()?.toLowerCase();

  if (!validExtensions.includes(fileExtension || '')) {
    swal.swalAlert('이미지 파일만 업로드 가능합니다.', 'warning');
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

      // 생성 모드에서는 이미지 필수
      if (isCreateMode.value && !imageFile.value) {
        await swal.swalAlert('상품 이미지를 업로드해주세요.', 'warning');
        return;
      }

      try {
        isSaving.value = true;
        let success = false;

        if (!isCreateMode.value && productData.value?.mileage_id) {
          // 수정 모드
          const payload: MileageProductUpdateRequest = {
            m_product_name: formData.m_product_name,
            m_product_value: formData.m_product_value,
            charge_point: formData.charge_point,
            valid_from: formData.valid_from,
            valid_until: formData.valid_until,
            ord: formData.ord,
            description: formData.description,
            is_active: formData.is_active,
            image: imageFile.value || undefined
          };
          success = await updateMileageProduct(productData.value.mileage_id, payload, props.doSearch);
        } else {
          // 생성 모드
          const payload: MileageProductCreateRequest = {
            m_product_name: formData.m_product_name!,
            m_product_value: formData.m_product_value!,
            charge_point: formData.charge_point!,
            valid_from: formData.valid_from!,
            valid_until: formData.valid_until!,
            ord: formData.ord,
            description: formData.description,
            is_active: formData.is_active,
            image: imageFile.value!
          };
          success = await createMileageProduct(payload, props.doSearch);
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
  if (!productData.value?.mileage_id) return;

  const result = await swal.swalConfirm('정말 삭제하시겠습니까?', 'warning');
  if (!result.isConfirmed) return;

  try {
    isSaving.value = true;
    const success = await deleteMileageProduct(productData.value.mileage_id);
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
    productData.value = null;
    formData.m_product_name = '';
    formData.m_product_value = 0;
    formData.charge_point = 0;
    formData.valid_from = '';
    formData.valid_until = '';
    formData.ord = 0;
    formData.description = '';
    formData.is_active = true;
    currentImageUrl.value = '';
    attachFile.value = [];
    imageFile.value = null;
    return;
  }

  // 수정 모드: 상품 상세 정보 조회
  const mileage_id = props.chooseRow?.mileage_id;
  if (!mileage_id) return;

  const detail = await getMileageProductDetail(mileage_id, attachFile);

  if (detail) {
    productData.value = detail;

    // 폼 데이터 초기화
    formData.m_product_name = detail.m_product_name;
    formData.m_product_value = detail.m_product_value;
    formData.charge_point = detail.charge_point;
    formData.valid_from = detail.valid_from;
    formData.valid_until = detail.valid_until;
    formData.ord = detail.ord;
    formData.description = detail.description || '';
    formData.is_active = detail.is_active;

    // 이미지 URL 설정
    if (detail.m_product_img) {
      const cdnBase = import.meta.env.VITE_APP_UPLOAD_URL;
      currentImageUrl.value = detail.m_product_img.startsWith('http')
        ? detail.m_product_img
        : `${cdnBase}mileage/${detail.m_product_img}`;
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
  productData.value = null;
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
