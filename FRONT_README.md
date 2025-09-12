## 사주라인 Frontend 아키텍처/상태 관리 정리 (Nuxt + Vue Query)

### TL;DR
- 인증: HttpOnly 쿠키 기반. 토큰은 JS에서 접근 불가, 세션 메타만 `localStorage('user_session')`에 영속.
- 서버통신: 전역 `$api` 플러그인(인터셉터 + 401 자동 리프레시 + 재시도) + 도메인별 컴포저블(`useUserQueries`, `useCounselorQueries`, `useAuthQueries`).
- 상태: 서버데이터는 Vue Query 캐시(SSR de/hydrate). UI/모달/토스트는 비영속 메모리. 인증 세션만 로컬스토리지 영속.
- 네임스페이스: Vue Query 키(`['user', id]`, `['users','list', params]`, `['availability','email', value]`, `['auth','me']`), 로컬스토리지 키(`user_session`), SSR 상태키(`useState('vue-query')`).

---

## 1) 기술 스택 개요
- Nuxt: `frontend/nuxt.config.ts` (SSR 활성, 하이브리드 `routeRules` 적용)
- 서버 통신: `$fetch` 기반 `$api` 플러그인 `frontend/plugins/api.client.ts`
- 서버 상태: TanStack Vue Query 플러그인 `frontend/plugins/vue-query.ts` (SSR de/hydration)
- 인증/도메인 훅: `frontend/composables/auth/*`, `frontend/composables/api/*`
- UI 유틸: `frontend/composables/ui/*`, `frontend/composables/utils/*`
- 타입: `frontend/types/*`
- Pinia: 모듈 로드(`@pinia/nuxt`)는 되어 있으나, 현재 `frontend` 디렉터리 내에는 Pinia 스토어 사용 없음(도입 여지만 존재).

---

## 2) 전역 API 클라이언트($api)와 에러/리프레시 정책
- 파일: `frontend/plugins/api.client.ts`
- 핵심:
  - `baseURL = runtimeConfig.public.apiBase`
  - `credentials: 'include'`로 HttpOnly 쿠키 자동 포함
  - onRequest: 공통 헤더 설정(Content-Type/Accept/X-Requested-With), 클라이언트에서 CSRF 메타 태그 반영
  - onResponse: 개발 로깅, 응답 헤더의 `x-csrf-token` → 메타 업데이트
  - onResponseError:
    - 401인 경우:
      - 로그인 요청은 갱신 시도 없이 에러 매핑
      - 그 외는 단일 비행(single-flight)로 `/v1/auth/refresh`(baseURL 상대) 호출 후 원 요청 재시도
      - 리프레시 실패 시 Notivue 알림 후 로그인 페이지로 이동
    - 403/5xx/4xx 별도 메시지 매핑

주의: 인증 리프레시 경로가 두 패턴 공존
- 플러그인 내부 자동 리프레시: `POST {apiBase}/v1/auth/refresh`
- 도메인 훅(아래) 수동 리프레시: `POST {apiBase}/api/v1/auth/refresh`
- 현재 코드 기준 두 경로 모두 사용되므로, `public.apiBase` 설정과 프록시 규칙으로 유효 경로가 되도록 환경을 일관되게 유지해야 합니다.

---

## 3) 서버 상태 관리(Vue Query)
- 파일: `frontend/plugins/vue-query.ts`
- 기본 옵션(요약):
  - queries: `staleTime=5m`, `gcTime=30m`, `refetchOnWindowFocus=false`, mount 시 always refetch, reconnect 시 refetch
  - 401/403/404는 재시도 안 함, 그 외 최대 3회 지수 백오프
  - mutations: 5xx에 한해 최대 2회 재시도
- SSR 연계:
  - 서버 렌더 종료 시 `dehydrate(queryClient)`를 `useState('vue-query')`에 저장
  - 클라이언트 앱 생성 시 `hydrate` 수행
- 영속성: 디스크(로컬스토리지 등)에는 저장하지 않음. 즉, 새로고침 시 캐시는 초기화되며 SSR로 초기 데이터만 복원됨.

---

## 4) 인증 상태와 세션 영속
- 파일: `frontend/composables/auth/useAuth.ts`
- 저장소:
  - 브라우저 쿠키(HttpOnly): access_token, refresh_token → JS 접근 불가(보안)
  - 로컬스토리지: `user_session` 키로 세션 메타 저장(로그인 시점, 만료 시각, 역할 등)
