# 브레인스토밍 세션: AI BI 어시스턴트 프론트엔드 통합

**날짜:** 2026-02-04
**주제:** admin-backend LangGraph AI BI 어시스턴트를 admin-front 대시보드에 el-drawer 채팅으로 통합
**참여자:** DongDong
**진행 방법:** SCAMPER + Mind Mapping + Starbursting

---

## 1. 브레인스토밍 목표

**주제 (Objective):**
admin-backend에 구현된 LangGraph 기반 AI BI 어시스턴트를 admin-front 대시보드 페이지에 Element Plus el-drawer를 활용한 채팅 UI로 통합

**현재 상황 (Context):**

### Backend (admin-backend)
- ✅ LangGraph 기반 Multi-Agent 오케스트레이션 완성
- ✅ SSE 스트리밍 API 구현 (`POST /api/v1/ai/chat?stream=true`)
- ✅ Text-to-SQL 기능 (MariaDB, MSSQL 2005, GA4)
- ✅ 4-Layer Security 적용
- ✅ 이벤트 타입: thinking, query, executing, result, done

### Frontend (admin-front)
- **기술 스택**: Vue 3.5.22 + TypeScript 5.5.4 + Element Plus 2.7.8
- **상태 관리**: Pinia
- **HTTP**: Axios (withCredentials, 120초 타임아웃)
- **인증**: HttpOnly 쿠키 + localStorage adminInfo
- **대시보드**: indexDashboard.vue (starterMain + RevenueChart)
- ❌ **SSE/WebSocket 사용 경험 없음**

**MVP 범위:**
1. Element Plus el-drawer로 채팅 UI 구현
2. 자연어 질의 입력 및 전송
3. SSE 스트리밍 응답 (타이핑 효과)
4. 빠른 질문 버튼 (옵션)

**원하는 결과 (Desired Outcome):**
- 구현 가능한 통합 전략 수립
- 기술적 구현 방안 도출
- Phase 1 MVP 범위 명확화
- Phase 2 확장 로드맵

---

## 2. 브레인스토밍 기법 적용

### 2.1 SCAMPER 기법

#### S (Substitute) - 대체
- **정적 통계 카드 → AI 인사이트 카드**: 클릭 시 drawer 열림
- **텍스트 입력 → 음성 입력**: Phase 2 고려
- **단순 텍스트 응답 → 구조화된 카드**: Element Plus 컴포넌트 활용

#### C (Combine) - 결합
- **채팅 + 빠른 질문 버튼**: Drawer 상단에 예시 질문 칩 (el-tag)
- **스트리밍 + 로딩 애니메이션**: el-skeleton + 타이핑 인디케이터
- **채팅 + 액션 버튼**: 응답 옆 "새 탭", "CSV 다운로드"

#### A (Adapt) - 적용
- **ChatGPT 스타일 UI**: 사용자 오른쪽, AI 왼쪽 정렬 + 아바타
- **Slack 스타일**: 쓰레드 그룹화, 이모지 반응
- **Element Plus 패턴**: el-timeline, el-skeleton, el-statistic

#### M (Modify) - 변경
- **Drawer 크기**: 기본 50%, 확장 70%, 최소 30% (모바일)
- **메시지 표시**: Markdown 지원 (표, 코드블록)
- **입력창**: 단일 → 멀티 라인 (긴 질의)

#### P (Put to other uses) - 다른 용도
- **다른 페이지 적용**: 상담사 페이지, 결제 페이지에도 AI 채팅
- **재사용 컴포넌트**: `<AIChatDrawer>` 글로벌 컴포넌트화

#### E (Eliminate) - 제거
- ❌ 복잡한 설정 메뉴
- ❌ 과도한 애니메이션
- ✅ 최소한의 UI로 시작

#### R (Reverse/Rearrange) - 역순/재배열
- **프로액티브 알림**: AI가 먼저 "매출이 평소보다 20% 낮습니다" 알림
- **역순 레이아웃**: 입력창을 상단으로 (실험적)

---

### 2.2 Mind Mapping - 아키텍처 구조화

