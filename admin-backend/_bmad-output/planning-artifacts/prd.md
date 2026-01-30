---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
inputDocuments:
  - '_bmad-output/planning-artifacts/product-brief-admin-backend-2026-01-29.md'
  - '_bmad-output/planning-artifacts/research/technical-langgraph-multi-db-agent-research-2026-01-29.md'
  - '_bmad-output/brainstorming/brainstorming-session-2026-01-29.md'
  - 'docs/ai-assistant/00-index.md'
  - 'docs/ai-assistant/01-architecture-overview.md'
  - 'docs/ai-assistant/02-constraints.md'
  - 'docs/ai-assistant/03-implementation-roadmap.md'
  - 'docs/ai-assistant/04-risk-mitigation.md'
  - 'docs/ai-assistant/05-ga4-integration.md'
  - 'docs/ai-assistant/06-langgraph-implementation.md'
documentCounts:
  brief: 1
  research: 1
  brainstorming: 1
  projectDocs: 7
workflowType: 'prd'
projectType: 'brownfield'
date: 2026-01-30
author: dongdong
---

# Product Requirements Document - AI BI 어시스턴트

**Author:** dongdong
**Date:** 2026-01-30
**Version:** 0.3.0

---

## 1. Executive Summary

### 1.1 제품 개요

**AI BI 어시스턴트**는 사이트 관리자가 자연어로 질문하면 **MariaDB, MSSQL 2005, GA4** 등 이기종 데이터베이스를 조회하여 실시간 인사이트를 제공하는 **LangGraph 기반 멀티 에이전트 대화형 BI 시스템**입니다.

### 1.2 핵심 가치 제안

| 측면 | 기존 방식 | AI BI 어시스턴트 |
|------|----------|-----------------|
| 데이터 접근 | SQL 직접 작성 필요 | 자연어 질문으로 즉시 답변 |
| 분석 범위 | 단일 DB 수동 분석 | 멀티 DB 자동 크로스 분석 |
| 인사이트 | 정적 보고서 대기 | 프로액티브 후속 분석 제안 |
| 응답 시간 | 수 시간 ~ 수 일 | 수 초 내 실시간 응답 |

### 1.3 프로젝트 분류

| 항목 | 분류 |
|------|------|
| **프로젝트 유형** | API Backend (기존 admin-backend에 모듈 추가) |
| **도메인** | BI/Analytics + Fintech |
| **복잡도** | High (멀티 에이전트 + 이기종 DB + Text-to-SQL 보안) |
| **프로젝트 컨텍스트** | Brownfield (기존 3-Layer 패턴 준수) |
| **PRD 범위** | Full roadmap (Phase 1-4) |

---

## 2. Success Criteria

### 2.1 User Success

#### Aha Moment 지표 (MVP 핵심)

| 지표 | 목표 | 측정 방법 | 근거 |
|------|------|----------|------|
| **첫 질문 성공률** | ≥90% | 첫 질의 시 정확한 답변 비율 | Aha Moment 달성 |
| **첫 답변 응답시간** | ≤5초 | "오늘 매출" 질문 → 응답 시간 | 신뢰 형성 |
| **온보딩 완료율** | ≥80% | 첫 방문 → 첫 질문까지 도달률 | 진입 장벽 제거 |

#### 핵심 사용 지표

| 지표 | 목표 | 측정 방법 | 근거 |
|------|------|----------|------|
| **일일 활성 질의** | ≥20회 | 김관리 기준 하루 질의 횟수 | 핵심 사용 Stage |
| **재방문율** | ≥70% | 7일 내 재사용 비율 | 의존성 형성 |
| **질의 다양성** | ≥3종류 | 매출/유저/상담사 등 질의 유형 분포 | 전체 기능 활용 |

### 2.2 Business Success

#### 3개월 목표 (Phase 1-2 완료 시점)

| 목표 | 지표 | 타겟 |
|------|------|------|
| **개발팀 부담 감소** | 데이터 요청 건수 | 50% 감소 |
| **의사결정 속도** | 매출 확인 → 조치 시간 | 2시간 → 30분 이내 |
| **데이터 자립도** | SQL 없이 답변 가능 비율 | 80%+ |

#### 12개월 목표 (Phase 4 완료 시점)

| 목표 | 지표 | 타겟 |
|------|------|------|
| **마케팅 ROI 측정** | 채널별 전환율 실시간 조회 | GA4 연동 완료 |
| **상담사 성과 관리** | 크로스 DB 성과 분석 자동화 | 주간 리포트 자동 생성 |
| **전사 데이터 접근** | AI 어시스턴트 사용자 수 | 4명 (전 담당자) |

### 2.3 Technical Success

| KPI | 목표 | 측정 주기 | 알림 임계값 |
|-----|------|----------|------------|
| 응답 정확도 | ≥95% | 일간 | <90% 경고 |
| 응답 시간 (p95) | ≤5초 | 실시간 | >7초 경고 |
| SQL 오류율 | ≤1% | 일간 | >3% 경고 |
| 시스템 가용성 | ≥99.5% | 월간 | <99% 경고 |

### 2.4 Measurable Outcomes

#### MVP Go/No-Go 판단 기준

| 지표 | 목표 | 측정 시점 | Go 조건 |
|------|------|----------|---------|
| 첫 질문 성공률 | ≥90% | 출시 후 1주 | 달성 시 Phase 2 진행 |
| 응답 시간 (p95) | ≤5초 | 출시 후 1주 | 달성 시 유지 |
| SQL 오류율 | ≤1% | 출시 후 1주 | 달성 시 유지 |
| 일일 사용 횟수 | ≥5회 | 출시 후 1주 | 달성 시 Phase 2 진행 |

#### 검증해야 할 가설

1. **가설 1**: 관리자는 자연어로 매출 질문을 할 수 있다
   - 검증: 첫 질문 성공률 ≥90%
2. **가설 2**: SQL 없이도 데이터 접근이 가능하다
   - 검증: 개발팀 데이터 요청 감소 추이
3. **가설 3**: 5초 내 응답이 사용자 만족을 이끈다
   - 검증: 재방문율 및 피드백

---

## 3. Product Scope

### 3.1 MVP - Phase 1 (2.5주)

| 기능 | 설명 | Aha Moment 연결 |
|------|------|----------------|
| **자연어 질의** | "오늘 매출 얼마야?" 형태 질문 수용 | 첫 질문 성공률 ≥90% |
| **MariaDB 단일 조회** | 매출, 결제, 유저 테이블 SELECT | 첫 답변 ≤5초 |
| **날짜 자동 파싱** | "오늘", "이번 달", "어제" 자연어 처리 | 사용 편의성 |
| **SQL 2중 보안** | Prompt 검증 + SQL Parser | 안전한 데이터 접근 |
| **응답 포맷터** | 자연어 + 테이블 형태 응답 | 직관적 결과 확인 |
| **빠른 질문 버튼** | 예시 질문 제공 (온보딩) | 온보딩 완료율 ≥80% |

