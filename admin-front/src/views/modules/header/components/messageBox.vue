<template>
    <div class="message notification-box">
        <svg>
            <use href="@/assets/svg/icon-sprite.svg#Message"></use>
        </svg><span class="rounded-pill badge-secondary"> </span>
    </div>
    <div class="onhover-show-div message-dropdown">
        <h6 class="f-18 mb-0 dropdown-title">Message </h6>
        <ul>
            <li v-for="(item, index) in data" :key="index">
                <div class="d-flex align-items-start">
                    <div class="flex-grow-1">
                        <h5 class="mb-1"><a href="email-application.html">{{ item.name }}</a></h5>
                        <p>{{ item.desc }}</p>
                    </div>
                    <div class="notification-right"><vue-feather type="x"></vue-feather></div>
                </div>
            </li>
            <li><a class="f-w-700" href="chat.html">Check all</a></li>
        </ul>
    </div>
</template>
<script lang="ts" setup>
import { useHeaderStore } from "@/store/header";
const store = useHeaderStore()
const data = store.meg
</script>