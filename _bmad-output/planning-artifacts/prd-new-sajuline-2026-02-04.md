---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-new-sajuline-2026-01-15.md
  - _bmad-output/analysis/brainstorming-ai-chat-integration-2026-02-04.md
  - _bmad-output/planning-artifacts/research/technical-vue3-langgraph-ai-streaming-chat-integration-2026-02-04.md
workflowType: 'prd'
date: 2026-02-04
author: DongDong
version: 1.0.0
---

# Product Requirements Document - new-sajuline

**Author:** DongDong
**Date:** 2026-02-04
**Version:** 1.0.0
**Status:** Draft

---

## Executive Summary

**new-sajuline**은 AI 기술을 활용한 현대화된 사주 상담 플랫폼으로, 두 가지 핵심 서비스로 구성됩니다:

1. **Part A: 사용자 서비스** - AI 기반 일일/주간/월간/연간 운세 제공
2. **Part B: 관리자 서비스** - LangGraph 기반 AI BI 어시스턴트 (자연어 데이터 조회)

본 PRD는 MVP 범위를 정의하며, 기존 sajuline.com의 올드한 UI와 느린 서비스 문제를 해결하고, AI 시대에 맞는 트렌디하고 빠른 사용자 경험을 제공하는 것을 목표로 합니다.

**핵심 차별점:**
- 낮은 진입장벽 (AI 운세로 간편한 첫 경험)
- 빠른 개발-테스트-배포 사이클 (1인 개발자 강점)
- 관리자 AI BI로 의사결정 속도 향상

---

## 1. Business Objectives (비즈니스 목표)

### 1.1 핵심 목표

| 우선순위 | 목표 | 설명 |
|----------|------|------|
| 1 | **서비스 안정성 확보** | 99%+ 가용성으로 안정적 운영 |
| 2 | **빠른 개발-배포 사이클** | 1인 개발자 강점 활용, 빠른 피드백 반영 |
| 3 | **사용자 경험 개선** | 모던 UI/UX, 빠른 성능 (LCP < 2.5s) |
| 4 | **AI 기능 확장** | Phase 1 운세 → Phase 2 하이브리드 → Phase 3 AI 상담 |

### 1.2 비즈니스 가치 제안

**사용자 서비스:**
- AI 기반 일일/주간/월간/연간 운세로 낮은 진입장벽 제공
- 10,000P 무료 제공으로 약 5분 체험 가능
- 모던하고 빠른 모바일 퍼스트 UX

**관리자 서비스:**
- LangGraph 기반 AI BI 어시스턴트로 자연어 데이터 조회 지원
- SQL 지식 없이도 "오늘 매출 얼마야?" 형태의 질문으로 데이터 조회
- 개발팀 데이터 요청 부담 50% 감소

---

## 2. Success Metrics (성공 지표)

### 2.1 기술 성능 지표 (KPI)

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **API 응답시간** | p95 < 300ms | 서버 모니터링 (Prometheus) |
| **AI 운세 응답시간** | < 3초 | OpenAI API 응답 추적 |
| **AI BI 응답시간** | p95 ≤ 5초 | LangGraph 에이전트 메트릭 |
| **페이지 로드 (LCP)** | < 2.5초 | Core Web Vitals |
| **서비스 가용성** | 99%+ | 업타임 모니터링 (UptimeRobot) |
| **SSE 연결 지연** | p95 < 500ms | SSE 메트릭 추적 |

### 2.2 사용자 경험 지표

**사용자 서비스:**
| 지표 | 의미 | 목표 |
|------|------|------|
| **첫 상담 완료율** | 신규 가입 → 첫 상담 전환 | - |
| **재방문율** | 서비스 만족도 간접 측정 | - |
| **AI 운세 이용률** | 새 기능 채택도 | 가입자의 30%+ |

**관리자 서비스:**
| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **첫 질문 성공률** | ≥90% | 첫 질의 시 정확한 답변 비율 |
| **SQL 오류율** | ≤1% | 생성된 SQL 오류 발생 비율 |
| **일일 사용 횟수** | ≥5회 | 관리자 1인 기준 하루 질의 횟수 |
| **개발팀 부담 감소** | 데이터 요청 50% 감소 | 개발팀 요청 건수 추적 |

### 2.3 개발 목표

| 목표 | 설명 |
|------|------|
| **빠른 이터레이션** | 1인 개발자 강점 활용, 빠른 피드백 반영 |
| **AI 기능 확장** | Phase 1(일일/주간 운세) → Phase 2(하이브리드) → Phase 3(AI 상담) |
| **기술 부채 최소화** | 리뉴얼 시 클린 아키텍처 유지 |

---

## 3. Target Users (타겟 유저)

### 3.1 Primary Users (주요 사용자)

#### 메인 페르소나: "민지" (30대 여성 헤비 유저)

| 항목 | 내용 |
|------|------|
| **프로필** | 34세, 직장인 여성, 기혼 |
| **상황** | 이직, 출산 등 인생의 중요한 결정을 앞두고 있음 |
| **이용 패턴** | 월 1-2회 정기 상담, 중요 결정 시 반드시 확인 |
| **니즈** | 신뢰할 수 있는 사주 상담으로 불확실한 미래에 대한 지침 얻기 |
| **Pain Point** | 기존 서비스의 올드한 UI, 느린 속도에 불만 |

#### 서브 페르소나별 특성

| 연령대 | 주요 관심사 | 이용 빈도 |
|--------|-------------|-----------|
| **20대** | 취업운, 연애운 | 가끔 (호기심/특정 이벤트 시) |
| **30~40대** | 커리어, 결혼, 인생 방향 | 정기적 (헤비 유저 다수) |
| **50대 이상** | 자녀 진로, 부모 건강, 가족 문제 | 정기적 |

**핵심 타겟**: 30대 이상 여성, 중요한 결정 앞에서 전문 상담을 받는 장기 이용 헤비 유저

### 3.2 Secondary Users (2차 사용자)

#### 상담사 (약 100명)
- **역할**: 전문 사주 상담 제공
- **중요성**: 서비스 만족도의 핵심 요소 (상담사 역량 = 사용자 만족도)
- **니즈**: 효율적인 상담 관리, 고객과의 원활한 소통 도구

#### 관리자 (3명)

| 역할 | 인원 | 담당 업무 |
|------|------|-----------|
| 개발/총괄 관리자 | 1명 | 개발, 전체 서비스 관리 |
| 운영 관리자 | 2명 | 일상 사이트 운영, 고객 지원 |

---

## 4. Functional Requirements (기능 요구사항)

### Part A: 사용자 서비스 - AI 운세

#### FR-A001: 일일 운세 조회

**Priority:** Must Have

