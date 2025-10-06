<template>
  <div class="m-b-20">
    <CommonSearch v-model:searchOptions="searchOptions" :doSearch="doSearch"/>
  </div>

  <div class="m-b-10">
    <div class="row m-t-10">
      <div class="d-flex justify-content-between">
        <div class="col-2">
          <div class="text-start">
          </div>
        </div>
        <div class="col-10">
          <div class="text-end d-flex justify-content-end">
            <!-- 선택 유저 기능은 필요시 추가 -->
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <CommonList
          v-model:tableOptions="tableOptions"
          :doSearch="doSearch"
      >
        <!-- 보유 포인트 커스텀 슬롯 -->
        <template v-slot:customSlot-u_point="{ data }">
          {{ numberComma(getUserPoint(data)) }}
        </template>
      </CommonList>
    </el-card>
  </div>

  <UserDetailDrawer
      v-model:isDrawerActive="tableOptions.isDrawerActive"
      :chooseRow="tableOptions.chooseRow"
      :doSearch="doSearch"
  />
</template>

<script lang="ts" setup>
import {ref, defineAsyncComponent, onMounted} from "vue"
import {getUsersList} from "@/views/pages/user/userPage"
import {userHeaders, userSearchOptions} from "@/views/pages/user/userConstants"
import {numberComma} from "@/commonUtils/utils";
import type {UserListItemResponse} from '@/types/user';
import type {TableOptions, SearchOptionsList} from '@/types/common';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const UserDetailDrawer = defineAsyncComponent(() => import("@/views/pages/user/components/UserDetailDrawer.vue"))

// 테이블 옵션 초기화
const tableOptions = ref<TableOptions<UserListItemResponse>>({
  headers: userHeaders,
  rowItems: [10, 20, 30, 50],
  currentPage: 1,
  totalCnt: 0,
  rowPage: 10,
  isLoading: false,
  isDrawerActive: false,
  isSelectActive: false,
  isNumberActive: false,
  isPagination: true,
  chooseRow: {},
  selectedItems: [],
  items: []
});

// 검색 옵션 초기화
const searchOptions = ref<SearchOptionsList>({
  optionsList: userSearchOptions
});

// 사용자 포인트 추출 (ars_user_info에서 u_point)
const getUserPoint = (user: UserListItemResponse) => {
  if (!user.ars_user_info) {
    return 0;
  }
  return user.ars_user_info.u_point || 0;
};

// 검색 실행
const doSearch = async () => {
  await getUsersList(searchOptions, tableOptions);
}

// 페이지 로드 시 초기 검색
onMounted(async () => {
  await doSearch();
})
</script>
