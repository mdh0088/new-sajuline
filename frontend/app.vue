<template>
  <NuxtLayout>
    <NuxtRouteAnnouncer />
    <NuxtPage />

    <!-- 전역 푸터 -->
    <AppFooter />

    <Notivue v-slot="item">
      <Notification :item="item" :theme="slateTheme" />
    </Notivue>
  </NuxtLayout>
</template>

<script setup>
import '~/assets/css/main.css'
import { slateTheme } from 'notivue'
import AppFooter from '~/components/common/AppFooter.vue'
</script>