**Description:**
로그인한 사용자가 자신의 사주 정보를 기반으로 오늘의 운세를 AI로 조회할 수 있다. OpenAI API를 통해 3초 이내에 일일 운세 분석 결과를 제공한다.

**Acceptance Criteria:**
- [ ] 로그인한 사용자만 접근 가능
- [ ] 사용자의 생년월일시 사주 정보를 자동으로 활용
- [ ] OpenAI API 호출하여 일일 운세 생성
- [ ] 응답 시간 3초 이내 (p95)
- [ ] 운세 결과를 읽기 쉬운 형태로 표시
- [ ] 에러 발생 시 사용자 친화적 메시지 표시

**Dependencies:** FR-A005 (사용자 인증)

---

#### FR-A002: 주간 운세 조회

**Priority:** Must Have

**Description:**
로그인한 사용자가 이번 주 운세를 AI로 조회할 수 있다. 일일 운세와 동일한 프롬프트 템플릿 방식이지만 주간 단위로 분석한다.

**Acceptance Criteria:**
- [ ] 로그인한 사용자만 접근 가능
- [ ] 이번 주 기간 자동 계산 (월~일)
- [ ] OpenAI API 호출하여 주간 운세 생성
- [ ] 응답 시간 3초 이내 (p95)
- [ ] 요일별 운세 또는 주간 전체 운세 표시
- [ ] 에러 처리 및 사용자 알림

**Dependencies:** FR-A005 (사용자 인증)

---

#### FR-A003: 월간 운세 조회

**Priority:** Must Have

**Description:**
로그인한 사용자가 이번 달 운세를 AI로 조회할 수 있다. 월간 단위 프롬프트 템플릿을 사용하여 전체적인 흐름을 분석한다.

**Acceptance Criteria:**
- [ ] 로그인한 사용자만 접근 가능
- [ ] 현재 월 자동 계산
- [ ] OpenAI API 호출하여 월간 운세 생성
- [ ] 응답 시간 3초 이내 (p95)
- [ ] 월간 종합 운세 및 분야별 운세 표시
- [ ] 에러 처리 및 사용자 알림

**Dependencies:** FR-A005 (사용자 인증)

---

#### FR-A004: 연간 운세 조회

**Priority:** Must Have

**Description:**
로그인한 사용자가 올해 운세를 AI로 조회할 수 있다. 연간 단위 프롬프트 템플릿을 사용하여 한 해 전체를 조망하는 분석을 제공한다.

**Acceptance Criteria:**
- [ ] 로그인한 사용자만 접근 가능
- [ ] 현재 연도 자동 계산
- [ ] OpenAI API 호출하여 연간 운세 생성
- [ ] 응답 시간 3초 이내 (p95)
- [ ] 연간 종합 운세 및 분기별/월별 흐름 표시
- [ ] 에러 처리 및 사용자 알림

**Dependencies:** FR-A005 (사용자 인증)

---

#### FR-A005: 사용자 인증 및 사주 정보 관리

**Priority:** Must Have

**Description:**
사용자는 회원가입 시 사주 정보(생년월일시)를 입력하고, 로그인 후 AI 운세 서비스를 이용할 수 있다. 사주 정보는 안전하게 저장되어 운세 조회 시 자동으로 활용된다.

**Acceptance Criteria:**
- [ ] 회원가입 시 생년월일시(사주 4주) 필수 입력
- [ ] 사주 정보 유효성 검증 (실제 날짜/시간 범위)
- [ ] 사주 정보 암호화 저장 (AES-256-GCM)
- [ ] 로그인한 사용자의 사주 정보를 세션에서 조회
- [ ] AI 운세 요청 시 추가 입력 없이 사주 정보 자동 전달
- [ ] 사주 정보 수정 기능

**Dependencies:** 없음

---

#### FR-A006: AI 운세 캐싱

**Priority:** Should Have

**Description:**
동일한 사용자가 같은 날/주/월/년에 중복 요청 시 OpenAI API를 재호출하지 않고 캐시된 결과를 반환하여 비용을 절감하고 응답 속도를 향상시킨다.

**Acceptance Criteria:**
- [ ] 사용자별 + 운세 타입별 + 날짜별 캐시 키 생성
- [ ] Redis에 캐시 저장 (TTL: 일일 24시간, 주간 7일, 월간 30일, 연간 365일)
- [ ] 캐시 히트 시 즉시 반환 (응답 시간 < 100ms)
- [ ] 캐시 미스 시 OpenAI API 호출 후 저장
- [ ] 캐시 무효화 기능 (관리자 또는 사용자 요청)

**Dependencies:** FR-A001, FR-A002, FR-A003, FR-A004

---

### Part B: 관리자 서비스 - AI BI 어시스턴트

#### FR-B001: 자연어 질의 처리

**Priority:** Must Have

**Description:**
관리자가 "오늘 매출 얼마야?", "이번 주 결제 건수는?" 같은 자연어 질문을 입력하면 LangGraph 멀티 에이전트가 SQL로 변환하여 데이터베이스를 조회하고 답변을 제공한다.

**Acceptance Criteria:**
- [ ] 관리자 권한이 있는 사용자만 접근 가능
- [ ] 자연어 질문을 입력받는 채팅 UI (el-drawer)
- [ ] LangGraph Supervisor가 질문을 분석하여 적절한 Agent로 라우팅
- [ ] 질문 의도 파악 및 SQL 생성
- [ ] 응답 시간 5초 이내 (p95)
- [ ] 사용자 친화적인 자연어 답변 생성

**Dependencies:** FR-B006 (관리자 인증)

---

#### FR-B002: 멀티 DB 조회 (MariaDB + MSSQL)

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 MariaDB(매출, 유저, 결제)와 MSSQL 2005(상담 로그, 실시간 상태) 두 데이터베이스를 통합 조회할 수 있다. 크로스 DB 조인이 필요한 경우 pandas로 메모리 조인을 수행한다.

**Acceptance Criteria:**
- [ ] MariaDB Agent: t_payment, t_user, t_point 등 조회
- [ ] MSSQL Agent: 상담 로그, 상담사 실시간 상태 조회
- [ ] Cross-DB Joiner: pandas를 통한 메모리 조인
- [ ] 각 DB별 읽기 전용 계정 사용
- [ ] 연결 풀 관리 및 타임아웃 설정
- [ ] DB별 에러 처리 및 재시도 로직

**Dependencies:** FR-B001 (자연어 질의)

---

#### FR-B003: SSE 스트리밍 응답

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 Server-Sent Events(SSE)를 통해 실시간으로 처리 상태를 스트리밍한다. 사용자는 "분석 중 → SQL 생성 → 실행 중 → 결과" 단계를 실시간으로 확인할 수 있다.

