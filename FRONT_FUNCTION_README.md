## 프론트엔드 공용/패칭 함수 정리 (Sajuline Frontend)

본 문서는 Nuxt 기반 프론트엔드 프로젝트에서 사용되는 공용 유틸리티와 데이터 패칭(HTTP, vue-query) 구조를 요약합니다.

### 개요
- **HTTP 클라이언트**: `plugins/api.client.ts`에서 `$fetch.create`로 `$api` 제공 (HttpOnly 쿠키/인터셉터/에러 처리/자동 리프레시)
- **쿼리 클라이언트**: `plugins/vue-query.ts`에서 QueryClient 전역 설정 및 SSR dehydrate/hydrate
- **타입 규약**: `types/common/api.ts`의 `APIResponse<T>`, `APIError` 등 공용 타입
- **도메인 컴포저블**:
  - `composables/api/useUserQueries.ts` 사용자 관련 조회/변경/중복검사/로그인/로그아웃
  - `composables/api/useAuthQueries.ts` 인증(권한확인, 토큰갱신)
  - `composables/api/useCounselorQueries.ts` 상담사 로그인/로그아웃
- **공용 유틸리티**:
  - `composables/utils/useNotify.ts` Notivue 알림
  - `composables/ui/useToast.ts` Element Plus 토스트
  - `composables/ui/useModal.ts` Element Plus 모달/확인/알림/프롬프트/로딩
  - `composables/utils/validation.ts` 검증 함수
- **인증 상태**: `composables/auth/useAuth.ts` 세션/역할/토큰 자동갱신/가드

---

### 1) HTTP 클라이언트: `plugins/api.client.ts`
- `$api = $fetch.create({ baseURL, credentials: 'include', onRequest, onResponse, onResponseError })`
- 특징
  - HttpOnly 쿠키 자동 전송, 공통 헤더(JSON, X-Requested-With), CSRF 메타 토큰 반영
  - 401 처리 시 `/v1/auth/refresh`로 자동 갱신(동시성 제어), 성공 시 원요청 재시도
  - 로그인 요청은 예외적으로 갱신 시도 없이 에러 메시지 반환
  - 403/5xx/4xx 표준화된 에러 변환 `createError({ statusCode, statusMessage, data })`

간단 사용 예시
```ts
const { $api } = useNuxtApp()
const data = await $api<APIResponse<UserResponse>>('/api/v1/users/123')
if (!data.success || !data.data) throw new Error(data.error?.message ?? '오류')
return data.data
```

---

### 2) Vue Query 전역 설정: `plugins/vue-query.ts`
- 기본 옵션
  - queries: `staleTime=5m`, `gcTime=30m`, `refetchOnWindowFocus=false`, `refetchOnMount='always'`, `refetchOnReconnect=true`
  - retry 정책: 4xx(401/403/404) 재시도 안함, 5xx는 지수 백오프로 최대 3회
  - mutations: 5xx에서만 최대 2회 재시도
- SSR 지원: 서버 `dehydrate` → 클라이언트 `hydrate`

---

### 3) 공용 타입: `types/common/api.ts`
- `APIResponse<T>`: `{ success, message?, data?, error?, meta? }`
- `APIError`: `{ message, statusCode, data? }`
- 페이지네이션/정렬/검색 파라미터 공통 정의 포함

---

### 4) 도메인별 패칭 컴포저블

#### 4-1) 사용자: `composables/api/useUserQueries.ts`
- 호출 함수들
  - `getUserById(userId): Promise<UserResponse>`
  - `getUserByEmail(email): Promise<UserResponse>`
  - `getUserList({ page?, size?, user_status? }): Promise<UserListData>`
  - `signupUser(payload: UserCreateRequest): Promise<UserResponse>`
  - `login(credentials: LoginRequest): Promise<LoginData>`
  - `logout(): Promise<void>`
  - `authenticateUser(credentials): Promise<UserResponse>`
  - 가용성 검사: `checkEmailAvailability`, `checkUserIdAvailability`, `checkPhoneAvailability`, `checkNicknameAvailability`
- 쿼리 훅
  - `useUserById(userId, options?)` key: `['user', userId]`, `staleTime=10m`
  - `useUserByEmail(email, options?)` key: `['user', 'email', email]`, `staleTime=10m`
  - `useUserList(params, options?)` key: `['users', 'list', params]`, `staleTime=2m`
  - 실시간 중복 검사 쿼리 4종: key `['availability', ...]`, `staleTime=30s`, `retry=1`, 입력 유효성 기반 `enabled`
