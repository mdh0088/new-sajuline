<template>
    <el-dialog
        v-model="isMileageUsagePopActive"
        title="마일리지 적립 내역"
        width="1200"
        @open="getUserPointHist"
        :before-close="handleClose"
    >

  
      <el-scrollbar :max-height="'400px'" :min-size="1">
        <CommonList
            v-model:tableOptions="tableOptions"
        >
          <template v-slot:customSlot-activePoint="{ data }">
            {{ data.send_cont }}
          </template>
        </CommonList>
      </el-scrollbar>
  
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="isMileageUsagePopActive = false">취소</el-button>
        </div>
      </template>
    </el-dialog>
  </template>
  <script lang="ts" setup>
  import {ref, defineAsyncComponent,computed} from "vue"
  import {getUserMileageUsageList} from "@/views/pages/user/userPage"
  import {TableOptionsClass} from "@/models/common"
  import {userMileageUsageHeader} from "@/views/pages/user/userConstants";
  import { TableOptions } from "@/types/common";
  
  const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
  const isMileageUsagePopActive = defineModel<boolean>("isMileageUsagePopActive",{ default: false});
  
  const props = defineProps({
    user_id: { Type: String, default: '' },
    openDrawer: {Type:Function, default:null}
  });

  const handleClose = () => {
    isMileageUsagePopActive.value = false;
  }
  
  const tableOptions = ref<TableOptions>(new TableOptionsClass({headers: userMileageUsageHeader, isSelectActive:false, isNumberActive:true, isPagination:false}))
  
  
  const getUserPointHist = async () => {
    await getUserMileageUsageList(props.user_id as string, tableOptions)
  }
  
  </script>
  