**Acceptance Criteria:**
- [ ] FastAPI SSE 엔드포인트 구현 (`POST /api/v1/ai/chat?stream=true`)
- [ ] 이벤트 타입: thinking, query, executing, result, done
- [ ] Vue 3 프론트엔드에서 EventSource로 연결
- [ ] VueUse useEventSource 컴포저블 사용
- [ ] 연결 끊김 시 자동 재연결 (exponential backoff, 최대 3회)
- [ ] 타이핑 효과로 응답 표시

**Dependencies:** FR-B001 (자연어 질의)

---

#### FR-B004: 채팅 UI (el-drawer)

**Priority:** Must Have

**Description:**
Admin-Frontend 대시보드에 Element Plus el-drawer를 활용한 채팅 UI를 제공한다. 사용자는 FAB 버튼을 클릭하여 드로어를 열고 AI BI 어시스턴트와 대화할 수 있다.

**Acceptance Criteria:**
- [ ] el-drawer 컴포넌트로 채팅 UI 구현 (기본 50% 너비)
- [ ] FAB(Floating Action Button) 우하단 고정 배치
- [ ] 메시지 입력창 (el-input + 전송 버튼)
- [ ] 사용자/AI 메시지 구분 표시 (오른쪽/왼쪽 정렬)
- [ ] 타임스탬프 표시
- [ ] 스크롤 자동 하단 이동
- [ ] 로딩 인디케이터 (el-skeleton)

**Dependencies:** FR-B003 (SSE 스트리밍)

---

#### FR-B005: 4중 보안 방어

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 SQL Injection 및 데이터 유출을 방지하기 위해 4개 레이어의 보안 검증을 수행한다.

**Acceptance Criteria:**
- [ ] Layer 1 - Prompt 검증: 악의적 프롬프트 차단
- [ ] Layer 2 - SQL 검증: 생성된 SQL의 안전성 검사 (SELECT만 허용)
- [ ] Layer 3 - 결과 검증: 민감 정보 마스킹 (전화번호, 이메일)
- [ ] Layer 4 - 사용자 확인: 위험한 쿼리 실행 전 관리자 승인
- [ ] 테이블 화이트리스트 적용
- [ ] 모든 보안 이벤트 로깅

**Dependencies:** FR-B001 (자연어 질의)

---

#### FR-B006: 관리자 인증 및 권한 관리

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 관리자 권한이 있는 사용자만 접근할 수 있다. HttpOnly 쿠키 기반 인증을 사용하며, SSE 연결 시 withCredentials로 자격 증명을 전송한다.

**Acceptance Criteria:**
- [ ] 관리자 로그인 시 HttpOnly 쿠키 발급
- [ ] AI BI 채팅 UI는 관리자 권한 확인 후 표시
- [ ] SSE 연결 시 withCredentials: true 설정
- [ ] 인증 실패 시 로그인 페이지로 리다이렉트
- [ ] 세션 타임아웃 처리 (30분)
- [ ] 권한 레벨별 접근 제어 (슈퍼 관리자, 운영 관리자)

**Dependencies:** 없음

---

#### FR-B007: 빠른 질문 버튼

**Priority:** Should Have

**Description:**
채팅 UI에 자주 사용하는 질문을 버튼으로 제공하여 사용자가 클릭 한 번으로 질의할 수 있다.

**Acceptance Criteria:**
- [ ] el-tag 스타일의 빠른 질문 칩 (예: "오늘 매출", "이번 주 결제 건수", "신규 가입자")
- [ ] 클릭 시 해당 질문이 입력창에 자동 입력 또는 즉시 전송
- [ ] 질문 목록은 설정 파일에서 관리
- [ ] 최소 5개 이상의 빠른 질문 제공
- [ ] 드로어 상단에 표시

**Dependencies:** FR-B004 (채팅 UI)

---

#### FR-B008: 쿼리 결과 테이블 표시

**Priority:** Must Have

**Description:**
AI BI 어시스턴트가 데이터베이스 조회 결과를 반환할 때, 테이블 형태의 데이터는 Element Plus el-table로 표시한다.

**Acceptance Criteria:**
- [ ] SSE result 이벤트에서 data.rows를 el-table에 바인딩
- [ ] 컬럼 헤더 자동 생성
- [ ] 행 개수 표시 (예: "총 25건")
- [ ] 페이지네이션 (10행 이상일 경우)
- [ ] CSV 다운로드 버튼 (선택)
- [ ] 반응형 테이블 (모바일 대응)

**Dependencies:** FR-B001 (자연어 질의), FR-B004 (채팅 UI)

---

#### FR-B009: 에러 처리 및 재시도

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 네트워크 에러, 타임아웃, SQL 에러 등 다양한 에러 상황을 처리하고 사용자에게 적절한 피드백을 제공한다.

**Acceptance Criteria:**
- [ ] SSE 연결 실패 시 자동 재연결 (exponential backoff, 최대 3회)
- [ ] 60초 타임아웃 처리
- [ ] SQL 에러 발생 시 사용자 친화적 메시지 표시
- [ ] LangGraph Agent 에러 로깅 및 Sentry 전송
- [ ] "재시도" 버튼 제공
- [ ] 에러 타입별 분류 (일시적/치명적)

**Dependencies:** FR-B001, FR-B003

---

#### FR-B010: Pinia 상태 관리

**Priority:** Must Have

**Description:**
AI BI 채팅 상태를 Pinia Store로 관리하여 컴포넌트 간 상태 공유 및 SSE 이벤트 처리를 효율적으로 수행한다.

**Acceptance Criteria:**
- [ ] useChatStore 생성 (messages[], isStreaming, drawerVisible)
- [ ] SSE 이벤트 핸들러 (handleThinkingEvent, handleResultEvent, handleDoneEvent)
- [ ] 메시지 추가/삭제 액션
- [ ] 연결 상태 추적 (connected, connecting, disconnected)
- [ ] 재연결 카운트 및 에러 상태 관리

**Dependencies:** FR-B003 (SSE 스트리밍), FR-B004 (채팅 UI)

---

## 5. Non-Functional Requirements (비기능 요구사항)

### 5.1 성능 (Performance)

#### NFR-001: API 응답 시간

**Priority:** Must Have

**Description:**
모든 API 엔드포인트는 p95 기준 300ms 이내에 응답해야 한다. (AI 관련 API 제외)

**Acceptance Criteria:**
- [ ] 일반 REST API 응답 시간 p95 < 300ms
- [ ] 데이터베이스 쿼리 최적화 (인덱스, 쿼리 튜닝)
- [ ] Prometheus로 응답 시간 모니터링
- [ ] p95 300ms 초과 시 알림 발생

**Rationale:**
빠른 사용자 경험 제공 및 모바일 환경에서의 원활한 서비스 이용을 위해 필수적입니다.

---

#### NFR-002: AI 운세 응답 시간

**Priority:** Must Have

