---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
workflowStatus: 'completed'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
documentCounts:
  prd: 1
  architecture: 1
  ux: 0
workflowType: 'create-epics-and-stories'
projectType: 'brownfield'
project_name: 'admin-backend'
user_name: 'dongdong'
date: '2026-01-30'
---

# admin-backend - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for admin-backend (AI BI 어시스턴트), decomposing the requirements from the PRD and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

#### 자연어 질의 (Natural Language Query)
- **FR1**: 관리자는 자연어로 데이터 질의를 입력할 수 있다
- **FR2**: 시스템은 자연어 질의를 SQL로 변환할 수 있다
- **FR3**: 시스템은 질의 결과를 자연어 답변으로 제공할 수 있다
- **FR4**: 시스템은 질의 결과를 테이블 형태로 표시할 수 있다
- **FR5**: 관리자는 생성된 SQL을 확인할 수 있다 (선택적)
- **FR6**: 관리자는 접근성 모드로 텍스트 요약을 받을 수 있다

#### 데이터 소스 접근 (Data Source Access)
- **FR7**: 시스템은 MariaDB 데이터를 조회할 수 있다
- **FR8**: 시스템은 MSSQL 데이터를 조회할 수 있다
- **FR9**: 시스템은 허용된 테이블/컬럼만 조회할 수 있다
- **FR10**: 시스템은 두 DB의 데이터를 크로스 조인할 수 있다 (Phase 2)
- **FR11**: 시스템은 GA4 데이터를 조회할 수 있다 (Phase 4)

#### 보안 및 접근 제어 (Security & Access Control)
- **FR12**: 시스템은 인증된 관리자만 접근을 허용할 수 있다
- **FR13**: 시스템은 역할별 데이터 접근을 제한할 수 있다
- **FR14**: 시스템은 SQL Injection 공격을 차단할 수 있다
- **FR15**: 시스템은 금지된 테이블 접근을 차단할 수 있다
- **FR16**: 시스템은 민감 데이터를 마스킹할 수 있다
- **FR17**: 시스템은 모든 질의와 접근을 로깅할 수 있다

#### 사용자 경험 (User Experience)
- **FR18**: 관리자는 예시 질문 목록을 볼 수 있다
- **FR19**: 관리자는 이전 질의 히스토리를 조회할 수 있다
- **FR20**: 시스템은 에러 발생 시 사용자 친화적 메시지를 제공할 수 있다
- **FR21**: 시스템은 에러 시 대안 질문을 제안할 수 있다
- **FR22**: 관리자는 자주 묻는 질문 자동완성을 사용할 수 있다 (Phase 1.5)
- **FR23**: 시스템은 맥락 기반 후속 질문을 제안할 수 있다 (Phase 2)

#### 피드백 및 학습 (Feedback & Learning)
- **FR24**: 관리자는 질의 결과에 대해 피드백을 제공할 수 있다
- **FR25**: 관리자는 잘못된 답변을 수정하여 제출할 수 있다
- **FR26**: 관리자는 질의 결과를 1-5점으로 평가할 수 있다
- **FR27**: 시스템은 피드백 데이터를 수집하고 저장할 수 있다

#### 시스템 운영 (System Operations)
- **FR28**: 시스템은 요청 빈도를 제한할 수 있다 (Rate Limiting)
- **FR29**: 시스템은 LLM 장애 시 대체 서비스로 전환할 수 있다
- **FR30**: 시스템은 동일 질의에 대해 캐시된 응답을 제공할 수 있다
- **FR31**: 시스템은 서비스 상태를 헬스체크로 확인할 수 있다
- **FR32**: 시스템은 SLA 위반 시 알림을 발송할 수 있다

#### 스트리밍 응답 (Streaming Response) - Phase 2
- **FR33**: 시스템은 SSE로 실시간 응답을 스트리밍할 수 있다
- **FR34**: 관리자는 스트리밍 중 진행 상태를 확인할 수 있다

#### 프로액티브 인사이트 (Proactive Insights) - Phase 3
- **FR35**: 시스템은 이상 패턴 감지 시 알림을 발송할 수 있다
- **FR36**: 시스템은 예약된 리포트를 자동 생성할 수 있다
- **FR37**: 관리자는 알림 조건을 설정할 수 있다

#### 시각화 (Visualization) - Phase 3
- **FR38**: 시스템은 질의 결과를 차트로 시각화할 수 있다
- **FR39**: 관리자는 시각화 유형을 선택할 수 있다

#### GA4 통합 (GA4 Integration) - Phase 4
- **FR40**: 시스템은 유입 경로별 데이터를 조회할 수 있다
- **FR41**: 시스템은 유입-매출 연계 분석을 수행할 수 있다
- **FR42**: 시스템은 전환율 분석을 제공할 수 있다

### NonFunctional Requirements

#### 성능 (Performance)
- **NFR-P1**: 단일 DB 질의 응답 시간 p95 ≤ 3초 (Phase 1)
- **NFR-P2**: 크로스 DB 질의 응답 시간 p95 ≤ 5초 (Phase 2)
- **NFR-P3**: 스트리밍 첫 토큰 시간 (TTFB) ≤ 500ms (Phase 2)
- **NFR-P4**: 동시 사용자 처리 10명 동시 질의 (Phase 1)
- **NFR-P5**: 캐시 히트율 ≥ 30% (Phase 1.5)
- **NFR-P6**: LLM API 호출 최적화 - 동일 질의 캐싱 5분 (Phase 1)

#### 보안 (Security)
- **NFR-S1**: SQL Injection 차단율 100% (Phase 1)
- **NFR-S2**: 인증 우회 시도 차단 100% (Phase 1)
- **NFR-S3**: 민감 테이블 접근 차단 100% (정의된 테이블에 한해) (Phase 1)
- **NFR-S4**: 민감 데이터 마스킹 100% (정의된 필드에 한해) (Phase 1)
- **NFR-S5**: 감사 로그 보존 90일 (Phase 1)
- **NFR-S6**: Rate Limiting 20 RPM / 200 RPH (Phase 1)
- **NFR-S7**: 보안 이벤트 로깅 - 모든 차단 이벤트 (Phase 1)

