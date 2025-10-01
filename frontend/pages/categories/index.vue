<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <main class="main-content">
      <div class="p-6">
        <h1 class="text-2xl font-bold">카테고리</h1>
        <ul class="list-disc pl-5 mt-4 space-y-2">
          <li><NuxtLink to="/categories/love" class="text-teal-400 underline">연애</NuxtLink></li>
          <li><NuxtLink to="/categories/work" class="text-teal-400 underline">직장</NuxtLink></li>
          <li><NuxtLink to="/categories/money" class="text-teal-400 underline">재물</NuxtLink></li>
        </ul>
        <NuxtLink to="/" class="text-teal-400 underline mt-6 inline-block">홈으로</NuxtLink>
      </div>
    </main>

  </div>
</template>