**Description:**
사용자 AI 운세 서비스는 OpenAI API 호출을 포함하여 3초 이내에 응답해야 한다.

**Acceptance Criteria:**
- [ ] 일일/주간/월간/연간 운세 응답 p95 < 3초
- [ ] OpenAI API 타임아웃 5초 설정
- [ ] 캐시 히트 시 100ms 이내 응답
- [ ] 타임아웃 발생 시 재시도 로직 (최대 1회)
- [ ] 응답 시간 메트릭 수집 및 대시보드 표시

**Rationale:**
사용자가 운세 결과를 기다리는 시간을 최소화하여 서비스 만족도를 높입니다.

---

#### NFR-003: AI BI 어시스턴트 응답 시간

**Priority:** Must Have

**Description:**
관리자 AI BI 어시스턴트는 자연어 질의를 5초 이내에 처리하고 응답해야 한다.

**Acceptance Criteria:**
- [ ] 자연어 질의 → SQL 생성 → 실행 → 응답 전체 과정 p95 ≤ 5초
- [ ] LangGraph 에이전트 타임아웃 60초 설정
- [ ] 복잡한 크로스 DB 조인도 5초 이내 처리
- [ ] 타임아웃 시 사용자 친화적 메시지 및 재시도 제안
- [ ] 응답 시간 메트릭 추적

**Rationale:**
관리자의 빠른 의사결정을 지원하기 위해 실시간 응답이 필요합니다.

---

#### NFR-004: 페이지 로드 성능

**Priority:** Must Have

**Description:**
웹 페이지는 Core Web Vitals 기준을 충족해야 한다.

**Acceptance Criteria:**
- [ ] LCP (Largest Contentful Paint) < 2.5초
- [ ] FID (First Input Delay) < 100ms
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] Google Lighthouse 점수 90+ (Performance)
- [ ] 모바일/데스크탑 모두 기준 충족

**Rationale:**
모바일 퍼스트 UX 전략에 따라 빠른 페이지 로드는 필수입니다.

---

#### NFR-005: SSE 연결 성능

**Priority:** Must Have

**Description:**
AI BI 어시스턴트의 SSE 연결은 빠르고 안정적으로 유지되어야 한다.

**Acceptance Criteria:**
- [ ] SSE 연결 지연 p95 < 500ms
- [ ] 하트비트 30초 주기
- [ ] 재연결 성공률 > 95%
- [ ] 연결 끊김 후 3초 이내 재연결 시도 (exponential backoff)
- [ ] 동시 연결 수 1000개 이상 지원

**Rationale:**
실시간 스트리밍 경험을 위해 안정적이고 빠른 SSE 연결이 필요합니다.

---

### 5.2 보안 (Security)

#### NFR-006: 데이터 암호화

**Priority:** Must Have

**Description:**
민감한 사용자 정보는 암호화하여 저장 및 전송해야 한다.

**Acceptance Criteria:**
- [ ] 전송 중 암호화: HTTPS/TLS 1.3 필수
- [ ] 저장 시 암호화: 사주 정보 AES-256-GCM 암호화
- [ ] 비밀번호: Argon2id 해싱
- [ ] PII 데이터 마스킹 (관리자 조회 시)
- [ ] 암호화 키는 환경 변수로 관리 (코드에 하드코딩 금지)

**Rationale:**
사용자의 개인정보 및 민감 정보 보호를 위해 필수적입니다.

---

#### NFR-007: 인증 및 권한 관리

**Priority:** Must Have

**Description:**
모든 API 엔드포인트는 적절한 인증 및 권한 검증을 수행해야 한다.

**Acceptance Criteria:**
- [ ] JWT 기반 인증 (HttpOnly 쿠키)
- [ ] CSRF 토큰 검증
- [ ] API 엔드포인트별 권한 확인 (사용자/관리자)
- [ ] 세션 타임아웃 30분 (연장 가능)
- [ ] 로그인 실패 5회 시 계정 잠금 (10분)

**Rationale:**
무단 접근을 방지하고 사용자 계정을 보호합니다.

---

#### NFR-008: AI BI 4중 보안 방어

**Priority:** Must Have

**Description:**
AI BI 어시스턴트는 SQL Injection 및 데이터 유출을 방지하기 위해 4개 레이어의 보안 검증을 수행해야 한다.

**Acceptance Criteria:**
- [ ] Layer 1 - Prompt 검증: 악의적 프롬프트 차단
- [ ] Layer 2 - SQL 검증: 생성된 SQL 안전성 검사 (SELECT만, 테이블 화이트리스트)
- [ ] Layer 3 - 결과 검증: 민감 정보 자동 마스킹
- [ ] Layer 4 - 사용자 확인: 위험한 쿼리 실행 전 관리자 승인
- [ ] 모든 보안 이벤트 로깅 및 Sentry 전송
- [ ] 읽기 전용 DB 계정 사용

**Rationale:**
관리자 서비스의 데이터베이스 접근 권한을 악용한 공격을 방지합니다.

---

#### NFR-009: API 보안

**Priority:** Must Have

**Description:**
API는 일반적인 보안 위협으로부터 보호되어야 한다.

**Acceptance Criteria:**
- [ ] CORS 설정: 허용된 출처만 접근
- [ ] 레이트 리밋: IP당 분당 100 요청, 사용자당 분당 60 요청
- [ ] SQL Injection 방지: Pydantic 스키마 검증, ORM 사용
- [ ] XSS 방지: 입력 데이터 sanitize, CSP 헤더
- [ ] 환경 변수로 비밀 관리 (API 키, DB 비밀번호)

**Rationale:**
API를 통한 공격 벡터를 차단하여 서비스 안정성을 확보합니다.

---

### 5.3 신뢰성 및 가용성 (Reliability & Availability)

#### NFR-010: 서비스 가용성

**Priority:** Must Have

**Description:**
서비스는 99% 이상의 가용성을 유지해야 한다.

**Acceptance Criteria:**
- [ ] 월간 가동 시간 99% 이상 (약 7.2시간 다운타임 허용)
- [ ] 계획된 유지보수는 사전 공지 (최소 24시간)
- [ ] 헬스체크 엔드포인트 제공 (`/health`)
- [ ] 자동 재시작 설정 (Docker, PM2)
- [ ] 업타임 모니터링 (UptimeRobot, Pingdom)

**Rationale:**
사용자가 언제든지 서비스를 이용할 수 있도록 안정성을 확보합니다.

---

#### NFR-011: 에러 복구

**Priority:** Must Have

**Description:**
시스템은 에러 발생 시 자동으로 복구하거나 적절한 대응 조치를 취해야 한다.

