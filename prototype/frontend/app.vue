<script setup lang="ts">
// 글로벌 메타 데이터 설정
useHead({
  htmlAttrs: {
    lang: 'ko',
  },
  link: [
    {
      rel: 'preconnect',
      href: 'https://fonts.googleapis.com',
    },
    {
      rel: 'preconnect',
      href: 'https://fonts.gstatic.com',
      crossorigin: '',
    },
    {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap',
    },
  ],
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <NuxtPage />
  </div>
</template>

<style>
/* 글로벌 스타일은 assets/css/main.css에서 관리 */
</style>
