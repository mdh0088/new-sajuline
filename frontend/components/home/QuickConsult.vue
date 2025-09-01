<template>
  <section class="px-5 py-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">빠른 상담</h2>
      <NuxtLink to="/categories" class="text-sm text-purple-300 flex items-center gap-1 hover:text-purple-200 transition-colors">
        전체보기 →
      </NuxtLink>
    </div>
    
    <div class="grid grid-cols-3 gap-3 max-w-md mx-auto">
      <NuxtLink
        v-for="(category, index) in categories"
        :key="index"
        :to="category.path"
        class="relative p-5 bg-white/3 border border-white/10 rounded-2xl text-center cursor-pointer transition-all duration-300 hover:bg-white/5 active:scale-98 group overflow-hidden"
      >
        <div class="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div class="relative z-10">
          <div class="w-14 h-14 mx-auto mb-3 bg-gradient-to-br from-purple-600/20 to-purple-700/10 rounded-2xl flex items-center justify-center text-2xl border border-purple-600/20">
            {{ category.icon }}
          </div>
          <div class="text-sm font-semibold text-white/90">{{ category.name }}</div>
        </div>
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
// Props 정의
interface Category {
  name: string
  path: string
  icon: string
}

interface Props {
  categories?: Category[]
}

const props = withDefaults(defineProps<Props>(), {
  categories: () => [
    { name: '연애', path: '/categories/love', icon: '❤️' },
    { name: '직장', path: '/categories/work', icon: '💼' },
    { name: '재물', path: '/categories/money', icon: '💰' }
  ]
})
</script>

<style scoped>
.active\:scale-98:active {
  transform: scale(0.98);
}
</style>