### 3.2 Growth Features - Phase 2-3

| Phase | 기능 | 완료 기준 |
|-------|------|----------|
| **Phase 2** | MSSQL Agent + 크로스 DB 조인 | "김철수 상담사 매출과 상담시간 알려줘" 답변 가능 |
| **Phase 2** | SSE 스트리밍 + Redis Checkpointing | 대화 맥락 유지 |
| **Phase 3** | Schema-aware RAG | 테이블/컬럼 자동 인식 |
| **Phase 3** | 프로액티브 인사이트 제안 | "매출 떨어졌네" → "원인 분석할까요?" |

### 3.3 Vision - Phase 4+

| 기능 | 설명 | 목표 |
|------|------|------|
| **GA4 Agent** | 유입-매출 연계 분석 | 마케팅 ROI 측정 |
| **시각화** | 차트 자동 생성 | 직관적 데이터 표현 |
| **예측 분석** | "다음 달 매출 예상치" | AI 기반 예측 |
| **자동 리포트** | 일간/주간 핵심 지표 | 정기 리포트 자동화 |

### 3.4 Out of Scope (명시적 제외)

- ❌ 데이터 수정/삭제 (INSERT/UPDATE/DELETE)
- ❌ 관리자 외 사용자 접근
- ❌ 모바일 전용 UI
- ❌ 음성 입력/출력

---

## 4. User Journeys

### 4.1 Journey Map Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI BI 어시스턴트 Journey Map              │
├─────────────────────────────────────────────────────────────┤
│ Phase 1 (MVP)                                               │
│ ├── Journey 1: 첫 발견 & 온보딩 (Aha Moment)                │
│ ├── Journey 2: 일상 매출 조회 (Core Usage)                  │
│ ├── Journey 3: 위기 상황 대응 (Edge Case)                   │
│ └── Journey 4: 실패 & 복구 (Error Handling)                 │
├─────────────────────────────────────────────────────────────┤
│ Phase 2 (멀티 DB)                                           │
│ └── Journey 5: 크로스 DB 분석 - 박씨에스 (Secondary User)    │
├─────────────────────────────────────────────────────────────┤
│ Phase 4 (GA4)                                               │
│ └── Journey 6: 마케팅 ROI 분석 - 이마케 (Secondary User)     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Journey 1: 첫 발견 & 온보딩 (Phase 1 - MVP)

**페르소나**: 김관리 (35세, 사이트 관리자)
**목표**: 첫 사용자가 AI 어시스턴트를 발견하고 성공적으로 첫 질문을 완료
**성공 지표**: 온보딩 완료율 ≥80%

#### Narrative

> **Opening Scene**: 월요일 아침, 김관리가 관리자 페이지에 로그인합니다. 사이드바에 새로운 메뉴 "🤖 AI 어시스턴트"가 보입니다. "이게 뭐지?" 호기심과 약간의 의심이 섞인 마음으로 클릭합니다.
>
> **Rising Action**: 대화 화면이 열리고, "무엇을 도와드릴까요?"라는 메시지와 함께 **빠른 질문 버튼**들이 보입니다:
> - "오늘 매출"
> - "이번 주 결제 건수"
> - "신규 가입자"
>
> 김관리는 "뭘 물어봐야 하지?" 고민하다가 "오늘 매출" 버튼을 클릭합니다.
>
> **Climax (Aha Moment)**: 3초 만에 "오늘 매출은 1,250,000원입니다. 어제 대비 12% 증가했습니다."라는 답변이 옵니다.
>
> **Resolution**: 김관리: "와, 진짜 되네!" 😊 후속 질문 "상담사별로 보여줘"를 직접 타이핑합니다.

#### 감정 여정

| 단계 | 감정 | UI 지원 |
|------|------|--------|
| 발견 | 🤔 호기심 + 의심 | 사이드바 메뉴 강조 |
| 진입 | 😰 불안 ("뭘 물어봐야 하지?") | 빠른 질문 버튼 제공 |
| 첫 질문 | 🙏 기대 | 로딩 인디케이터 |
| 첫 답변 | 😊 놀라움 + 신뢰 | 명확한 응답 포맷 |

### 4.3 Journey 2: 일상 매출 조회 (Phase 1 - Core Usage)

**페르소나**: 김관리
**목표**: 매일 반복되는 매출 확인 작업을 자연어로 빠르게 수행
**성공 지표**: 일일 활성 질의 ≥20회, 응답 시간 ≤5초

#### Narrative

> **Opening Scene**: 화요일 아침 9시, 김관리가 출근해서 노트북을 켭니다. 주말 동안 매출이 얼마나 됐는지 확인하고 싶습니다.
>
> **Rising Action**: AI 어시스턴트를 열고 "주말 매출 얼마야?"라고 입력합니다.
>
> **Climax**: 3초 만에 응답:
> ```
> 주말(1/25~1/26) 총 매출: 2,450,000원
> - 토요일: 1,200,000원
> - 일요일: 1,250,000원
> 전주 대비 15% 증가했습니다.
> ```
>
> **Resolution**: 김관리는 "매출 상위 상담사 3명 알려줘"라고 후속 질문합니다. 예전 같으면 2시간 걸릴 일이 10초 만에 해결됩니다.

#### 도출된 요구사항

- 날짜 자연어 파싱 ("주말", "어제", "이번 달")
- 기간 자동 계산 및 표시
- 전주/전월 대비 비교 자동 제공
- 후속 질문 지원 (대화 맥락 유지 - Phase 2)

### 4.4 Journey 3: 위기 상황 대응 (Phase 1 - Edge Case)

**페르소나**: 김관리
**목표**: 이상 상황 발생 시 빠른 원인 파악 및 대응
**성공 지표**: 의사결정 시간 2시간 → 30분 이내

#### Narrative

> **Opening Scene**: 오후 3시, 갑자기 환불 CS가 3건 연속으로 들어옵니다. "오늘 뭔가 이상하다"고 느낀 김관리.
>
> **Rising Action**: "오늘 환불 건 몇 건이야?"라고 질문합니다.
>
> **Climax**: 시스템 응답:
> ```
> 오늘 환불: 5건 (총 350,000원)
> ⚠️ 평균 대비 200% 높음
>
> 상담사별 분포:
> - 김철수: 3건
> - 이영희: 1건
> - 박지민: 1건
> ```
>
> **Resolution**: 특정 상담사에게 환불이 집중된 것을 발견하고 즉시 조치합니다.

#### 도출된 요구사항

