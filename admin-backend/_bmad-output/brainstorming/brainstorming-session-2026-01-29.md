---
stepsCompleted: [1, 2, 3, 4]
workflow_completed: true
inputDocuments: []
session_topic: 'LangGraph 기반 멀티 DB(MariaDB + MSSQL 2005) 조회 및 보고서 생성 에이전트 시스템'
session_goals: 'LLM RAG 에이전트가 자연어로 이기종 DB를 쿼리하고 결과를 분석하여 보고서로 제공하는 서비스 구현'
selected_approach: 'ai-recommended'
techniques_used: ['First Principles Thinking', 'Morphological Analysis', 'Constraint Mapping']
ideas_generated: 15
context_file: '/mnt/c/Users/user/mdh/project/temp/new-sajuline/admin-backend/src/core/database.py'
output_documents:
  - 'docs/ai-assistant/01-architecture-overview.md'
  - 'docs/ai-assistant/02-constraints.md'
  - 'docs/ai-assistant/03-implementation-roadmap.md'
---

# Brainstorming Session Results

**Facilitator:** dongdong
**Date:** 2026-01-29

## Session Overview

**Topic:** LangGraph 기반 멀티 DB(MariaDB + MSSQL 2005) 조회 및 보고서 생성 에이전트 시스템

**Goals:** LLM RAG 에이전트가 자연어로 이기종 DB를 쿼리하고 결과를 분석하여 보고서로 제공하는 서비스 구현

### Context Guidance

**데이터베이스 구성:**
| DB | 유형 | 연결 방식 | 용도 |
|----|------|----------|------|
| MariaDB | 비동기 (aiomysql) | `get_maria_db()` | 주 데이터베이스 |
| MSSQL 2005 | 동기 (pymssql, TDS 7.0/7.1) | `get_mssql_db()` | 외부 ARS 시스템 연동 |

**기술적 고려사항:**
- MariaDB는 비동기, MSSQL은 동기 → 혼합 async/sync 처리 필요
- MSSQL 2005 구형 버전 → TDS 프로토콜 호환성 고려
- 두 DB 간 데이터 조인/통합 로직 필요 가능성

### Session Setup

_세션 설정 완료_

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** LangGraph 기반 멀티 DB 에이전트 시스템 with focus on 실용적 구현 + 혁신적 아키텍처

**Recommended Techniques:**

| Phase | 기법 | 카테고리 | 목적 |
|-------|------|----------|------|
| 1 | **First Principles Thinking** | creative | 근본적 요구사항 정의, 가정 제거 |
| 2 | **Morphological Analysis** | deep | 시스템 파라미터 조합 체계적 탐색 |
| 3 | **Constraint Mapping** | deep | 기술적 제약사항 파악 및 해결 경로 |

**AI Rationale:**
- 복잡한 기술 스택(LangGraph + LLM + RAG + 멀티 DB)에서 본질부터 시작
- 체계적 조합 탐색으로 혁신적 아키텍처 발견
- 실제 제약사항(MSSQL 2005, async/sync 혼합) 기반 실현 가능한 솔루션 도출

---

## Phase 1: First Principles Thinking 결과

### 도출된 근본적 진실

| # | 근본 진실 | 시스템 영향 |
|---|-----------|------------|
| 1 | 보고서가 아닌 **대화형 BI** | 문답 UI + 스트리밍 응답 |
| 2 | **크로스 DB 조인** 필수 | 메모리 내 조인 또는 가상 뷰 |
| 3 | tm60_chatlog가 **진실의 원천** | 이 테이블 중심 쿼리 설계 |
| 4 | **읽기 전용** 절대 원칙 | DB/코드 이중 보안 |
| 5 | **인사이트 → 액션** 흐름 | 후속 분석 제안 로직 |
| 6 | **GA4 통합** 확장 | 멀티 소스 에이전트 |

### 크로스 DB 연결 키 매핑

- 상담사: `t_counselor.counselor_code` ↔ `tm60_member.m_code` / `tm60_chatlog.m_code`
- 유저: `t_user.user_id` ↔ `tm60_users.u_id` / `tm60_chatlog.u_id`

