<template>
  <el-drawer
      v-model="isDrawerActive"
      title="회원 정보"
      size="50%"
      :close-on-click-modal="!isSaving"
      :close-on-press-escape="!isSaving"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div v-if="userData">
      <!-- 기본정보 섹션 -->
      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="12">
              <h4>기본정보</h4>
            </el-col>
            <el-col :span="12" class="text-end">
              <span class="f-12">
                가입일: {{ formatDate(userData.user.created_at) }}
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
            status-icon>
          <el-form-item label="아이디">
            <el-input v-model="formData.user_id" :disabled="true"/>
          </el-form-item>

          <el-form-item label="닉네임" prop="nickname">
            <el-input v-model="formData.nickname"/>
          </el-form-item>

          <el-form-item label="이메일" prop="email">
            <el-input v-model="formData.email"/>
          </el-form-item>

          <el-form-item label="휴대폰 번호" prop="phone">
            <el-input v-model="formData.phone"/>
          </el-form-item>

          <el-form-item label="비밀번호" prop="password">
            <el-input
                type="password"
                placeholder="비밀번호 변경 (변경 시에만 입력)"
                v-model="formData.password"/>
          </el-form-item>

          <el-form-item label="등급">
            <el-select v-model="formData.grade" placeholder="등급 선택" style="width: 240px">
              <el-option
                  v-for="item in gradeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="생년월일">
            <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="생년월일 선택"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="가입경로">
            <el-input v-model="userData.user.join_type" :disabled="true"/>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 포인트 정보 섹션 -->
      <div>
        <div class="m-b-20">
          <h4>포인트 정보</h4>
        </div>
        <el-form label-position="left" label-width="120px">
          <el-form-item label="보유 포인트">
            <span>{{ numberComma(getTotalPoint()) }} P</span>
          </el-form-item>
        </el-form>

        <div class="m-t-20">
          <el-button type="primary" @click="openPointAdjustModal">포인트 지급/차감</el-button>
          <el-button type="info" @click="openAlarmLogsModal" class="m-l-10">알림톡 로그</el-button>
        </div>
      </div>

      <el-divider />

      <!-- ARS 정보 섹션 (있을 경우에만 표시) -->
      <div v-if="userData.ars_user_info">
        <div class="m-b-20">
          <h4>ARS 연동 정보</h4>
        </div>
        <el-form label-position="left" label-width="120px">
          <el-form-item label="IDX">
            <span>{{ userData.ars_user_info.idx }}</span>
          </el-form-item>
          <el-form-item label="이름">
            <span>{{ userData.ars_user_info.u_kname }}</span>
          </el-form-item>
          <el-form-item label="전화번호">
            <span>{{ userData.ars_user_info.u_tel }}</span>
          </el-form-item>
          <el-form-item label="포인트">
            <span>{{ numberComma(userData.ars_user_info.u_point) }} P</span>
          </el-form-item>
          <el-form-item label="상태">
            <span>{{ userData.ars_user_info.u_state }}</span>
          </el-form-item>
        </el-form>
      </div>

      <!-- 저장 버튼 -->
      <div class="m-t-20 text-end">
        <el-button @click="closeDrawer" :disabled="isSaving">취소</el-button>
        <el-button type="primary" @click="saveUserInfo" :loading="isSaving">저장</el-button>
      </div>
    </div>
  </el-drawer>

  <!-- 포인트 조정 팝업 -->
  <UserPointPopup
      v-model:isPointPopActive="isPointAdjustModalOpen"
      :userData="props.chooseRow"
      :doRefresh="openDrawer"
  />

  <!-- 알림톡 로그 팝업 -->
  <UserKakaoAlarmPopup
      v-model:isAlarmPopActive="isAlarmLogsModalOpen"
      :userData="props.chooseRow"
  />
</template>

