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
            <div>
              <!-- <el-badge :value="tableOptions.selectedItems.length" :max="99" class="item">
                <el-button type="danger" :icon="Delete" @click="deleteInquiries">
                  문의 삭제
                </el-button>
              </el-badge> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <el-card>
      <el-tabs v-model="activeTab" class="demo-tabs" @tab-click="handleTabClick">
        <el-tab-pane :label="`상담사 문의(${counselorTableOptions.totalCnt})`" name="counselor"/>
        <el-tab-pane :label="`1:1 고객센터 문의(${userInquirytableOptions.totalCnt})`" name="user"/>
        <el-tab-pane :label="`1:1 상담사 문의(${usertToCstableOptions.totalCnt})`" name="userToCs"/>

        <template v-if="activeTab == 'counselor'">
          <CommonList
              v-model:tableOptions="counselorTableOptions"
              :doSearch="doSearch"
          >
            <template #reply_status="{ row }">
              <el-tag v-if="row.inquiry?.reply_content" type="success">답변완료</el-tag>
              <el-tag v-else type="warning">대기중</el-tag>
            </template>

            <template #customSlot-counselor_id="{ data }">
              <span class="cursor-link-pointer" @click="chooseRow(data)">
                <template v-if="data.counselor.counselor_id">
                  <el-tooltip
                      class="box-item f-12"
                      effect="dark"
                      :content="data.counselor.counselor_id"
                      placement="top">
                    {{replaceStringToComma(data.counselor.counselor_id.replaceAll('\n',''),40)}}
                  </el-tooltip>
                </template>
              </span>
            </template>

            <template #customSlot-counselor_name="{ data }">
              {{ data.counselor.name }}
            </template>
            <template #customSlot-counselor_nickname="{ data }">
                {{ data.counselor.nickname }}
            </template>

            <template #customSlot-cs_contnet="{ data }">
                <template v-if="data.inquiry.content">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="data.inquiry.content"
                    placement="top">
                  <el-text :class="'w-x'" class="f-12" truncated>
                    {{data.inquiry.content}}
                  </el-text>
                </el-tooltip>
              </template>
            </template>

            <template #customSlot-inquiry_category="{ data }">
                {{ data.inquiry.category }}
            </template>
            <template #customSlot-inquiry_user_title="{ data }">
                {{ data.inquiry.title }}
            </template>
            <template #customSlot-inquiry_created_at="{ data }">
                {{formatDate(data.inquiry.created_at)}}
            </template>
            <template #customSlot-inquiry_reply_content="{ data }">
                <template v-if="data.inquiry.reply_content">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="data.inquiry.reply_content"
                    placement="top">
                  <el-text :class="'w-x'" class="f-12" truncated>
                    {{data.inquiry.reply_content}}
                  </el-text>
                </el-tooltip>
              </template>
            </template>
            <template #customSlot-inquiry_answered_at="{ data }">
                {{formatDate(data.inquiry.answered_at)}}
            </template>
          </CommonList>
        </template>
       
        <template v-else-if="activeTab == 'user'">
          <CommonList
              v-model:tableOptions="userInquirytableOptions"
              :doSearch="doSearch"
            >
              <!-- user to admin -->
              <template #customSlot-user_name="{ data }">
                <span class="cursor-link-pointer" @click="chooseRow(data)">
                <template v-if="data.user.user_id">
                  <el-tooltip
                      class="box-item f-12"
                      effect="dark"
                      :content="data.user.user_id"
                      placement="top">
                    {{replaceStringToComma(data.user.user_id.replaceAll('\n',''),40)}}
                  </el-tooltip>
                </template>
              </span>
            </template>
            <template #customSlot-user_nickname="{ data }">
                {{ data.user.nickname }}
            </template>
            <template #customSlot-inquiry_category="{ data }">
                {{ data.inquiry.category }}
            </template>
            <template #customSlot-inquiry_user_title="{ data }">
              <template v-if="data.inquiry.title">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="data.inquiry.title"
                    placement="top">
                  <el-text :class="'w-x'" class="f-12" truncated>
                    {{data.inquiry.title}}
                  </el-text>