```
AI BI Drawer 채팅
├── 1. 프론트엔드 아키텍처
│   ├── 컴포넌트 구조
│   │   ├── AIChatDrawer.vue (메인)
│   │   ├── ChatMessage.vue (메시지)
│   │   ├── ChatInput.vue (입력창)
│   │   ├── QuickQuestions.vue (빠른 질문)
│   │   └── StreamingIndicator.vue (타이핑)
│   ├── 상태 관리
│   │   ├── Pinia Store: useAIChatStore
│   │   ├── messages: Message[]
│   │   ├── isStreaming: boolean
│   │   └── drawerVisible: boolean
│   └── API 레이어
│       ├── aiChatApi.ts
│       ├── SSE 연결 관리
│       └── 에러 핸들링
│
├── 2. SSE 스트리밍 구현
│   ├── EventSource 설정
│   │   ├── withCredentials: true
│   │   ├── 재연결 로직 (3회, 3초 간격)
│   │   └── 타임아웃 처리 (60초)
│   ├── 이벤트 타입
│   │   ├── thinking: 분석 중
│   │   ├── query: SQL 생성
│   │   ├── executing: 실행 중
│   │   ├── result: 결과 도착
│   │   └── done: 완료
│   └── 스트림 파싱
│       ├── data: JSON 파싱
│       ├── 청크 누적
│       └── UI 업데이트
│
├── 3. UI/UX 디자인
│   ├── Drawer 레이아웃
│   │   ├── 헤더: 타이틀 + 닫기
│   │   ├── 본문: 스크롤 영역
│   │   └── 푸터: 입력창
│   ├── 메시지 스타일
│   │   ├── 사용자: 오른쪽, 파란색
│   │   ├── AI: 왼쪽, 회색
│   │   └── 타임스탬프
│   ├── 응답 포맷
│   │   ├── 텍스트: Markdown
│   │   ├── 테이블: el-table
│   │   ├── 숫자: el-statistic
│   │   └── 로딩: el-skeleton
│   └── 애니메이션
│       ├── Drawer open/close
│       ├── 메시지 fade-in
│       └── 타이핑 indicator
│
├── 4. 데이터 흐름
│   ├── 요청 흐름
│   │   ├── 사용자 입력
│   │   ├── 유효성 검증
│   │   ├── API 호출
│   │   └── SSE 연결
│   ├── 응답 흐름
│   │   ├── SSE 이벤트 수신
│   │   ├── 타입별 처리
│   │   ├── Store 업데이트
│   │   └── UI 렌더링
│   └── 에러 흐름
│       ├── 네트워크 에러
│       ├── 타임아웃
│       └── 사용자 알림
│
├── 5. 통합 포인트
│   ├── 대시보드 진입점
│   │   ├── FAB 버튼 (우하단 고정)
│   │   ├── 헤더 아이콘
│   │   └── 통계 카드 클릭
│   ├── 인증 연동
│   │   ├── adminInfo 활용
│   │   ├── 쿠키 자동 전송
│   │   └── 권한 체크
│   └── 기존 API 재사용
│       ├── http.ts 인터셉터
│       └── 에러 핸들링
│
└── 6. 확장성
    ├── Phase 2 기능
    │   ├── 대화 히스토리
    │   ├── 북마크
    │   └── 공유
    ├── 다른 페이지 적용
    │   ├── 글로벌 컴포넌트화
    │   └── 컨텍스트 주입
    └── 고급 기능
        ├── 음성 입력
        ├── 차트 생성
        └── 자동 새로고침
```

---

### 2.3 Starbursting - 구현 질문 탐색

#### Who (누가?)
- **Q1**: 누가 이 기능을 주로 사용하나요?
  - A: 사이트 관리자 (김관리), CS 매니저 (박씨에스)
- **Q2**: 누가 컴포넌트를 개발하나요?
  - A: 프론트엔드 개발자 (Vue 3 + TypeScript 경험)
- **Q3**: 누가 SSE 연결을 관리하나요?
  - A: aiChatApi.ts 모듈 (EventSource 래퍼)

#### What (무엇을?)
- **Q4**: 무엇을 화면에 표시하나요?
  - A: 사용자 질의, AI 응답, 로딩 상태, 에러 메시지