- 세션 스키마(`UserSession` in `frontend/types/user/models.ts`):
  - `user_id`, `email`, `nickname`, `isAuthenticated`, `loginAt`
  - `access_token_expires_at?`, `refresh_token_expires_at?`
  - `role: 'user' | 'counselor'`
- 동작:
  - 로그인: 이메일 형식이면 상담사, 아니면 사용자 로그인 API 선택 호출 → 성공 시 `user_session` 저장(만료 시각 포함)
  - 로그아웃: 역할에 따라 해당 로그아웃 API 호출 → 성공/실패와 무관하게 `user_session` 제거 후 `/login`
  - 초기화: 마운트 시 `localStorage('user_session')` 복원; access 만료 시 `attemptTokenRefresh()`로 갱신 시도
  - 주기 점검: 1분마다 토큰 만료 임박(≤5분) 시 `refresh` 시도
  - 가드: `requireAuth()`, `requireGuest()` 지원

---

## 5) 상태 분류표(영속/비영속/네임스페이스)

| 이름 | 소유/위치 | 영속성 | 네임스페이스/키 | 데이터 스키마 | 주요 용도 | 변경 트리거 |
|---|---|---|---|---|---|---|
| 인증 세션 | `composables/auth/useAuth.ts` | 영속(로컬스토리지) | `localStorage: 'user_session'` | `UserSession` | 로그인 상태 유지, 역할/만료 시각 추적 | 로그인/로그아웃, 토큰 갱신, 프로필 수정 |
| 인증 쿠키 | 서버(브라우저 쿠키) | 영속(HttpOnly) | 쿠키(`access_token`, `refresh_token`) | 토큰 본문 | 서버 호출 인증 | 로그인/리프레시/만료 |
| Vue Query 캐시 | `plugins/vue-query.ts` | 비영속(메모리) + SSR de/hydrate | `useState('vue-query')` | 쿼리 결과 | 서버데이터 캐싱 | 쿼리 무효화/갱신, 페이지 전환 |
| 사용자 쿼리들 | `composables/api/useUserQueries.ts` | 비영속 | Query Keys: `['user', id]`, `['users','list',params]` | 각 응답 타입 | 사용자 정보 조회/목록/중복검사 | 입력값 변화, 뮤테이션 성공 시 invalidate |
| 상담사 뮤테이션 | `composables/api/useCounselorQueries.ts` | 비영속 | Query Keys: `['counselor']`(무효화/제거 용) | 로그인 응답 | 상담사 로그인/로그아웃 | 호출 성공 시 캐시 무효화 |
| 인증 쿼리/뮤테이션 | `composables/api/useAuthQueries.ts` | 비영속 | `['auth','me']` | `AuthMePayload`/`TokenResponse` | whoAmI, 토큰 갱신 | 명시 호출 시 |
| 모달 상태 | `composables/ui/useModal.ts` | 비영속 | 내부 배열(`modals[]`) | 모달 메타 | 확인/알림/프롬프트/커스텀 다이얼로그 | 열기/닫기 호출 |
| 토스트/알림 | `composables/ui/useToast.ts`, `composables/utils/useNotify.ts` | 비영속 | 없음(즉시 호출) | 메시지 | 성공/오류/정보 노출 | 함수 호출 |

설계 원칙
- 서버데이터는 Vue Query로 일시 캐싱(필요시 invalidate). 디스크 영속은 세션 메타(`user_session`)만.
- UI 상태(모달/토스트)는 컴포넌트 수명 범위의 메모리로 한정.

---

## 6) 인증 플로우 상세
- 로그인
  - 사용자: `POST /api/v1/users/login`
  - 상담사: `POST /api/v1/counselors/login`
  - 성공 시 서버가 HttpOnly 쿠키 설정, 프론트는 `UserSession`에 만료시각/역할 등만 저장
- API 호출
  - 모든 호출은 `$api`로 수행(`credentials: 'include'`)
  - 응답 401 시: `$api` 인터셉터가 단일 비행으로 `POST {apiBase}/v1/auth/refresh` 호출 → 성공 시 원요청 재시도
- 수동/사전 갱신
  - `useAuth`는 1분 주기로 만료 임박 시 `useAuthQueries.useRefreshToken()`(경로: `/api/v1/auth/refresh`)로 갱신 시도