- 이상치 탐지 및 경고 표시 (평균 대비 %)
- 그룹별 분포 자동 제공
- 상담사 코드 → 이름 매핑

### 4.5 Journey 4: 실패 & 복구 (Phase 1 - Error Handling)

**페르소나**: 김관리
**목표**: 시스템 한계 상황에서 사용자가 좌절하지 않고 대안을 찾도록 유도
**성공 지표**: SQL 오류율 ≤1%, 에러 후 재시도율 ≥50%

#### Narrative

> **Opening Scene**: 김관리가 "작년 전체 상담사별 일별 매출 추이 보여줘"라고 질문합니다.
>
> **Rising Action**: 시스템이 쿼리를 생성하지만, 결과가 너무 많습니다 (10,000건+).
>
> **Climax**: 시스템 응답:
> ```
> ⚠️ 결과가 10,000건 이상입니다.
>
> 다음 중 하나를 선택해주세요:
> 1. 기간을 좁혀주세요 (예: "이번 달만")
> 2. 특정 상담사만 (예: "김철수 상담사만")
> 3. 월별 요약으로 보기
> ```
>
> **Resolution**: 김관리가 "이번 달만"을 선택하고 성공적으로 결과를 받습니다.

#### 추가 시나리오: 보안 차단

> **상황**: "상담사 급여 알려줘"
>
> **시스템 응답**:
> ```
> 🔒 죄송합니다. 민감정보(급여, 주민번호 등)는 조회할 수 없습니다.
>
> 대신 이런 정보는 조회 가능합니다:
> - 상담사별 매출
> - 상담사별 상담 건수
> ```

#### 도출된 요구사항

- 결과 건수 임계값 체크 (예: 1,000건)
- 친절한 대안 제시
- 민감정보 필드 탐지 및 차단
- 차단 시 대안 질문 제안

### 4.6 Journey 5: 크로스 DB 분석 (Phase 2 - Secondary User)

**페르소나**: 박씨에스 (42세, CS 매니저)
**목표**: MariaDB(매출)와 MSSQL(상담로그)를 통합 분석
**성공 지표**: 크로스 DB 질의 성공률 ≥85%

#### Narrative

> **Opening Scene**: 금요일 오후, 박씨에스가 주간 상담사 성과를 정리해야 합니다. 예전에는 MariaDB에서 매출을 뽑고, MSSQL에서 상담시간을 뽑아서 엑셀로 합쳤습니다.
>
> **Rising Action**: "이번 주 상담사별 매출과 평균 상담시간 알려줘"라고 질문합니다.
>
> **Climax**: 시스템이 두 DB를 병렬 조회하고 pandas.merge()로 조인:
> ```
> 이번 주 상담사 성과 (매출순):
>
> | 상담사 | 매출 | 상담건수 | 평균상담시간 |
> |--------|------|---------|-------------|
> | 김철수 | 850,000원 | 42건 | 18분 |
> | 이영희 | 720,000원 | 38건 | 22분 |
> | 박지민 | 650,000원 | 35건 | 15분 |
> ```
>
> **Resolution**: 한눈에 성과를 파악하고, "응대율 낮은 상담사"로 후속 질문합니다.

#### 도출된 요구사항

- 크로스 DB 조인 (counselor_code ↔ m_code)
- 병렬 쿼리 실행 (asyncio.gather)
- MSSQL 동기→비동기 래핑 (run_in_executor)
- 통합 결과 테이블 포맷

### 4.7 Journey 6: 마케팅 ROI 분석 (Phase 4 - Secondary User)

**페르소나**: 이마케 (28세, 마케팅 담당자)
**목표**: GA4 유입 데이터와 매출 데이터를 연계 분석
**성공 지표**: 채널별 전환율 실시간 조회

#### Narrative

> **Opening Scene**: 이마케가 이번 달 카카오 광고 성과를 확인하고 싶습니다.
>
> **Rising Action**: "카카오 유입 유저 중 결제한 사람 몇 명이야?"
>
> **Climax**: 시스템이 GA4 + MariaDB를 조합:
> ```
> 이번 달 카카오 유입 분석:
>
> - 유입: 1,250명
> - 가입: 320명 (전환율 25.6%)
> - 결제: 48명 (가입 대비 15%)
> - 매출: 2,400,000원
> - 객단가: 50,000원
> - ROAS: 240%
> ```
>
> **Resolution**: 광고 효율을 즉시 파악하고 예산 조정 의사결정을 합니다.

#### 도출된 요구사항

- GA4 Data API 연동
- 유입 경로 → 유저 ID 매핑
- 퍼널 분석 (유입→가입→결제)
- ROAS 자동 계산

---

### 4.8 Journey Requirements Summary

| Journey | 도출된 요구사항 | Phase |
|---------|----------------|-------|
| J1: 온보딩 | 빠른 질문 버튼, 예시 질문 제공 | 1 |
| J2: 일상 조회 | 날짜 파싱, 기간 비교, 후속 질문 | 1 |
| J3: 위기 대응 | 이상치 탐지, 그룹별 분포 | 1 |
| J4: 에러 복구 | 결과 임계값, 대안 제시, 민감정보 차단 | 1 |
| J5: 크로스 DB | 병렬 조회, pandas 조인, MSSQL 래핑 | 2 |
| J6: GA4 연동 | GA4 API, 퍼널 분석, ROAS 계산 | 4 |

---

## 5. Domain-Specific Requirements

### 5.1 보안 아키텍처 (Security Architecture)

#### 5중 방어 체계

```
Layer 0: 네트워크 보안 (추가)
├── 관리자 IP 화이트리스트
├── Rate Limiting (분당 30회)
└── 요청 크기 제한 (1KB)

Layer 1: Prompt Engineering
├── Few-shot 예시로 정확한 SQL 패턴 학습
├── Schema-aware RAG로 테이블/컬럼 정보 주입
└── 명확한 제약조건 프롬프트

Layer 2: SQL 검증
├── AST 파싱으로 SELECT만 허용
├── 화이트리스트 키워드 검증
├── 테이블/컬럼 존재 여부 검증
├── 위험 패턴 탐지 (UNION, 서브쿼리 등)
└── 민감 테이블 블랙리스트 체크

Layer 3: 결과 검증
├── 결과 row 수 임계값 체크 (1,000건)
├── 이상치 탐지 (극단적 수치)
└── NULL/빈 결과 처리

Layer 4: 사용자 확인
├── 생성된 SQL 미리보기 (옵션)
├── 위험 쿼리 시 확인 요청
└── 실행 취소 옵션
```

#### 민감 테이블 블랙리스트

```python
BLOCKED_TABLES = [
    't_admin',           # 관리자 계정
    't_user_password',   # 비밀번호 해시
    't_payment_card',    # 카드 정보
    't_user_identity',   # 주민등록번호
]
```

