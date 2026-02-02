# Story 3.4: 운세 로딩/에러 UI

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **사용자**,
I want **운세 로딩 중과 에러 상황에서 적절한 피드백**,
So that **현재 상태를 명확히 인지하고 대응할 수 있다**.

## Acceptance Criteria

1. **AC 1 - 기본 로딩 상태**: Given 운세 API 호출 중일 때, When 로딩 상태가 표시되면, Then FortuneLoading 컴포넌트가 스켈레톤 UI로 표시된다. And "운세를 분석 중입니다..." 메시지가 표시된다. And 애니메이션 로딩 인디케이터가 표시된다.

2. **AC 2 - 장시간 로딩 피드백**: Given AI 운세 생성이 3초 이상 걸릴 때, When 로딩이 지속되면, Then "AI가 사주를 분석하고 있어요. 잠시만 기다려주세요" 메시지로 변경된다.

3. **AC 3 - 일반 에러 처리**: Given API 호출이 실패할 때, When 에러가 발생하면, Then FortuneError 컴포넌트가 표시된다. And 사용자 친화적 에러 메시지가 표시된다 (예: "운세를 불러오지 못했어요"). And "다시 시도" 버튼이 표시된다.

4. **AC 4 - 사주 정보 미등록 에러**: Given 사주 정보가 없는 사용자일 때, When 운세 페이지에 접근하면, Then "사주 정보를 먼저 등록해주세요" 메시지가 표시된다. And "사주 등록하기" 버튼이 프로필 페이지로 연결된다.

5. **AC 5 - 네트워크 오류 처리**: Given 네트워크 오류 시, When API 호출이 실패하면, Then "네트워크 연결을 확인해주세요" 메시지가 표시된다. And 오프라인 상태 아이콘이 표시된다.

## Tasks / Subtasks

- [x] **Task 1: FortuneLoading 컴포넌트 개선** (AC: 1, 2)
  - [x] 1.1. `frontend/components/fortune/FortuneLoading.vue` 파일 생성
  - [x] 1.2. Props: `isExtendedLoading: boolean` (3초 이상 로딩 상태)
  - [x] 1.3. 기본 메시지: "운세를 분석 중입니다..."
  - [x] 1.4. 확장 메시지: "AI가 사주를 분석하고 있어요. 잠시만 기다려주세요"
  - [x] 1.5. 애니메이션 로딩 인디케이터 (pulse + spin 조합)
  - [x] 1.6. FortuneCardSkeleton 컴포넌트 통합

- [x] **Task 2: FortuneError 컴포넌트 개선** (AC: 3, 4, 5)
  - [x] 2.1. `frontend/components/fortune/FortuneError.vue` 수정
  - [x] 2.2. Props 확장: `errorType: 'general' | 'saju_required' | 'network'`
  - [x] 2.3. 에러 타입별 아이콘 분기 (😢, 🎂, 📡)
  - [x] 2.4. 에러 타입별 메시지 분기
  - [x] 2.5. 네트워크 오류 시 오프라인 아이콘 표시

- [x] **Task 3: 운세 페이지 로딩 타이머 통합** (AC: 2)
  - [x] 3.1. `frontend/pages/fortune/index.vue` 수정
  - [x] 3.2. 3초 타이머 로직 추가 (useTimeout 또는 setTimeout)
  - [x] 3.3. `isExtendedLoading` 상태 관리
  - [x] 3.4. 로딩 완료 시 타이머 정리 (cleanup)

- [x] **Task 4: 에러 타입 자동 감지** (AC: 3, 4, 5)
  - [x] 4.1. 에러 응답에서 에러 타입 추출 로직
  - [x] 4.2. 네트워크 오류 감지 (navigator.onLine, fetch 에러)
  - [x] 4.3. `errorType` computed 속성 구현

