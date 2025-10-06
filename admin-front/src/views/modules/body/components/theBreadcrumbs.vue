<template>
    <div class="container-fluid">
        <div class="page-title m-b-10 m-t-10">
            <div class="row">
                <div class="col-sm-6">
                  <ol class="breadcrumb">
                    <li class="breadcrumb-item"><router-link to="/"><vue-feather
                        type="home"></vue-feather></router-link></li>
                    <li class="breadcrumb-item" v-if="props.main">{{ props.main }}</li>
                    <li class="breadcrumb-item active">{{ currentRoute.name }}</li>
<!--                    <li class="breadcrumb-item active" v-if="title">{{ title }}</li>-->
                  </ol>
                </div>
                <div class="col-sm-6">

                </div>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import {ref, inject, onMounted } from "vue"

const router = inject('$router');
const currentRoute = ref(router.currentRoute);

onMounted(() => {

});

let props = defineProps({
    title: {
        default: 'home'
    },
    main: {
        default: ''
    }
})
</script>