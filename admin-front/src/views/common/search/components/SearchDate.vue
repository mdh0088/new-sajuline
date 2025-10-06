<template>
  <el-config-provider :locale="kor">

    <el-date-picker
        v-model="searchValue"
        class="date-search-input"
        type="daterange"
        unlink-panels
        range-separator="~"
        popper-class="date-search-popper"
        :shortcuts="$dateTotalShortCuts"
        @change="props.doSearch()"
        :clearable="false"
        :editable="false"
    />
  </el-config-provider>
</template>
<script lang="ts" setup>
import kor from 'element-plus/dist/locale/ko.mjs';
const props = defineProps({
  doSearch: { Type: Function, default: null },
  searchOption : {Type: Object, default:{}}
});

const searchValue =  defineModel<any>("searchValue",{ default: null});

</script>