**Acceptance Criteria:**
- [ ] 자동 재시도 로직 (네트워크 에러, 일시적 장애)
- [ ] Circuit Breaker 패턴 (외부 API 호출)
- [ ] Graceful Degradation (OpenAI API 장애 시 캐시된 응답 제공)
- [ ] 에러 발생 시 사용자 친화적 메시지
- [ ] 모든 에러 로깅 및 Sentry 전송

**Rationale:**
외부 의존성 장애 시에도 서비스가 부분적으로 동작하도록 합니다.

---

#### NFR-012: 데이터 백업

**Priority:** Must Have

**Description:**
중요 데이터는 정기적으로 백업되어야 한다.

**Acceptance Criteria:**
- [ ] 데이터베이스 일일 자동 백업
- [ ] 백업 파일 AWS S3 저장 (암호화)
- [ ] 백업 보관 기간: 30일
- [ ] 백업 복구 절차 문서화
- [ ] 월 1회 백업 복구 테스트

**Rationale:**
데이터 손실 시 빠르게 복구할 수 있도록 준비합니다.

---

### 5.4 확장성 (Scalability)

#### NFR-013: 동시 사용자 처리

**Priority:** Should Have

**Description:**
시스템은 동시 사용자 증가에 대응할 수 있어야 한다.

**Acceptance Criteria:**
- [ ] 동시 사용자 500명 처리 (피크 시간)
- [ ] 수평적 확장 가능 (서버 추가로 용량 증대)
- [ ] 로드 밸런싱 설정 (Nginx, AWS ALB)
- [ ] 데이터베이스 연결 풀 관리 (최대 100 연결)
- [ ] Redis 캐싱으로 DB 부하 감소

**Rationale:**
사용자 증가에 따라 서비스 품질을 유지합니다.

---

#### NFR-014: AI 요청 확장성

**Priority:** Should Have

**Description:**
AI 운세 및 AI BI 요청이 증가해도 성능 저하 없이 처리해야 한다.

**Acceptance Criteria:**
- [ ] OpenAI API 레이트 리밋 관리 (TPM, RPM)
- [ ] 요청 큐잉 시스템 (Redis Queue)
- [ ] 캐싱 전략으로 중복 요청 최소화
- [ ] 비동기 처리로 동시 요청 처리
- [ ] 피크 시간 모니터링 및 자동 알림

**Rationale:**
AI API 비용을 관리하면서 사용자 경험을 유지합니다.

---

### 5.5 사용성 (Usability)

#### NFR-015: 접근성

**Priority:** Should Have

**Description:**
웹 서비스는 접근성 표준을 준수해야 한다.

**Acceptance Criteria:**
- [ ] WCAG 2.1 AA 레벨 준수
- [ ] 키보드 네비게이션 지원
- [ ] 스크린 리더 호환
- [ ] 적절한 색상 대비 (4.5:1 이상)
- [ ] ARIA 라벨 적용

**Rationale:**
모든 사용자가 서비스를 이용할 수 있도록 합니다.

---

#### NFR-016: 브라우저 호환성

**Priority:** Must Have

**Description:**
주요 모던 브라우저에서 정상 동작해야 한다.

**Acceptance Criteria:**
- [ ] Chrome 최신 버전 + 이전 2개 버전
- [ ] Firefox 최신 버전 + 이전 2개 버전
- [ ] Safari 최신 버전 + 이전 2개 버전
- [ ] Edge 최신 버전 + 이전 2개 버전
- [ ] 모바일 브라우저 (iOS Safari, Android Chrome)
- [ ] SSE 지원 브라우저 (98%+ 호환성 확인됨)

**Rationale:**
다양한 환경에서 사용자가 서비스를 이용할 수 있도록 합니다.

---

#### NFR-017: 반응형 디자인

**Priority:** Must Have

**Description:**
모바일 퍼스트 UX 전략에 따라 모든 화면 크기에서 최적화된 UI를 제공해야 한다.

**Acceptance Criteria:**
- [ ] 모바일 (320px~768px), 태블릿 (768px~1024px), 데스크탑 (1024px+) 지원
- [ ] Tailwind CSS 반응형 유틸리티 사용
- [ ] 터치 친화적 UI (버튼 최소 44x44px)
- [ ] 모바일에서 드로어 100% 너비
- [ ] Google Mobile-Friendly Test 통과

**Rationale:**
모바일 사용자가 대다수이므로 모바일 경험 최적화가 필수입니다.

---

### 5.6 유지보수성 (Maintainability)

#### NFR-018: 코드 품질

**Priority:** Must Have

**Description:**
코드는 읽기 쉽고 유지보수하기 쉬워야 한다.

**Acceptance Criteria:**
- [ ] Backend: Black 포매팅, isort, flake8, mypy (strict 모드)
- [ ] Frontend: ESLint, Prettier, TypeScript strict 모드
- [ ] 테스트 커버리지 80% 이상
- [ ] 함수/클래스 복잡도 제한 (cyclomatic complexity < 10)
- [ ] 코드 리뷰 필수 (1명 이상 승인)

**Rationale:**
1인 개발자 환경에서 코드 품질을 유지하여 장기적 유지보수성을 확보합니다.

---

#### NFR-019: 로깅 및 모니터링

**Priority:** Must Have

**Description:**
시스템은 구조화된 로그를 생성하고 주요 메트릭을 모니터링해야 한다.

**Acceptance Criteria:**
- [ ] JSON 형태의 구조화 로그 (timestamp, level, message, context)
- [ ] 요청 ID 기반 로그 상관관계 추적
- [ ] Sentry 에러 추적 및 성능 모니터링
- [ ] Prometheus 메트릭 수집 (응답 시간, 에러율, 처리량)
- [ ] LangSmith AI 에이전트 추적
- [ ] Grafana 대시보드

**Rationale:**
문제 발생 시 빠르게 원인을 파악하고 해결할 수 있도록 합니다.

---

#### NFR-020: 문서화

**Priority:** Should Have

**Description:**
시스템 아키텍처, API, 설정 방법 등이 문서화되어야 한다.

**Acceptance Criteria:**
- [ ] API 문서 (FastAPI Swagger UI)
- [ ] 아키텍처 다이어그램
- [ ] 환경 설정 가이드 (README.md)
- [ ] 배포 절차 문서
- [ ] 코드 주석 (복잡한 로직만)

**Rationale:**
새로운 팀원 합류 또는 향후 유지보수 시 빠른 이해를 돕습니다.

---

### 5.7 호환성 (Compatibility)

#### NFR-021: 외부 시스템 연동

**Priority:** Must Have

**Description:**
외부 서비스 및 레거시 시스템과 안정적으로 연동해야 한다.

**Acceptance Criteria:**
- [ ] OpenAI API v1 호환
- [ ] MariaDB 10.6+ 호환
- [ ] MSSQL 2005 연동 (읽기 전용)
- [ ] AWS S3 API 호환
- [ ] Kakao/Naver 소셜 로그인 OAuth 2.0
- [ ] Payletter 결제 웹훅

