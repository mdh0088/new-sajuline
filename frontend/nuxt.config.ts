// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Nuxt 호환성 날짜 (기능 변경사항 추적용)
  compatibilityDate: '2025-01-01',
  // 개발자 도구 활성화
  devtools: { enabled: true },
  // SSR 활성화 (SEO 및 초기 렌더링 성능)
  ssr: true,
  
  // 하이브리드 렌더링 전략 (즉시 적용 권장)
  routeRules: {
    // 정적 페이지는 빌드 시점에 프리렌더링
    '/': { prerender: true },
    '/about': { prerender: true },
    '/terms': { prerender: true },
    '/privacy': { prerender: true },
    
    // 동적 콘텐츠는 SWR(Stale-While-Revalidate) 캐싱
    '/horoscope/**': { 
      headers: { 
        'Cache-Control': 'max-age=3600' // 1시간 캐시
      },
      swr: 3600 // 1시간 스테일 허용
    },
    '/chat/**': { 
      headers: {
        'Cache-Control': 'no-cache' // 채팅은 실시간성 중요
      }
    },
    
    // 사용자 프로필은 클라이언트 사이드 렌더링
    '/profile/**': { ssr: false },
    '/settings/**': { ssr: false }
  },
  
  // 앱 전역 설정
  app: {
    head: {
      titleTemplate: '%s - 사주라인',
      title: '사주라인',
      htmlAttrs: {
        lang: 'ko'
      },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI와 전문가의 하이브리드 사주 상담 플랫폼' },
        { name: 'format-detection', content: 'telephone=no' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // 전역 CSS 파일
  css: [
    '~/assets/css/main.css'
  ],

  // Nuxt 모듈 설정
  modules: [
    '@nuxt/image',        // 이미지 최적화
    '@nuxt/scripts',      // 스크립트 관리 (Analytics, 외부 스크립트)
    '@nuxt/icon',         // 아이콘 시스템
    '@nuxt/fonts',        // 웹폰트 최적화
    '@nuxtjs/tailwindcss', // Tailwind CSS
    '@pinia/nuxt',        // 상태 관리
    '@vueuse/nuxt',       // Vue 유틸리티 컬렉션
    ...(process.env.NODE_ENV === 'development' ? ['@nuxt/test-utils'] : [])
  ],

  // 이미지 최적화 설정 (즉시 적용 권장)
  image: {
    quality: 80,
    format: ['webp', 'avif', 'jpg', 'png'], // AVIF 추가 (최신 브라우저 최적화)
    densities: [1, 2, 3], // 레티나 디스플레이 대응
    screens: {
      xs: 375,   // iPhone SE 기준
      sm: 640,   // 큰 모바일
      md: 768,   // 태블릿
      lg: 1024,  // 작은 데스크톱
      xl: 1280,  // 데스크톱
      xxl: 1536  // 대형 데스크톱
    },
    domains: [], // 외부 이미지 도메인 (CDN 등)
    presets: {
      avatar: {
        modifiers: {
          format: 'webp',
          width: 80,
          height: 80,
          quality: 85
        }
      },
      hero: {
        modifiers: {
          format: 'webp',
          width: 1200,
          height: 630,
          quality: 90
        }
      }
    }
  },

  // 웹폰트 설정
  fonts: {
    families: [
      { name: 'Noto Sans KR', provider: 'google' }
    ]
  },

  // 런타임 환경변수 (서버/클라이언트 구분)
  runtimeConfig: {
    // 서버 전용 (민감한 정보)
    apiSecret: process.env.API_SECRET,
    proxyTarget: process.env.NUXT_PROXY_TARGET,
    
    // 클라이언트 공개 (브라우저에서 접근 가능)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
      kakaoClientId: process.env.NUXT_PUBLIC_KAKAO_CLIENT_ID,
      naverClientId: process.env.NUXT_PUBLIC_NAVER_CLIENT_ID,
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL,
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN
    }
  },

  // TypeScript 설정
  typescript: {
    strict: true,
    typeCheck: true
  },

  // 경로 별칭 설정
  alias: {
    '@': './src',
    '~': './',
    '@@': './',
    '~~': './',
    'assets': './assets',
    'public': './public',
    'components': './components',
    'composables': './composables',
    'layouts': './layouts',
    'middleware': './middleware',
    'pages': './pages',
    'plugins': './plugins',
    'stores': './stores',
    'types': './types',
    'utils': './utils'
  },

  // Vite 빌드 설정
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          // SCSS 전역 변수 자동 import
          additionalData: '@use "~/assets/scss/variables.scss" as *;'
        }
      }
    },
    build: {
      target: 'esnext',
      rollupOptions: {
        output: {
          chunkFileNames: '_nuxt/[name]-[hash].js',
          entryFileNames: '_nuxt/[name]-[hash].js'
        }
      }
    },
    optimizeDeps: {
      include: ['@tanstack/vue-query']
    }
  },

  // 개발 서버 프록시 설정 (CORS 해결) 및 보안 헤더 (즉시 적용 권장)
  nitro: {
    devProxy: {
      '/api': {
        target: process.env.NUXT_PROXY_TARGET,
        changeOrigin: true,
        prependPath: true
      }
    },
    // 보안 헤더 추가
    routeRules: {
      '/**': {
        headers: {
          'X-Frame-Options': 'DENY',
          'X-Content-Type-Options': 'nosniff',
          'Referrer-Policy': 'strict-origin-when-cross-origin',
          'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
          'X-XSS-Protection': '1; mode=block'
        }
      }
    }
  },

  // Nuxt 4.x 호환성 설정
  future: {
    compatibilityVersion: 4
  },

  // 성능 및 SEO 최적화
  experimental: {
    payloadExtraction: false,    // 페이로드 추출 비활성화 (성능)
    viewTransition: true         // 페이지 전환 애니메이션
  },

  // 라우터 설정
  router: {
    options: {
      scrollBehaviorType: 'smooth'  // 부드러운 스크롤
    }
  }
})