#### 안정성 (Reliability)
- **NFR-R1**: 서비스 가용성 ≥ 99.5% (Phase 1)
- **NFR-R2**: LLM Fallback 성공률 ≥ 95% (Phase 1)
- **NFR-R3**: Circuit Breaker 동작 - 5회 실패 후 Open (Phase 1.5)
- **NFR-R4**: DB 연결 풀 안정성 - 연결 누수 0건 (Phase 1)
- **NFR-R5**: 에러 복구 시간 ≤ 30초 (Phase 1.5)
- **NFR-R6**: 질의 재시도 - 최대 3회 exponential backoff (Phase 1)

#### 통합 (Integration)
- **NFR-I1**: MariaDB 연결 풀 크기 5-20 connections (Phase 1)
- **NFR-I2**: MSSQL 연결 안정성 - TDS 7.0/7.1 호환 (Phase 2)
- **NFR-I3**: Redis 캐시 연결 - 실패 시 무캐시 동작 (Phase 1)
- **NFR-I4**: LLM API 타임아웃 10초 (Phase 1)
- **NFR-I5**: 기존 인증 시스템 통합 100% 호환 (Phase 1)
- **NFR-I6**: GA4 API 연동 - 일 10,000 요청 쿼터 (Phase 4)

#### 접근성 (Accessibility)
- **NFR-A1**: 스크린리더 호환 - 주요 기능 음성 안내 (Phase 1.5)
- **NFR-A2**: 키보드 네비게이션 - 모든 기능 키보드 접근 (Phase 1.5)
- **NFR-A3**: 텍스트 요약 모드 - 테이블 대신 텍스트 제공 (Phase 1)

#### 운영성 (Operability)
- **NFR-O1**: 구조화 로깅 - JSON 형식 + 요청 ID (Phase 1)
- **NFR-O2**: 메트릭 대시보드 - 주요 KPI 실시간 조회 (Phase 1.5)
- **NFR-O3**: 알림 설정 - SLA 위반 시 즉시 알림 (Phase 1.5)
- **NFR-O4**: LLM 비용 모니터링 - 월 상한 알림 (Phase 1)

#### 테스트 가능성 (Testability)
- **NFR-T1**: 단위 테스트 커버리지 ≥ 90% (Phase 1)

### Additional Requirements

#### Architecture Starter Template
- **AR1**: LangGraph 표준 통합 (Option A) 선택 - 공식 문서/예제 풍부, Redis Checkpointing 내장
- **AR2**: 의존성 설치: `uv add langchain langchain-openai langgraph langchain-community aiomysql pymssql pandas redis`

#### 디렉토리 구조
- **AR3**: `src/services/ai/` 하위에 AI 모듈 집중 구조
- **AR4**: agents/, tools/, prompts/, security/, utils/ 서브디렉토리 분리
- **AR5**: 테스트 구조: `tests/services/ai/` 하위에 unit/, integration/, golden/ 분리

#### 4-Layer Security 구현
- **AR6**: Layer 1 (Prompt): 시스템 프롬프트에 보안 지침 내장
- **AR7**: Layer 2 (Validation): SQL 화이트리스트 + 패턴 검증
- **AR8**: Layer 3 (Result): 결과 내 PII 마스킹, 행 수 제한
- **AR9**: Layer 4 (User): 위험 쿼리 시 확인 다이얼로그

#### AI Agent 패턴
- **AR10**: LLM 제공자: OpenAI gpt-4o-mini + Fallback (gpt-3.5-turbo)
- **AR11**: 에이전트 실행 패턴: Adaptive (Supervisor가 순차/병렬 결정)
- **AR12**: Checkpointing: Redis 기반 대화 컨텍스트 저장

#### 타입 및 출력 패턴
- **AR13**: 상태 타입: TypedDict 사용 (LangGraph 공식 패턴)
- **AR14**: 에이전트 출력 타입 계층: BaseAgentOutput → SQLAgentOutput
- **AR15**: SSE 이벤트 포맷: thinking|query|executing|result|error|done

#### 에러 처리 패턴
- **AR16**: AIError 클래스: code, technical_message, user_message, suggestion, recoverable
- **AR17**: 에러 코드 체계: AI_ERR_001 (LLM Timeout) ~ AI_ERR_004 (Rate Limited)

#### 운영 패턴
- **AR18**: Rate Limiting: Super Admin 60 req/min, Admin 30 req/min, Viewer 10 req/min
- **AR19**: Graceful Degradation: 4단계 (LLM Fallback → 단일 DB → 캐시 기반 → 에러 메시지)
- **AR20**: Timeout 계층: LLM Call 30초, Single Agent 45초, Full Request 60초

#### 테스트 패턴
- **AR21**: LLM Mock Fixture 사용 필수
- **AR22**: Golden Dataset 테스트: queries.json, sql_validation.json, responses.json
- **AR23**: Security 모듈 100% 테스트 커버리지 필수

### FR Coverage Map

| FR | Epic | 설명 |
|----|------|------|
| FR1 | Epic 2 | 자연어 데이터 질의 입력 |
| FR2 | Epic 2 | 자연어 → SQL 변환 |
| FR3 | Epic 2 | 자연어 답변 제공 |
| FR4 | Epic 2 | 테이블 형태 표시 |
| FR5 | Epic 2 | 생성된 SQL 확인 |
| FR6 | Epic 2 | 접근성 텍스트 요약 |
| FR7 | Epic 2 | MariaDB 조회 |
| FR8 | Epic 7 | MSSQL 조회 |
| FR9 | Epic 2 | 허용 테이블/컬럼만 조회 |
| FR10 | Epic 7 | 크로스 DB 조인 |
| FR11 | Epic 10 | GA4 조회 |
| FR12 | Epic 1 | 인증된 관리자만 접근 |
| FR13 | Epic 1 | 역할별 접근 제한 |
| FR14 | Epic 3 | SQL Injection 차단 |
| FR15 | Epic 3 | 금지 테이블 접근 차단 |
| FR16 | Epic 3 | 민감 데이터 마스킹 |
| FR17 | Epic 3 | 질의/접근 로깅 |
| FR18 | Epic 4 | 예시 질문 목록 |
| FR19 | Epic 4 | 질의 히스토리 조회 |
| FR20 | Epic 4 | 사용자 친화적 에러 메시지 |
| FR21 | Epic 4 | 대안 질문 제안 |
| FR22 | Epic 4 | 자동완성 (Phase 1.5) |
| FR23 | Epic 7 | 후속 질문 제안 |
| FR24 | Epic 5 | 피드백 제공 |
| FR25 | Epic 5 | 답변 수정 제출 |
| FR26 | Epic 5 | 1-5점 평가 |
| FR27 | Epic 5 | 피드백 저장 |
| FR28 | Epic 3 | Rate Limiting |
| FR29 | Epic 6 | LLM Fallback |
| FR30 | Epic 6 | 캐시 응답 |
| FR31 | Epic 1 | 헬스체크 |
| FR32 | Epic 6 | SLA 알림 |
| FR33 | Epic 8 | SSE 스트리밍 |
| FR34 | Epic 8 | 진행 상태 확인 |
| FR35 | Epic 9 | 이상 패턴 알림 |
| FR36 | Epic 9 | 자동 리포트 |
| FR37 | Epic 9 | 알림 조건 설정 |
| FR38 | Epic 9 | 차트 시각화 |
| FR39 | Epic 9 | 시각화 유형 선택 |
| FR40 | Epic 10 | 유입 경로 조회 |
| FR41 | Epic 10 | 유입-매출 연계 분석 |
| FR42 | Epic 10 | 전환율 분석 |