- **Q5**: 무엇을 Pinia Store에 저장하나요?
  - A: messages[], isStreaming, drawerVisible, sessionId
- **Q6**: 무엇을 백엔드로 전송하나요?
  - A: `{ question: string, stream: true }`
- **Q7**: 무엇을 SSE로 받나요?
  - A: `{ event: "thinking|query|executing|result|done", data: {...} }`

#### Where (어디에?)
- **Q9**: Drawer를 어디에 마운트하나요?
  - A: indexDashboard.vue의 최상위 레벨
- **Q10**: SSE 엔드포인트는?
  - A: `POST /api/v1/ai/chat?stream=true`
- **Q11**: 컴포넌트 파일 위치?
  - A: `/src/components/ai-chat/`
- **Q12**: API 파일 위치?
  - A: `/src/api/ai-chat/aiChatApi.ts`

#### When (언제?)
- **Q13**: Drawer는 언제 열리나요?
  - A: FAB 버튼 클릭, 헤더 아이콘 클릭, 통계 카드 클릭
- **Q14**: SSE 연결은 언제 시작되나요?
  - A: 메시지 전송 직후
- **Q15**: 언제 재연결을 시도하나요?
  - A: 연결 끊김 후 3초 후 (최대 3회)
- **Q16**: 언제 타임아웃 처리하나요?
  - A: 60초 응답 없으면

#### Why (왜?)
- **Q18**: 왜 el-drawer를 선택했나요?
  - A: Element Plus 기존 사용, 일관된 UI, 모바일 대응
- **Q19**: 왜 SSE를 사용하나요?
  - A: 실시간 스트리밍, WebSocket보다 간단, 재연결 자동
- **Q20**: 왜 Pinia Store를 사용하나요?
  - A: 대화 상태 전역 관리, 다른 컴포넌트 접근 가능
- **Q21**: 왜 컴포넌트를 분리하나요?
  - A: 재사용성, 테스트 용이성, 유지보수성

#### How (어떻게?)
- **Q22**: SSE를 어떻게 구현하나요?
```typescript
const eventSource = new EventSource('/api/v1/ai/chat?stream=true', {
  withCredentials: true
});
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  handleSSEEvent(data);
});
```

- **Q23**: 타이핑 효과를 어떻게 구현하나요?
  - A: SSE 청크를 받을 때마다 문자열 누적 + Vue watch로 UI 업데이트

- **Q24**: 에러를 어떻게 처리하나요?
  - A: try-catch + Element Plus Message 알림 + 재시도 버튼

- **Q25**: Markdown을 어떻게 렌더링하나요?
  - A: `marked` 라이브러리 또는 Element Plus v-html + sanitize

- **Q26**: 테이블 데이터를 어떻게 표시하나요?
  - A: SSE result 이벤트에서 data.rows를 el-table에 바인딩

- **Q27**: 스크롤을 어떻게 관리하나요?
  - A: 새 메시지 추가 시 `scrollIntoView({ behavior: 'smooth' })`

- **Q28**: 재연결을 어떻게 구현하나요?
```typescript
eventSource.onerror = () => {
  if (retryCount < 3) {
    setTimeout(() => reconnect(), 3000);
    retryCount++;
  }
};
```

---

## 3. 생성된 아이디어 (총 19개)

### 카테고리 1: 핵심 구현 (MVP) - 5개

**1. AIChatDrawer.vue 메인 컴포넌트**
- el-drawer with 50% width
- 헤더: 타이틀 + 닫기 버튼
- 본문: 메시지 리스트 (스크롤)
- 푸터: ChatInput 컴포넌트

**2. SSE 스트리밍 연결**
- aiChatApi.ts에 EventSource 래퍼
- 이벤트 타입별 핸들러 (thinking, query, executing, result, done)
- 재연결 로직 (3회, 3초 간격)
- withCredentials: true

**3. Pinia Store (useAIChatStore)**
```typescript
{
  messages: Message[],
  isStreaming: boolean,
  drawerVisible: boolean,
  currentSessionId: string | null,
  actions: {
    sendMessage(text: string),
    addMessage(message: Message),
    clearMessages()
  }
}
```