- 로그아웃
  - 역할별 로그아웃 API 호출 후 `user_session` 제거 및 `/login` 이동
- 권한/역할
  - `isAuthenticated`, `role`, `isUser`, `isCounselor`, `hasRole()` 제공
  - 페이지 가드: `requireAuth()`, `requireGuest()`

---

## 7) 훅 카탈로그(용도별)

### 인증/세션: `composables/auth/useAuth.ts`
- 상태: `userSession`, `isAuthenticated`, `role`, `isAuthChecking`
- 메서드: `login(credentials)`, `logout()`, `attemptTokenRefresh()`, `checkTokenExpiry()`, `restoreSession()`, `clearSession()`, `setRole()`, `hasRole()`, `updateUserInfo()`
- 가드: `requireAuth()`, `requireGuest()`

### 인증 API: `composables/api/useAuthQueries.ts`
- Queries: `useWhoAmI({ enabled: false })`
- Mutations: `useRefreshToken()`

### 사용자 API: `composables/api/useUserQueries.ts`
- Queries: `useUserById(userId)`, `useUserByEmail(email)`, `useUserList(params)`
- Availability: `useEmailAvailability(email)`, `useUserIdAvailability(userId)`, `usePhoneAvailability(phone)`, `useNicknameAvailability(nickname)`
- Mutations: `useSignupUser()`, `useUpdateUser()`, `useDeleteUser()`, `useLogin()`, `useLogout()`, `useAuthenticateUser()`
- 캐시 정책: 생성/수정/삭제/로그인/로그아웃 시 관련 키 invalidate 또는 제거 수행

### 상담사 API: `composables/api/useCounselorQueries.ts`
- Mutations: `useLogin()`, `useLogout()`(+ 관련 키 invalidate/remove)

### UI 유틸
- 모달: `composables/ui/useModal.ts` → `openDialog()`, `closeDialog()`, `confirm()`, `alert()`, `prompt()`, `showLoading()`, `closeAllDialogs()`
- 토스트: `composables/ui/useToast.ts` → `success()`, `error()`, `warning()`, `info()`, `message()`, `loading()`, `closeAll()`
- 알림: `composables/utils/useNotify.ts` → `notifySuccess()`, `notifyError()`, `notifyWarning()`, `notifyInfo()`

---

## 8) 네임스페이스 가이드
- Vue Query 키
  - 개체 단건: `['user', userId]`
  - 리스트: `['users','list', {page,size,...}]`
  - 가용성 검사: `['availability','email', email]`, `['availability','user-id', userId]`, ...
  - 인증: `['auth','me']`
- 로컬 스토리지 키: `'user_session'`
- SSR 상태 키: `useState('vue-query')`

---

## 9) 보안/에러 처리 정책
- 토큰은 항상 HttpOnly 쿠키로만 저장(XSS 방어). 프런트는 만료 시각 등 메타만 보유.
- 401 자동 처리: 인터셉터 기반 리프레시 → 실패 시 사용자 친화적 알림과 로그인 리다이렉트(지연 3초)
- 403/5xx/4xx는 표준화된 메시지로 변환(`createError`) 후 상위에서 핸들링 용이

---

## 10) 사용 레시피

### 인증이 필요한 화면 보호
```ts
const { requireAuth } = useAuth()
if (!requireAuth()) return
// 안전: 여기부터는 인증됨
```

### 만료 임박 시 사전 갱신 확인(수동 호출)
```ts
const { checkTokenExpiry } = useAuth()
await checkTokenExpiry()
```

### 사용자 단건 조회 + 캐시 무효화 예시
```ts
const { useUserById, useUpdateUser } = useUserQueries()
const user = useUserById(userId)
const updateUser = useUpdateUser()
await updateUser.mutateAsync({ userId, userData }) // 성공 시 관련 캐시 invalidate
```

---

## 11) 현재 구현상 주의사항(일관성)
- 토큰 리프레시 경로를 `/api/v1/auth/refresh`로 통일했습니다. `$api` 인터셉터와 `useAuthQueries` 모두 동일 경로를 사용합니다.
- `@pinia/nuxt`는 로드되나, `frontend` 디렉터리 내 실제 Pinia 스토어는 현재 없음(향후 도메인 스토어 도입 시 기준 합의 필요).

이 문서는 코드 기준 실제 동작을 정리했으며, 이후 일관성 정비(경로 규칙, 스토어 도입 등)는 별도 결정에 따릅니다.