<!--                  {{replaceStringToComma(scope.row[header.value].replaceAll('\n',''),20)}}-->
                </el-tooltip>
              </template>
            </template>

            <template #customSlot-inquiry_user_content="{ data }">
              <template v-if="data.inquiry.content">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="data.inquiry.content"
                    placement="top">
                  <el-text :class="'w-x'" class="f-12" truncated>
                    {{data.inquiry.content}}
                  </el-text>
                </el-tooltip>
              </template>
            </template>

            <template #customSlot-inquiry_created_at="{ data }">
                {{formatDate(data.inquiry.created_at)}}
            </template>
            <template #customSlot-inquiry_reply_content="{ data }">
              <template v-if="data.inquiry.reply_content">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="data.inquiry.reply_content"
                    placement="top">
                  <el-text :class="'w-x'" class="f-12" truncated>
                    {{data.inquiry.reply_content}}
                  </el-text>
<!--                  {{replaceStringToComma(scope.row[header.value].replaceAll('\n',''),20)}}-->
                </el-tooltip>
              </template>
            </template>

            <template #customSlot-inquiry_answered_at="{ data }">
                {{formatDate(data.inquiry.answered_at)}}
            </template>
          </CommonList>
        </template>

        
        <template v-else-if="activeTab == 'userToCs'">
          <CommonList
            v-model:tableOptions="usertToCstableOptions"
            :doSearch="doSearch"
            >
            <template #customSlot-user_id="{ data }">

                <span class="cursor-link-pointer" @click="chooseRow(data)">
                  <template v-if="data.user.user_id">
                    <el-tooltip
                        class="box-item f-12"
                        effect="dark"
                        :content="data.user.user_id"
                        placement="top">
                      {{replaceStringToComma(data.user.user_id.replaceAll('\n',''),40)}}
                    </el-tooltip>
                  </template>
                </span>
              </template>
              <template #customSlot-user_nickname="{ data }">
                  {{ data.user.nickname }}
              </template>

              <template #customSlot-user_content="{ data }">
                <template v-if="data.inquiry.content">
                  <el-tooltip
                      class="box-item f-12"
                      effect="dark"
                      :content="data.inquiry.content"
                      placement="top">
                    <el-text :class="'w-x'" class="f-12" truncated>
                      {{data.inquiry.content}}
                    </el-text>
                  </el-tooltip>
                </template>

              </template>

              <template #customSlot-counselor_id="{ data }">
                  {{ data.counselor.counselor_id }}
              </template>
              <template #customSlot-counselor_name="{ data }">
                  {{ data.counselor.name }}
              </template>
              <template #customSlot-counselor_nickname="{ data }">
                  {{ data.counselor.nickname }}
              </template>
              <template #customSlot-inquiry_reply_content="{ data }">

                  <template v-if="data.inquiry.reply_content">
                  <el-tooltip
                      class="box-item f-12"
                      effect="dark"
                      :content="data.inquiry.reply_content"
                      placement="top">
                    <el-text :class="'w-x'" class="f-12" truncated>
                      {{data.inquiry.reply_content}}
                    </el-text>
                  </el-tooltip>
                </template>
              </template>

              <template #customSlot-inquiry_category="{ data }">
                  {{ data.inquiry.category }}
              </template>
              
              <template #customSlot-inquiry_created_at="{ data }">
                  {{ data.inquiry.created_at }}
                  {{formatDate(data.inquiry.created_at)}}
              </template>

              <template #customSlot-inquiry_answered_at="{ data }">
                  {{formatDate(data.inquiry.answered_at)}}
              </template>
              
            </CommonList>
        </template>
        
      </el-tabs>
    </el-card>
  </div>

  <InquiryDetailDrawer
      v-if="activeTab == 'counselor'"
      v-model:isDrawerActive="counselorTableOptions.isDrawerActive"
      :chooseRow="counselorTableOptions.chooseRow"
      :activeTab="activeTab"
      :doSearch="doSearch"
  />

  <InquiryDetailDrawer
      v-if="activeTab == 'user'"
      v-model:isDrawerActive="userInquirytableOptions.isDrawerActive"
      :chooseRow="userInquirytableOptions.chooseRow"
      :activeTab="activeTab"
      :doSearch="doSearch"
  />

  <InquiryDetailDrawer
      v-if="activeTab == 'userToCs'"
      v-model:isDrawerActive="usertToCstableOptions.isDrawerActive"
      :chooseRow="usertToCstableOptions.chooseRow"
      :activeTab="activeTab"
      :doSearch="doSearch"
  />
</template>