**4. ChatMessage.vue 컴포넌트**
- 사용자/AI 구분 (role: 'user' | 'assistant')
- 타임스탬프
- 마크다운 렌더링 (marked 라이브러리)
- 테이블 표시 (el-table)

**5. ChatInput.vue**
- el-input with append slot (전송 버튼)
- Enter 키로 전송 (Shift+Enter는 줄바꿈)
- 전송 중 disabled
- 플레이스홀더: "무엇을 도와드릴까요?"

---

### 카테고리 2: UX 개선 - 5개

**6. 빠른 질문 버튼 (QuickQuestions.vue)**
- el-tag 스타일의 질문 칩
- 예시: "오늘 매출", "이번 주 결제 건수", "신규 가입자"
- 클릭 시 자동 입력

**7. 타이핑 인디케이터**
- SSE "thinking" 이벤트 시 애니메이션
- "AI가 생각 중입니다..." (3개 점 애니메이션)
- el-skeleton 활용

**8. FAB 버튼 (Floating Action Button)**
- 대시보드 우하단 고정
- 아이콘: 💬 또는 Element Plus ChatDotRound
- 클릭 시 Drawer 열림
- 뱃지: 새 알림 개수 (Phase 2)

**9. 스크롤 애니메이션**
- 새 메시지 추가 시 부드럽게 스크롤
- "맨 아래로" 버튼 (스크롤 위치가 위일 때)

**10. 메시지 액션 버튼**
- 복사 버튼
- 새 탭으로 보기
- CSV 다운로드 (테이블 데이터)

---

### 카테고리 3: 에러 처리 - 3개

**11. 네트워크 에러 처리**
- SSE 연결 실패 시 Element Plus Message 알림
- "재시도" 버튼 표시
- 3회 실패 시 "서비스 일시 중단" 메시지

**12. 타임아웃 처리**
- 60초 응답 없으면 연결 종료
- "응답 시간 초과" 메시지 + 재시도 버튼

**13. 사용자 친화적 에러 메시지**
- 백엔드 에러 코드를 읽기 쉬운 메시지로 변환
- 예: "AI_ERR_001" → "잠시 후 다시 시도해주세요"

---

### 카테고리 4: 통합 & 배포 - 3개

**14. 대시보드 통합**
- indexDashboard.vue에 AIChatDrawer 추가
- FAB 버튼 추가
- 헤더에 AI 아이콘 추가 (선택)

**15. API 엔드포인트 설정**
- .env 파일에 AI_CHAT_API_URL 추가
- http.ts에 SSE 타임아웃 설정

**16. 빌드 최적화**
- 컴포넌트 lazy loading
- marked 라이브러리 dynamic import

---

### 카테고리 5: Phase 2 기능 - 3개

**17. 대화 히스토리**
- 이전 대화 불러오기
- 로컬스토리지 또는 백엔드 저장

**18. 북마크**
- 중요한 답변 북마크
- 북마크 목록 페이지

**19. 차트 자동 생성**
- 숫자 데이터 → amCharts 차트
- "차트로 보기" 버튼

---

## 4. 핵심 인사이트 (Key Insights)

### Insight 1: SSE 스트리밍은 EventSource + Pinia로 간단히 구현 가능

**출처**: Mind Mapping (데이터 흐름), Starbursting (How Q22)
**Impact**: High | **Effort**: Low

**설명**:
Vue 3에서 SSE를 구현하는 가장 간단한 방법은 EventSource API를 사용하고, Pinia Store로 상태 관리하는 것입니다.

**Why it matters**:
- SSE 경험이 없는 팀도 빠르게 구현 가능
- 재연결 로직이 내장되어 안정적
- admin-backend의 SSE 엔드포인트와 완벽 호환

**구현 예시**:
```typescript
// aiChatApi.ts
export function connectSSE(question: string, onMessage: (data: any) => void) {
  const eventSource = new EventSource(
    `/api/v1/ai/chat?stream=true&question=${encodeURIComponent(question)}`,
    { withCredentials: true }
  );

  eventSource.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  });

  return eventSource; // 나중에 close() 호출
}
```

---

### Insight 2: Element Plus 기존 패턴 활용으로 개발 속도 3배 향상