## Epic List

### Phase 1 (MVP) - 6 Epics

### Epic 1: AI 어시스턴트 접근 및 권한 (Access & Authorization)
관리자가 AI 어시스턴트 서비스에 안전하게 접근하고, 역할 기반 권한으로 데이터 조회 범위가 제한되며, LangGraph 기반 AI 인프라가 구축된다.

**FRs covered:** FR12, FR13, FR31
**Additional Requirements:** AR1-AR5 (Starter Template, 디렉토리 구조)
**Phase:** 1 (MVP)

---

### Epic 2: 자연어 MariaDB 질의 (Natural Language Query - MariaDB)
관리자가 자연어로 질문하면 MariaDB 데이터를 조회하고, 자연어 답변과 테이블 형태로 결과를 확인할 수 있다.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR9
**Additional Requirements:** AR10-AR15 (LLM 제공자, 에이전트 패턴, 타입/출력)
**Phase:** 1 (MVP)

---

### Epic 3: SQL 보안 및 감사 체계 (Security & Audit)
시스템이 SQL Injection을 차단하고, 민감 데이터를 마스킹하며, 모든 질의와 접근을 로깅하여 안전한 데이터 접근을 보장한다.

**FRs covered:** FR14, FR15, FR16, FR17, FR28
**Additional Requirements:** AR6-AR9 (4-Layer Security), AR18 (Rate Limiting)
**Phase:** 1 (MVP)

---

### Epic 4: 질의 경험 향상 (Query Experience Enhancement)
관리자가 예시 질문, 히스토리 조회, 친절한 에러 메시지와 대안 질문 제안으로 AI 어시스턴트를 쉽게 사용할 수 있다.

**FRs covered:** FR18, FR19, FR20, FR21, FR22
**Phase:** 1 (MVP), FR22는 Phase 1.5

---

### Epic 5: 피드백 수집 (Feedback Collection)
관리자가 AI 응답에 피드백을 제공하고, 잘못된 답변을 수정하며, 1-5점 평가를 통해 서비스 개선에 기여할 수 있다.

**FRs covered:** FR24, FR25, FR26, FR27
**Phase:** 1 (MVP)

---

### Epic 6: 시스템 안정성 및 운영 (System Reliability & Operations)
LLM 장애 시 자동 폴백, 캐싱, SLA 모니터링으로 관리자가 안정적이고 빠른 서비스를 경험할 수 있다.

**FRs covered:** FR29, FR30, FR32
**Additional Requirements:** AR16-AR17 (에러 처리), AR19-AR20 (Degradation, Timeout), AR21-AR23 (테스트)
**Phase:** 1 (MVP)

---

### Phase 2 - 2 Epics

### Epic 7: MSSQL 및 크로스 DB 분석 (Cross-DB Analysis)
관리자가 MSSQL 데이터를 조회하고, MariaDB와 MSSQL을 통합 분석하여 상담사 성과 등 크로스 DB 인사이트를 얻을 수 있다.

**FRs covered:** FR8, FR10, FR23
**Phase:** 2

---

### Epic 8: 실시간 SSE 스트리밍 (Real-time Streaming)
관리자가 AI 응답을 실시간으로 스트리밍 받으며, 진행 상태를 확인할 수 있다.

**FRs covered:** FR33, FR34
**Phase:** 2

---

### Phase 3 - 1 Epic

### Epic 9: 프로액티브 인사이트 및 시각화 (Insights & Visualization)
시스템이 이상 패턴을 감지하여 알림을 발송하고, 자동 리포트를 생성하며, 차트로 데이터를 시각화한다.

**FRs covered:** FR35, FR36, FR37, FR38, FR39
**Phase:** 3

---

### Phase 4 - 1 Epic

### Epic 10: GA4 통합 분석 (GA4 Integration)
관리자가 GA4 데이터를 조회하여 유입-매출 연계 분석, 전환율 분석을 수행할 수 있다.

**FRs covered:** FR11, FR40, FR41, FR42
**Phase:** 4

---

## Epic Summary

| Phase | Epic 수 | FR 수 | 핵심 가치 |
|-------|---------|-------|----------|
| **Phase 1 (MVP)** | 6 | 31 | 기본 AI 질의, 보안, UX, 피드백, 안정성 |
| **Phase 2** | 2 | 5 | 크로스 DB, 스트리밍 |
| **Phase 3** | 1 | 5 | 인사이트, 시각화 |
| **Phase 4** | 1 | 4 | GA4 통합 |
| **Total** | **10** | **42** | |

---

## User Stories

### Phase 1 (MVP) Stories

---

### Epic 1: AI 어시스턴트 접근 및 권한 (3 Stories)

#### Story 1.1: LangGraph 기반 AI 인프라 설정

**As a** 시스템 관리자
**I want** LangGraph 기반 AI 에이전트 인프라가 구축되어 있기를
**So that** AI 어시스턴트 서비스의 기반 아키텍처가 준비된다

**Acceptance Criteria:**
1. LangGraph, LangChain, OpenAI 의존성이 설치된다
2. `src/services/ai/` 디렉토리 구조가 생성된다 (agents/, tools/, prompts/, security/, utils/)
3. Redis 기반 LangGraph Checkpointing이 설정된다
4. 기본 Supervisor 에이전트 스켈레톤이 생성된다
5. 헬스체크 엔드포인트가 AI 서비스 상태를 포함한다