<script lang="ts" setup>
import { Delete } from '@element-plus/icons-vue'
import { defineAsyncComponent, onMounted, ref, watch, nextTick } from "vue";
import {
  counselorInquiryHeaders,
  userInquiryHeaders,
  userToCsHeaders,
  counselorInquirySearchOptions,
  userInquirySearchOptions,
  userToCsSearchOptions
} from "@/views/pages/customer-support/inquiry/inquiryConstants"
import {
  getCounselorInquiryList,
  getUserInquiryList,
  getUserToCsList,
  deleteCounselorInquiry,
  deleteUserInquiry,
  deleteUserToCs
} from "@/views/pages/customer-support/inquiry/inquiryPage"
import { TableOptionsClass, SearchOptionsClassList } from "@/models/common"
import * as swal from "@/commonUtils/swal";
import {replaceStringToComma, numberComma, toPercentage, formatDate} from "@/commonUtils/utils"
import type { TabsPaneContext } from "element-plus";
import type { CounselorInquiryItem, UserInquiryItem, UserToCsInquiryItem } from '@/types/inquiry';

const CommonSearch = defineAsyncComponent(() => import("@/views/common/search/CommonSearch.vue"))
const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
const InquiryDetailDrawer = defineAsyncComponent(() => import("@/views/pages/customer-support/inquiry/components/InquiryDetailDrawer.vue"))

const activeTab = ref<string>('counselor')
const counselorTableOptions = ref<TableOptions<CounselorInquiryItem | UserInquiryItem | UserToCsInquiryItem>>(
  new TableOptionsClass({ headers: counselorInquiryHeaders })
)

const userInquirytableOptions = ref<TableOptions<CounselorInquiryItem | UserInquiryItem | UserToCsInquiryItem>>(
  new TableOptionsClass({ headers: userInquiryHeaders })
)

const usertToCstableOptions = ref<TableOptions<CounselorInquiryItem | UserInquiryItem | UserToCsInquiryItem>>(
  new TableOptionsClass({ headers: userToCsHeaders })
)

const searchOptions = ref(new SearchOptionsClassList(counselorInquirySearchOptions))

// const deleteInquiries = async () => {
//   if (tableOptions.value.selectedItems.length === 0) {
//     await swal.swalAlert('삭제할 문의를 선택해주세요.', 'warning');
//     return;
//   }

//   const result = await swal.swalConfirm('선택한 문의를 삭제하시겠습니까?', 'warning');
//   if (result.isConfirmed) {
//     for (const item of tableOptions.value.selectedItems) {
//       const inquiry_id = item.inquiry?.inquiry_id;
//       if (!inquiry_id) continue;

//       if (activeTab.value === "counselor") {
//         await deleteCounselorInquiry(inquiry_id);
//       } else if (activeTab.value === "user") {
//         await deleteUserInquiry(inquiry_id);
//       } else {
//         await deleteUserToCs(inquiry_id);
//       }
//     }
//     await doSearch();
//   }
// }

const handleTabClick = async (tab: TabsPaneContext, event: Event) => {
  await nextTick();
  await doSearch();
}

const chooseRow = (row:any) => {
  if (activeTab.value === "counselor") {
    counselorTableOptions.value.isDrawerActive = true;
    counselorTableOptions.value.chooseRow = row;
  } else if (activeTab.value === "user") {
    userInquirytableOptions.value.isDrawerActive = true;
    userInquirytableOptions.value.chooseRow = row;
  } else {
    usertToCstableOptions.value.isDrawerActive = true;
    usertToCstableOptions.value.chooseRow = row;
  }
}

const doSearch = async () => {
  if (activeTab.value === "counselor") {
    await getCounselorInquiryList(searchOptions, counselorTableOptions);
  } else if (activeTab.value === "user") {
    await getUserInquiryList(searchOptions, userInquirytableOptions);
  } else {
    await getUserToCsList(searchOptions, usertToCstableOptions);
  }
}

const activeTabEvent = async (tab:string) => {
  activeTab.value = tab;
  if (tab === "counselor") {
    await getCounselorInquiryList(searchOptions, counselorTableOptions);
  } else if (tab === "user") {
    await getUserInquiryList(searchOptions, userInquirytableOptions);
  } else {
    await getUserToCsList(searchOptions, usertToCstableOptions);
  }
}


watch(
    () => activeTab.value,
    (newValue) => {
      if (newValue === 'counselor') {
        searchOptions.value = new SearchOptionsClassList(counselorInquirySearchOptions);
      } else if (newValue === 'user') {
        searchOptions.value = new SearchOptionsClassList(userInquirySearchOptions);
      } else {
        searchOptions.value = new SearchOptionsClassList(userToCsSearchOptions);
      }
    },
    { immediate: true }
);

onMounted(async () => {
  //await doSearch();
  await activeTabEvent("userToCs");
  await activeTabEvent("user");
  await activeTabEvent("counselor");
})
</script>
