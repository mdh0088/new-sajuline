<template>
  <div class="loader-wrapper" v-if='showLoader'>
    <div class="loader"></div>
  </div>
  <router-view />
</template>
<script lang="ts" setup>
import { onMounted, ref, watch, onUnmounted } from "vue"
import { useRouter } from 'vue-router'
const showLoader = ref<boolean>(false)
const router = useRouter()

watch(
    () => router,
    () => {
      showLoader.value = true;
      setTimeout(() => {
        showLoader.value = false
      }, 3000);
    },
    { deep: true },
);

</script>
<style>
.cursor-pointer {
  cursor: pointer;
}
</style>