<template>
  <el-dialog
      v-model="isPopActive"
      title="등급별 유저 목록"
      width="1000"
      @open="openPopup"
      :before-close="handleClose"
  >
    <div v-if="isLoading" class="text-center p-20">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p class="m-t-10">로딩 중...</p>
    </div>

    <div v-else-if="usersData">
      <div class="m-b-10">
        <el-input
            v-model="search"
            placeholder="아이디, 이메일, 닉네임, 휴대폰 번호로 검색"
            clearable
        />
      </div>

      <el-scrollbar :max-height="'500px'">
        <el-table :data="filteredUsers" stripe border>
          <el-table-column prop="user_id" label="아이디" width="150"/>
          <el-table-column prop="email" label="이메일" width="200"/>
          <el-table-column prop="nickname" label="닉네임" width="120"/>
          <el-table-column prop="phone" label="휴대폰 번호" width="150"/>
          <el-table-column prop="join_type" label="가입 유형" width="100"/>
          <el-table-column prop="created_at" label="등록일" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-scrollbar>
    </div>

    <div v-else class="text-center p-20">
      <p>유저 정보를 불러올 수 없습니다.</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="isPopActive = false">닫기</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import {ref, computed} from "vue"
import {getUsersByGrade} from "@/views/pages/grade/gradePage"
import type {UsersByGradeResponse} from '@/types/grade';
import {Loading} from '@element-plus/icons-vue'

const isPopActive = defineModel<boolean>("isPopActive", {default: false});

const props = defineProps({
  targetGradeCode: {Type: String, default: ''},
});

const usersData = ref<UsersByGradeResponse | null>(null);
const isLoading = ref<boolean>(false);
const search = ref('');

const filteredUsers = computed(() => {
  if (!usersData.value || !usersData.value.users) return [];

  return usersData.value.users.filter(
    (user) =>
      !search.value ||
      user.user_id?.toLowerCase().includes(search.value.toLowerCase()) ||
      user.email?.toLowerCase().includes(search.value.toLowerCase()) ||
      user.nickname?.toLowerCase().includes(search.value.toLowerCase()) ||
      user.phone?.includes(search.value)
  );
});

const handleClose = () => {
  isPopActive.value = false;
  usersData.value = null;
  search.value = '';
}

// 팝업 열릴 때 등급별 유저 조회
const openPopup = async () => {
  if (!props.targetGradeCode) {
    return;
  }

  isLoading.value = true;
  try {
    const data = await getUsersByGrade(props.targetGradeCode);
    if (data) {
      usersData.value = data;
    }
  } finally {
    isLoading.value = false;
  }
}

// 날짜 포맷팅
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>
  