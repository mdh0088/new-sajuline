<template>
  <NuxtLayout>
    <!-- 페이지 전환 시 로딩 인디케이터 -->
    <NuxtLoadingIndicator color="#6366f1" :height="3" />

    <NuxtRouteAnnouncer />
    <div style="display: flex; flex-direction: column;">
      <div style="flex: 1;">
        <NuxtPage />
      </div>
      <!-- 전역 푸터를 페이지 하단에 배치 -->
      <AppFooter />
    </div>

    <Notivue v-slot="item">
      <Notification :item="item" :theme="slateTheme" />
    </Notivue>
  </NuxtLayout>
</template>

<script setup>
import '~/assets/css/main.css'
import '~/assets/css/typography.css'
import { slateTheme } from 'notivue'
</script>