**Technical Notes:**
- AR1: LangGraph 표준 통합 (Option A)
- AR2: `uv add langchain langchain-openai langgraph langchain-community aiomysql redis`
- AR3-AR5: 디렉토리 구조 생성
- AR12: Redis Checkpointing 설정

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** 없음

---

#### Story 1.2: 기존 인증 시스템 연동

**As a** 관리자
**I want** 기존 admin-backend 인증 시스템으로 AI 어시스턴트에 접근하기를
**So that** 별도 로그인 없이 안전하게 AI 서비스를 사용할 수 있다

**Acceptance Criteria:**
1. 기존 JWT 인증 토큰으로 AI 엔드포인트 접근이 가능하다
2. 인증되지 않은 요청은 401 에러를 반환한다
3. 세션 만료 시 적절한 에러 메시지를 표시한다
4. AI 서비스 인증 로그가 기록된다

**Technical Notes:**
- FR12: 인증된 관리자만 접근 허용
- NFR-I5: 기존 인증 시스템 100% 호환
- 기존 `src/services/auth_service.py` 활용

**Story Points:** 3
**Priority:** P0 - MVP 필수
**Dependencies:** Story 1.1

---

#### Story 1.3: 역할 기반 접근 제어 설정

**As a** Super Admin
**I want** 역할별로 AI 어시스턴트 접근 권한이 제한되기를
**So that** 각 역할에 적합한 데이터만 조회할 수 있다

**Acceptance Criteria:**
1. Super Admin은 모든 AI 기능에 접근 가능하다
2. Admin은 제한된 테이블 집합에 접근 가능하다
3. Viewer는 읽기 전용 질의만 가능하다
4. 권한이 없는 접근 시도는 403 에러와 함께 로깅된다
5. 역할별 Rate Limiting이 적용된다 (Super Admin: 60/min, Admin: 30/min, Viewer: 10/min)

**Technical Notes:**
- FR13: 역할별 데이터 접근 제한
- FR31: 헬스체크 (역할 확인 포함)
- AR18: 역할별 Rate Limiting
- 테이블-역할 매핑 설정 파일 필요

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 1.2

---

### Epic 2: 자연어 MariaDB 질의 (5 Stories)

#### Story 2.1: 자연어 질의 입력 인터페이스

**As a** 관리자
**I want** 자연어로 데이터 질문을 입력할 수 있기를
**So that** SQL을 몰라도 데이터를 조회할 수 있다

**Acceptance Criteria:**
1. 질의 입력 텍스트 영역이 제공된다
2. 질의 제출 버튼이 제공된다
3. 입력 유효성 검사가 수행된다 (빈 값, 최대 길이)
4. 로딩 상태가 표시된다
5. API 엔드포인트 `POST /api/v1/ai/query`가 구현된다

**Technical Notes:**
- FR1: 자연어 질의 입력
- Admin Frontend Vue 컴포넌트 구현 필요
- API 스키마: `AIQueryRequest`, `AIQueryResponse`

**Story Points:** 3
**Priority:** P0 - MVP 필수
**Dependencies:** Story 1.3

---

#### Story 2.2: LLM 기반 SQL 생성 에이전트

**As a** 시스템
**I want** 자연어 질의를 SQL로 변환할 수 있기를
**So that** MariaDB에서 데이터를 조회할 수 있다

**Acceptance Criteria:**
1. OpenAI gpt-4o-mini를 사용하여 자연어를 SQL로 변환한다
2. 시스템 프롬프트에 DB 스키마 정보가 포함된다
3. SELECT 문만 생성되도록 제한된다
4. 생성된 SQL이 응답에 포함된다 (선택적 표시)
5. LLM 호출 타임아웃이 10초로 설정된다

**Technical Notes:**
- FR2: 자연어 → SQL 변환
- AR10: gpt-4o-mini 사용
- AR11: Adaptive 실행 패턴
- NFR-I4: LLM API 타임아웃 10초
- 프롬프트 템플릿: `src/services/ai/prompts/sql_generation.py`

**Story Points:** 8
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.1

---

#### Story 2.3: MariaDB 질의 실행 및 허용 필터링

**As a** 시스템
**I want** 생성된 SQL을 MariaDB에서 실행하고 허용된 테이블만 접근하기를
**So that** 안전하게 데이터를 조회할 수 있다

**Acceptance Criteria:**
1. MariaDB 에이전트가 SQL을 실행한다
2. 화이트리스트 테이블/컬럼만 접근이 허용된다
3. 허용되지 않은 테이블 접근 시 에러가 반환된다
4. 쿼리 결과 행 수가 1000개로 제한된다
5. 연결 풀이 5-20 connections로 관리된다

**Technical Notes:**
- FR7: MariaDB 조회
- FR9: 허용 테이블/컬럼만 조회
- NFR-I1: 연결 풀 크기 5-20
- NFR-R4: 연결 누수 0건
- `src/services/ai/tools/mariadb_tool.py` 구현

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.2

---

#### Story 2.4: 자연어 응답 생성 및 결과 포맷팅

**As a** 관리자
**I want** 질의 결과를 자연어 답변과 테이블로 확인하기를
**So that** 데이터를 쉽게 이해할 수 있다

**Acceptance Criteria:**
1. LLM이 쿼리 결과를 자연어 요약으로 변환한다
2. 테이블 형태의 결과가 함께 표시된다
3. 결과가 없을 경우 적절한 메시지가 표시된다
4. 응답 시간이 p95 3초 이내이다
5. TypedDict 기반 응답 타입이 사용된다

**Technical Notes:**
- FR3: 자연어 답변 제공
- FR4: 테이블 형태 표시
- AR13-AR15: TypedDict 타입, BaseAgentOutput
- NFR-P1: 응답 시간 p95 ≤ 3초
- 응답 포맷터: `src/services/ai/utils/response_formatter.py`

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.3

---

#### Story 2.5: SQL 확인 및 접근성 모드

**As a** 관리자
**I want** 생성된 SQL을 선택적으로 확인하고 접근성 모드로 텍스트 요약을 받기를
**So that** 투명성과 접근성이 보장된다

**Acceptance Criteria:**
1. "SQL 보기" 토글 버튼이 제공된다
2. 토글 시 생성된 SQL이 코드 블록으로 표시된다
3. 접근성 모드 설정이 제공된다
4. 접근성 모드에서는 테이블 대신 텍스트 요약만 제공된다
5. 스크린리더 호환 마크업이 적용된다

