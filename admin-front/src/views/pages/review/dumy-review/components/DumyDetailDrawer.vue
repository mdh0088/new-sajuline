<template>
  <el-drawer
      v-model="isDrawerActive"
      title="후기 정보"
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>

      <div>

        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>유저 후기 정보</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{reviewInfo.userRegistDate}}
              </span>
            </el-col>
          </el-row>
        </div>

        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>

          <el-form-item label=" 아이디" prop="title">
            <el-input v-model="reviewInfo.userId" :disabled="true"/>
          </el-form-item>
          <el-form-item label="내용" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="reviewInfo.userCont"/>
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>상담사 후기 정보</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{reviewInfo.csRegistDate}}
              </span>
            </el-col>
          </el-row>
        </div>

        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>

          <el-form-item label=" 아이디" prop="title">
            <el-input v-model="reviewInfo.nickName" :disabled="true"/>
          </el-form-item>
          <el-form-item label="내용" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="reviewInfo.csCont"/>
          </el-form-item>
        </el-form>

      </div>
    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false">취소</el-button>
        <el-button type="primary" @click="confirmClick()">저장</el-button>
      </div>
    </template>
  </el-drawer>



  <!--  -->
</template>
<script lang="ts" setup>
import {ref} from 'vue'
import {getDumyReview, updateDumyReview } from "@/views/pages/review/dumy-review/dumyReviewPage"
import {DumyReviewClass} from "@/models/review"
import * as swal from "@/commonUtils/swal";

const props = defineProps({
  chooseRow: { type: Object, default: {} },
  doSearch: {type:Function, default: null}
});


const reviewInfo = ref<DumyReviewInfo>(new DumyReviewClass());
const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});


const confirmClick = async () => {
  if (openType.value == "update") {
    const msg = '정말 저장하시겠습니까?.';
    const swalResult = await swal.swalConfirm(msg, 'warning');
    if (swalResult.isConfirmed) {
      await updateDumyReview(reviewInfo, props.doSearch as Function)
    }
  }
}

const closeDrawer = () => {
  openType.value = "update"
}

const openDrawer = async () => {
  if (openType.value == "update") {
    console.log('chk props >>>',props.chooseRow)
    reviewInfo.value.idx = props.chooseRow.idx as number | null;
    console.log('chk reviewInfo >>>',reviewInfo.value)

    await getDumyReview(reviewInfo)
  }
}

</script>
