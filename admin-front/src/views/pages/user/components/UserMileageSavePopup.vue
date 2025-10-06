<template>
    <el-dialog
        v-model="isMileageSavePopActive"
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
          <el-button @click="isMileageSavePopActive = false">취소</el-button>
        </div>
      </template>
    </el-dialog>
  </template>
  <script lang="ts" setup>
  import {ref, defineAsyncComponent,computed} from "vue"
  import {getUserMileageSaveList} from "@/views/pages/user/userPage"
  import {TableOptionsClass} from "@/models/common"
  import {userMileageSaveHeader} from "@/views/pages/user/userConstants";
  import { TableOptions } from "@/types/common";
  
  const CommonList = defineAsyncComponent(() => import("@/views/common/list/CommonList.vue"))
  const isMileageSavePopActive = defineModel<boolean>("isMileageSavePopActive",{ default: false});
  
  const props = defineProps({
    user_id: { Type: String, default: '' },
    openDrawer: {Type:Function, default:null}
  });

  const handleClose = () => {
    isMileageSavePopActive.value = false;
  }
  
  const tableOptions = ref<TableOptions>(new TableOptionsClass({headers: userMileageSaveHeader, isSelectActive:false, isNumberActive:true, isPagination:false}))
  
  
  const getUserPointHist = async () => {
    await getUserMileageSaveList(props.user_id as string, tableOptions)
  }
  
  </script>
  