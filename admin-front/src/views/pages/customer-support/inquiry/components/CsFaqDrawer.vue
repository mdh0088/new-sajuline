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
              <h4>1:상담사 문의</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{csFaqInfo.userRegistDate}}
              </span>
            </el-col>
          </el-row>

        </div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            status-icon>
          <el-form-item label="유저 아이디" prop="title">
            <el-input v-model="csFaqInfo.userId" :disabled="true"/>
          </el-form-item>
          <el-form-item label="유저 닉네임" prop="title">
            <el-input v-model="csFaqInfo.userNickName" :disabled="true"/>
          </el-form-item>
          <el-form-item label="내용" prop="title">
            <el-input
                :autosize="{ minRows: 10 }"
                maxlength="200"
                type="textarea" v-model="csFaqInfo.userCont" :disabled="true"/>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />


      <div>
        <div class="m-b-20">
          <el-row :gutter="20">
            <el-col :span="6">
              <h4>상담사 답변</h4>
            </el-col>
            <el-col :span="6" :offset="12">
              <span class="f-12">
                등록일 : {{csFaqInfo.csRegistDate}}
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
                type="textarea" v-model="csFaqInfo.csCont"/>
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
import {getCsFaq, modifyCsFaq} from "@/views/pages/customer-support/inquiry/inquiryPage";
import { CsFaqClass} from "@/models/customer-support"

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const csFaqInfo = reactive<CsFaqInfo>(new CsFaqClass())
const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});


const confirmClick = async () => {
  await modifyCsFaq(csFaqInfo, props.doSearch)
}

const closeDrawer = () => {
  openType.value = "update"
}

const openDrawer = async () => {

  csFaqInfo.idx= props.chooseRow.idx;
  await getCsFaq(csFaqInfo)
}

</script>