### 5.2 데이터베이스 권한 분리

| 계정 | 권한 | 접근 테이블 |
|------|------|------------|
| `ai_bi_maria_ro` | SELECT only | t_payment, t_user, t_counselor |
| `ai_bi_mssql_ro` | SELECT only | tm60_chatlog, tm60_member |

### 5.3 기술적 제약사항 (Technical Constraints)

#### MSSQL 2005 호환성

| 제한사항 | 해결책 |
|----------|--------|
| TDS 프로토콜 | pymssql + TDS 7.0/7.1 명시 |
| OFFSET/FETCH 미지원 | TOP N 사용 |
| CTE(WITH) 미지원 | 서브쿼리로 대체 |
| 일부 윈도우 함수 | 자체 조인으로 구현 |
| EUC-KR 인코딩 | `charset='euc-kr'` 설정 필수 |

#### Async/Sync 혼합 아키텍처

```python
# MariaDB: 비동기 (aiomysql)
async def query_maria(sql: str) -> pd.DataFrame:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            return await cur.fetchall()

# MSSQL: 동기 → 비동기 래핑
async def query_mssql(sql: str) -> pd.DataFrame:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, _sync_mssql_query, sql
    )
```

### 5.4 감사 요구사항 (Audit Requirements)

| 항목 | 로깅 내용 | 보존 기간 |
|------|----------|----------|
| **질의 로그** | user_id, timestamp, question, generated_sql | 90일 |
| **결과 로그** | row_count, execution_time, error_code | 90일 |
| **보안 이벤트** | 민감정보 접근 시도, 차단된 쿼리 | 1년 |

### 5.5 보안 테스트 요구사항

#### SQL Injection 테스트 시나리오

| # | 공격 패턴 | 예시 입력 | 예상 결과 |
|---|----------|----------|----------|
| 1 | UNION Injection | "매출 UNION SELECT * FROM t_admin" | ❌ 차단 |
| 2 | Tautology | "1=1인 모든 유저" | ❌ 차단 |
| 3 | Comment Injection | "매출 -- DROP TABLE" | ❌ 차단 |
| 4 | Stacked Query | "매출; DELETE FROM t_user" | ❌ 차단 |
| 5 | Time-based | "매출 AND SLEEP(10)" | ❌ 차단 |

#### 보안 테스트 통과 기준

| 테스트 | 통과 기준 |
|--------|----------|
| SQL Injection | **100% 차단** |
| 민감정보 노출 | **0건** |
| 블랙리스트 테이블 접근 | **100% 차단** |

### 5.6 인프라 요구사항

#### LLM API Fallback Chain

```python
LLM_FALLBACK_CHAIN = [
    {"provider": "openai", "model": "gpt-4-turbo"},
    {"provider": "anthropic", "model": "claude-3-sonnet"},
    {"provider": "google", "model": "gemini-1.5-pro"},
]
```

#### Redis 캐싱 전략

| 캐시 유형 | TTL | 키 패턴 |
|----------|-----|--------|
| 동일 질의 | 5분 | `ai_bi:{user_id}:{query_hash}` |
| 스키마 메타데이터 | 1시간 | `ai_bi:schema:{db_name}` |

### 5.7 디렉토리 구조 표준

```
src/
├── services/
│   └── ai_bi/
│       ├── ai_bi_service.py      # 메인 서비스
│       ├── sql_validator.py      # Layer 2: SQL 검증
│       ├── result_sanitizer.py   # Layer 3: 결과 검증
│       └── prompt_builder.py     # Layer 1: 프롬프트
├── repositories/
│   └── ai_bi/
│       ├── maria_query_repo.py   # MariaDB 쿼리
│       └── mssql_query_repo.py   # MSSQL 쿼리
└── api/v1/
    └── ai_bi_api.py              # FastAPI 라우터
```

---

## 6. 혁신 & 신규 패턴 (Innovation & Novel Patterns)

### 6.1 혁신 요소 검증 매트릭스

| # | 혁신 요소 | 검증 방법 | 실패 시 대안 |
|---|----------|----------|-------------|
| 1 | 멀티 에이전트 오케스트레이션 | Phase 2에서 크로스 DB 질의 성공률 측정 | 단일 에이전트로 폴백 |
| 2 | **MSSQL 2005 호환성** | ✅ 이미 검증됨 (기존 시스템) | 기존 `get_db_mssql()` 재사용 |
| 3 | 5중 보안 체계 | SQL Injection 테스트 100% 통과 | 레이어별 개별 검증 |
| 4 | pandas 메모리 조인 | 10,000건 이상 조인 성능 테스트 | 페이지네이션 적용 |

### 6.2 기존 인프라 활용

본 프로젝트의 핵심 강점은 **검증된 기존 인프라를 재사용**하는 것입니다:

```python
# src/core/database.py (기존 코드 - Lines 99-101)
if settings.mssql_driver.lower() == "pymssql":
    tds_version = "7.0" if settings.is_production else "7.1"
    connect_args = {"tds_version": tds_version, "login_timeout": 30, "timeout": settings.mssql_timeout}
```

- **pymssql==2.3.0**: 이미 MSSQL 2005와 정상 연결 중
- **TDS 7.0/7.1**: 프로덕션/개발 환경 분리 완료
- **get_db_mssql()**: 즉시 재사용 가능

### 6.3 리스크 완화 전략

| 리스크 | 확률 | 영향도 | 완화 전략 |
|--------|------|--------|----------|
| LLM 환각(Hallucination) | 중 | 고 | SQL 검증 레이어 + 화이트리스트 테이블 |
| 대용량 조인 메모리 | 저 | 중 | Row 제한(5,000건) + 스트리밍 페이지네이션 |
| MSSQL 연결 실패 | 저 | 중 | ✅ 기존 연결 풀 재사용으로 완화됨 |
| 프롬프트 인젝션 | 중 | 고 | 5중 보안 체계로 다층 방어 |

---

## 7. API Backend 기술 요구사항

### 7.1 엔드포인트 명세 (Endpoint Specification)

#### Phase 1: Core API Endpoints (MVP)

| Method | Endpoint | 설명 | 응답 SLA | MVP |
|--------|----------|------|----------|-----|
| POST | `/api/v1/ai-bi/query` | 자연어 질의 (stream=true 시 SSE) | 3s | ✅ Must |
| POST | `/api/v1/ai-bi/feedback` | 질의 결과 피드백 수집 | 200ms | ✅ Must |
| GET | `/api/v1/ai-bi/history` | 질의 히스토리 조회 | 200ms | ⚠️ Should |
| GET | `/api/v1/ai-bi/health` | 서비스 헬스체크 | 50ms | ✅ Must |