**Technical Notes:**
- FR5: 생성된 SQL 확인 (선택적)
- FR6: 접근성 텍스트 요약
- NFR-A1: 스크린리더 호환
- NFR-A3: 텍스트 요약 모드

**Story Points:** 3
**Priority:** P1 - Phase 1.5
**Dependencies:** Story 2.4

---

### Epic 3: SQL 보안 및 감사 체계 (4 Stories)

#### Story 3.1: 4-Layer Security 프레임워크

**As a** 시스템
**I want** 4계층 보안 프레임워크가 적용되기를
**So that** 다층 방어로 데이터 보안이 보장된다

**Acceptance Criteria:**
1. Layer 1 (Prompt): 시스템 프롬프트에 보안 지침이 내장된다
2. Layer 2 (Validation): SQL 화이트리스트 검증이 구현된다
3. Layer 3 (Result): 결과 내 PII 마스킹이 구현된다
4. Layer 4 (User): 위험 쿼리 시 확인 다이얼로그가 표시된다
5. 보안 모듈 테스트 커버리지가 100%이다

**Technical Notes:**
- AR6-AR9: 4-Layer Security 구현
- AR23: Security 모듈 100% 테스트 커버리지
- `src/services/ai/security/` 디렉토리 구현

**Story Points:** 8
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.3

---

#### Story 3.2: SQL Injection 방지 및 테이블 접근 제어

**As a** 시스템
**I want** SQL Injection 공격을 차단하고 금지된 테이블 접근을 방지하기를
**So that** 악의적 공격으로부터 데이터가 보호된다

**Acceptance Criteria:**
1. SQL Injection 패턴이 탐지되면 요청이 차단된다
2. 금지된 테이블 접근 시도가 차단된다
3. 차단된 모든 시도가 보안 로그에 기록된다
4. SQL Injection 차단율이 100%이다
5. 화이트리스트 외 테이블 접근 차단율이 100%이다

**Technical Notes:**
- FR14: SQL Injection 차단
- FR15: 금지 테이블 접근 차단
- NFR-S1: SQL Injection 차단율 100%
- NFR-S3: 민감 테이블 접근 차단 100%
- NFR-S7: 보안 이벤트 로깅
- `src/services/ai/security/sql_validator.py` 구현

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 3.1

---

#### Story 3.3: 민감 데이터 마스킹

**As a** 시스템
**I want** 질의 결과 내 민감 데이터를 마스킹하기를
**So that** PII가 노출되지 않는다

**Acceptance Criteria:**
1. 정의된 민감 필드가 마스킹된다 (전화번호, 이메일 등)
2. 마스킹 규칙이 설정 파일로 관리된다
3. 마스킹된 필드가 로그에 표시된다
4. 민감 데이터 마스킹율이 100%이다
5. 역할별 마스킹 수준이 다르게 적용된다

**Technical Notes:**
- FR16: 민감 데이터 마스킹
- NFR-S4: 민감 데이터 마스킹 100%
- AR8: Layer 3 Result Validation
- `src/services/ai/security/data_masking.py` 구현

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 3.1

---

#### Story 3.4: 감사 로깅 및 Rate Limiting

**As a** 시스템 관리자
**I want** 모든 질의와 접근이 로깅되고 요청 빈도가 제한되기를
**So that** 보안 감사와 남용 방지가 가능하다

**Acceptance Criteria:**
1. 모든 AI 질의가 JSON 형식으로 로깅된다
2. 로그에 요청 ID, 사용자, 질의, 결과 요약이 포함된다
3. 감사 로그가 90일간 보존된다
4. Rate Limiting이 역할별로 적용된다
5. Rate Limit 초과 시 429 에러가 반환된다

**Technical Notes:**
- FR17: 질의/접근 로깅
- FR28: Rate Limiting
- NFR-S5: 감사 로그 보존 90일
- NFR-S6: Rate Limiting 20 RPM / 200 RPH
- NFR-O1: 구조화 로깅 JSON + 요청 ID
- AR18: 역할별 Rate Limiting

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 1.3

---

### Epic 4: 질의 경험 향상 (3 Stories)

#### Story 4.1: 예시 질문 및 질의 히스토리

**As a** 관리자
**I want** 예시 질문을 보고 이전 질의 히스토리를 조회하기를
**So that** AI 어시스턴트를 쉽게 시작하고 이전 작업을 이어갈 수 있다

**Acceptance Criteria:**
1. 도메인별 예시 질문 목록이 표시된다 (최소 10개)
2. 예시 질문 클릭 시 입력 필드에 자동 입력된다
3. 최근 질의 히스토리가 표시된다 (최대 20개)
4. 히스토리 항목 클릭 시 해당 질의가 재실행된다
5. 히스토리 검색 기능이 제공된다

**Technical Notes:**
- FR18: 예시 질문 목록
- FR19: 질의 히스토리 조회
- API: `GET /api/v1/ai/examples`, `GET /api/v1/ai/history`
- Redis 캐시: 예시 질문 목록

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.4

---

#### Story 4.2: 사용자 친화적 에러 및 대안 제안

**As a** 관리자
**I want** 에러 발생 시 친절한 메시지와 대안 질문을 받기를
**So that** 에러 상황에서도 원하는 데이터를 찾을 수 있다

**Acceptance Criteria:**
1. 기술적 에러가 사용자 친화적 메시지로 변환된다
2. 에러 시 관련된 대안 질문이 최대 3개 제안된다
3. 대안 질문 클릭 시 해당 질의가 실행된다
4. 에러 코드와 기술적 메시지가 선택적으로 표시된다
5. 에러 유형별 적절한 안내가 제공된다

**Technical Notes:**
- FR20: 사용자 친화적 에러 메시지
- FR21: 대안 질문 제안
- AR16-AR17: AIError 클래스, 에러 코드 체계
- `src/services/ai/utils/error_handler.py` 구현

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.4

---

#### Story 4.3: 자동완성 기능

**As a** 관리자
**I want** 질의 입력 시 자동완성 제안을 받기를
**So that** 빠르게 정확한 질문을 작성할 수 있다

**Acceptance Criteria:**
1. 입력 중 실시간 자동완성 제안이 표시된다
2. 자주 사용된 질문이 우선 제안된다
3. 테이블/컬럼 이름이 자동완성에 포함된다
4. 키보드로 자동완성 항목을 선택할 수 있다
5. 캐시 히트율이 30% 이상이다

