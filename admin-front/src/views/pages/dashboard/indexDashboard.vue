<template>
    <div class="container-fluid">
        <div class="row starter-main">
            <starterMain />
        </div>
        <div class="row" style="margin-top: 20px;">
            <div class="col-12">
                <RevenueChart />
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { defineAsyncComponent } from 'vue'
const starterMain = defineAsyncComponent(() => import("@/views/pages/dashboard/components/starterMain.vue"))
const RevenueChart = defineAsyncComponent(() => import("@/views/pages/dashboard/components/RevenueChart.vue"))
</script>