#### Phase 2: Enhanced Endpoints

| Method | Endpoint | 설명 | 응답 SLA |
|--------|----------|------|----------|
| POST | `/api/v1/ai-bi/cross-db` | 크로스 DB 조인 질의 | 5s |
| GET | `/api/v1/ai-bi/suggestions` | 컨텍스트 기반 후속 질문 제안 | 500ms |
| GET | `/api/v1/ai-bi/schema` | 허용된 테이블/컬럼 스키마 조회 | 100ms |

> **설계 결정**: 스트리밍은 `/query?stream=true` 쿼리 파라미터로 통합

### 7.2 인증 모델 (Authentication Model)

기존 admin-backend 인증 체계 재사용:

```python
@router.post("/query")
async def ai_bi_query(
    request: AIBIQueryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if "AI_BI_ACCESS" not in current_admin.permissions:
        raise HTTPException(status_code=403, detail="AI BI 접근 권한 없음")
```

#### 권한 매트릭스

| 역할 | 단일 DB 질의 | 크로스 DB 질의 | 민감 테이블 접근 | 감사 로그 조회 |
|------|-------------|---------------|-----------------|---------------|
| SUPER_ADMIN | ✅ | ✅ | ✅ | ✅ |
| ADMIN | ✅ | ✅ | ❌ | ❌ |
| OPERATOR | ✅ | ❌ | ❌ | ❌ |

### 7.3 데이터 스키마 (Data Schemas)

#### 요청 스키마

```python
class AIBIQueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    db_scope: Literal["mariadb", "mssql", "cross"] = Field(default="mariadb")
    max_rows: int = Field(default=100, le=5000)
    include_sql: bool = Field(default=False)
    stream: bool = Field(default=False, description="SSE 스트리밍 응답")
    accessibility_mode: bool = Field(default=False, description="테이블 대신 텍스트 요약 반환")

class AIBIFeedbackRequest(BaseModel):
    query_id: str = Field(..., description="질의 고유 ID")
    helpful: bool = Field(..., description="도움이 되었는지 여부")
    correction: Optional[str] = Field(None, description="사용자가 수정한 답변")
    rating: Optional[int] = Field(None, ge=1, le=5, description="1-5점 평가")
```

#### 응답 스키마

```python
class AIBIQueryResponse(BaseModel):
    success: bool
    query_id: str  # 피드백 연결용
    answer: str
    answer_summary: Optional[str] = None  # accessibility_mode=True 시
    data: Optional[List[Dict[str, Any]]] = None
    generated_sql: Optional[str] = None
    execution_time_ms: int
    suggestions: List[str] = []
    metadata: AIBIMetadata

class AIBIErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    suggestions: List[str] = []  # 사용자 가이드
    retry_after: Optional[int] = None  # Rate limit 시
```

### 7.4 에러 코드 및 사용자 가이드

| 코드 | HTTP | 사용자 메시지 | suggestions 예시 |
|------|------|--------------|-----------------|
| AIBI_PARSE_ERROR | 400 | "질문을 이해하지 못했어요." | ["더 구체적으로: '이번 달' → '2026년 1월'"] |
| AIBI_SQL_GEN_FAILED | 400 | "SQL 생성에 실패했습니다." | ["다른 표현으로 시도해보세요"] |
| AIBI_ACCESS_DENIED | 403 | "해당 데이터에 접근 권한이 없습니다." | ["관리자에게 권한 요청"] |
| AIBI_INJECTION_BLOCKED | 403 | "보안 정책에 위배되는 질의입니다." | ["일반적인 질문 형태로 다시 시도"] |
| AIBI_LLM_TIMEOUT | 408 | "AI 응답 시간이 초과되었습니다." | ["잠시 후 다시 시도"] |
| AIBI_RATE_LIMITED | 429 | "요청 한도를 초과했습니다." | ["N초 후 다시 시도 가능"] |
| AIBI_DB_ERROR | 500 | "데이터베이스 연결에 문제가 발생했습니다." | ["잠시 후 다시 시도"] |
| AIBI_LLM_UNAVAILABLE | 503 | "AI 서비스가 일시적으로 불가합니다." | ["잠시 후 다시 시도"] |

### 7.5 SLA 정의 및 측정

```yaml
sla_definition:
  query_endpoint:
    metric: p95_response_time
    target: 3000ms
    measurement_window: 5min_rolling
    exclusions:
      - cold_start_first_request
      - cross_db_queries  # 별도 SLA: 5000ms
    monitoring: Sentry Performance
    alerting:
      warning: p95 > 2500ms
      critical: p95 > 3000ms
```

### 7.6 Rate Limiting & Retry

```python
RATE_LIMITS = {
    "ai_bi_query": {"rpm": 20, "rph": 200, "burst": 5},
    "ai_bi_cross_db": {"rpm": 10, "rph": 50, "burst": 3}
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(LLMTimeoutError)
)
async def call_llm(prompt: str) -> str:
    ...
```

### 7.7 Circuit Breaker 패턴

```python
class LLMCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.state: Literal["closed", "open", "half-open"] = "closed"
        self.failure_count: int = 0
        self.last_failure_time: Optional[datetime] = None
```

### 7.8 데이터 거버넌스 및 보존 정책

| 데이터 유형 | 보존 기간 | 삭제 방법 | 근거 |
|------------|----------|----------|------|
| 질의 로그 | 90일 | 자동 삭제 (cron) | 개인정보보호법 |
| 생성된 SQL | 90일 | 질의 로그와 함께 | 감사 추적 |
| 피드백 데이터 | 1년 | 익명화 후 보존 | ML 학습용 |
| 에러 로그 | 30일 | 자동 삭제 | 운영 목적 |
| 보안 이벤트 | 1년 | 별도 아카이브 | 컴플라이언스 |

### 7.9 API 테스트 요구사항

#### 테스트 커버리지 목표

| 테스트 유형 | 커버리지 목표 | 주요 대상 |
|------------|--------------|----------|
| Unit | 90% | SQL Validator, Prompt Builder |
| Integration | 80% | MariaDB/MSSQL 쿼리 실행 |
| Contract | 100% | OpenAPI 스키마 일치 |
| E2E | 핵심 플로우 | 질의→응답 전체 흐름 |

#### 수용 기준 (Acceptance Criteria) 예시

```gherkin
Scenario: 단일 DB 질의 성공
  Given 인증된 ADMIN 사용자
  And MariaDB 연결 정상
  When "이번 달 매출 합계" 질의 전송
  Then 3초 이내 응답
  And answer 필드에 자연어 답변 포함
  And query_id 반환됨

Scenario: SQL Injection 차단
  Given 인증된 사용자
  When "매출; DROP TABLE t_user" 질의 전송
  Then 403 응답
  And error_code = "AIBI_INJECTION_BLOCKED"
  And 보안 이벤트 로깅됨
```