<script lang="ts" setup>
import {ref, computed, watch, defineAsyncComponent} from 'vue';
import {getUserDetail, updateUser} from "@/views/pages/user/userPage";
import {gradeOptions, joinTypeOptions} from "@/views/pages/user/userConstants";
import {numberComma} from "@/commonUtils/utils";
import * as swal from '@/commonUtils/swal';
import type {
  UserDetailResponse,
  UserUpdateRequest,
  UserListItemResponse
} from '@/types/user';
import type {FormInstance, FormRules} from 'element-plus';

const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"));
const UserPointPopup = defineAsyncComponent(() => import("@/views/pages/user/components/UserPointPopup.vue"));
const UserKakaoAlarmPopup = defineAsyncComponent(() => import("@/views/pages/user/components/UserKakaoAlarmPopup.vue"));

// Props
const props = defineProps<{
  isDrawerActive: boolean;
  chooseRow: any;
  doSearch?: () => void;
}>();

const emit = defineEmits<{
  'update:isDrawerActive': [value: boolean];
}>();

// Data
const isDrawerActive = computed({
  get: () => props.isDrawerActive,
  set: (value) => emit('update:isDrawerActive', value)
});

const userData = ref<UserDetailResponse | null>(null);
const isSaving = ref(false);
const ruleFormRef = ref<FormInstance>();
const isPointAdjustModalOpen = ref(false);
const isAlarmLogsModalOpen = ref(false);

// Form Data
const formData = ref<UserUpdateRequest>({
  user_id: '',
  nickname: null,
  email: null,
  phone: null,
  password: null,
  grade: null,
  birth_date: null
});


// Validation Rules
const rules: FormRules = {
  nickname: [
    {required: true, message: '닉네임을 입력해주세요', trigger: 'blur'},
    {min: 2, max: 20, message: '닉네임은 2-20자로 입력해주세요', trigger: 'blur'}
  ],
  email: [
    {required: true, message: '이메일을 입력해주세요', trigger: 'blur'},
    {type: 'email', message: '올바른 이메일 형식이 아닙니다', trigger: 'blur'}
  ],
  phone: [
    {required: true, message: '휴대폰 번호를 입력해주세요', trigger: 'blur'},
    {pattern: /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/, message: '올바른 휴대폰 번호 형식이 아닙니다', trigger: 'blur'}
  ]
};

// Methods
const formatDate = (dateStr: string | null) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('ko-KR');
};

const getTotalPoint = () => {
  if (!userData.value?.ars_user_info) {
    return 0;
  }
  return userData.value.ars_user_info.u_point || 0;
};

const openDrawer = async () => {
  if (!props.chooseRow || !props.chooseRow.user_id) {
    swal.swalAlert('사용자 정보를 불러올 수 없습니다.', 'error');
    return;
  }

  const user_id = props.chooseRow.user_id;
  const data = await getUserDetail(user_id);

  if (data) {
    userData.value = data;
    formData.value = {
      user_id: data.user.user_id,
      nickname: data.user.nickname,
      email: data.user.email,
      phone: data.user.phone,
      password: null,
      grade: data.user.grade_code,
      birth_date: data.user.birth_date
    };
  }
};

const closeDrawer = () => {
  isDrawerActive.value = false;
  userData.value = null;
};

const saveUserInfo = async () => {
  if (!ruleFormRef.value) return;

  await ruleFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await swal.swalConfirm('회원 정보를 수정하시겠습니까?', 'question');

      if (result.isConfirmed) {
        isSaving.value = true;

        const success = await updateUser(formData.value, props.doSearch);

        if (success) {
          closeDrawer();
        }

        isSaving.value = false;
      }
    }
  });
};

const openPointAdjustModal = () => {
  isPointAdjustModalOpen.value = true;
};

const openAlarmLogsModal = () => {
  isAlarmLogsModalOpen.value = true;
};

// Watch
watch(() => props.chooseRow, () => {
  if (props.isDrawerActive) {
    openDrawer();
  }
});
</script>

<style scoped>
.f-12 {
  font-size: 12px;
}

.m-l-10 {
  margin-left: 10px;
}
</style>
