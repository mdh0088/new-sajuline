<template>
  <el-input
      style="width: 300px; font-size:12px"
      placeholder="검색어를 입력해주세요."
      v-model="searchValue"
      v-on:keyup="$event.keyCode === 13 ? props.doSearch() : ''"
  >
    <template #append>
      <el-button :icon="Search" @click="props.doSearch()"/>
    </template>
  </el-input>
</template>
<script lang="ts" setup>
import { Search } from '@element-plus/icons-vue';
const props = defineProps({
  doSearch: { Type: Function, default: null },
  searchOption : {Type: Object, default:{}}
});

const searchValue =  defineModel<string>("searchValue",{ default: null});

</script>