### 7.10 구현 의존성 체크리스트

```yaml
dependencies:
  phase_1_blockers:
    - [ ] SQL Validator 화이트리스트 테이블 목록 확정
    - [ ] LLM 프롬프트 템플릿 v1 확정
    - [ ] 에러 코드 표준 문서화
    - [ ] Rate Limit Redis 키 설계
    - [ ] OpenAPI 스키마 초안
```

### 7.11 스토리 분할 가이드

```
Epic: AI BI Query API (Phase 1)
├── Story 1.1: 기본 질의 엔드포인트 (/query) - 5pt
├── Story 1.2: SQL Validator 구현 - 3pt
├── Story 1.3: 피드백 수집 (/feedback) - 2pt
├── Story 1.4: Rate Limiting 적용 - 2pt
├── Story 1.5: Circuit Breaker 구현 - 3pt
├── Story 1.6: 히스토리 조회 (/history) - 2pt
└── Story 1.7: 스트리밍 응답 (stream=true) - 3pt
```

### 7.12 버전 관리 및 기능 플래그

```python
class AIBIFeatures(BaseModel):
    streaming_enabled: bool = True
    cross_db_enabled: bool = False  # Phase 2
    ga4_enabled: bool = False       # Phase 4
    accessibility_mode_enabled: bool = True
```

---

## 8. 프로젝트 스코핑 & 단계별 개발

### 8.1 MVP 전략 및 철학

**MVP 접근법:** Problem-Solving MVP (문제 해결 중심)

> "개발팀 데이터 요청 80% 감소"라는 명확한 문제 해결에 집중

**핵심 원칙:**
- ✅ **Day 1 Value**: 첫 배포부터 즉시 사용 가능한 가치 제공
- ✅ **기존 인프라 재사용**: 검증된 MariaDB/MSSQL 연결 활용
- ✅ **점진적 확장**: 단일 DB → 크로스 DB → GA4 통합

### 8.2 ROI 분석 (시나리오별)

| 시나리오 | 감소율 | 월 절감 | 투자 회수 |
|----------|--------|---------|----------|
| 낙관적 | 80% | 8,000,000원 | 2.4개월 |
| **현실적** | **60%** | **6,000,000원** | **3.2개월** |
| 보수적 | 40% | 4,000,000원 | 4.8개월 |

> ⚠️ **현실적 시나리오 기준으로 계획**

### 8.3 숨겨진 비용 예산

| 항목 | 월 비용 | 비고 |
|------|---------|------|
| LLM 비용 (상한) | 2,000,000원 | 초과 시 알림 |
| 유지보수 | 800,000원 | 0.2명 환산 |
| 프롬프트 튜닝 | 분기별 1주 | 지속적 개선 |

### 8.4 기술 스택

```python
REQUIRED_DEPENDENCIES = {
    "langgraph": ">=0.0.40",
    "langchain": ">=0.1.0",
    "openai": ">=1.0.0",
    "anthropic": ">=0.18.0",
    "pandas": ">=2.0.0",
    "sse-starlette": ">=1.0.0",
}
```

### 8.5 Day 0 준비 체크리스트

```yaml
technical:
  - [ ] LangGraph PoC 완료 (4시간)
  - [ ] OpenAI/Anthropic API 키 발급
  - [ ] 테스트 DB 접근 권한 확보
  - [ ] LLM Fallback PoC 검증

infrastructure:
  - [ ] CI/CD 파이프라인 설정
  - [ ] Sentry 프로젝트 생성
```

### 8.6 Phase 1 Core (Week 1-5, 버퍼 포함)

**조정된 목표**: 성공률 70%, SLA p95 < 5s

#### 스프린트 분할

| Sprint | 주차 | 포인트 | 버퍼 |
|--------|------|--------|------|
| 1 | 1-2 | 11pt | 2pt |
| 2 | 3-4 | 11pt | 2pt |
| 버퍼 | 5 | - | 전체 |

#### 중간 체크포인트 (Week 2)

| 확인 항목 | 통과 기준 | 실패 시 조치 |
|----------|----------|-------------|
| LangGraph 기본 동작 | Supervisor 패턴 동작 | 범위 축소 논의 |
| MariaDB 단순 질의 | 3개 이상 성공 | 일정 조정 |
| SQL Validator 기본 | Injection 차단 동작 | 보안 우선 수정 |

### 8.7 Phase 1.5 Polish (Week 6-8, 버퍼 포함)

| 기능 | 우선순위 |
|------|----------|
| /feedback 엔드포인트 | P0 |
| Rate Limiting | P0 |
| Circuit Breaker | P1 |
| 에러 UX 개선 | P1 |

**목표**: 성공률 85%, SLA p95 < 3s

### 8.8 Phase 2-4 요약

| Phase | 기간 | 핵심 기능 |
|-------|------|----------|
| Phase 2 | Week 9-12 | 크로스 DB, SSE 스트리밍 |
| Phase 3 | Week 13-16 | 프로액티브 알림, 시각화 |
| Phase 4 | Week 17+ | GA4 통합 |

### 8.9 조정된 Go/No-Go 기준

| 전환 | 기존 | 조정 |
|------|------|------|
| 1→1.5 성공률 | 85% | **70%** |
| 1→1.5 SLA | p95<3s | **p95<5s** |
| 1.5→2 성공률 | 90% | **85%** |

### 8.10 최악의 시나리오 대응

| 4주 후 상황 | 대응 |
|------------|------|
| 성공률 ≥ 70% | ✅ 계속 진행 |
| 성공률 50-70% | ⚠️ 범위 축소 (MariaDB only) |
| 성공률 < 50% | ❌ Go/No-Go 재검토 |

### 8.11 테스트 전략

| Phase | Unit | Integration | Security |
|-------|------|-------------|----------|
| 1 | 90% | 80% | Basic |
| 1.5 | 90% | 85% | Fuzzing 100패턴 |
| 2 | 90% | 85% | Full + WAF |

### 8.12 Definition of Done

```yaml
code:
  - [ ] 코드 리뷰 완료
  - [ ] 유닛 테스트 통과
  - [ ] 린팅/타입 체크 통과

deployment:
  - [ ] 스테이징 배포 완료
  - [ ] 스모크 테스트 통과
```

### 8.13 커뮤니케이션 계획

| 주기 | 내용 | 대상 |
|------|------|------|
| Daily | 스탠드업 | 개발팀 |
| Weekly | 진행 상황 | PM, 리드 |
| Phase 완료 | 데모 | 전체 |

### 8.14 팀 구성