**출처**: SCAMPER (Adapt), Mind Mapping (UI/UX 디자인)
**Impact**: High | **Effort**: Low

**설명**:
admin-front가 이미 Element Plus를 사용 중이므로, el-drawer, el-input, el-table 등을 활용하면 빠르게 UI를 구성할 수 있습니다.

**Why it matters**:
- 일관된 디자인 시스템
- 접근성(Accessibility) 자동 지원
- 모바일 반응형 자동 처리
- 개발 시간 단축 (커스텀 컴포넌트 불필요)

**재사용 컴포넌트**:
- el-drawer: 채팅 메인 컨테이너
- el-input: 메시지 입력창
- el-table: 쿼리 결과 테이블
- el-statistic: 숫자 결과 표시
- el-skeleton: 로딩 상태
- el-tag: 빠른 질문 버튼
- el-message: 에러 알림

---

### Insight 3: 컴포넌트 분리로 재사용성 및 확장성 확보

**출처**: SCAMPER (Put to other uses), Mind Mapping (확장성)
**Impact**: Medium | **Effort**: Low

**설명**:
AIChatDrawer를 독립적인 컴포넌트로 만들면, 대시보드뿐만 아니라 다른 페이지(상담사, 결제 등)에서도 쉽게 재사용할 수 있습니다.

**Why it matters**:
- 코드 중복 방지
- 다른 페이지에 1줄로 추가 가능: `<AIChatDrawer />`
- 유지보수 용이 (한 곳만 수정하면 전체 적용)
- Phase 2에서 컨텍스트별 질의 지원 가능

**컴포넌트 구조**:
```
/src/components/ai-chat/
├── AIChatDrawer.vue      # 메인 컴포넌트 (재사용 가능)
├── ChatMessage.vue       # 메시지 표시
├── ChatInput.vue         # 입력창
├── QuickQuestions.vue    # 빠른 질문
└── StreamingIndicator.vue # 타이핑 애니메이션
```

---

### Insight 4: 타이핑 효과는 청크 누적 + Vue watch로 간단 구현

**출처**: Starbursting (How Q23), Mind Mapping (SSE 스트리밍)
**Impact**: Medium | **Effort**: Low

**설명**:
SSE에서 청크를 받을 때마다 문자열을 누적하고, Vue의 반응성 시스템을 활용하면 자연스러운 타이핑 효과를 구현할 수 있습니다.

**Why it matters**:
- 사용자 경험 향상 (ChatGPT 스타일)
- 복잡한 애니메이션 라이브러리 불필요
- Vue 3 Composition API의 `ref`만으로 구현 가능

**구현 예시**:
```typescript
// useAIChatStore.ts
const currentMessage = ref('');

function handleSSEChunk(chunk: string) {
  currentMessage.value += chunk; // 누적
}

// ChatMessage.vue에서 자동으로 렌더링됨
```

---

### Insight 5: FAB 버튼으로 진입 장벽 최소화

**출처**: SCAMPER (Adapt - ChatGPT/Slack 패턴), Mind Mapping (통합 포인트)
**Impact**: High | **Effort**: Low

**설명**:
대시보드 우하단에 고정된 FAB(Floating Action Button)을 추가하면, 사용자가 언제든지 AI 채팅에 접근할 수 있습니다.

**Why it matters**:
- 발견 가능성(Discoverability) 향상
- 어느 페이지에서든 접근 가능
- 모바일 친화적 (엄지 손가락 영역)
- 최소한의 UI 변경으로 큰 효과

**UI 예시**:
```vue
<!-- FAB Button -->
<el-button
  circle
  type="primary"
  size="large"
  style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;"
  @click="drawerVisible = true"
>
  <el-icon><ChatDotRound /></el-icon>
</el-button>
```

---

### Insight 6: 에러 복구 전략으로 사용자 이탈 방지

**출처**: Starbursting (When Q15, How Q28), Mind Mapping (에러 흐름)
**Impact**: High | **Effort**: Medium

**설명**:
SSE 연결 실패 시 자동 재연결(3회, 3초 간격) + "재시도" 버튼 제공으로 사용자가 좌절하지 않도록 합니다.

