<template>
  <div class="min-h-screen p-6 bg-slate-950 text-white">
    <h1 class="text-2xl font-bold">카테고리: {{ slug }}</h1>
    <NuxtLink to="/categories" class="text-teal-400 underline mt-4 inline-block">카테고리 목록</NuxtLink>
    <NuxtLink to="/" class="text-teal-400 underline mt-2 inline-block">홈으로</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'nuxt/app'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
</script>


