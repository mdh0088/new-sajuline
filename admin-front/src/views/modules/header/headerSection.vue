<template>
    <div class="header-wrapper">
      <el-row :gutter="20">
        <el-col :span="1">
          <logoSection />
        </el-col>
        <el-col :span="18">
          <SearchBar />
        </el-col>
        <el-col :span="4">
          <div class="m-t-5 nav-right col-auto pull-right right-header p-0 ms-auto">
            <ul class="nav-menus">
              <li class="onhover-dropdown">
                <NotificationBox />
              </li>
              <!--
                <li class="serchinput">
                    <SearchInput />
                </li>



                <li class="onhover-dropdown">
                    <bookmarkSearch />
                </li>
                <li class="cart-nav onhover-dropdown">
                    <cartBox />
                </li>
                <li class="onhover-dropdown message-box">
                    <messageBox />
                </li>

                <li>
                    <modeView />
                </li>-->

              <li class="profile-nav onhover-dropdown pe-0 py-0">
                <ProfileView />
              </li>
            </ul>
          </div>
        </el-col>
      </el-row>



    </div>
</template>
<script lang="ts" setup>
import { defineAsyncComponent } from 'vue';

const SearchBar = defineAsyncComponent(() => import("@/views/modules/header/components/searchBar.vue"))
const NotificationBox = defineAsyncComponent(() => import("@/views/modules/header/components/notificationBox.vue"))
const ProfileView = defineAsyncComponent(() => import("@/views/modules/header/components/profileView.vue"))

const SearchInput = defineAsyncComponent(() => import("@/views/modules/header/components/searchInput.vue"))
const logoSection = defineAsyncComponent(() => import("@/views/modules/header/components/logoSection.vue"))
const bookmarkSearch = defineAsyncComponent(() => import("@/views/modules/header/components/bookmarkSearch.vue"))
const messageBox = defineAsyncComponent(() => import("@/views/modules/header/components/messageBox.vue"))
const cartBox = defineAsyncComponent(() => import("@/views/modules/header/components/cartBox.vue"))
const modeView = defineAsyncComponent(() => import("@/views/modules/header/components/modeView.vue"))

</script>