- [x] **Task 5: 품질 검증** (AC: 1-5)
  - [x] 5.1. `npm run type-check` Story 3.4 관련 파일 타입 에러 없음 (기존 테스트 파일 및 다른 페이지 에러는 별도)
  - [x] 5.2. `npm run build` 빌드 확인
  - [x] 5.3. 로딩 타이머 테스트 (3초 전/후 메시지 변경)
  - [x] 5.4. 에러 타입별 UI 테스트
  - [x] 5.5. 접근성 테스트 (aria-live, role="alert")

## Dev Notes

### Previous Story Intelligence (Story 3.1, 3.2, 3.3)

**Story 3.1에서 완료된 구현물 (재사용 필수):**
- `frontend/composables/api/useFortune.ts` - 운세 API composable
  - `useFortuneApi().useFortune(type)` - 통합 쿼리 훅
  - `getFortuneErrorMessage(error)` - 에러 메시지 추출
  - `invalidateFortuneCache(type?)` - 캐시 무효화
  - `FortuneApiError` 클래스 - 타입 안전 에러 처리
- `frontend/types/fortune/index.ts` - 운세 타입 정의
  - `FortuneErrorCode = 'SAJU_INFO_REQUIRED' | 'INVALID_DATE_RANGE' | ...`

**Story 3.2에서 완료된 구현물 (재사용/수정 대상):**
- `frontend/components/fortune/FortuneCardSkeleton.vue` - 로딩 스켈레톤 (재사용)
- `frontend/components/fortune/FortuneError.vue` - 에러 컴포넌트 (수정 대상)
- `frontend/pages/fortune/index.vue` - 운세 페이지 (수정 대상)

**Story 3.3에서 완료된 구현물:**
- `frontend/components/fortune/FortuneTabs.vue` - 탭 컴포넌트
- URL 쿼리 파라미터 동기화 패턴
- 스와이프 제스처 패턴

**핵심 학습사항:**
- TanStack Query `isLoading` 상태로 로딩 관리
- `error` 객체에서 `extractErrorCode()` 함수로 에러 코드 추출
- FortuneError 컴포넌트: `isSajuRequired` prop으로 사주 미등록 분기
- 기존 FortuneCardSkeleton은 애니메이션 (`animate-pulse`) 포함

**Code Review 후 확립된 패턴:**
- 에러 처리: `FortuneApiError` 클래스 사용 (타입 안전)
- 접근성: `role="alert"`, `aria-live="polite"` 적용
- 버튼 최소 크기: 44px × 44px (NFR-A6)

### Architecture Compliance

**파일 위치 규칙:**
```
frontend/
├── pages/
│   └── fortune/
│       └── index.vue          # 운세 페이지 (수정)
└── components/
    └── fortune/
        ├── FortuneLoading.vue     # 로딩 컴포넌트 (신규)
        ├── FortuneError.vue       # 에러 컴포넌트 (수정)
        └── FortuneCardSkeleton.vue  # 기존 (재사용)
```

**네이밍 규칙:**
- 컴포넌트: PascalCase (`FortuneLoading.vue`)
- 함수/변수: camelCase (`isExtendedLoading`, `handleRetry`)
- Props 타입: Props interface (`interface Props {}`)
- Emits: kebab-case 이벤트명 (`@retry`)

### Technical Requirements

**FortuneLoading 컴포넌트 구조:**
```typescript
// components/fortune/FortuneLoading.vue
interface Props {
  /** 3초 이상 로딩 상태 여부 */
  isExtendedLoading?: boolean
}

withDefaults(defineProps<Props>(), {
  isExtendedLoading: false
})
```