**Technical Notes:**
- FR22: 자동완성 (Phase 1.5)
- NFR-P5: 캐시 히트율 ≥ 30%
- Debounce 적용 (300ms)
- Redis 기반 자동완성 인덱스

**Story Points:** 5
**Priority:** P1 - Phase 1.5
**Dependencies:** Story 4.1

---

### Epic 5: 피드백 수집 (3 Stories)

#### Story 5.1: 피드백 제출 인터페이스

**As a** 관리자
**I want** AI 응답에 대해 별점과 피드백을 제출하기를
**So that** 서비스 개선에 기여할 수 있다

**Acceptance Criteria:**
1. 각 응답에 1-5점 별점 평가 UI가 제공된다
2. 선택적 텍스트 피드백 입력란이 제공된다
3. 피드백 제출 시 확인 메시지가 표시된다
4. 피드백 제출이 비동기로 처리되어 UX가 방해받지 않는다
5. 제출된 피드백이 응답 ID와 연결된다

**Technical Notes:**
- FR24: 피드백 제공
- FR26: 1-5점 평가
- API: `POST /api/v1/ai/feedback`
- 스키마: `AIFeedbackRequest`, `AIFeedbackResponse`

**Story Points:** 3
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.4

---

#### Story 5.2: 답변 수정 기능

**As a** 관리자
**I want** 잘못된 AI 답변을 수정하여 제출하기를
**So that** 정확한 데이터로 AI가 학습할 수 있다

**Acceptance Criteria:**
1. "답변 수정" 버튼이 각 응답에 제공된다
2. 수정 모드에서 자연어 답변을 편집할 수 있다
3. 수정된 답변이 원본과 함께 저장된다
4. 수정 이력이 관리된다
5. 수정된 답변이 향후 학습 데이터로 표시된다

**Technical Notes:**
- FR25: 답변 수정 제출
- API: `PUT /api/v1/ai/feedback/{response_id}/correction`
- 데이터 모델: `AIFeedbackCorrection`

**Story Points:** 5
**Priority:** P1 - Phase 1.5
**Dependencies:** Story 5.1

---

#### Story 5.3: 피드백 저장 및 분석 API

**As a** 시스템 관리자
**I want** 피드백 데이터가 저장되고 분석 가능하기를
**So that** AI 성능을 모니터링하고 개선 방향을 파악할 수 있다

**Acceptance Criteria:**
1. 모든 피드백이 DB에 저장된다
2. 피드백 통계 API가 제공된다 (평균 점수, 분포)
3. 낮은 점수 피드백 목록 조회가 가능하다
4. 피드백 데이터 내보내기가 가능하다
5. 피드백 대시보드가 제공된다 (Phase 1.5)

**Technical Notes:**
- FR27: 피드백 저장
- API: `GET /api/v1/ai/feedback/stats`, `GET /api/v1/ai/feedback/low-score`
- 데이터 모델: `AIFeedback` 테이블

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 5.1

---

### Epic 6: 시스템 안정성 및 운영 (3 Stories)

#### Story 6.1: LLM Fallback 및 Circuit Breaker

**As a** 시스템
**I want** LLM 장애 시 자동으로 대체 모델로 전환하기를
**So that** 서비스 연속성이 보장된다

**Acceptance Criteria:**
1. gpt-4o-mini 실패 시 gpt-3.5-turbo로 자동 전환된다
2. Circuit Breaker가 5회 실패 후 Open 상태가 된다
3. Half-Open 상태에서 테스트 요청이 시도된다
4. Fallback 성공률이 95% 이상이다
5. 상태 변경이 로깅된다

**Technical Notes:**
- FR29: LLM Fallback
- AR10: gpt-4o-mini + Fallback (gpt-3.5-turbo)
- AR19: 4단계 Graceful Degradation
- NFR-R2: LLM Fallback 성공률 ≥ 95%
- NFR-R3: Circuit Breaker 5회 실패 후 Open
- `src/services/ai/utils/circuit_breaker.py` 구현

**Story Points:** 8
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.2

---

#### Story 6.2: 응답 캐싱 시스템

**As a** 시스템
**I want** 동일 질의에 대해 캐시된 응답을 제공하기를
**So that** 응답 속도가 향상되고 LLM 비용이 절감된다

**Acceptance Criteria:**
1. 동일 질의에 대해 5분간 캐시된 응답이 제공된다
2. 캐시 히트 시 응답에 캐시 표시가 포함된다
3. 스키마 변경 시 관련 캐시가 무효화된다
4. 캐시 통계가 모니터링된다
5. Redis 연결 실패 시 무캐시로 동작한다

**Technical Notes:**
- FR30: 캐시 응답
- NFR-P6: 동일 질의 캐싱 5분
- NFR-I3: Redis 실패 시 무캐시 동작
- Redis 스키마 캐시: TTL 1시간, 쿼리 캐시: TTL 5분
- `src/services/ai/utils/cache_manager.py` 구현

**Story Points:** 5
**Priority:** P0 - MVP 필수
**Dependencies:** Story 2.4

---

#### Story 6.3: SLA 모니터링 및 알림

**As a** 시스템 관리자
**I want** SLA 위반 시 알림을 받기를
**So that** 서비스 문제를 빠르게 인지하고 대응할 수 있다

**Acceptance Criteria:**
1. 응답 시간 SLA (p95 3초) 위반이 감지된다
2. 에러율 임계값 초과가 감지된다
3. LLM 비용 월 상한 도달 시 알림이 발송된다
4. Slack/이메일 알림이 지원된다
5. 메트릭 대시보드가 제공된다 (Phase 1.5)

**Technical Notes:**
- FR32: SLA 알림
- NFR-O3: SLA 위반 시 즉시 알림
- NFR-O4: LLM 비용 월 상한 알림
- AR21-AR23: 테스트 패턴, Golden Dataset
- Sentry 연동, 커스텀 메트릭

**Story Points:** 5
**Priority:** P1 - Phase 1.5
**Dependencies:** Story 6.1

---

### Phase 2 Stories

---

### Epic 7: MSSQL 및 크로스 DB 분석 (3 Stories)

#### Story 7.1: MSSQL 에이전트 구현

**As a** 관리자
**I want** MSSQL (상담사 시스템) 데이터를 조회하기를
**So that** 상담사 관련 정보를 AI로 분석할 수 있다

