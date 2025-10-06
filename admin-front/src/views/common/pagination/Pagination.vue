<template>

  <div class="row m-t-10">
    <div class="d-flex justify-content-between">
      <div class="col-2">
        <div class="text-start">
        </div>
      </div>
      <div class="col-10">
        <div class="text-end d-flex justify-content-end">
          <el-select
              class="m-r-10"
              v-model="rowPage"
              @change="props.doSearch"
              placeholder="Select"
              style="width: 80px"
          >
            <el-option
                v-for="item in rowItems"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>

          <el-pagination
              v-model:current-page="currentPage"
              background
              :page-size="rowPage"
              :pager-count="5"
              layout="prev, pager, next"
              :total="props.totalCnt"
              @current-change="props.doSearch"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
const props = defineProps({
  totalCnt: { Type: Number, default: 0 },
  doSearch: { Type: Function, default: null },
});

const currentPage = defineModel<number>("currentPage",{ default: 1});
const rowItems = defineModel<Array<number>>("rowItems",{ default: []});
const rowPage = defineModel<number>("rowPage",{ default: 10});

</script>