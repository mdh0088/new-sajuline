import { createApp } from 'vue'

import App from '@/App.vue'
import router from '@/router'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import 'bootstrap/dist/js/bootstrap.bundle'
import "bootstrap/dist/js/bootstrap.min.js";
import "@/assets/scss/app.scss"
import ElementPlus from 'element-plus';
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css';

import VueFeather from "vue-feather";
import Breadcrumbs from '@/views/modules/body/components/theBreadcrumbs.vue';
import {shortcuts} from '@/commonUtils/dateUtils';

/// pinia
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

import { createPinia } from 'pinia';
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);

app.use(router);
app.use(createPinia());
app.use(ElementPlus);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.provide('$router', router);
app.provide('$pinia', pinia)

app.component('vue-feather', VueFeather);
app.component('Breadcrumbs', Breadcrumbs);

app.mount('#app');
app.config.globalProperties.$dateTotalShortCuts = shortcuts;