**Acceptance Criteria:**
1. MSSQL 2005 연결이 TDS 7.0/7.1 프로토콜로 구현된다
2. pymssql 드라이버가 사용된다
3. EUC-KR 인코딩이 처리된다
4. asyncio.to_thread()로 비동기 래핑된다
5. MSSQL 전용 프롬프트 템플릿이 구현된다

**Technical Notes:**
- FR8: MSSQL 조회
- NFR-I2: MSSQL TDS 7.0/7.1 호환
- `src/services/ai/agents/mssql_agent.py` 구현
- `src/services/ai/tools/mssql_tool.py` 구현

**Story Points:** 8
**Priority:** P0 - Phase 2 필수
**Dependencies:** Epic 1-6 완료

---

#### Story 7.2: 크로스 DB 조인 Supervisor

**As a** 관리자
**I want** MariaDB와 MSSQL 데이터를 통합 분석하기를
**So that** 상담사 성과와 사용자 데이터를 연계하여 인사이트를 얻을 수 있다

**Acceptance Criteria:**
1. Supervisor 에이전트가 크로스 DB 질의를 감지한다
2. MariaDB와 MSSQL 에이전트가 병렬로 실행된다
3. pandas.merge()로 결과가 조인된다
4. asyncio.Semaphore(5)로 동시성이 제어된다
5. 크로스 DB 응답 시간이 p95 5초 이내이다

**Technical Notes:**
- FR10: 크로스 DB 조인
- NFR-P2: 크로스 DB 응답 p95 ≤ 5초
- AR11: Adaptive 실행 (순차/병렬 결정)
- `src/services/ai/agents/supervisor.py` 확장

**Story Points:** 8
**Priority:** P0 - Phase 2 필수
**Dependencies:** Story 7.1

---

#### Story 7.3: 맥락 기반 후속 질문 제안

**As a** 관리자
**I want** 현재 질의에 관련된 후속 질문을 제안받기를
**So that** 더 깊은 분석을 쉽게 수행할 수 있다

**Acceptance Criteria:**
1. 각 응답에 관련 후속 질문 3개가 제안된다
2. 후속 질문은 현재 컨텍스트를 기반으로 생성된다
3. 후속 질문 클릭 시 컨텍스트가 유지된 채 실행된다
4. LangGraph Checkpointing이 대화 컨텍스트를 저장한다
5. 후속 질문은 크로스 DB 분석을 포함할 수 있다

**Technical Notes:**
- FR23: 맥락 기반 후속 질문 제안
- AR12: Redis Checkpointing
- 프롬프트: 후속 질문 생성 전용

**Story Points:** 5
**Priority:** P1 - Phase 2
**Dependencies:** Story 7.2

---

### Epic 8: 실시간 SSE 스트리밍 (2 Stories)

#### Story 8.1: SSE 스트리밍 인프라

**As a** 관리자
**I want** AI 응답을 실시간으로 스트리밍 받기를
**So that** 긴 응답도 대기 없이 점진적으로 확인할 수 있다

**Acceptance Criteria:**
1. FastAPI StreamingResponse로 SSE가 구현된다
2. 이벤트 타입: thinking|query|executing|result|error|done
3. 첫 토큰 시간 (TTFB)이 500ms 이내이다
4. 연결 끊김 시 재연결이 지원된다
5. 클라이언트 EventSource 구현이 포함된다

**Technical Notes:**
- FR33: SSE 스트리밍
- AR15: SSE 이벤트 포맷
- NFR-P3: TTFB ≤ 500ms
- API: `GET /api/v1/ai/query/stream`

**Story Points:** 8
**Priority:** P0 - Phase 2 필수
**Dependencies:** Epic 7 완료

---

#### Story 8.2: 진행 상태 UI

**As a** 관리자
**I want** AI 처리 진행 상태를 실시간으로 확인하기를
**So that** 현재 무슨 단계인지 알 수 있다

**Acceptance Criteria:**
1. "생각 중...", "SQL 생성 중...", "실행 중..." 등 단계가 표시된다
2. 각 단계의 예상 시간이 표시된다
3. 에러 발생 시 해당 단계에서 에러가 표시된다
4. 완료 시 전체 소요 시간이 표시된다
5. 진행률 표시가 제공된다

**Technical Notes:**
- FR34: 진행 상태 확인
- SSE 이벤트 기반 UI 업데이트
- Vue 컴포넌트: `QueryProgress.vue`

**Story Points:** 3
**Priority:** P0 - Phase 2 필수
**Dependencies:** Story 8.1

---

### Phase 3 Stories

---

### Epic 9: 프로액티브 인사이트 및 시각화 (4 Stories)

#### Story 9.1: 이상 패턴 감지 엔진

**As a** 관리자
**I want** 데이터의 이상 패턴이 감지되면 알림을 받기를
**So that** 문제를 사전에 인지하고 대응할 수 있다

**Acceptance Criteria:**
1. 정의된 이상 패턴 규칙이 주기적으로 검사된다
2. 이상 감지 시 알림이 발송된다
3. 이상 패턴 유형: 급격한 변화, 임계값 초과, 패턴 이탈
4. 이상 감지 히스토리가 조회 가능하다
5. 오탐 피드백으로 규칙이 개선된다

**Technical Notes:**
- FR35: 이상 패턴 알림
- Celery/APScheduler 기반 스케줄링
- 알림 채널: Slack, 이메일, 인앱

**Story Points:** 8
**Priority:** P0 - Phase 3 필수
**Dependencies:** Phase 2 완료

---

#### Story 9.2: 예약 리포트 생성기

**As a** 관리자
**I want** 정의된 리포트가 자동으로 생성되기를
**So that** 반복 작업 없이 정기 보고서를 받을 수 있다

**Acceptance Criteria:**
1. 리포트 템플릿을 정의할 수 있다
2. 일/주/월 스케줄을 설정할 수 있다
3. 리포트가 이메일로 발송된다
4. PDF/Excel 형식이 지원된다
5. 리포트 히스토리가 조회 가능하다

**Technical Notes:**
- FR36: 자동 리포트 생성
- 템플릿 엔진: Jinja2
- PDF 생성: WeasyPrint 또는 puppeteer

**Story Points:** 8
**Priority:** P1 - Phase 3
**Dependencies:** Story 9.1

---

#### Story 9.3: 알림 조건 관리

