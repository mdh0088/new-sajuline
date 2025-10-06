<template>
    <div class="notification-box">
        <svg>
            <use href="@/assets/svg/icon-sprite.svg#Bell"></use>
        </svg>
    </div>
    <div class="onhover-show-div notification-dropdown">
        <h6 class="f-18 mb-0 dropdown-title">Notitications</h6>
        <ul>
            <li class=" border-4 mt-3" :class="item.class" v-for="(item, index) in data" :key="index"><a
                    href="email-application.html">
                    <p>{{ item.title }}<span :class="item.font">{{ item.time }}</span></p>
                </a></li>
            <li><a class="f-w-700" href="email-application.html">Check all</a></li>
        </ul>
    </div>
</template>
<script lang="ts" setup>
import { useHeaderStore } from "@/store/header";
const store = useHeaderStore()
const data = store.data
</script>