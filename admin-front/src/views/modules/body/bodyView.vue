<template>
<!--    <tapTop />-->
    <div class="page-wrapper " :class="display ? 'compact-sidebar compact-small material-icon' : layoutobj"
        id="pageWrapper">
        <div class="page-header" :class="{ close_icon: !store.togglesidebar }">
            <Header @clicked="sidebar_toggle" />
        </div>
        <div class="page-body-wrapper">
            <div class="sidebar-wrapper " :data-layout="storeLayout.svg == 'stroke-svg' ? 'stroke-svg' : 'fill-svg'"
                :class="[{ close_icon: !store.togglesidebar, 'sidebar-default': store.perentName }]">
                <Sidebar @clicked="sidebar_toggle" />
            </div>
            <div class="page-body">
                <Breadcrumbs title="Layout Light" />
                <router-view></router-view>
            </div>
<!--            <footerView />-->
        </div>
    </div>
</template>
<script lang="ts" setup>
const Header = defineAsyncComponent(() => import("@/views/modules/header/headerSection.vue"))
const Sidebar = defineAsyncComponent(() => import("@/views/modules/sidebar/sidebarSection.vue"))

import { useMenuStore } from "@/store/menu";
import { uselayoutStore } from "@/store/layout";
import { storeToRefs } from "pinia";
import { ref, defineAsyncComponent, watch, onMounted } from 'vue'

const layoutobj = ref<any>({});
const sidebar_toggle_var = ref<boolean>(false);
const display = ref<boolean>(false)
const store = useMenuStore();
const storeLayout = uselayoutStore();
const { layout: layout } = storeToRefs(storeLayout);
watch(
    () => layout,
    () => {
        layoutobj.value = storeLayout.layout.settings.sidebar_setting;
    },
    { deep: true },
);
watch(
    () => "router",
    () => {

        if ((window.innerWidth < 991 && storeLayout.layout.settings.layout === 'Horizontal')) {
            const newlayout = JSON.parse(JSON.stringify(layoutobj).replace('horizontal-wrapper', 'compact-wrapper'));
            layoutobj.value = JSON.parse(JSON.stringify(newlayout))[storeLayout.layout.settings.layout];
        } else {
            layoutobj.value = JSON.parse(JSON.stringify(layoutobj))[storeLayout.layout.settings.layout];
        }
    }
)
function sidebar_toggle(value: boolean) {
    sidebar_toggle_var.value = !value;
}
function handleScroll() {
    if (window.innerWidth <= 1199) {
        display.value = true;
    } else {
        display.value = false;
    }
}
onMounted(() => {

    window.addEventListener('resize', handleScroll);
    layoutobj.value = storeLayout.layout.settings.sidebar_setting;
    // localStorage.setItem("cartItem", JSON.stringify(product.cart));
});
</script>