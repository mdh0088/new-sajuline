# AI 관리자 어시스턴트 - 문서 인덱스

> **최종 수정**: 2026-01-29
> **프로젝트 상태**: 설계 단계

---

## 문서 목록

| # | 문서 | 설명 | 상태 |
|---|------|------|------|
| 01 | [아키텍처 개요](./01-architecture-overview.md) | 시스템 아키텍처, LangGraph 구조, 프로젝트 구조 | ✅ 완료 |
| 02 | [제약사항 및 비즈니스 규칙](./02-constraints.md) | 기술적 제약, 데이터 소스 규칙, 보안 규칙 | ✅ 완료 |
| 03 | [구현 로드맵](./03-implementation-roadmap.md) | Phase별 구현 계획, 작업 목록, 완료 기준 | ✅ 완료 |
| 04 | [리스크 평가 및 완화 전략](./04-risk-mitigation.md) | 리스크 매트릭스, 4중 방어 체계, 모니터링 | ✅ 완료 |
| 05 | [GA4 연동 가이드](./05-ga4-integration.md) | GA4 Data API 연동, 유입-매출 연계 분석 | ✅ 완료 |
| 06 | [LangGraph 구현 설계](./06-langgraph-implementation.md) | StateGraph 노드 설계, 조건부 라우팅, 스트리밍 | ✅ 완료 |

---

## 빠른 참조

### 핵심 아키텍처

```
자연어 질문 → Supervisor → [MariaDB Agent | MSSQL Agent | GA4 Agent]
                                      ↓
                              pandas.merge() (크로스 조인)
                                      ↓
                              자연어 응답 + 후속 분석 제안
```

### 데이터 소스

| DB | 연결 방식 | 주요 데이터 |
|----|----------|------------|
| MariaDB | aiomysql (Async) | 매출, 유저, 상담사 프로필 |
| MSSQL 2005 | pymssql (Sync→Async 래핑) | 상담 로그, 실시간 상태 |
| GA4 | Data API | 유입 경로, 전환율 |

### 크로스 DB 조인 키

| 엔티티 | MariaDB | MSSQL |
|--------|---------|-------|
| 상담사 | `t_counselor.counselor_code` | `tm60_member.m_code` |
| 유저 | `t_user.user_id` | `tm60_users.u_id` |

### 보안 원칙

- ✅ **읽기 전용**: SELECT만 허용
- ✅ **4중 방어**: Prompt → SQL 검증 → 결과 검증 → 사용자 확인
- ✅ **민감정보 마스킹**: 비밀번호, 주민번호 등

### 구현 Phase

| Phase | 목표 | 핵심 산출물 |
|-------|------|------------|
| 1 | MVP Core | 단일 DB 질의 |
| 2 | 멀티 DB | 크로스 DB 분석 |
| 3 | UX 고도화 | 프로액티브 인사이트 |
| 4 | 확장 | GA4 통합, 시각화 |

---

## 관련 문서

- [Product Brief](../../_bmad-output/planning-artifacts/product-brief-admin-backend-2026-01-29.md)
- [기술 리서치](../../_bmad-output/planning-artifacts/research/technical-langgraph-multi-db-agent-research-2026-01-29.md)
- [브레인스토밍 결과](../../_bmad-output/brainstorming/brainstorming-session-2026-01-29.md)

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-29 | 초기 문서 인덱스 생성 |
| 2026-01-29 | 리스크 평가 및 GA4 연동 가이드 추가 |
| 2026-01-29 | LangGraph 구현 설계 문서 추가 |