**FortuneLoading 템플릿:**
```html
<template>
  <div class="text-center py-8">
    <!-- 로딩 인디케이터 -->
    <div class="relative mx-auto w-16 h-16 mb-4">
      <div class="absolute inset-0 rounded-full border-4 border-purple-600/20" />
      <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-600 animate-spin" />
      <div class="absolute inset-2 flex items-center justify-center text-2xl">🔮</div>
    </div>

    <!-- 로딩 메시지 -->
    <p
      class="text-white/80 mb-6"
      role="status"
      aria-live="polite"
    >
      {{ loadingMessage }}
    </p>

    <!-- 스켈레톤 UI -->
    <FortuneCardSkeleton />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FortuneCardSkeleton from './FortuneCardSkeleton.vue'

interface Props {
  isExtendedLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isExtendedLoading: false
})

const loadingMessage = computed(() => {
  return props.isExtendedLoading
    ? 'AI가 사주를 분석하고 있어요. 잠시만 기다려주세요'
    : '운세를 분석 중입니다...'
})
</script>
```

**FortuneError 컴포넌트 확장 (수정):**
```typescript
// components/fortune/FortuneError.vue
interface Props {
  /** 에러 메시지 */
  message?: string | null
  /** 에러 유형 */
  errorType?: 'general' | 'saju_required' | 'network'
}

// 기존 isSajuRequired prop → errorType === 'saju_required'로 마이그레이션
```

**에러 타입별 UI 분기:**
```typescript
const errorConfig = computed(() => {
  switch (props.errorType) {
    case 'saju_required':
      return {
        icon: '🎂',
        title: '사주 정보가 필요해요',
        description: '운세를 확인하려면 먼저 생년월일시 정보를 등록해주세요.',
        actionLabel: '사주 정보 등록하기',
        actionLink: '/user/edit'
      }
    case 'network':
      return {
        icon: '📡',
        title: '네트워크 오류',
        description: '네트워크 연결을 확인해주세요.',
        actionLabel: '다시 시도',
        actionLink: null
      }
    default:
      return {
        icon: '😢',
        title: '운세를 불러올 수 없어요',
        description: props.message || '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        actionLabel: '다시 시도',
        actionLink: null
      }
  }
})
```

**운세 페이지 로딩 타이머 (AC 2):**
```typescript
// pages/fortune/index.vue
import { ref, watch, onUnmounted } from 'vue'

const EXTENDED_LOADING_THRESHOLD = 3000 // 3초

const isExtendedLoading = ref(false)
let loadingTimer: NodeJS.Timeout | null = null

// 로딩 상태 감시
watch(isLoading, (loading) => {
  if (loading) {
    // 3초 타이머 시작
    loadingTimer = setTimeout(() => {
      isExtendedLoading.value = true
    }, EXTENDED_LOADING_THRESHOLD)
  } else {
    // 로딩 완료 시 타이머 정리
    if (loadingTimer) {
      clearTimeout(loadingTimer)
      loadingTimer = null
    }
    isExtendedLoading.value = false
  }
})

// 컴포넌트 언마운트 시 타이머 정리
onUnmounted(() => {
  if (loadingTimer) {
    clearTimeout(loadingTimer)
  }
})
```

**에러 타입 자동 감지 (AC 3, 4, 5):**
```typescript
// pages/fortune/index.vue
import { computed } from 'vue'

// 에러 타입 추출 함수
const getErrorType = (err: unknown): 'general' | 'saju_required' | 'network' => {
  // 네트워크 오류 체크
  if (!navigator.onLine) {
    return 'network'
  }

  // Fetch 에러 체크
  if (err instanceof TypeError && err.message.includes('fetch')) {
    return 'network'
  }

  // 서버 에러 코드 체크
  const errorCode = extractErrorCode(err)
  if (errorCode === 'SAJU_INFO_REQUIRED') {
    return 'saju_required'
  }

  return 'general'
}

const errorType = computed(() => {
  if (!error.value) return 'general'
  return getErrorType(error.value)
})
```

### UI/UX Design Guidelines

**로딩 인디케이터 디자인 (기존 보라색 테마 준수):**
- 스피너: 보라색 (`border-t-purple-600`) + 회전 애니메이션 (`animate-spin`)
- 중앙 아이콘: 🔮 (운세 아이콘)
- 배경: 투명 보라색 링 (`border-purple-600/20`)

