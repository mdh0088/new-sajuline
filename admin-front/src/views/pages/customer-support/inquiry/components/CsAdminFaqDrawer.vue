<template>
  <el-drawer
      v-model="isDrawerActive"
      title=""
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>

      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>상담사 문의</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{csAdminFaqInfo.csRegistDate}}
              </span>
            </el-col>
          </el-row>

        </div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>
          <!--          <el-form-item label="등록일" prop="name">
                      <el-input v-model="userInfo.userId" :disabled="true"/>
                    </el-form-item>-->

          <el-form-item label="상담사 닉네임" prop="title">
            <el-input v-model="csAdminFaqInfo.nickName" :disabled="true"/>
          </el-form-item>
          <el-form-item label="내용" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="csAdminFaqInfo.csCont" :disabled="true"/>
          </el-form-item>

          <el-form-item label="첩부 파일">
            {{csAdminFaqInfo.attachFile}}
<!--            <el-upload
                v-model:file-list="csAdminFaqInfo.attachFile"
                :show-file-list="true"
                :auto-upload="false"
                class="upload-subfiles w-100"
                list-type="picture"
                multiple
                drag
            >
            </el-upload>-->
          </el-form-item>

        </el-form>
      </div>

      <el-divider />


      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>관리자 답변</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{csAdminFaqInfo.adminRegistDate}}
              </span>
            </el-col>
          </el-row>

        </div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>
          <el-form-item label="답변" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="csAdminFaqInfo.adminCont"/>
          </el-form-item>
        </el-form>
      </div>

    </div>

    <template #footer>
      <div style="flex: auto">
        <el-button @click="isDrawerActive = false">취소</el-button>
        <el-button type="primary" @click="confirmClick(ruleFormRef)">저장</el-button>
      </div>
    </template>
  </el-drawer>



  <!--  -->
</template>
<script lang="ts" setup>
import {ref, reactive, defineAsyncComponent, nextTick} from 'vue'
import {getCsAdminFaqInfo, modifyCsAdminFaq} from "@/views/pages/customer-support/inquiry/inquiryPage";
import { CsAdminFaqClass} from "@/models/customer-support"

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});
const csAdminFaqInfo = reactive<CsAdminFaqInfo>(new CsAdminFaqClass())
const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});


const confirmClick = async () => {
  await modifyCsAdminFaq(csAdminFaqInfo, props.doSearch)
}

const closeDrawer = () => {
  openType.value = "update"
}

const openDrawer = async () => {

  csAdminFaqInfo.idx= props.chooseRow.idx;
  await getCsAdminFaqInfo(csAdminFaqInfo)
}

</script>
