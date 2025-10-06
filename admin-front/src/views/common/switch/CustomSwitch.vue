<template>
  <div class="switch-sm m-b-5">
    <label class="switch custom-switch" style="vertical-align: -0.2em; margin-top: 0px">
      <input
          type="checkbox"
          @change="changeEvent"
          :checked="switchValue"
      />
      <span class="custom-switch-state switch-state d-flex align-items-center">
      <div
          v-show="switchValue"
          class="el-switch__inner font-light"
          style="font-size: 10px">
        <strong class="is-text m-l-10" aria-hidden="false">Y</strong>
      </div>
      <div
          v-show="!switchValue"
          class="m-l-5 el-switch__inner font-dark"
          style="font-size: 10px">
        <strong class="is-text m-l-30" aria-hidden="false">N</strong>
      </div>
    </span>
    </label>
  </div>
</template>
<script lang="ts" setup>
const props = defineProps({
  switchEvent: { type: Function, default: null },
  rowValue: { type: Object, default: null },
});
const switchValue = defineModel<boolean>("switchValue",{ default: true});

const changeEvent = () => {
  switchValue.value == true? switchValue.value = false : switchValue.value = true
  if (props.switchEvent){
    props.switchEvent(props.rowValue);
  }

}
</script>
