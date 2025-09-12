## FRONTEND 페이지 렌더링 현황 요약 (Nuxt 3)

- 마지막 업데이트: 2025-09-11
- 대상: `frontend/` Nuxt 애플리케이션

### 전역 설정 (현재 적용)
- `ssr: true` (전역 SSR 활성)
- 파일 기반 라우팅 활성: `pages: true`
- `routeRules` (프로덕션/전역)
  - 프리렌더: `'/'`, `'/about'`, `'/terms'`, `'/privacy'`
  - SWR 캐시: `'/horoscope/**'` → `swr: 3600`, 헤더 `Cache-Control: max-age=3600`
  - 실시간 헤더: `'/chat/**'` → 헤더 `Cache-Control: no-cache`
  - CSR 강제: `'/profile/**'`, `'/settings/**'` → `ssr: false`
- Nitro `routeRules`
  - `'/api/**'` → `proxy: ${NUXT_PROXY_TARGET}/api/**`
  - `'/**'` → 보안 헤더(`X-Frame-Options: DENY` 등) 적용

### 페이지별 렌더링 상태 (현재 코드 기준)
- `pages/index.vue` → `/` : SSR, 프로덕션 프리렌더
- `pages/login.vue` → `/login` : SSR(기본)
- `pages/signup.vue` → `/signup` : SSR(기본), `definePageMeta({ layout: false })`
- `pages/mypage.vue` → `/mypage` : SSR(기본)
- `pages/counselor/mypage.vue` → `/counselor/mypage` : SSR(기본)
- `pages/profile.vue` → `/profile` : CSR (전역 `routeRules`에 의해 `ssr: false`)
- `pages/chat.vue` → `/chat` : SSR(기본), 전역 헤더 `no-cache`
- `pages/fortune.vue` → `/fortune` : SSR(기본)
- `pages/categories/index.vue` → `/categories` : SSR(기본)
- `pages/categories/[slug].vue` → `/categories/:slug` : SSR(기본)
- `pages/auth/role.vue` → `/auth/role` : SSR(기본)

### 비고
- 위 목록은 실제 `pages/` 내 존재하는 파일 기준입니다.
- 전역 `routeRules`에 정의된 `'/settings/**'` CSR, `'/about'`, `'/terms'`, `'/privacy'` 프리렌더는 설정 상 존재합니다(해당 경로의 페이지 파일 존재 여부와 무관한 현재 설정 정보).