**Rationale:**
기존 시스템 및 외부 서비스와의 원활한 통합을 보장합니다.

---

## 6. Epics and User Stories

### 6.1 Epic Summary

| Epic ID | Epic Name | Priority | FRs | Story Estimate |
|---------|-----------|----------|-----|----------------|
| **EPIC-A01** | 사용자 인증 및 사주 정보 관리 | Must Have | FR-A005 | 3-4개 |
| **EPIC-A02** | AI 운세 서비스 | Must Have | FR-A001~A004, FR-A006 | 6-8개 |
| **EPIC-B01** | 관리자 인증 및 권한 관리 | Must Have | FR-B006 | 2-3개 |
| **EPIC-B02** | LangGraph AI BI 엔진 | Must Have | FR-B001, FR-B002, FR-B005 | 7-9개 |
| **EPIC-B03** | AI BI 채팅 UI (프론트엔드) | Must Have | FR-B003, FR-B004, FR-B007~B010 | 8-10개 |
| **EPIC-B04** | 모니터링 및 운영 | Should Have | NFR-019, NFR-011 | 4-5개 |

**총 예상 스토리 수:** 30-39개

---

### 6.2 Epic Details

#### EPIC-A01: 사용자 인증 및 사주 정보 관리

**Description:**
사용자가 회원가입 시 사주 정보(생년월일시)를 안전하게 등록하고, 로그인하여 AI 운세 서비스를 이용할 수 있는 인증 시스템을 구축한다.

**Business Value:**
사용자가 서비스를 이용하기 위한 기본 진입점이며, 사주 정보는 AI 운세의 핵심 입력 데이터로 사용된다.

**Acceptance Criteria:**
- [ ] 사용자가 생년월일시를 입력하여 회원가입 가능
- [ ] 사주 정보는 암호화되어 안전하게 저장됨
- [ ] 로그인 후 사주 정보가 세션에서 자동으로 조회됨
- [ ] 사용자가 사주 정보를 수정할 수 있음

---

#### EPIC-A02: AI 운세 서비스

**Description:**
OpenAI API를 활용하여 사용자의 사주 정보를 기반으로 일일/주간/월간/연간 운세를 제공한다. 캐싱을 통해 중복 요청을 최적화하고 비용을 절감한다.

**Business Value:**
MVP의 핵심 기능으로, AI 기반 사주 서비스의 차별화 포인트이다. 사용자가 낮은 진입장벽으로 운세를 체험할 수 있다.

**Acceptance Criteria:**
- [ ] 사용자가 4가지 기간(일/주/월/연) 운세를 조회 가능
- [ ] 모든 운세는 3초 이내에 응답
- [ ] 동일 사용자의 동일 기간 재요청 시 캐시에서 즉시 반환
- [ ] 운세 결과를 읽기 쉽고 모바일 친화적인 UI로 표시
- [ ] OpenAI API 에러 발생 시 사용자 친화적 메시지 표시

---

#### EPIC-B01: 관리자 인증 및 권한 관리

**Description:**
AI BI 어시스턴트에 접근할 수 있는 관리자 권한을 관리하고, HttpOnly 쿠키 기반 인증을 통해 보안을 강화한다.

**Business Value:**
민감한 데이터베이스 조회 권한을 보호하고, 권한이 있는 관리자만 AI BI 서비스를 이용하도록 제한한다.

**Acceptance Criteria:**
- [ ] 관리자 로그인 시 HttpOnly 쿠키 발급
- [ ] AI BI 채팅 UI는 관리자 권한 확인 후에만 표시
- [ ] SSE 연결 시 withCredentials로 인증 정보 전송
- [ ] 세션 타임아웃 및 재인증 처리
- [ ] 권한 레벨별 접근 제어 (슈퍼 관리자, 운영 관리자)

---

#### EPIC-B02: LangGraph AI BI 엔진

**Description:**
LangGraph 멀티 에이전트 오케스트레이션을 통해 자연어 질의를 SQL로 변환하고, MariaDB와 MSSQL 2005를 통합 조회하는 AI BI 엔진을 구축한다. 4중 보안 방어로 SQL Injection 및 데이터 유출을 방지한다.

**Business Value:**
관리자가 SQL을 몰라도 자연어로 데이터를 조회할 수 있어 의사결정 속도가 크게 향상된다. 개발팀의 데이터 요청 부담이 50% 감소한다.

**Acceptance Criteria:**
- [ ] "오늘 매출 얼마야?" 같은 자연어 질문을 정확히 이해
- [ ] LangGraph Supervisor가 질문을 분석하여 적절한 Agent로 라우팅
- [ ] MariaDB Agent, MSSQL Agent, Cross-DB Joiner 구현
- [ ] 4중 보안 방어 (Prompt, SQL, Result, User 검증)
- [ ] SELECT만 허용, 테이블 화이트리스트 적용
- [ ] 응답 시간 p95 5초 이내
- [ ] SQL 오류율 1% 이하

---

#### EPIC-B03: AI BI 채팅 UI (프론트엔드)

**Description:**
Admin-Frontend 대시보드에 Element Plus el-drawer를 활용한 채팅 UI를 구현하고, SSE 스트리밍으로 실시간 응답을 표시한다. VueUse useEventSource와 Pinia로 상태를 관리한다.

**Business Value:**
직관적인 채팅 UI로 관리자가 쉽게 데이터를 조회할 수 있으며, 실시간 스트리밍으로 AI의 사고 과정을 투명하게 보여준다.

**Acceptance Criteria:**
- [ ] el-drawer로 채팅 UI 구현 (기본 50% 너비)
- [ ] FAB 버튼 클릭으로 드로어 열기
- [ ] SSE 스트리밍으로 thinking → query → executing → result → done 단계 표시
- [ ] VueUse useEventSource로 SSE 연결 관리
- [ ] Pinia Store로 메시지, 스트리밍 상태, 드로어 표시 여부 관리
- [ ] 빠른 질문 버튼 5개 이상 제공
- [ ] 쿼리 결과를 el-table로 표시 (페이지네이션 포함)
- [ ] 연결 끊김 시 exponential backoff로 재연결
- [ ] 에러 발생 시 사용자 친화적 메시지 및 재시도 버튼

---

#### EPIC-B04: 모니터링 및 운영

**Description:**
AI BI 서비스의 안정성을 보장하기 위해 구조화된 로깅, 에러 추적, 성능 모니터링을 구축한다. LangSmith로 AI 에이전트를 추적하고, Sentry로 에러를 관리한다.

**Business Value:**
문제 발생 시 빠르게 원인을 파악하고 해결하여 서비스 다운타임을 최소화한다. AI 에이전트의 성능과 정확도를 지속적으로 개선할 수 있다.