**Why it matters**:
- 네트워크 불안정 환경 대응
- 사용자 이탈률 감소
- 신뢰성 향상

**에러 복구 로직**:
```typescript
let retryCount = 0;

function connectWithRetry() {
  const eventSource = new EventSource(url);

  eventSource.onerror = () => {
    eventSource.close();

    if (retryCount < 3) {
      setTimeout(() => {
        retryCount++;
        connectWithRetry();
      }, 3000);
    } else {
      showErrorMessage('서비스에 연결할 수 없습니다. 재시도 버튼을 눌러주세요.');
    }
  };
}
```

---

### Insight 7: Markdown + Element Plus Table로 다양한 응답 형식 지원

**출처**: SCAMPER (Modify), Mind Mapping (응답 포맷), Starbursting (How Q25, Q26)
**Impact**: High | **Effort**: Medium

**설명**:
AI 응답이 텍스트, 테이블, 숫자 등 다양한 형식일 수 있으므로, Markdown 렌더링과 Element Plus 컴포넌트를 조합하면 모든 형식을 지원할 수 있습니다.

**Why it matters**:
- 백엔드 응답 형식 유연성
- 사용자 친화적 표시
- 추후 차트 추가 용이

**응답 타입별 처리**:
```typescript
if (data.type === 'text') {
  // Markdown 렌더링
  return marked(data.content);
} else if (data.type === 'table') {
  // Element Plus Table
  return <el-table :data="data.rows" />;
} else if (data.type === 'number') {
  // Element Plus Statistic
  return <el-statistic :value="data.value" />;
}
```

---

## 5. 통계

- **총 아이디어**: 19개
- **카테고리**: 5개 (핵심 구현, UX 개선, 에러 처리, 통합, Phase 2)
- **핵심 인사이트**: 7개
- **적용 기법**: 3개 (SCAMPER, Mind Mapping, Starbursting)

---

## 6. 추천 다음 단계

### Phase 1 (MVP) - 1-2주

**우선순위 1 (Must Have)**:
1. ✅ **SSE API 연결 검증** (aiChatApi.ts)
2. ✅ **Pinia Store 생성** (useAIChatStore)
3. ✅ **AIChatDrawer.vue 기본 UI**
4. ✅ **ChatMessage.vue** (사용자/AI 구분, 타임스탬프)
5. ✅ **ChatInput.vue** (el-input + 전송 버튼)

**우선순위 2 (Should Have)**:
6. ✅ **FAB 버튼** (대시보드 우하단)
7. ✅ **타이핑 인디케이터** (el-skeleton)
8. ✅ **에러 처리** (재연결, 타임아웃)
9. ✅ **빠른 질문 버튼** (QuickQuestions.vue)

**우선순위 3 (Nice to Have)**:
10. ⚠️ **Markdown 렌더링**
11. ⚠️ **테이블 표시** (el-table)
12. ⚠️ **스크롤 애니메이션**

### Phase 2 (확장) - 2-3주

- 대화 히스토리
- 북마크
- 차트 자동 생성
- 다른 페이지 적용

---

## 7. 리스크 및 고려사항

### 기술적 리스크
- **SSE 브라우저 호환성**: IE 지원 불가 (현대 브라우저만)
- **SSE 연결 제한**: 동시 6개 연결 제한 (HTTP/1.1)
- **타임아웃 설정**: 프록시/방화벽 설정 확인 필요

### 대응 방안
- ✅ 브라우저 호환성 체크 (IE 접근 차단)
- ✅ 연결 풀링 관리 (하나의 EventSource 재사용)
- ✅ Keep-alive 설정 (백엔드 SSE 설정)

---

## 8. 결론

**브레인스토밍 완료!**

- **총 19개 아이디어** 도출
- **7개 핵심 인사이트** 추출
- **명확한 MVP 범위** 정의
- **구현 가능성** 검증 완료

**다음 단계**:
본 브레인스토밍 결과를 바탕으로 **구현 스토리 작성** 및 **기술 스펙 문서 생성** 진행

---

**생성 일시**: 2026-02-04
**Generated by**: BMAD Method v6 - Creative Intelligence
**세션 시간**: 약 45분