| 역할 | 최소 | 권장 |
|------|------|------|
| Backend Senior | 1명 | 1명 |
| Backend Mid | 0.5명 | 1명 |
| **총계** | **1.5명** | **2명** |

> ⚠️ **1.5명은 일정 리스크 높음, 2명 권장**

### 8.15 운영 요구사항

```yaml
monitoring:
  - LLM 비용 대시보드 (상한 알림)
  - 질의 성공률 실시간 모니터링
  - SLA 위반 알림

scaling:
  phase_1: "단일 인스턴스 (10 req/s)"
  phase_2: "수평 확장 준비"
```

### 8.16 보안 감사 체크리스트

```yaml
pre_production:
  - [ ] SQL Injection 퍼징 (100패턴)
  - [ ] 민감 테이블 접근 차단
  - [ ] 인증/권한 검증
  - [ ] WAF 레이어 검토

post_production:
  - [ ] 월간 보안 리뷰
```

### 8.17 베이스라인 측정 (Phase 1 전 2주)

| 측정 항목 | 수집 방법 | 목적 |
|----------|----------|------|
| 주간 데이터 요청 건수 | Jira 티켓 집계 | ROI 베이스라인 |
| 요청당 평균 처리 시간 | 개발팀 인터뷰 | 시간 절감 계산 |
| 요청 유형 분류 | 요청 내용 분석 | AI 처리 가능 비율 |

### 8.18 Day 0 LLM Fallback PoC

```yaml
fallback_poc_checklist:
  - [ ] OpenAI 정상 호출 테스트 (gpt-4-turbo)
  - [ ] OpenAI 타임아웃(10s) 시뮬레이션
  - [ ] Anthropic 자동 전환 확인 (claude-3-sonnet)
  - [ ] 전환 시간 측정 (< 2초 목표)
```

### 8.19 최종 승인 현황

| 승인자 | 영역 | 결정 | 조건 |
|--------|------|------|------|
| John (PM) | 제품 | ✅ | 중간 체크포인트 |
| Winston (Architect) | 기술 | ✅ | Fallback PoC |
| Mary (Analyst) | 비즈니스 | ✅ | 베이스라인 측정 |

**최종 상태: ✅ 조건부 승인 완료**

---

## 9. 기능 요구사항 (Functional Requirements)

