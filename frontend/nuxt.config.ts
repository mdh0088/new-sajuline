// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Nuxt 4 compatibility
  future: {
    compatibilityVersion: 4
  },
  
  // 개발 도구
  devtools: { enabled: true },
  
  // 모듈
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@element-plus/nuxt'
  ],
  
  // Pinia 설정
  pinia: {
    storesDirs: ['./stores/**']
  },
  
  // Element Plus 설정
  elementPlus: {
    /** Options */
  },
  
  // CSS 설정
  css: ['~/assets/css/main.css'],
  
  // 런타임 설정
  runtimeConfig: {
    // 서버에서만 접근 가능한 설정
    public: {
      // 클라이언트에서도 접근 가능한 설정
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  
  // TypeScript 설정
  typescript: {
    strict: true,
    typeCheck: true
  }
})