**에러 UI 디자인:**
- 배경: 빨간색 그라데이션 (`from-red-600/10 to-red-700/5`)
- 테두리: 빨간색 (`border-red-600/20`)
- 네트워크 오류: 노란색/주황색 톤으로 변경 고려

**접근성 필수 요소:**
- `role="status"` - 로딩 메시지
- `aria-live="polite"` - 동적 메시지 변경 알림
- `role="alert"` - 에러 메시지
- 버튼 최소 크기: 44px × 44px (NFR-A6)

### Library/Framework Requirements

**이미 설치된 패키지 (설치 불필요):**
- `@tanstack/vue-query` - 데이터 페칭 (isLoading, error 상태)
- `nuxt` 3.17+ - SSR/CSR 프레임워크
- `vue` 3.5+ - Vue 3 Composition API
- `tailwindcss` - 스타일링 (animate-spin, animate-pulse)

**신규 패키지 필요 없음**

### Testing Requirements

**품질 검사 명령어:**
```bash
cd frontend
npm run type-check   # TypeScript 타입 체크
npm run build        # 프로덕션 빌드 확인
```

**수동 테스트 시나리오:**

1. **로딩 상태 테스트**
   - 운세 API 호출 시 FortuneLoading 컴포넌트 표시 확인
   - 스켈레톤 UI + 로딩 인디케이터 표시 확인
   - "운세를 분석 중입니다..." 메시지 확인

2. **장시간 로딩 테스트 (AC 2)**
   - DevTools Network → Throttling → Slow 3G 설정
   - 3초 후 메시지 변경 확인: "AI가 사주를 분석하고 있어요..."
   - 로딩 완료 시 메시지 초기화 확인

3. **에러 상태 테스트 (AC 3)**
   - Backend 서버 중지 후 API 호출 → 에러 UI 표시 확인
   - "운세를 불러올 수 없어요" 메시지 확인
   - "다시 시도" 버튼 동작 확인

4. **사주 미등록 테스트 (AC 4)**
   - 사주 정보 없는 계정으로 로그인
   - 운세 페이지 접근 → 사주 등록 안내 UI 확인
   - "사주 정보 등록하기" 버튼 클릭 → /user/edit 이동 확인

5. **네트워크 오류 테스트 (AC 5)**
   - 브라우저 오프라인 모드 활성화 (DevTools → Network → Offline)
   - 운세 페이지 새로고침 → 네트워크 오류 UI 확인
   - "네트워크 연결을 확인해주세요" 메시지 확인
   - 📡 아이콘 표시 확인

6. **접근성 테스트**
   - 스크린 리더에서 로딩 메시지 변경 알림 확인 (aria-live)
   - 에러 메시지 role="alert" 동작 확인
   - 키보드로 "다시 시도" 버튼 접근 가능 확인

### Project Structure Notes

**기존 컴포넌트 재사용:**
- `FortuneCardSkeleton.vue` - FortuneLoading 내부에서 사용

**수정 대상 파일:**
- `components/fortune/FortuneError.vue` - errorType prop 추가, UI 분기
- `pages/fortune/index.vue` - FortuneLoading 통합, 로딩 타이머, 에러 타입 감지

**신규 파일:**
- `components/fortune/FortuneLoading.vue` - 로딩 컴포넌트

### Anti-Pattern Prevention

**절대 하지 말 것:**
1. **FortuneCardSkeleton 중복 구현 금지** - FortuneLoading 내부에서 import하여 사용
2. **setTimeout 정리 누락 금지** - onUnmounted에서 반드시 clearTimeout
3. **에러 타입 하드코딩 금지** - extractErrorCode 함수 재사용
4. **navigator.onLine 단독 사용 금지** - fetch 에러도 함께 체크
5. **aria-live 누락 금지** - 동적 메시지는 반드시 aria-live 적용
6. **isSajuRequired prop 유지 금지** - errorType으로 마이그레이션 (하위 호환성 제거)