**As a** 관리자
**I want** 알림 조건을 직접 설정하기를
**So that** 내 업무에 맞는 알림을 받을 수 있다

**Acceptance Criteria:**
1. 알림 조건 CRUD UI가 제공된다
2. 조건: 메트릭, 연산자, 임계값을 설정할 수 있다
3. 알림 채널을 선택할 수 있다
4. 알림 빈도를 제한할 수 있다 (예: 1시간에 1회)
5. 알림 조건 템플릿이 제공된다

**Technical Notes:**
- FR37: 알림 조건 설정
- 데이터 모델: `AlertRule` 테이블
- API: `CRUD /api/v1/ai/alerts`

**Story Points:** 5
**Priority:** P1 - Phase 3
**Dependencies:** Story 9.1

---

#### Story 9.4: 차트 시각화

**As a** 관리자
**I want** 질의 결과를 차트로 시각화하기를
**So that** 데이터 트렌드를 직관적으로 파악할 수 있다

**Acceptance Criteria:**
1. 라인, 바, 파이 차트가 지원된다
2. AI가 적합한 차트 유형을 자동 추천한다
3. 차트 유형을 수동으로 변경할 수 있다
4. 차트를 이미지로 다운로드할 수 있다
5. 차트 설정이 저장/재사용 가능하다

**Technical Notes:**
- FR38: 차트 시각화
- FR39: 시각화 유형 선택
- 라이브러리: Chart.js 또는 ECharts
- Vue 컴포넌트: `DataChart.vue`

**Story Points:** 8
**Priority:** P0 - Phase 3 필수
**Dependencies:** Phase 2 완료

---

### Phase 4 Stories

---

### Epic 10: GA4 통합 분석 (4 Stories)

#### Story 10.1: GA4 에이전트 및 API 연동

**As a** 관리자
**I want** GA4 데이터를 조회하기를
**So that** 웹사이트 트래픽 데이터를 AI로 분석할 수 있다

**Acceptance Criteria:**
1. Google Analytics Data API가 연동된다
2. GA4 전용 에이전트가 구현된다
3. 일 10,000 요청 쿼터가 관리된다
4. 유입 경로, 페이지뷰, 이벤트 데이터가 조회된다
5. GA4 프롬프트 템플릿이 구현된다

**Technical Notes:**
- FR11: GA4 조회
- FR40: 유입 경로 조회
- NFR-I6: GA4 API 일 10,000 요청 쿼터
- `src/services/ai/agents/ga4_agent.py` 구현

**Story Points:** 8
**Priority:** P0 - Phase 4 필수
**Dependencies:** Phase 3 완료

---

#### Story 10.2: 유입-매출 연계 분석

**As a** 관리자
**I want** GA4 유입 데이터와 매출 데이터를 연계 분석하기를
**So that** 마케팅 ROI를 파악할 수 있다

**Acceptance Criteria:**
1. GA4 유입 경로별 매출이 분석된다
2. 캠페인별 ROI가 계산된다
3. 유입 소스별 전환율이 표시된다
4. 기간 비교 분석이 지원된다
5. 분석 결과가 차트로 시각화된다

**Technical Notes:**
- FR41: 유입-매출 연계 분석
- GA4 + MariaDB 크로스 분석
- 사용자 식별자 매핑 필요

**Story Points:** 8
**Priority:** P0 - Phase 4 필수
**Dependencies:** Story 10.1

---

#### Story 10.3: 전환율 분석

**As a** 관리자
**I want** 퍼널별 전환율을 분석하기를
**So that** 전환 병목을 파악하고 개선할 수 있다

**Acceptance Criteria:**
1. 정의된 퍼널 단계별 전환율이 계산된다
2. 이탈 지점이 시각화된다
3. 기간별 전환율 트렌드가 표시된다
4. 세그먼트별 전환율 비교가 가능하다
5. AI가 전환율 개선 인사이트를 제공한다

**Technical Notes:**
- FR42: 전환율 분석
- GA4 이벤트 기반 퍼널
- 퍼널 정의 설정 UI 필요

**Story Points:** 5
**Priority:** P0 - Phase 4 필수
**Dependencies:** Story 10.1

---

#### Story 10.4: 통합 분석 대시보드

**As a** 관리자
**I want** 모든 데이터 소스를 한 화면에서 분석하기를
**So that** 전체적인 비즈니스 현황을 파악할 수 있다

**Acceptance Criteria:**
1. MariaDB, MSSQL, GA4 데이터가 통합 표시된다
2. 주요 KPI 위젯이 제공된다
3. 대시보드 레이아웃을 커스터마이징할 수 있다
4. 대시보드가 저장/공유 가능하다
5. 자동 새로고침이 지원된다

**Technical Notes:**
- 3개 데이터 소스 통합 뷰
- 대시보드 설정 저장
- Vue 컴포넌트: `IntegratedDashboard.vue`

**Story Points:** 8
**Priority:** P1 - Phase 4
**Dependencies:** Story 10.2, Story 10.3

---

## Story Summary

| Phase | Epic 수 | Story 수 | Story Points |
|-------|---------|----------|--------------|
| **Phase 1 (MVP)** | 6 | 21 | 96 |
| **Phase 2** | 2 | 5 | 32 |
| **Phase 3** | 1 | 4 | 29 |
| **Phase 4** | 1 | 4 | 29 |
| **Total** | **10** | **34** | **186** |

---

## Implementation Priority Order

### Phase 1 MVP 구현 순서

1. **Story 1.1** → 1.2 → 1.3 (인프라 및 인증)
2. **Story 2.1** → 2.2 → 2.3 → 2.4 (자연어 질의 핵심)
3. **Story 3.1** → 3.2 → 3.3 → 3.4 (보안)
4. **Story 6.1** → 6.2 (안정성)
5. **Story 4.1** → 4.2 (UX)
6. **Story 5.1** → 5.3 (피드백)

### Phase 1.5 (Optional)
- Story 2.5, 4.3, 5.2, 6.3

### Phase 2 구현 순서
1. **Story 7.1** → 7.2 → 7.3 (크로스 DB)
2. **Story 8.1** → 8.2 (스트리밍)

### Phase 3 구현 순서
1. **Story 9.1** → 9.2 → 9.3 (인사이트)
2. **Story 9.4** (시각화)

### Phase 4 구현 순서
1. **Story 10.1** → 10.2 → 10.3 (GA4)
2. **Story 10.4** (통합 대시보드)
