<template>
  <el-select
      style="width: 150px; font-size: 12px"
      v-model="searchValue"
      @change="props.doSearch()"
      filterable
      default-first-option
      :multiple="props.searchOption.options.multiple"
      :reserve-keyword="false"
      :placeholder="searchOption.options.placeholder"
      :no-data-text="'데이터가 없습니다.'"
  >
    <el-option
        v-for="item in props.searchOption.options.items"
        :key="item.value"
        :label="item.label"
        :value="item.value"
    />
  </el-select>
</template>
<script lang="ts" setup>
const props = defineProps({
  doSearch: { Type: Function, default: null },
  searchOption : {Type: Object, default:{}}
});

const searchValue =  defineModel<string>("searchValue",{ default: null});

</script>