- 뮤테이션 훅
  - `useSignupUser`: 성공 시 목록 무효화 + 신규 유저 캐시 설정
  - `useUpdateUser`: 성공 시 상세/목록 무효화 + 캐시 갱신
  - `useDeleteUser`: 성공 시 관련 캐시 제거 + 목록 무효화
  - `useLogin`: 성공 시 사용자 관련 쿼리 무효화
  - `useLogout`: 성공 시 사용자 관련 캐시 제거

간단 사용 예시
```ts
const { useUserById, useUpdateUser } = useUserQueries()
const { data, isLoading } = useUserById(userId)
const updateMutation = useUpdateUser({
  onSuccess: (updated) => console.log('updated', updated)
})
updateMutation.mutate({ userId, userData })
```

#### 4-2) 인증: `composables/api/useAuthQueries.ts`
- 호출 함수
  - `whoAmI(): Promise<AuthMePayload>` → `/api/v1/auth/me`
  - `refreshToken(payload?): Promise<TokenResponse>` → `/api/v1/auth/refresh`
- 훅
  - `useWhoAmI(options?)` key: `['auth', 'me']`, 기본 `enabled=false`, `retry=0`, `staleTime=0`
  - `useRefreshToken(options?)` 뮤테이션

#### 4-3) 상담사: `composables/api/useCounselorQueries.ts`
- 호출 함수
  - `login(credentials): Promise<LoginData>` → `/api/v1/counselors/login`
  - `logout(): Promise<void>` → `/api/v1/counselors/logout`
- 훅
  - `useLogin(options?)`: 성공 시 `['counselor']` 쿼리 무효화
  - `useLogout(options?)`: 성공 시 `['counselor']` 관련 캐시 제거

---

### 5) 공용 유틸리티
- 알림: `useNotify()` → `{ notifySuccess, notifyError, notifyWarning, notifyInfo }`
- 토스트: `useToast()` / `toast` → `{ success, error, warning, info, message, loading, closeAll }`
- 모달: `useModal()` → 커스텀 다이얼로그 `openDialog/closeDialog/closeAllDialogs`, 기본 `confirm/alert/prompt`, `showLoading`
- 검증: `isEmailFormat(input: string): boolean`

---

### 6) 인증 상태 관리: `composables/auth/useAuth.ts`
- 세션 로컬 저장/복원, 역할 관리, 토큰 자동 갱신(만료 5분 이내 시 갱신 시도), 1분 주기 만료 체크
- 페이지 가드: `requireAuth()`, `requireGuest()`
- API 연동: 사용자/상담사 로그인/로그아웃 뮤테이션과 연계, `useAuthQueries().useRefreshToken` 사용

간단 사용 예시
```ts
const { login, logout, isAuthenticated, role } = useAuth()
await login({ user_id, password })
if (isAuthenticated.value) console.log('role:', role.value)
```

---

### 7) 환경설정 참고: `nuxt.config.ts`
- `runtimeConfig.public.apiBase`로 API 베이스 설정 (프록시는 `nitro.routeRules` 사용)
- Notivue/Element Plus 포함, 전역 CSS 로드, 폰트/이미지 최적화, 빌드 청크 분리

---

### 8) 공통 패턴 가이드
- `$api` 반환 타입은 항상 `APIResponse<T>`로 가정 → `success`와 `data` 확인 후 `data` 반환
- vue-query 쿼리 키는 도메인 중심으로 구성: 예) `['user', userId]`, `['users', 'list', params]`
- 중복 검사 등 실시간 검증은 `enabled` 조건을 엄격히 설정하여 불필요 호출 방지
- 인증 만료(401)는 플러그인에서 처리되므로, 화면단에서는 표준 에러 메시지 처리에 집중

---

### 9) 빠른 레시피
- 사용자 상세 받기
```ts
const { useUserById } = useUserQueries()
const { data, isLoading, error } = useUserById('u-123')
```
- 회원가입 후 목록/캐시 동기화
```ts
const { useSignupUser } = useUserQueries()
const signup = useSignupUser({ onSuccess: (u) => console.log('ok', u) })
signup.mutate(payload)
```
- 토큰 갱신 트리거
```ts
const { useRefreshToken } = useAuthQueries()
await useRefreshToken().mutateAsync({})
```
