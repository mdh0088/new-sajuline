# 프론트엔드 디렉토리 구조 요약 (Nuxt 4 / Vue 3)

본 문서는 `frontend` 프로젝트의 실제 구조와 설정을 요약합니다. (작성일: 2025-09-11)

## 기술 스택
- 프레임워크: Nuxt ^4.0.3 (Vue 3)
- 상태관리: Pinia ^3
- 데이터패칭: @tanstack/vue-query ^5
- 유틸리티: @vueuse/nuxt
- UI: Element Plus, Notivue
- 스타일: Tailwind CSS ^3, 전역 CSS (`assets/css`)
- 번들러: Vite (Nuxt 내장)
- 타입: TypeScript (strict, typeCheck: true)

## 명령어 (package.json)
- dev: `nuxt dev`
- build: `nuxt build`
- generate: `nuxt generate`
- preview: `nuxt preview`

## 핵심 설정 파일
- `nuxt.config.ts`: SSR, routeRules, head(meta/og/twitter), modules, Notivue, image 최적화, fonts, runtimeConfig, typescript(strict), vite 최적화, nitro 보안/프록시, experimental, router 옵션 등 정의
- `tailwind.config.js`: 커스텀 컬러(`primary`), 폰트 패밀리(`Noto Sans KR`) 등 확장
- `tsconfig.json`: Nuxt가 생성하는 참조 tsconfig들을 포함(references)
- `app.vue`: 전역 레이아웃과 Notivue 마운트, 전역 CSS(`assets/css/main.css`) import

## 디렉토리 구조 (요약)
```
frontend/
├─ app.vue
├─ assets/
│  └─ css/
│     ├─ main.css
│     ├─ login/
│     │  └─ common.css
│     └─ signup/
│        ├─ common.css
│        ├─ signup_step1.css
│        ├─ signup_step2.css
│        ├─ signup_step3.css
│        └─ signup_step4.css
├─ components/
│  ├─ common/ (헤더/하단 네비 등 UI 공통)
│  ├─ home/ (홈 히어로/라이브 통계/퀵 상담/오늘의 운세)
│  ├─ auth/
│  │  ├─ login/ (LoginForm, SocialLogin)
│  │  └─ signup/ (스텝별 회원가입 컴포넌트, 약관 모달)
│  ├─ chat/
│  ├─ fortune/
│  └─ profile/
├─ composables/
│  ├─ api/ (useAuthQueries, useUserQueries, useCounselorQueries)
│  ├─ auth/ (useAuth)
│  ├─ ui/ (useModal, useToast)
│  ├─ utils/ (useNotify, validation)
│  └─ validation/ (useValidation)
├─ pages/
│  ├─ index.vue, login.vue, signup.vue, chat.vue, fortune.vue, mypage.vue, profile.vue
│  ├─ auth/role.vue
│  ├─ categories/index.vue, categories/[slug].vue
│  └─ counselor/mypage.vue
├─ plugins/
│  ├─ api.client.ts (브라우저 전용 API 클라이언트 초기화)
│  └─ vue-query.ts (Vue Query 설정)
├─ public/ (정적 파일: favicon, robots.txt, manifest)
├─ types/
│  ├─ auth/signup.ts
│  ├─ common/api.ts
│  └─ user/models.ts
├─ nuxt.config.ts, tailwind.config.js, tsconfig.json
└─ package.json, package-lock.json, README.md
```

## 라우팅/렌더링 전략
- 기본: SSR 활성화, `pages/` 기반 자동 라우팅
- 프리렌더: `/`, `/about`, `/terms`, `/privacy` (프로덕션에서만)
- 캐시(SWR): `/horoscope/**` (1시간 캐시)
- 실시간: `/chat/**` (no-cache)
- CSR 강제: `/profile/**`, `/settings/**`

## 런타임 환경변수
- 서버 전용: `apiSecret`, `proxyTarget`
- 클라이언트 공개: `apiBase`, `kakaoClientId`, `naverClientId`, `siteUrl`, `sentryDsn`

## 빌드/번들 최적화
- Vite build target `esnext`, 청크 네이밍 고정
- manualChunks: `vendor`(vue 등), `ui`(vue-query/vueuse/element-plus)
- optimizeDeps: vue-query, vueuse, element-plus 사전 최적화

## 보안/프록시(Nitro)
- `/api/**`를 `NUXT_PROXY_TARGET`으로 프록시
- 공통 보안 헤더 설정: X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-XSS-Protection

## 전역 스타일/Tailwind
- `assets/css/main.css` 전역 import (in `app.vue`)
- Tailwind 파일 스캔 경로: components/layouts/pages/plugins/app.vue/error.vue
- 커스텀 컬러 `primary`, 폰트 `Noto Sans KR`

## 자동 컴포넌트 import
- `~/components` 경로 전체 자동 import, `pathPrefix: false`

## 기타
- Dev 전용 모듈: `@nuxt/test-utils`, `@nuxt/devtools`
- 이미지 preset: `avatar`, `hero`
- experimental: `viewTransition` 활성화

