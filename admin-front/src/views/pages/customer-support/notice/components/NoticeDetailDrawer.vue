<template>
  <el-drawer
      v-model="isDrawerActive"
      title="공지사항 등록"
      size="50%"
      @open="openDrawer"
      @close="closeDrawer"
  >
    <div>

      <div>
        <el-form
            ref="ruleFormRef"
            label-position="left"
            label-width="auto"
            :model="csNoticeInfo"
            status-icon>
<!--          <el-form-item label="등록일" prop="name">
            <el-input v-model="userInfo.userId" :disabled="true"/>
          </el-form-item>-->

          <el-form-item label="제목" prop="title">
            <el-input v-model="csNoticeInfo.title"/>
          </el-form-item>
          <el-form-item label="내용" prop="cont">
            <Editor
                v-model="csNoticeInfo.cont"
                api-key="e33t8vsld7z7z11ixrdky8uqoq3xn7njdnvist7r010a953m"
                :init="{plugins: 'lists link image table code help wordcount'}"
            />
          </el-form-item>

          <el-form-item label="첨부파일 업로드" prop="phone">
            <el-upload
                v-model:file-list="attachFile"
                class="upload-demo w-100"
                :show-file-list="true"
                :auto-upload="false"
                multiple
                :limit="1"
            >
              <el-button :icon="Upload" type="primary"/>
              <template #tip>
                <div class="el-upload__tip">
                  jpg/png files with a size less than 500KB.
                </div>
              </template>
            </el-upload>
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
import Editor from '@tinymce/tinymce-vue'
import { Upload } from '@element-plus/icons-vue'
import {ref, reactive } from 'vue'
import {getCsNoticeInfo, modifyCsNotice, createCsNotice} from "@/views/pages/customer-support/notice/noticePage";
import {CsNoticeClass} from "@/models/customer-support"
import {UploadUserFile} from "element-plus";

const props = defineProps({
  chooseRow: { Type: Object, default: {} },
  doSearch: {Type:Function, default: null}
});

const attachFile = ref<UploadUserFile[]>([])
const isDrawerActive = defineModel<boolean>("isDrawerActive",{ default: false});
const openType = defineModel<string>("openType",{ default: "update"});
const csNoticeInfo = reactive<CsNoticeInfo>(new CsNoticeClass());


const confirmClick = async () => {
  if (openType.value == "update") {
    await modifyCsNotice(csNoticeInfo, attachFile, props.doSearch)
  } else {
    await createCsNotice(csNoticeInfo, attachFile, props.doSearch)
  }
}

const closeDrawer = () => {
  openType.value = "update"
}

const openDrawer = async () => {

  csNoticeInfo.idx = 0;
  csNoticeInfo.title = "";
  csNoticeInfo.cont = "";
  attachFile.value = [];

  if (openType.value == "update") {
    const csNoticeIdx = props.chooseRow.idx;
    csNoticeInfo.idx= csNoticeIdx;
    await getCsNoticeInfo(csNoticeInfo, attachFile)
  }
}

</script>
