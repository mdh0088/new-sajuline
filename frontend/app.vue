<template>
  <NuxtLayout>
    <NuxtRouteAnnouncer />
    <NuxtPage />

    <Notivue v-slot="item">
      <Notification :item="item" :theme="slateTheme" />
    </Notivue>
  </NuxtLayout>
</template>

<script setup>
import '~/assets/css/main.css'
import { slateTheme } from 'notivue'
</script>


