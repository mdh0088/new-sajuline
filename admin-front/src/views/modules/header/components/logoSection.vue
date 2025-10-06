<template>
    <div class="logo-wrapper"><a href="../../../../../index.html"><img class="img-fluid" src="@/assets/images/logo/logo.png" alt=""></a>
    </div>
    <svg class="stroke-icon toggle-sidebar" @click="store.toggle_sidebar">
        <use class="status_toggle middle sidebar-toggle" href="@/assets/svg/icon-sprite.svg#Grid"> </use>
    </svg>
</template>
<script lang="ts" setup>
import { useMenuStore } from "@/store/menu";
const store = useMenuStore();
</script>