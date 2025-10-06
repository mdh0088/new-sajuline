<template>
    <div class="test">
        <div class="logo-wrapper"><router-link to="/"><img class="img-fluid" src="@/assets/images/logo/logo.png"
                    alt=""></router-link>
            <div class="back-btn"><i class="fa fa-angle-left"> </i></div>
        </div>
        <div class="sidebar-main">
            <div id="sidebar-menu">
                <ul class="sidebar-links custom-scrollbar" id="simple-bar">
                    <navMenu />
                </ul>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { defineAsyncComponent } from 'vue';
const navMenu = defineAsyncComponent(() => import("@/views/modules/sidebar/components/navMenu.vue"))
</script>