**Acceptance Criteria:**
- [ ] JSON 형태의 구조화 로그 생성
- [ ] 요청 ID 기반 로그 상관관계 추적
- [ ] Sentry 에러 추적 및 알림
- [ ] Prometheus 메트릭 수집 (응답 시간, 에러율, SQL 성공률)
- [ ] LangSmith AI 에이전트 추적 및 분석
- [ ] Grafana 대시보드로 실시간 모니터링
- [ ] Circuit Breaker 패턴으로 외부 API 장애 격리

---

## 7. Traceability Matrix (추적성 매트릭스)

### 7.1 Epic to FR Mapping

| Epic ID | Epic Name | Related FRs | Story Estimate |
|---------|-----------|-------------|----------------|
| EPIC-A01 | 사용자 인증 및 사주 정보 관리 | FR-A005 | 3-4개 |
| EPIC-A02 | AI 운세 서비스 | FR-A001, FR-A002, FR-A003, FR-A004, FR-A006 | 6-8개 |
| EPIC-B01 | 관리자 인증 및 권한 관리 | FR-B006 | 2-3개 |
| EPIC-B02 | LangGraph AI BI 엔진 | FR-B001, FR-B002, FR-B005 | 7-9개 |
| EPIC-B03 | AI BI 채팅 UI (프론트엔드) | FR-B003, FR-B004, FR-B007, FR-B008, FR-B009, FR-B010 | 8-10개 |
| EPIC-B04 | 모니터링 및 운영 | NFR-019, NFR-011 | 4-5개 |

### 7.2 FR Coverage

**Part A (사용자 서비스):**
- 총 6개 FR
- Epic 커버리지: 100% (모든 FR이 Epic에 할당됨)

**Part B (관리자 서비스):**
- 총 10개 FR
- Epic 커버리지: 100% (모든 FR이 Epic에 할당됨)

---

## 8. Prioritization Summary (우선순위 요약)

### 8.1 Functional Requirements

| Priority | Part A (사용자) | Part B (관리자) | 합계 |
|----------|----------------|----------------|------|
| **Must Have** | 5개 | 9개 | 14개 |
| **Should Have** | 1개 | 1개 | 2개 |
| **Could Have** | 0개 | 0개 | 0개 |
| **총계** | 6개 | 10개 | 16개 |

### 8.2 Non-Functional Requirements

| Category | Must Have | Should Have | 합계 |
|----------|-----------|-------------|------|
| 성능 (Performance) | 5개 | 0개 | 5개 |
| 보안 (Security) | 4개 | 0개 | 4개 |
| 신뢰성/가용성 (Reliability) | 3개 | 0개 | 3개 |
| 확장성 (Scalability) | 0개 | 2개 | 2개 |
| 사용성 (Usability) | 2개 | 1개 | 3개 |
| 유지보수성 (Maintainability) | 2개 | 1개 | 3개 |
| 호환성 (Compatibility) | 1개 | 0개 | 1개 |
| **총계** | **17개** | **4개** | **21개** |

### 8.3 Epic Priority

| Priority | Epic Count | Story Estimate |
|----------|-----------|----------------|
| **Must Have** | 5개 | 26-33개 |
| **Should Have** | 1개 | 4-5개 |
| **총계** | 6개 | 30-38개 |

---

## 9. User Flows (사용자 흐름)

### 9.1 신규 사용자 AI 운세 이용 흐름

```
1. 회원가입
   └─> 사주 정보 입력 (생년월일시)
       └─> 유효성 검증
           └─> 암호화 저장

2. 로그인
   └─> 세션 생성
       └─> 사주 정보 조회

3. AI 운세 메뉴 선택
   └─> 일/주/월/연 중 선택
       └─> 캐시 확인
           ├─> 캐시 히트: 즉시 결과 반환 (< 100ms)
           └─> 캐시 미스: OpenAI API 호출 (< 3초)
               └─> 결과 표시
                   └─> Redis 캐시 저장

4. 운세 결과 확인
   └─> 만족 시 재방문 / 유료 상담 전환
```

### 9.2 관리자 AI BI 데이터 조회 흐름

```
1. 관리자 로그인
   └─> HttpOnly 쿠키 발급
       └─> 관리자 권한 확인

2. 대시보드 접속
   └─> FAB 버튼 표시

3. FAB 버튼 클릭
   └─> el-drawer 채팅 UI 열림
       └─> 빠른 질문 버튼 표시

4. 자연어 질문 입력
   └─> SSE 연결 시작 (withCredentials)
       └─> LangGraph Supervisor 라우팅
           ├─> MariaDB Agent
           ├─> MSSQL Agent
           └─> Cross-DB Joiner

5. SSE 스트리밍 응답
   ├─> thinking: "분석 중..."
   ├─> query: "생성된 SQL 표시"
   ├─> executing: "실행 중..."
   ├─> result: 테이블/텍스트 결과
   └─> done: "완료"

6. 결과 확인
   └─> 추가 질문 또는 드로어 닫기
```

### 9.3 관리자 빠른 질문 이용 흐름

```
1. 드로어 열림
   └─> 빠른 질문 버튼 표시

2. 빠른 질문 버튼 클릭 (예: "오늘 매출")
   └─> 즉시 SSE 스트리밍 시작
       └─> AI 응답 (5초 이내)

3. 결과 확인
   └─> 후속 질문 또는 다른 빠른 질문 클릭
```

---

## 10. Dependencies (의존성)

### 10.1 Internal Dependencies (내부 의존성)

| 의존성 | 상태 | 설명 |
|--------|------|------|
| **기존 상담 서비스** | ✅ 완료 | 상담사 목록, 예약, 채팅 |
| **회원 시스템** | ✅ 완료 | 가입, 로그인, 소셜 로그인 |
| **결제 시스템** | ✅ 완료 | 포인트 충전, Payletter 연동 |
| **관리자 시스템 기본 구조** | ✅ 완료 | Admin-Backend + Admin-Frontend |

### 10.2 External Dependencies (외부 의존성)

| 의존성 | 용도 | 버전/계약 | 우선순위 |
|--------|------|-----------|----------|
| **OpenAI API** | AI 운세, AI BI | v1, API 키 필요 | Must Have |
| **MariaDB** | 주 데이터베이스 | 10.6+ | Must Have |
| **MSSQL 2005** | 레거시 상담 로그 | 읽기 전용 | Must Have |
| **Redis** | 캐싱, 세션, 실시간 | 7+ | Must Have |
| **AWS S3** | 파일 저장 | API 키 필요 | Must Have |
| **Kakao OAuth** | 소셜 로그인 | OAuth 2.0 | Should Have |
| **Naver OAuth** | 소셜 로그인 | OAuth 2.0 | Should Have |
| **Payletter** | 포인트 충전 | 결제 웹훅 | Must Have |
| **Sentry** | 에러 추적 | SaaS | Should Have |

