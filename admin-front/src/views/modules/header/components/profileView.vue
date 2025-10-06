<template>
    <div class="d-flex align-items-center profile-media"><img class="b-r-25" src="@/assets/images/dashboard/profile.png"
            alt="">
        <div class="flex-grow-1 user"><span>Helen Walter</span>
            <p class="mb-0 font-nunito">Admin
                <svg>
                    <use href="@/assets/svg/icon-sprite.svg#header-arrow-down"></use>
                </svg>
            </p>
        </div>
    </div>
    <ul class="profile-dropdown onhover-show-div">
      <li @click="isAccountActive=true"><a ><vue-feather type="user"></vue-feather><span>내 정보</span></a></li>
      <!--
      <li><a ><vue-feather type="mail"></vue-feather><span>Inbox</span></a></li>
      <li><a ><vue-feather type="file-text"></vue-feather><span>Taskboard</span></a></li>
      <li><a ><vue-feather type="settings"></vue-feather><span>Settings</span></a></li>
      -->
      <li><a ><vue-feather type="log-in"></vue-feather><span>Log Out</span></a></li>
    </ul>
    <ManagerInfo v-model:isAccountActive="isAccountActive"/>
</template>
<script lang="ts" setup>
import {ref} from "vue"
import ManagerInfo from "@/views/modules/header/components/options/ManagerInfo.vue"

const isAccountActive = ref<boolean>(false)
</script>