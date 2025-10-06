<template>

    <div class="container-fluid">
        <div class="row starter-main">
            <starterMain />
            <!-- <simpleCard /> -->
        </div>
    </div>
</template>
<script lang="ts" setup>
import { defineAsyncComponent } from 'vue'
const starterMain = defineAsyncComponent(() => import("@/views/pages/dashboard/components/starterMain.vue"))
const simpleCard = defineAsyncComponent(() => import("@/views/pages/dashboard/components/simpleCard.vue"))
</script>