---

## 11. Assumptions (가정 사항)

1. **OpenAI API 안정성**
   - OpenAI API가 안정적으로 운영되며, 평균 응답 시간 2초 이내 유지
   - 레이트 리밋 범위 내에서 운영 가능

2. **사용자 사주 정보 정확성**
   - 사용자가 입력한 생년월일시가 정확하다고 가정
   - 사주 정보는 변경되지 않음 (캐싱 가능)

3. **캐싱 유효성**
   - 동일 사용자의 동일 날짜 운세는 변경되지 않는다고 가정
   - 일일 운세는 24시간, 주간은 7일, 월간은 30일, 연간은 365일 캐싱

4. **레거시 DB 안정성**
   - MSSQL 2005는 읽기 전용으로만 사용하며, 안정적으로 접근 가능
   - 레거시 DB 스키마 변경 없음

5. **관리자 수 제한**
   - 관리자는 최대 5명까지 동시 접속 가정 (초기 MVP)
   - 관리자 증가 시 SSE 연결 확장 필요

6. **AI BI 질의 범위**
   - 관리자 질문은 매출, 유저, 결제, 상담사 성과 등 정형 데이터 조회에 한정
   - 복잡한 비즈니스 로직은 Phase 2 이후 확장

7. **네트워크 안정성**
   - SSE 스트리밍은 HTTP/2 지원 환경에서 안정적으로 작동
   - 프록시/방화벽이 장기 연결을 차단하지 않음

8. **모바일 우선**
   - 사용자의 70% 이상이 모바일에서 접속
   - 모바일 퍼스트 UX 전략 유효

---

## 12. Out of Scope (MVP 제외 항목)

### 12.1 Part A: 사용자 서비스

| 기능 | 제외 이유 | 향후 계획 |
|------|-----------|-----------|
| **AI 채팅 상담** | Phase 2 범위 | 전문 상담사 데이터 기반 구현 |
| **상담사 AI 어시스턴트** | Phase 3 범위 | 상담사가 데이터 제공 → AI 상담 |
| **궁합 분석** | 추가 개발 필요 | 운세 안정화 후 검토 |
| **타로/꿈해몽** | 다른 도메인 | 장기 검토 |

### 12.2 Part B: 관리자 서비스

| 기능 | 제외 이유 | 향후 계획 |
|------|-----------|-----------|
| **GA4 연동** | Phase 4 범위 | 마케팅 ROI 측정 기능 |
| **SSE 스트리밍 응답 UI 고도화** | Phase 2 범위 | 타이핑 효과, 프로그레스바 등 |
| **Redis Checkpointing** | Phase 2 범위 | 대화 맥락 유지 기능 |
| **프로액티브 인사이트 제안** | Phase 3 범위 | "매출 떨어졌네요" → "원인 분석할까요?" |
| **시각화/차트 생성** | Phase 4 범위 | 텍스트/테이블 응답 우선 |
| **Schema-aware RAG** | Phase 3 범위 | 정확도 향상 기능 |

---

## 13. Open Questions (미해결 질문)

1. **OpenAI 모델 선택**
   - 질문: gpt-4o vs gpt-3.5-turbo vs gpt-4o-mini?
   - 영향: 비용 vs 품질 트레이드오프
   - 다음 단계: 운세 품질 테스트 필요

2. **AI 운세 프롬프트 템플릿**
   - 질문: 초기 프롬프트 버전을 누가 작성하나?
   - 영향: 운세 품질 및 사용자 만족도
   - 다음 단계: 사주 전문가 협력 필요 여부 검토

3. **AI BI 테이블 화이트리스트**
   - 질문: 어떤 테이블을 허용할 것인가?
   - 영향: 보안 vs 활용성
   - 다음 단계: 민감 정보 테이블 제외 기준 수립

4. **SSE 연결 수 제한**
   - 질문: 프로덕션 환경에서 동시 SSE 연결 제한은?
   - 영향: 서버 리소스 및 비용
   - 다음 단계: 서버 리소스 기반 결정 필요

5. **AI 운세 캐싱 정책**
   - 질문: 사용자가 캐시를 무효화하고 재생성을 요청할 수 있나?
   - 영향: 비용 vs 사용자 만족도
   - 다음 단계: UX 측면에서 "새로 운세 보기" 기능 필요 여부 검토

---

## 14. Stakeholders (이해관계자)

| 역할 | 인원 | 담당 | 주요 관심사 |
|------|------|------|-------------|
| **개발/총괄 관리자** | 1명 | 전체 개발, 서비스 관리 | 개발 속도, 기술 부채 최소화, AI 품질 |
| **운영 관리자** | 2명 | 일상 운영, 고객 지원 | AI BI 사용성, 데이터 정확성, 응답 속도 |
| **상담사** | 약 100명 | 전문 사주 상담 | AI 운세 품질, 사용자 만족도 |
| **사용자** | 수천 명 | 서비스 이용 | AI 운세 정확도, 빠른 응답, 모바일 UX |

---

## 15. Next Steps (다음 단계)

### 15.1 PRD 승인 후

1. **Architecture 설계**
   - 시스템 아키텍처 다이어그램 작성
   - 기술 스택 결정 (OpenAI 모델 선택 포함)
   - 데이터베이스 스키마 설계

2. **Epic Breakdown**
   - 각 Epic을 User Story로 분해
   - Story별 Acceptance Criteria 상세화
   - Story Point 산정

3. **Sprint Planning**
   - Sprint 1: EPIC-A01 + EPIC-B01 (인증 시스템)
   - Sprint 2: EPIC-A02 (AI 운세 서비스)
   - Sprint 3-4: EPIC-B02 + EPIC-B03 (AI BI 엔진 + 채팅 UI)
   - Sprint 5: EPIC-B04 (모니터링 및 운영)

4. **기술 검증 (PoC)**
   - OpenAI API 운세 품질 테스트
   - LangGraph 멀티 에이전트 프로토타입
   - SSE 스트리밍 연결 안정성 검증

### 15.2 Phase 2 이후 계획

- AI 채팅 상담 (사용자 서비스)
- SSE UI 고도화 + Redis Checkpointing (관리자 서비스)
- 대화 히스토리 및 북마크 기능

---

## 16. Revision History (변경 이력)

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2026-02-04 | 1.0.0 | 초기 PRD 생성 (Part A + Part B 통합) | DongDong |

---

**문서 끝**

---

**Generated by:** BMAD Method v6 - PRD Workflow
**Workflow Mode:** Integrated (Part A + Part B)
**Total Time:** ~90 minutes
**Quality Check:** ✅ All Must-Have FRs covered, NFRs comprehensive, Epics traceable
