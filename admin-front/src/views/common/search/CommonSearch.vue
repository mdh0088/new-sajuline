<template>
  <el-card>
    <div>
      <el-form label-position="top" label-width="auto" :inline="true">
        <template v-for="(item, index) in searchOptions.optionsList" :key="item.key">
          <el-form-item :label="item.label">
            <template v-if="item.type == 'string'">
              <SearchInput v-model:searchValue="item.value" :searchOption="item" :doSearch="props.doSearch"/>
            </template>
            <template v-if="item.type == 'number'">
              <SearchNumberInput v-model:searchValue="item.value" :searchOption="item" :doSearch="props.doSearch"/>
            </template>
            <template v-else-if="item.type=='select'">
              <SearchSelect v-model:searchValue="item.value" :searchOption="item" :doSearch="props.doSearch"/>
            </template>
            <template v-else-if="item.type=='date'">
              <SearchDate v-model:searchValue="item.value" :searchOption="item"  :doSearch="props.doSearch"/>
            </template>
          </el-form-item>
        </template>
      </el-form>
    </div>
  </el-card>
</template>
<script lang="ts" setup>
import {defineAsyncComponent, ref} from "vue"
const SearchInput = defineAsyncComponent(() => import("@/views/common/search/components/SearchInput.vue"))
const SearchNumberInput = defineAsyncComponent(() => import("@/views/common/search/components/SearchNumberInput.vue"))
const SearchSelect = defineAsyncComponent(() => import("@/views/common/search/components/SearchSelect.vue"))
const SearchDate = defineAsyncComponent(() => import("@/views/common/search/components/SearchDate.vue"))

const props = defineProps({
  doSearch: { Type: Function, default: null },
});

const searchOptions = defineModel<SearchOptionsList>("searchOptions",{ default: {optionsList:[]}});



</script>