### Backward Compatibility

**FortuneError 컴포넌트 마이그레이션:**
- 기존: `isSajuRequired: boolean` prop
- 신규: `errorType: 'general' | 'saju_required' | 'network'` prop
- 전환 전략: isSajuRequired → errorType === 'saju_required' 내부 변환 일시 지원 후 제거

**pages/fortune/index.vue 수정:**
- 기존: `<FortuneCardSkeleton />` 직접 사용
- 신규: `<FortuneLoading :is-extended-loading="isExtendedLoading" />`
- 에러: `<FortuneError :error-type="errorType" ... />`

### References

- [Source: frontend/composables/api/useFortune.ts#extractErrorCode] - 에러 코드 추출 함수
- [Source: frontend/types/fortune/index.ts#FortuneErrorCode] - 에러 코드 타입
- [Source: frontend/components/fortune/FortuneCardSkeleton.vue] - 기존 스켈레톤 컴포넌트
- [Source: frontend/components/fortune/FortuneError.vue] - 기존 에러 컴포넌트 (수정 대상)
- [Source: frontend/pages/fortune/index.vue] - 현재 운세 페이지 (수정 대상)
- [Source: _bmad-output/implementation-artifacts/3-3-fortune-period-tabs.md] - Story 3.3 컨텍스트
- [Source: _bmad-output/planning-artifacts/epics.md#story-3.4] - 스토리 요구사항
- [Source: docs/architecture/implementation-patterns-consistency-rules.md] - 구현 패턴 규칙

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- 타입 체크 에러: 기존 테스트 파일(vitest, @vue/test-utils) 및 다른 페이지(counselor/mypage.vue, user/find-id.vue) 관련 - Story 3.4 무관
- 빌드: 정상 진행 (client 2002 modules transformed)

### Completion Notes List

- **2026-02-02**: Story 3.4 구현 완료
  - FortuneLoading 컴포넌트 신규 생성 (AC 1, 2)
  - FortuneError 컴포넌트 errorType prop 확장 (AC 3, 4, 5)
  - 3초 로딩 타이머 및 확장 메시지 구현
  - 네트워크 오류 자동 감지 및 오프라인 아이콘 표시
  - 접근성: role="status", aria-live="polite", role="alert" 적용
  - 버튼 최소 크기 44px x 44px 준수 (NFR-A6)

- **2026-02-02**: Code Review 수정 완료
  - [H1] extractErrorCode 함수 중복 제거 - useFortune.ts에서 export 후 index.vue에서 import
  - [H2] FortuneErrorType 타입 위치 이동 - types/fortune/index.ts로 중앙화
  - [M1] handleRetry 함수에 try-catch 에러 처리 추가
  - [M3] FortuneLoading.vue 불필요한 Vue import 제거 (Nuxt 3 auto-import 활용)
  - [M4] FortuneError.vue 오프라인 상태 텍스트 접근성 개선 (div→p 태그)

### File List

**신규 파일:**
- `frontend/components/fortune/FortuneLoading.vue` - 로딩 컴포넌트 (AC 1, 2)

**수정 파일:**
- `frontend/components/fortune/FortuneError.vue` - errorType prop 추가, 에러 타입별 UI 분기 (AC 3, 4, 5)
- `frontend/pages/fortune/index.vue` - FortuneLoading 통합, 로딩 타이머, 에러 타입 감지
- `frontend/types/fortune/index.ts` - FortuneErrorType 타입 추가 (Code Review H2)
- `frontend/composables/api/useFortune.ts` - extractErrorCode 함수 export 추가 (Code Review H1)

### Change Log

- **2026-02-02**: Story 3.4 구현 - 운세 로딩/에러 UI 개선
- **2026-02-02**: Code Review 수정 - H1, H2, M1, M3, M4 이슈 해결