### 생성된 아이디어 (Phase 1)

**[비즈니스 #1]**: 대화형 관리자 BI 어시스턴트
- 자연어로 "오늘 매출 얼마야?" 질문 → AI가 두 DB 조회 후 대화로 답변

**[아키텍처 #1]**: 듀얼 DB 조인 에이전트
- 크로스 DB 질의 시 공통 키로 메모리 내 조인 수행

**[아키텍처 #2]**: 질의 유형 기반 라우팅
- "매출" → MariaDB, "상담시간" → MSSQL, "상담사 성과" → 크로스 조인 자동 라우팅

**[데이터 #1]**: tm60_chatlog 중심 분석 허브
- ARS 상담 로그 기반 상담사 성과, 유저 활동량, 포인트 소비 패턴 분석

**[보안 #1]**: 읽기 전용 DB 커넥션 강제
- 에이전트용 별도 DB 계정, SELECT 권한만 부여

**[보안 #2]**: SQL 화이트리스트 검증 레이어
- 생성된 SQL 파싱하여 SELECT만 허용, DML 탐지 차단

**[UX #1]**: 프로액티브 인사이트 에이전트
- 답변 후 관련 후속 분석 자동 제안 ("원인 분석할까요?")

**[데이터 #2]**: GA4 + DB 크로스 분석
- DB 결제 데이터 + GA4 유입 경로 통합 분석

---

## Phase 2: Morphological Analysis 결과

### 선택된 조합: "확장 가능한 멀티 에이전트" (조합 B)

| 파라미터 | 최종 선택 | 구현 방식 |
|----------|----------|----------|
| **쿼리 생성** | Schema-aware RAG + Few-shot | ChromaDB + 프롬프트 예시 |
| **DB 연결** | 병렬 조회 | asyncio.gather + run_in_executor |
| **에이전트 구조** | 멀티 에이전트 (DB별 1:1) | LangGraph StateGraph |
| **Supervisor** | 오케스트레이터형 | Task 분할 → 병렬 실행 → 통합 |
| **응답 형식** | 스트리밍 + 테이블 | SSE + Markdown 테이블 |
| **크로스 조인** | pandas + 템플릿 | merge() + 사전정의 패턴 |
| **보안** | 이중 + 결과 필터링 | SQL 검증 + DB 권한 + 마스킹 |

### 생성된 아이디어 (Phase 2)

**[아키텍처 #3]**: 오케스트레이터형 Supervisor
- Task 분할 → 병렬 실행 → 결과 통합 → 인사이트 도출

**[아키텍처 #4]**: DB별 1:1 전문 에이전트
- MariaDB Agent (매출/유저/상담사), MSSQL Agent (상담로그/시간), GA4 Agent (유입/전환)

**[아키텍처 #5]**: Schema-aware RAG + Few-shot 하이브리드
- 테이블별 스키마 청킹 + 자주 쓰는 쿼리 패턴 예시

**[데이터 #3]**: pandas 메모리 조인 + 템플릿
- 기본은 pandas.merge(), 자주 쓰는 패턴은 사전 정의

### 문서화

📁 **상세 아키텍처 문서 저장 완료**:
`docs/ai-assistant/01-architecture-overview.md`

---

## Phase 3: Constraint Mapping 결과

### 핵심 제약사항

| 우선순위 | 제약사항 | 해결책 |
|----------|----------|--------|
| 🔴 CRITICAL | 상담사 상태는 MSSQL `tm60_member.m_state`가 진실의 원천 | 라우팅 규칙에 반영 |
| 🔴 CRITICAL | 읽기 전용 (SELECT만 허용) | SQL 검증 레이어 + DB 권한 |
| 🟠 HIGH | EUC-KR 인코딩 (u_kname, m_name, m_nickname) | pymssql charset 설정 |
| 🟠 HIGH | MSSQL 2005 SQL 문법 제한 | 호환 쿼리 패턴 사용 |
| 🟡 MEDIUM | Async/Sync 혼합 | run_in_executor 래핑 |

### tm60_chatlog 테이블 핵심 정보

- **chattm**: 상담시간 (초 단위) ★핵심★
- **상담시간 계산**: `FLOOR(SUM(chattm)/3600)` + 분 + 초 변환
- **결제 완료**: `payment_status = 'SUCCESS'`

### 비즈니스 규칙 요약

1. 상담사 상태 조회 → MSSQL (실시간)
2. 매출/결제 조회 → MariaDB
3. 상담시간/로그 → MSSQL tm60_chatlog
4. 기본 날짜 범위: 최근 7일
5. TOP N 기본값: 10개

### 문서화

📁 **제약사항 문서 저장 완료**:
`docs/ai-assistant/02-constraints.md`

---

## Phase 4: Idea Organization 결과

### 아이디어 분류

| 카테고리 | 아이디어 수 | 핵심 아이디어 |
|----------|------------|--------------|
| 비즈니스 | 1 | 대화형 관리자 BI 어시스턴트 |
| 아키텍처 | 5 | 오케스트레이터 Supervisor, DB별 1:1 에이전트, Schema-aware RAG |
| 데이터 | 3 | tm60_chatlog 중심 분석, pandas 조인, GA4 통합 |
| 보안 | 2 | 읽기 전용 DB 커넥션, SQL 화이트리스트 검증 |
| UX | 1 | 프로액티브 인사이트 제안 |

### 우선순위 매트릭스

| 우선순위 | 아이디어 | 가치 | 난이도 |
|----------|----------|------|--------|
| 🥇 1순위 | MariaDB Agent + SQL 보안 | 매우 높음 | 중간 |
| 🥇 1순위 | API 엔드포인트 | 높음 | 낮음 |
| 🥈 2순위 | MSSQL Agent + Cross-DB Join | 높음 | 중간-높음 |
| 🥈 2순위 | 오케스트레이터 Supervisor | 매우 높음 | 높음 |
| 🥉 3순위 | Schema-aware RAG | 중간 | 높음 |
| 🥉 3순위 | 프로액티브 인사이트 | 중간 | 중간 |
| 🔮 미래 | GA4 통합 | 중간 | 높음 |

### 구현 로드맵

📁 **구현 로드맵 문서 저장 완료**:
`docs/ai-assistant/03-implementation-roadmap.md`

---

## 세션 완료 요약

### 생성된 문서

1. **`docs/ai-assistant/01-architecture-overview.md`**
   - LangGraph 멀티 에이전트 아키텍처 상세
   - 프로젝트 구조 및 의존성
   - LangGraph StateGraph 플로우

2. **`docs/ai-assistant/02-constraints.md`**
   - 기술적 제약사항 (MSSQL 2005, EUC-KR, async/sync)
   - 비즈니스 규칙 및 데이터 소스 라우팅
   - 보안 규칙 및 LLM 환경변수 설정

3. **`docs/ai-assistant/03-implementation-roadmap.md`**
   - 4단계 구현 계획
   - 상세 작업 목록 및 완료 기준
   - 리스크 및 대응 방안

### 핵심 결정사항

| 항목 | 결정 |
|------|------|
| 에이전트 구조 | 멀티 에이전트 (DB별 1:1) |
| Supervisor 유형 | 오케스트레이터형 (Task 분할 → 병렬 → 통합) |
| 쿼리 생성 | Schema-aware RAG + Few-shot 하이브리드 |
| 크로스 조인 | pandas + 템플릿 패턴 |
| 보안 | 이중 레이어 (SQL 검증 + DB 권한) |
| LLM | OpenAI, Gemini, Claude 지원 (환경변수 전환) |

### 다음 단계

**Phase 1 MVP 시작 권장**:
1. `tm60_chatlog` 모델 추가
2. `pyproject.toml` 의존성 추가
3. AI config 설정 (`src/ai/config.py`)
4. LangGraph 기본 구조 구현
5. SQL 보안 검증 레이어 구현
6. MariaDB Agent 구현
7. API 엔드포인트 (`/api/v1/ai/chat`)
8. 기본 테스트

---

**세션 종료**: 2026-01-29
**상태**: ✅ 완료

