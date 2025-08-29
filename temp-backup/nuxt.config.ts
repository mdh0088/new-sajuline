// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  
  // TypeScript 설정
  typescript: {
    strict: true,
    typeCheck: false
  },

  // CSS 프레임워크
  css: ['~/assets/css/main.css'],

  // 모듈 설정
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],

  // Tailwind CSS 설정
  tailwindcss: {
    configPath: '~/tailwind.config.js',
    cssPath: '~/assets/css/main.css',
    config: {
      darkMode: 'class',
    }
  },

  // SSR 활성화
  ssr: true,

  // 빌드 설정
  build: {
    transpile: []
  },

  // Vite 설정
  vite: {
    css: {
      postcss: {
        plugins: [
          require('tailwindcss'),
          require('autoprefixer'),
        ]
      }
    }
  },

  // 런타임 설정 (환경 변수 관리)
  runtimeConfig: {
    // Private keys (서버 측에서만 접근 가능)
    apiSecret: process.env.API_SECRET,
    
    // Public keys (클라이언트에서도 접근 가능)
    public: {
      // API 설정
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
      
      // 소셜 로그인 설정
      kakaoClientId: process.env.NUXT_PUBLIC_KAKAO_CLIENT_ID,
      naverClientId: process.env.NUXT_PUBLIC_NAVER_CLIENT_ID,
      
      // 모니터링
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN,
    }
  },

  // Nitro 서버 설정 (API 프록시)
  nitro: {
    devProxy: {
      '/api': {
        target: process.env.NUXT_PROXY_TARGET,
        changeOrigin: true,
      }
    }
  },

  // App 설정
  app: {
    head: {
      title: '사주라인 - 전통과 혁신이 만나는 온라인 사주 상담',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { key: 'description', name: 'description', content: '전통 사주 상담 서비스' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})