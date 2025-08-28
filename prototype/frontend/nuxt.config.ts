// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  
  // TypeScript 설정 (일시적으로 타입 체크 비활성화)
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

  // SSR 활성화 (기본값이지만 명시적으로 설정)
  ssr: true,

  // 빌드 설정
  build: {
    transpile: []
  },

  // Vite 설정 (개발 서버 최적화)
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
    apiSecret: process.env.API_SECRET || 'your-api-secret-key',
    
    // Public keys (클라이언트에서도 접근 가능)
    public: {
      // 환경 설정
      environment: process.env.NUXT_PUBLIC_ENVIRONMENT || 'development',
      
      // API 설정
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
      apiTimeout: parseInt(process.env.NUXT_PUBLIC_API_TIMEOUT || '30000'),
      wsTimeout: parseInt(process.env.NUXT_PUBLIC_WS_TIMEOUT || '5000'),
      
      // 소셜 로그인 설정 (공개 키만)
      kakaoClientId: process.env.NUXT_PUBLIC_KAKAO_CLIENT_ID || '',
      naverClientId: process.env.NUXT_PUBLIC_NAVER_CLIENT_ID || '',
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID || '',
      
      // SEO & Meta 설정
      siteName: process.env.NUXT_PUBLIC_SITE_NAME || '사주라인',
      siteDescription: process.env.NUXT_PUBLIC_SITE_DESCRIPTION || '전통과 혁신이 만나는 온라인 사주 상담',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
      
      // CDN & Static Assets
      cdnUrl: process.env.NUXT_PUBLIC_CDN_URL || '',
      assetPrefix: process.env.NUXT_PUBLIC_ASSET_PREFIX || '',
      
      // 모니터링 & Analytics
      gaId: process.env.NUXT_PUBLIC_GA_ID || '',
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN || '',
      
      // Theme 설정
      defaultTheme: process.env.NUXT_PUBLIC_DEFAULT_THEME || 'light',
      themePersistence: process.env.NUXT_PUBLIC_THEME_PERSISTENCE === 'true',
      
      // 기능 플래그 (MVP: AI, 채팅, 결제 기능 제거)
      enableDebugMode: process.env.NUXT_PUBLIC_ENABLE_DEBUG_MODE === 'true',
      enableSocialLogin: process.env.NUXT_PUBLIC_ENABLE_SOCIAL_LOGIN === 'true',
      
      // 개발 설정
      mockApi: process.env.NUXT_PUBLIC_MOCK_API === 'true',
      hotReload: process.env.NUXT_PUBLIC_HOT_RELOAD === 'true',
      
      // 쿠키 기반 인증으로 변경됨 - 암호화 키 불필요
      }
  },

  // Nitro 서버 설정 (API 프록시)
  nitro: {
    devProxy: {
      '/api': {
        target: process.env.DOCKER_ENV ? 'http://backend:8000' : 'http://localhost:8000',
        changeOrigin: true,
        // prependPath를 true로 하거나 제거하여 /api 경로를 유지
      }
    }
  },

  // App 설정 (MVP: AI 관련 설명 제거)
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
  },

  // 환경별 설정 오버라이드
  $development: {
    // 개발 환경 특정 설정
    runtimeConfig: {
      public: {
        apiBase: 'http://localhost:8000',
        enableDebugMode: true,
        hotReload: true,
        mockApi: false,
      }
    }
  },

  $production: {
    // 프로덕션 환경 특정 설정
    runtimeConfig: {
      public: {
        apiBase: 'https://api.sajuline.com',
        enableDebugMode: false,
        hotReload: false,
        mockApi: false,
      }
    }
  }
})
