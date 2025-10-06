<template>
  <el-dialog
      v-model="isAccountActive"
      @open="openModal"
      @close="cloaseModal"
      title="내 정보 수정"
      width="500">

    <div>
      <el-form :model="form" label-width="auto" style="max-width: 600px">
        <el-form-item label="비밀번호">
          <el-input v-model="form.password" />
        </el-form-item>
        <el-form-item label="전화번호">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="권한">
          {{getUserInfo.auth}}
        </el-form-item>
        <el-form-item label="마지막 로그인">
          {{format(new Date(getUserInfo.lastLogin ), 'yyyy-MM-dd hh:mm:ss')}}
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="cloaseModal">취소</el-button>
        <el-button type="primary" @click="saveManagerInfo">
          저장
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useUserStore } from '@/store/user.js';
import { storeToRefs } from 'pinia';
import { format } from 'date-fns';
import { modifyMnager } from "@/views/modules/header/components/options/managerInfo"

const userStore = useUserStore();
const { getUserInfo } = storeToRefs(userStore);

const isAccountActive = defineModel<boolean>("isAccountActive");

const form = ref({
  password: '',
  phone: '',
})


const openModal = () => {
  form.value.phone = getUserInfo.value.phone;
}


const cloaseModal = () => {
  isAccountActive.value = false;
}

const saveManagerInfo = async () => {
  await modifyMnager(form);
}


watch(form, async newValue => {
  // 숫자만 남기는 정규 표현식
  let numericValue = newValue.phone.replace(/\D/g, '');

  // 최대 11자리로 제한
  const maxLength = 11;
  if (numericValue.length > maxLength) {
    numericValue = numericValue.slice(0, maxLength); // 초과된 부분을 자름
  }

  // 숫자만 포함된 값으로 다시 설정
  form.value.phone = numericValue;
}, {
  deep: true
});
</script>