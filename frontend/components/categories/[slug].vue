<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <main class="main-content">
      <div class="p-6">
        <h1 class="text-2xl font-bold">카테고리: {{ slug }}</h1>
        <NuxtLink to="/categories" class="text-teal-400 underline mt-4 inline-block">카테고리 목록</NuxtLink>
        <NuxtLink to="/" class="text-teal-400 underline mt-2 inline-block">홈으로</NuxtLink>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'nuxt/app'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
</script>


