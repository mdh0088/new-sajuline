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
  </NuxtLayout>

  <!-- Notivue를 body로 teleport하여 최상단에 표시 -->
  <Teleport to="body">
    <div style="position: fixed; top: 16px; left: 50%; transform: translateX(-50%); z-index: 999999; width: calc(100% - 32px); max-width: 440px; pointer-events: none;">
      <Notivue v-slot="item">
        <div style="pointer-events: auto; margin-bottom: 12px;">
          <Notification :item="item" :theme="slateTheme" />
        </div>
      </Notivue>
    </div>
  </Teleport>
</template>

<script setup>
import '~/assets/css/main.css'
import '~/assets/css/typography.css'
import { slateTheme } from 'notivue'
</script>


