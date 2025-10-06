<template>
  <div>
    <el-table
        v-loading="tableOptions.isLoading"
        :data="tableOptions.items"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        style="width: 100%; font-size:12px">

      <template v-if="tableOptions.isSelectActive">
        <el-table-column type="selection" width="55" />
      </template>

      <template v-if="tableOptions.isNumberActive">
        <el-table-column type="index" width="50" />
      </template>

      <template v-for="header in tableOptions.headers" :key="header.value">
        <el-table-column v-if="header.isShow" :label="header.label" :width="header.width" :prop="header.value" :sortable="header.isSortable">
          <template #default="scope">

            <template v-if="header.type == 'key'" >
              <span class="cursor-link-pointer" @click="chooseRow(scope.row)">
                <template v-if="scope.row[header.value]">
                  <el-tooltip
                      class="box-item f-12"
                      effect="dark"
                      :content="scope.row[header.value]"
                      placement="top">
                    {{replaceStringToComma(scope.row[header.value].replaceAll('\n',''),40)}}
                  </el-tooltip>
                </template>
              </span>
            </template>

<!--            <template v-else-if="header.type == 'switch'" >
              <CustomSwitch
                  v-model:switchValue="scope.row[header.value]"
                  :rowValue="scope.row"
                  :switchEvent="header.options.switchEvent"
              />
            </template>-->

            <template v-else-if="header.type == 'button'">
              <el-button type="primary" @click="header.options.btnEvent(scope.row[header.value])">
                {{header.options.label}}
              </el-button>
            </template>

            <template v-else-if="header.type == 'custom'">
              <slot :name="`customSlot-${header.value}`" :data="scope.row"/>
<!--              {{header.options.customEvent(scope.row)}}-->
            </template>

            <template v-else-if="header.type == 'text'">
              <template v-if="scope.row[header.value]">
                <el-tooltip
                    class="box-item f-12"
                    effect="dark"
                    :content="scope.row[header.value]"
                    placement="top">
                  <el-text :class="'w-'+header.width+'x'" class="f-12" truncated>
                    {{scope.row[header.value]}}
                  </el-text>
<!--                  {{replaceStringToComma(scope.row[header.value].replaceAll('\n',''),20)}}-->
                </el-tooltip>
              </template>
            </template>

            <template v-else-if="header.type == 'number'">
              <el-text class="f-12">
                {{numberComma(scope.row[header.value].toFixed(0))}}
              </el-text>
            </template>

            <template v-else-if="header.type == 'rate'">
              <el-text class="f-12">
                {{toPercentage(scope.row[header.value])}}
              </el-text>
            </template>

            <template v-else-if="header.type == 'date'">
              <span>
                {{formatDate(scope.row[header.value],scope.row[header.options.formatDate] )}}
              </span>
            </template>

            <template v-else>
              <span>
                {{scope.row[header.value]}}
              </span>
            </template>

          </template>
        </el-table-column>
      </template>
    </el-table>
  </div>
 <Pagination
    v-if="tableOptions.isPagination"
    v-model:rowItems="tableOptions.rowItems"
    v-model:rowPage="tableOptions.rowPage"
    v-model:currentPage="tableOptions.currentPage"
    :totalCnt="tableOptions.totalCnt"
    :doSearch="props.doSearch"
 />

</template>

<script lang="ts" setup>
import { defineAsyncComponent, watch } from "vue"
import {replaceStringToComma, numberComma, toPercentage} from "@/commonUtils/utils"
import {TableOptions} from "@/types/common"
import {formatDate} from "@/commonUtils/utils"

const CustomSwitch = defineAsyncComponent(() => import("@/views/common/switch/CustomSwitch.vue"))
const Pagination = defineAsyncComponent(() => import("@/views/common/pagination/Pagination.vue"))

const props = defineProps({
  doSearch: { Type: Function, default: null },
});

const tableOptions = defineModel<TableOptions>("tableOptions",{ default: {}});

const handleSelectionChange = (selectedItems) =>{
  tableOptions.value.selectedItems = selectedItems;
}

const chooseRow = (row:any) => {
  tableOptions.value.isDrawerActive = true;
  tableOptions.value.chooseRow = row;
}

// 페이지 단위 변경시 감지
watch(
    () => tableOptions.value.rowPage,
    (newValue, oldValue) => {
      console.log("rowPage changed from", oldValue, "to", newValue);
    },
    { deep: true }
);

// 페이지 변경시 감지
watch(
    () => tableOptions.value.currentPage,
    (newValue, oldValue) => {
      console.log("currentPage changed from", oldValue, "to", newValue);
    },
    { deep: true }
);

const handleSortChange = (column:any) => {
  // 단순히 문자열로 변환
  let sort = 'asc';
  let sortKey = column.prop;
  tableOptions.value.currentPage = 1;
  if (column.order == 'ascending') {
    sort = 'asc';
  } else if (column.order == 'descending') {
    sort = 'desc';
  }
  console.log("sort sort, sortKey, from", sort, sortKey, typeof props.doSearch);
  
  // 문자열로 확실하게 변환
  const sortParam = String(sort);
  
  try {
    if (props.doSearch) {
      props.doSearch(sortParam, sortKey);
    }
  } catch (error) {
    console.error('doSearch error:', error);
  }
}
</script>
<style>


</style>