> ⚠️ **Capability Contract**: 이 목록에 없는 기능은 최종 제품에 포함되지 않습니다.
>
> **관련 섹션**: [Success Criteria](#2-success-criteria) | [User Journeys](#4-user-journeys) | [Scoping](#8-프로젝트-스코핑--단계별-개발)

### 9.1 자연어 질의 (Natural Language Query)

- **FR1**: 관리자는 자연어로 데이터 질의를 입력할 수 있다
- **FR2**: 시스템은 자연어 질의를 SQL로 변환할 수 있다
- **FR3**: 시스템은 질의 결과를 자연어 답변으로 제공할 수 있다
- **FR4**: 시스템은 질의 결과를 테이블 형태로 표시할 수 있다
- **FR5**: 관리자는 생성된 SQL을 확인할 수 있다 (선택적)
- **FR6**: 관리자는 접근성 모드로 텍스트 요약을 받을 수 있다

### 9.2 데이터 소스 접근 (Data Source Access)

- **FR7**: 시스템은 MariaDB 데이터를 조회할 수 있다
- **FR8**: 시스템은 MSSQL 데이터를 조회할 수 있다
- **FR9**: 시스템은 허용된 테이블/컬럼만 조회할 수 있다
- **FR10**: 시스템은 두 DB의 데이터를 크로스 조인할 수 있다 (Phase 2)
- **FR11**: 시스템은 GA4 데이터를 조회할 수 있다 (Phase 4)

### 9.3 보안 및 접근 제어 (Security & Access Control)

- **FR12**: 시스템은 인증된 관리자만 접근을 허용할 수 있다
- **FR13**: 시스템은 역할별 데이터 접근을 제한할 수 있다
- **FR14**: 시스템은 SQL Injection 공격을 차단할 수 있다
- **FR15**: 시스템은 금지된 테이블 접근을 차단할 수 있다
- **FR16**: 시스템은 민감 데이터를 마스킹할 수 있다
- **FR17**: 시스템은 모든 질의와 접근을 로깅할 수 있다

### 9.4 사용자 경험 (User Experience)

- **FR18**: 관리자는 예시 질문 목록을 볼 수 있다
- **FR19**: 관리자는 이전 질의 히스토리를 조회할 수 있다
- **FR20**: 시스템은 에러 발생 시 사용자 친화적 메시지를 제공할 수 있다
- **FR21**: 시스템은 에러 시 대안 질문을 제안할 수 있다
- **FR22**: 관리자는 자주 묻는 질문 자동완성을 사용할 수 있다 (Phase 1.5)
- **FR23**: 시스템은 맥락 기반 후속 질문을 제안할 수 있다 (Phase 2)

### 9.5 피드백 및 학습 (Feedback & Learning)

- **FR24**: 관리자는 질의 결과에 대해 피드백을 제공할 수 있다
- **FR25**: 관리자는 잘못된 답변을 수정하여 제출할 수 있다
- **FR26**: 관리자는 질의 결과를 1-5점으로 평가할 수 있다
- **FR27**: 시스템은 피드백 데이터를 수집하고 저장할 수 있다

### 9.6 시스템 운영 (System Operations)

- **FR28**: 시스템은 요청 빈도를 제한할 수 있다 (Rate Limiting)
- **FR29**: 시스템은 LLM 장애 시 대체 서비스로 전환할 수 있다
- **FR30**: 시스템은 동일 질의에 대해 캐시된 응답을 제공할 수 있다
- **FR31**: 시스템은 서비스 상태를 헬스체크로 확인할 수 있다
- **FR32**: 시스템은 SLA 위반 시 알림을 발송할 수 있다

### 9.7 스트리밍 응답 (Streaming Response) - Phase 2

- **FR33**: 시스템은 SSE로 실시간 응답을 스트리밍할 수 있다
- **FR34**: 관리자는 스트리밍 중 진행 상태를 확인할 수 있다

### 9.8 프로액티브 인사이트 (Proactive Insights) - Phase 3

- **FR35**: 시스템은 이상 패턴 감지 시 알림을 발송할 수 있다
- **FR36**: 시스템은 예약된 리포트를 자동 생성할 수 있다
- **FR37**: 관리자는 알림 조건을 설정할 수 있다

### 9.9 시각화 (Visualization) - Phase 3

- **FR38**: 시스템은 질의 결과를 차트로 시각화할 수 있다
- **FR39**: 관리자는 시각화 유형을 선택할 수 있다

### 9.10 GA4 통합 (GA4 Integration) - Phase 4

- **FR40**: 시스템은 유입 경로별 데이터를 조회할 수 있다
- **FR41**: 시스템은 유입-매출 연계 분석을 수행할 수 있다
- **FR42**: 시스템은 전환율 분석을 제공할 수 있다

### 9.11 기능 요구사항 요약

| Phase | FR 범위 | 기능 수 |
|-------|---------|---------|
| Phase 1 | FR1-FR21, FR24-FR32 | 30개 |
| Phase 1.5 | FR22 추가 | +1개 |
| Phase 2 | FR10, FR23, FR33-FR34 추가 | +4개 |
| Phase 3 | FR35-FR39 추가 | +5개 |
| Phase 4 | FR11, FR40-FR42 추가 | +4개 |
| **총계** | | **42개** |

---

## 10. 비기능 요구사항 (Non-Functional Requirements)

> ⚠️ **Quality Contract**: 시스템이 "얼마나 잘" 동작해야 하는지 정의합니다.
>
> **관련 섹션**: [Technical Success](#23-technical-success) | [Domain Security](#5-domain-specific-requirements) | [Test Strategy](#811-테스트-전략)

### 10.1 성능 (Performance)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-P1** | 단일 DB 질의 응답 시간 | p95 ≤ 3초 | Sentry Performance | 1 |
| **NFR-P2** | 크로스 DB 질의 응답 시간 | p95 ≤ 5초 | Sentry Performance | 2 |
| **NFR-P3** | 스트리밍 첫 토큰 시간 (TTFB) | ≤ 500ms | SSE 측정 | 2 |
| **NFR-P4** | 동시 사용자 처리 | 10명 동시 질의 | 부하 테스트 | 1 |
| **NFR-P5** | 캐시 히트율 | ≥ 30% | Redis 모니터링 | 1.5 |
| **NFR-P6** | LLM API 호출 최적화 | 동일 질의 캐싱 5분 | 캐시 로그 | 1 |

### 10.2 보안 (Security)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-S1** | SQL Injection 차단율 | 100% | 퍼징 테스트 100패턴 | 1 |
| **NFR-S2** | 인증 우회 시도 차단 | 100% | 보안 테스트 | 1 |
| **NFR-S3** | 민감 테이블 접근 차단 | 100% (정의된 테이블에 한해) | 접근 로그 | 1 |
| **NFR-S4** | 민감 데이터 마스킹 | 100% (정의된 필드에 한해) | 결과 검증 | 1 |
| **NFR-S5** | 감사 로그 보존 | 90일 | 자동화 검증 | 1 |
| **NFR-S6** | Rate Limiting | 20 RPM / 200 RPH | Redis 기반 | 1 |
| **NFR-S7** | 보안 이벤트 로깅 | 모든 차단 이벤트 | 로그 분석 | 1 |

> **참고 (NFR-S3, NFR-S4)**: 기능은 구현하되, 민감 테이블/필드 목록이 정의되지 않은 경우 해당 검증은 SKIP합니다.

### 10.3 안정성 (Reliability)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-R1** | 서비스 가용성 | ≥ 99.5% | 업타임 모니터링 | 1 |
| **NFR-R2** | LLM Fallback 성공률 | ≥ 95% | Fallback 로그 | 1 |
| **NFR-R3** | Circuit Breaker 동작 | 5회 실패 후 Open | 상태 로그 | 1.5 |
| **NFR-R4** | DB 연결 풀 안정성 | 연결 누수 0건 | 풀 모니터링 | 1 |
| **NFR-R5** | 에러 복구 시간 | ≤ 30초 | 장애 테스트 | 1.5 |
| **NFR-R6** | 질의 재시도 | 최대 3회 exponential backoff | 재시도 로그 | 1 |

### 10.4 통합 (Integration)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-I1** | MariaDB 연결 풀 크기 | 5-20 connections | 연결 모니터링 | 1 |
| **NFR-I2** | MSSQL 연결 안정성 | TDS 7.0/7.1 호환 | 연결 테스트 | 2 |
| **NFR-I3** | Redis 캐시 연결 | 연결 실패 시 무캐시 동작 | Fallback 테스트 | 1 |
| **NFR-I4** | LLM API 타임아웃 | 10초 | API 모니터링 | 1 |
| **NFR-I5** | 기존 인증 시스템 통합 | 100% 호환 | 통합 테스트 | 1 |
| **NFR-I6** | GA4 API 연동 | 일 10,000 요청 쿼터 | API 사용량 | 4 |

### 10.5 접근성 (Accessibility)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-A1** | 스크린리더 호환 | 주요 기능 음성 안내 | 수동 테스트 | 1.5 |
| **NFR-A2** | 키보드 네비게이션 | 모든 기능 키보드 접근 | 수동 테스트 | 1.5 |
| **NFR-A3** | 텍스트 요약 모드 | 테이블 대신 텍스트 제공 | 기능 테스트 | 1 |

### 10.6 운영성 (Operability)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-O1** | 구조화 로깅 | JSON 형식 + 요청 ID | 로그 검증 | 1 |
| **NFR-O2** | 메트릭 대시보드 | 주요 KPI 실시간 조회 | Sentry/Grafana | 1.5 |
| **NFR-O3** | 알림 설정 | SLA 위반 시 즉시 알림 | 알림 테스트 | 1.5 |
| **NFR-O4** | LLM 비용 모니터링 | 월 상한 알림 | 비용 대시보드 | 1 |

### 10.7 테스트 가능성 (Testability)

| ID | 요구사항 | 목표 | 측정 방법 | Phase |
|----|----------|------|----------|-------|
| **NFR-T1** | 단위 테스트 커버리지 | ≥ 90% | Coverage 리포트 | 1 |

### 10.8 테스트 매트릭스

| 테스트 유형 | Phase 1 | Phase 1.5 | Phase 2 |
|------------|---------|-----------|---------|
| Unit Test | 90% | 90% | 90% |
| Integration Test | 80% | 85% | 85% |
| Security Test | 기본 | 퍼징 100패턴 | Full + WAF |
| E2E Test | 핵심 플로우 | 확장 플로우 | 크로스 DB |
| Performance Test | 기본 부하 | 스트레스 | 동시성 |

### 10.9 비기능 요구사항 요약

| 카테고리 | NFR 수 | 핵심 목표 |
|----------|--------|----------|
| 성능 | 6 | p95 ≤ 3초, 동시 10명 |
| 보안 | 7 | Injection 100% 차단 |
| 안정성 | 6 | 가용성 99.5%+ |
| 통합 | 6 | 기존 시스템 호환 |
| 접근성 | 3 | 기본 접근성 보장 |
| 운영성 | 4 | 실시간 모니터링 |
| 테스트 가능성 | 1 | 커버리지 90%+ |
| **총계** | **33** | |
