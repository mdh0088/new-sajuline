---
stepsCompleted: [1, 2, 3, 4]
partyModeUsed: true
epicStructureApproved: true
storiesReviewed: true
validationPassed: true
status: ready-for-dev
completedAt: 2026-01-28
inputDocuments:
  - docs/prd/functional-requirements.md
  - docs/prd/non-functional-requirements.md
  - docs/prd/project-scoping-phased-development.md
  - docs/architecture/core-architectural-decisions.md
  - docs/architecture/implementation-patterns-consistency-rules.md
  - _bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md
---

# new-sajuline - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for **사주라인 리뉴얼 MVP**, decomposing the requirements from the PRD and Architecture into implementable stories.

**프로젝트 특성:**
- **Brownfield 프로젝트**: 회원/결제 시스템은 이미 완료됨
- **MVP 핵심**: AI 운세 서비스 (일/주/월/연) 신규 개발
- **Tech Spec 존재**: AI 사주 일운 서비스 상세 스펙 완료 (ready-for-dev)
- **POST-MVP**: 실시간 상담 서비스 (FR17-FR25)는 향후 구현 예정

## Requirements Inventory

### Functional Requirements

**사용자 계정 관리 (User Account)**
- FR1: 사용자는 이메일과 비밀번호로 회원가입할 수 있다
- FR2: 사용자는 카카오 계정으로 소셜 로그인할 수 있다
- FR3: 사용자는 네이버 계정으로 소셜 로그인할 수 있다
- FR4: 사용자는 휴대폰 번호로 본인인증을 완료할 수 있다
- FR5: 사용자는 사주 정보(생년월일, 태어난 시간, 성별, 음력 여부)를 입력할 수 있다
- FR6: 사용자는 프로필 정보를 조회하고 수정할 수 있다
- FR7: 사용자는 비밀번호를 변경할 수 있다
- FR8: 사용자는 회원 탈퇴를 요청할 수 있다
- FR9: 신규 가입 사용자는 가입 완료 시 웰컴 포인트를 자동 지급받는다

**AI 운세 서비스 (AI Fortune) - MVP 핵심**
- FR10: 로그인한 사용자는 일일 운세를 AI 분석으로 조회할 수 있다
- FR11: 로그인한 사용자는 주간 운세를 AI 분석으로 조회할 수 있다
- FR12: 로그인한 사용자는 월간 운세를 AI 분석으로 조회할 수 있다
- FR13: 로그인한 사용자는 연간 운세를 AI 분석으로 조회할 수 있다
- FR14: 사용자는 운세 기간 유형(일/주/월/연)을 탭으로 전환할 수 있다
- FR15: 시스템은 사용자의 기존 사주 정보를 기반으로 AI 운세를 생성한다
- FR16: 시스템은 동일 사용자의 동일 기간 운세 요청 시 캐시된 결과를 제공한다

**상담 서비스 (Consultation)**
- FR17: 사용자는 온라인 상태인 상담사 목록을 조회할 수 있다
- FR18: 사용자는 상담사 프로필(소개, 전문분야, 평점, 가격)을 확인할 수 있다
- FR19: 사용자는 특정 상담사와 채팅 상담을 시작할 수 있다
- FR20: 사용자는 상담사에게 텍스트 메시지를 전송할 수 있다
- FR21: 사용자는 상담사로부터 실시간으로 메시지를 수신할 수 있다
- FR22: 사용자는 진행 중인 채팅에서 상담사의 타이핑 상태를 확인할 수 있다
- FR23: 사용자는 상담 완료 후 상담사에게 별점 리뷰를 작성할 수 있다
- FR24: 상담사는 고객의 채팅 요청을 수락하거나 거절할 수 있다
- FR25: 상담사는 자신의 온라인/오프라인 상태를 변경할 수 있다

**결제 및 포인트 (Payment & Points)**
- FR26: 사용자는 현재 보유 포인트 잔액을 조회할 수 있다
- FR27: 사용자는 포인트 충전 상품 목록을 조회할 수 있다
- FR28: 사용자는 신용카드로 포인트를 충전할 수 있다
- FR29: 사용자는 가상계좌로 포인트를 충전할 수 있다
- FR30: 사용자는 카카오페이/네이버페이로 포인트를 충전할 수 있다
- FR31: 시스템은 상담 진행 시 분당 요금으로 포인트를 자동 차감한다
- FR32: 사용자는 포인트 사용/충전 내역을 조회할 수 있다
- FR33: 시스템은 포인트 잔액 부족 시 상담을 자동 종료한다

**콘텐츠 및 공지 (Content & Notices)**
- FR34: 사용자는 공지사항 목록을 조회할 수 있다
- FR35: 사용자는 공지사항 상세 내용을 확인할 수 있다
- FR36: 사용자는 배너를 통해 이벤트/프로모션 정보를 확인할 수 있다
- FR37: 사용자는 1:1 문의를 작성할 수 있다
- FR38: 사용자는 자신의 문의 내역과 답변을 조회할 수 있다

**알림 (Notifications)**
- FR39: 사용자는 상담 관련 알림을 수신할 수 있다
- FR40: 사용자는 결제/포인트 관련 알림을 수신할 수 있다
- FR41: 사용자는 시스템 공지 알림을 수신할 수 있다
- FR42: 사용자는 알림 목록을 조회하고 읽음 처리할 수 있다

**관리자 기능 (Admin)**
- FR43: 관리자는 전체 회원 목록을 조회하고 검색할 수 있다
- FR44: 관리자는 회원 상세 정보와 활동 내역을 확인할 수 있다
- FR45: 관리자는 상담사 목록을 관리(승인/정지/삭제)할 수 있다
- FR46: 관리자는 상담사 신청서를 검토하고 승인/반려할 수 있다
- FR47: 관리자는 공지사항을 등록/수정/삭제할 수 있다
- FR48: 관리자는 배너를 등록/수정/삭제할 수 있다
- FR49: 관리자는 결제 내역을 조회할 수 있다
- FR50: 관리자는 1:1 문의에 답변을 작성할 수 있다
- FR51: 관리자는 AI 운세 이용 통계를 확인할 수 있다
- FR52: 관리자는 대시보드에서 핵심 지표를 확인할 수 있다

### NonFunctional Requirements

**Performance**
- NFR-P1: API 응답시간 p95 < 300ms
- NFR-P2: AI 운세 응답 < 3초
- NFR-P3: 채팅 메시지 RTT < 200ms
- NFR-P4: 페이지 초기 로드 LCP < 2.5초
- NFR-P5: 인터랙티브 시간 TTI < 3.5초
- NFR-P6: 초기 JS 번들 < 200KB (gzipped)
- NFR-P7: 전체 페이지 < 1MB
- NFR-P8: CLS < 0.1

**Security**
- NFR-S1: 모든 통신은 HTTPS(TLS 1.2+)로 암호화
- NFR-S2: 비밀번호는 Argon2id 알고리즘으로 해싱
- NFR-S3: 채팅 메시지는 AES-256-GCM으로 암호화 저장
- NFR-S4: 개인정보(사주 정보)는 암호화되어 저장
- NFR-S5: JWT 토큰 만료 시간 Access 15분, Refresh 7일
- NFR-S6: 인증 토큰은 HttpOnly 쿠키로 저장
- NFR-S7: CSRF 토큰으로 상태 변경 요청 보호
- NFR-S8: Rate Limiting 100 req/min per IP
- NFR-S9: CORS 정책 허용된 도메인만 접근
- NFR-S10: SQL Injection, XSS 공격 방어
- NFR-S11: 결제 정보는 PG사를 통해 처리, 서버 저장 안함
- NFR-S12: 결제 웹훅 서명 검증

**Scalability**
- NFR-SC1: 동시 접속 사용자 500명 지원 (MVP)
- NFR-SC2: 일일 AI 운세 요청 10,000건 처리
- NFR-SC3: 동시 채팅 세션 100개 지원
- NFR-SC4: Stateless 아키텍처로 수평 확장 가능
- NFR-SC5: 세션 데이터 Redis 저장 (서버 간 공유)
- NFR-SC6: 데이터베이스 연결 풀링 사용

**Reliability**
- NFR-R1: 서비스 가용성 99% 이상
- NFR-R2: 계획된 유지보수 사전 공지
- NFR-R3: AI API 장애 시 캐시 또는 에러 메시지 표시
- NFR-R4: WebSocket 연결 끊김 시 자동 재연결 (exponential backoff)
- NFR-R5: 결제 실패 시 포인트 이중 차감 방지
- NFR-R6: 포인트 거래 트랜잭션 원자성 보장
- NFR-R7: 데이터베이스 백업 일 1회 이상

**Accessibility**
- NFR-A1: 텍스트/배경 명암비 4.5:1 이상
- NFR-A2: 모든 인터랙티브 요소 키보드 접근 가능
- NFR-A3: 포커스 표시자 명확히 표시
- NFR-A4: 폼 요소 레이블 연결
- NFR-A5: 이미지 대체 텍스트 제공
- NFR-A6: 터치 타겟 최소 44px × 44px
- NFR-A7: 200% 확대 시 레이아웃 유지

**Integration**
- NFR-I1: OpenAI API 타임아웃 10초, 실패 시 재시도 1회
- NFR-I2: Payletter (PG) 웹훅 5초 이내 응답
- NFR-I3: KCP (본인인증) 실시간 처리
- NFR-I4: Kakao/Naver OAuth 토큰 자동 갱신
- NFR-I5: MSSQL (ARS) 읽기 전용, 타임아웃 5초
- NFR-I6: REST API JSON 형식
- NFR-I7: API 버저닝 /api/v1/ 지원
- NFR-I8: 에러 응답 일관된 형식

**Monitoring & Observability**
- NFR-M1: API 요청/응답 구조화된 JSON 로그
- NFR-M2: 로그에 요청 ID 포함 (추적 가능)
- NFR-M3: 민감 정보 로그 기록 금지
- NFR-M4: Sentry 에러 실시간 수집
- NFR-M5: 핵심 지표 대시보드 확인 가능

### Additional Requirements

**Architecture 결정사항:**
- Brownfield 프로젝트: 기존 시스템 활용 (회원/결제 완료, 상담 POST-MVP)
- AI 캐싱 전략: 일운 24h, 주운 7d, 월운 30d, 연운 365d TTL
- fortune_histories 테이블 스키마 정의됨
- OpenAI 연동: GPT-4o-mini, 10s timeout, 1회 retry, 캐시 폴백
- 렌더링 전략: 메인/상담사목록 SSR, 운세/마이페이지/채팅 CSR

**Implementation Patterns:**
- Backend: DDD 레이어드 (api → service → repository → model)
- Frontend: Nuxt 4 + Vue 3 + Tailwind + Pinia + TanStack Query
- 네이밍: Python snake_case, TypeScript camelCase
- API 응답: 표준 형식 { success, data, error, pagination }

**Tech Spec 참조 (AI 일운 서비스):**
- 파일: `_bmad-output/implementation-artifacts/tech-spec-ai-saju-daily-fortune.md`
- 상태: ready-for-dev
- 내용: 사주 지식베이스 DB, LangChain RAG, 일운 API, 15개 구현 Task, 16개 AC

**MVP 범위:**
- ✅ 완료: 회원 시스템, 결제 시스템, 콘텐츠, 알림
- 🆕 신규 개발: AI 운세 4종 (일/주/월/연)
- ⏳ POST-MVP: 실시간 상담 서비스 (FR17-FR25)
- ❌ 제외: AI 채팅 상담, 궁합 분석, 타로/꿈해몽

### FR Coverage Map

| FR | Epic | 설명 | 상태 |
|----|------|------|------|
| FR1-FR9 | Epic 1 | 사용자 인증 및 프로필 | ✅ EXISTING |
| FR10 | Epic 2, 3 | 일일 운세 조회 | 🆕 NEW |
| FR11-FR13 | Epic 2, 3 | 주/월/연 운세 조회 (Story 2.6, 3.3) | 🆕 NEW |
| FR14 | Epic 3 | 운세 탭 전환 | 🆕 NEW |
| FR15 | Epic 2 | AI 운세 생성 (Backend) | 🆕 NEW |
| FR16 | Epic 2 | 운세 캐싱 | 🆕 NEW |
| FR17-FR25 | - | 상담 서비스 | ⏳ POST-MVP |
| FR26-FR33 | Epic 4 | 결제 및 포인트 | ✅ EXISTING |
| FR34-FR38 | Epic 5 | 콘텐츠 및 고객 지원 | ✅ EXISTING |
| FR39-FR42 | Epic 6 | 알림 서비스 | ✅ EXISTING |
| FR43-FR50 | Epic 7 | 관리자 기능 (기존) | ✅ EXISTING |
| FR51 | Epic 7 | AI 운세 통계 | 🆕 NEW |
| FR52 | Epic 7 | 대시보드 | ✅ EXISTING |

## Epic List

### Epic 1: 사용자 인증 및 프로필 관리 ✅ EXISTING

**목표:** 사용자가 계정을 생성하고, 소셜 로그인하고, 사주 정보를 입력할 수 있다

- **FRs:** FR1-FR9
- **상태:** 이미 구현 완료
- **비고:** AI 운세 서비스의 기반 (사주 정보 필요)

---

### Epic 2: AI 일일 운세 서비스 (Backend) 🆕 NEW

**목표:** 시스템이 사용자의 사주 정보를 기반으로 AI 일일 운세를 생성하고 API로 제공할 수 있다

- **FRs:** FR10 (부분), FR15, FR16
- **상태:** 신규 개발 (MVP 핵심)
- **Tech Spec:** `tech-spec-ai-saju-daily-fortune.md` 참조
- **산출물:**
  - 사주 지식베이스 DB (천간/지지/십성 160~200행)
  - 사주 계산 유틸리티 (일진, 십성)
  - LangChain RAG 체인
  - `/api/v1/fortune/daily` API 엔드포인트
  - Redis 캐싱 (TTL: 24h) + LLM 폴백

**구현 Task (Tech Spec 기준):**
- Phase A: 의존성 + 기반 (Task 1-2)
- Phase B: 데이터 모델 + 시드 (Task 3-8)
- Phase C: 리포지토리 + 스키마 (Task 9-10)
- Phase D: LangChain 체인 + 서비스 (Task 11-13)
- Phase E: API 엔드포인트 (Task 14-15)

---

### Epic 3: AI 운세 프론트엔드 🆕 NEW

**목표:** 사용자가 AI 운세 결과를 보기 좋게 조회하고, 기간별(일/주/월/연)로 전환할 수 있다

- **FRs:** FR10, FR11, FR12, FR13, FR14
- **상태:** 신규 개발
- **의존성:** Epic 2 완료 필요
- **산출물:**
  - 운세 페이지 (`/fortune`)
  - FortuneTabs 컴포넌트 (일/주/월/연 탭)
  - FortuneCard 컴포넌트 (운세 결과 표시)
  - FortuneLoading, FortuneError 컴포넌트
  - useFortune composable (API 연동)

---

### Epic 4: 결제 및 포인트 시스템 ✅ EXISTING

**목표:** 사용자가 포인트를 충전하고 서비스 이용 시 차감된다

- **FRs:** FR26-FR33
- **상태:** 이미 구현 완료

---

### Epic 5: 콘텐츠 및 고객 지원 ✅ EXISTING

**목표:** 사용자가 공지사항을 확인하고 1:1 문의를 할 수 있다

- **FRs:** FR34-FR38
- **상태:** 이미 구현 완료

---

### Epic 6: 알림 서비스 ✅ EXISTING

**목표:** 사용자가 중요한 알림을 수신하고 관리할 수 있다

- **FRs:** FR39-FR42
- **상태:** 이미 구현 완료

---

### Epic 7: 관리자 운영 도구 🔄 EXTEND

**목표:** 관리자가 서비스를 운영하고 AI 운세 통계를 확인할 수 있다

- **FRs:** FR43-FR52
- **상태:** 기존 완료 + FR51 신규 (AI 운세 통계)
- **의존성:** Epic 2 완료 필요 (통계 데이터)
- **산출물:** AI 운세 이용 통계 대시보드

---

## MVP 개발 우선순위

| 순서 | Epic | 예상 기간 | 의존성 |
|------|------|----------|--------|
| **1** | Epic 2: AI 일일 운세 Backend | ~2주 | 없음 |
| **2** | Epic 3: AI 운세 프론트엔드 | ~1주 | Epic 2 |
| **3** | Epic 7: 관리자 (FR51 추가) | ~2일 | Epic 2 |

**총 예상 기간:** 3~4주

---

## User Stories

### Epic 2: AI 일일 운세 서비스 (Backend)

#### Story 2.1: 사주 지식베이스 데이터 모델

As a **시스템**,
I want **천간, 지지, 십성 등 사주 기초 데이터를 DB에 저장**,
So that **AI 운세 생성 시 사주 해석 지식을 RAG로 검색할 수 있다**.

**Acceptance Criteria:**

**Given** 백엔드 서버가 실행 중일 때
**When** 데이터베이스 마이그레이션이 실행되면
**Then** `saju_heavenly_stems` (천간 10행), `saju_earthly_branches` (지지 12행), `saju_ten_gods` (십성 10행) 테이블이 생성된다
**And** 각 테이블에 `name`, `hanja`, `element`, `meaning`, `description` 컬럼이 포함된다
**And** 시드 데이터 160~200행이 정상적으로 삽입된다
**And** `fortune_histories` 테이블이 생성된다 (user_id, fortune_type, date, content, created_at)

**기술 참조:**
- Tech Spec Task 3-8 (데이터 모델 + 시드)
- SQLAlchemy 2.0 + Alembic 마이그레이션
- `fortune_histories` 스키마: Tech Spec 참조

---

#### Story 2.2: 사주 계산 유틸리티

As a **시스템**,
I want **사용자의 생년월일시를 기반으로 일진과 십성을 계산**,
So that **해당 날짜의 사주 운세 분석에 필요한 기초 데이터를 생성할 수 있다**.

**Acceptance Criteria:**

**Given** 사용자의 생년월일시 정보가 있을 때
**When** `calculate_daily_pillar(date)` 함수가 호출되면
**Then** 해당 날짜의 일간(천간)과 일지(지지)가 정확히 계산된다
**And** 계산 결과는 60갑자 순환을 따른다

**Given** 일간과 사용자의 일주가 있을 때
**When** `calculate_ten_gods(day_stem, birth_stem)` 함수가 호출되면
**Then** 정확한 십성(비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인)이 반환된다

**Given** 잘못된 날짜 형식이 입력될 때
**When** 계산 함수가 호출되면
**Then** `ValueError`와 함께 명확한 에러 메시지가 반환된다

**기술 참조:**
- `backend/src/utils/saju_calculator.py`
- 단위 테스트 커버리지 90% 이상

---

#### Story 2.3: 운세 캐시 시스템

As a **시스템**,
I want **생성된 운세를 Redis와 DB에 캐싱**,
So that **동일 사용자의 동일 기간 운세 재요청 시 빠르게 응답할 수 있다 (FR16)**.

**Acceptance Criteria:**

**Given** 운세가 최초 생성될 때
**When** 운세 서비스가 결과를 저장하면
**Then** Redis에 `fortune:daily:{user_id}:{date}` 키로 캐싱된다 (TTL: 24시간)
**And** `fortune_histories` 테이블에 영구 저장된다

**Given** 동일 사용자가 동일 날짜 운세를 재요청할 때
**When** API가 호출되면
**Then** Redis 캐시에서 먼저 조회하고, 캐시 히트 시 DB 조회 없이 즉시 반환된다
**And** 응답 헤더에 `X-Cache: HIT`가 포함된다

**Given** Redis 캐시가 만료되었을 때
**When** 운세가 요청되면
**Then** `fortune_histories` 테이블에서 조회하여 반환한다
**And** Redis 캐시를 다시 설정한다

**Given** Redis 서버 장애 시
**When** 운세가 요청되면
**Then** DB 폴백으로 정상 응답하고, 에러 로그가 기록된다

**기술 참조:**
- `fortune_histories` 테이블 스키마 (Tech Spec)
- Redis TTL: daily 24h, weekly 7d, monthly 30d, yearly 365d

---

#### Story 2.4: LangChain RAG 체인 구축

As a **시스템**,
I want **사주 지식베이스를 검색하고 GPT-4o-mini로 운세를 생성하는 RAG 체인**,
So that **개인화된 고품질 AI 운세를 생성할 수 있다 (FR15)**.

**Acceptance Criteria:**

**Given** 사용자의 사주 정보와 오늘 날짜가 있을 때
**When** RAG 체인이 실행되면
**Then** 사주 지식베이스에서 관련 천간/지지/십성 정보가 검색된다
**And** GPT-4o-mini에 컨텍스트와 함께 프롬프트가 전송된다
**And** 운세 결과가 정상적으로 생성된다 (성능 목표: NFR-P2 참조)

**Given** OpenAI API를 mock으로 테스트할 때
**When** RAG 체인이 실행되면
**Then** mock 응답으로 정상 동작이 검증된다

**Given** OpenAI API 호출 시
**When** 타임아웃(10초)이 발생하면
**Then** 1회 자동 재시도한다
**And** 재시도 실패 시 캐시된 일반 운세 또는 에러 메시지를 반환한다 (NFR-R3)

**Given** 운세 생성 요청 시
**When** RAG 체인이 실행되면
**Then** 응답에 `overall` (총운), `love` (애정운), `career` (직장운), `health` (건강운), `wealth` (재물운) 섹션이 포함된다
**And** 각 섹션은 50~150자 이내로 생성된다

**기술 참조:**
- LangChain + langchain-openai
- 모델: GPT-4o-mini, temperature: 0.7
- 프롬프트 템플릿: Tech Spec 참조

---

#### Story 2.5: 일일 운세 API 엔드포인트

As a **로그인한 사용자**,
I want **일일 운세를 API로 조회 (FR10)**,
So that **오늘의 AI 운세 분석 결과를 확인할 수 있다**.

**Acceptance Criteria:**

**Given** 로그인한 사용자가 사주 정보를 등록했을 때
**When** `GET /api/v1/fortune/daily` API를 호출하면
**Then** 오늘 날짜 기준 일일 운세가 JSON 형식으로 반환된다
**And** 응답 스키마: `{ success: true, data: { date, fortune_type, day_pillar: { stem, branch }, overall, love, career, health, wealth, created_at } }`
**And** 응답 시간은 p95 < 300ms (캐시 히트 시) 또는 < 3초 (신규 생성 시)

**Given** 사주 정보가 등록되지 않은 사용자일 때
**When** API를 호출하면
**Then** HTTP 400과 `{ success: false, error: { code: "SAJU_INFO_REQUIRED", message: "사주 정보를 먼저 등록해주세요" } }` 반환

**Given** 비로그인 사용자일 때
**When** API를 호출하면
**Then** HTTP 401 Unauthorized 반환

**Given** 특정 날짜의 운세를 조회할 때
**When** `GET /api/v1/fortune/daily?date=2026-01-28` 쿼리 파라미터로 호출하면
**Then** 해당 날짜의 운세가 반환된다 (과거 7일까지만 허용)

**기술 참조:**
- FastAPI Router + Pydantic 스키마
- JWT 인증 필수 (HttpOnly 쿠키)
- Rate Limit: 100 req/min (NFR-S8)

---

#### Story 2.6: 주간/월간/연간 운세 API 확장

As a **로그인한 사용자**,
I want **주간, 월간, 연간 운세를 API로 조회 (FR11, FR12, FR13)**,
So that **다양한 기간의 AI 운세 분석 결과를 확인할 수 있다**.

**Acceptance Criteria:**

**Given** 로그인한 사용자가 사주 정보를 등록했을 때
**When** `GET /api/v1/fortune/weekly` API를 호출하면
**Then** 이번 주 기준 주간 운세가 반환된다
**And** Redis 캐시 TTL은 7일이다

**Given** 로그인한 사용자가 사주 정보를 등록했을 때
**When** `GET /api/v1/fortune/monthly` API를 호출하면
**Then** 이번 달 기준 월간 운세가 반환된다
**And** Redis 캐시 TTL은 30일이다

**Given** 로그인한 사용자가 사주 정보를 등록했을 때
**When** `GET /api/v1/fortune/yearly` API를 호출하면
**Then** 올해 기준 연간 운세가 반환된다
**And** Redis 캐시 TTL은 365일이다

**Given** 각 기간별 운세 응답 시
**When** API가 반환되면
**Then** 응답 스키마는 일일 운세와 동일하며, `fortune_type`이 각각 `weekly`, `monthly`, `yearly`로 구분된다
**And** 해당 기간에 맞는 운세 내용이 생성된다 (주간: 7일 흐름, 월간: 월별 흐름, 연간: 연간 운세)

**기술 참조:**
- Story 2.4 LangChain RAG 체인 재사용
- 프롬프트 템플릿만 기간별로 분기
- 캐싱 전략: Architecture 결정사항 참조

---

### Epic 3: AI 운세 프론트엔드

#### Story 3.1: 운세 API 연동 Composable

As a **프론트엔드 개발자**,
I want **운세 API를 호출하고 상태를 관리하는 composable**,
So that **여러 컴포넌트에서 운세 데이터를 일관되게 사용할 수 있다**.

**Acceptance Criteria:**

**Given** `useFortune` composable이 import될 때
**When** `fetchDailyFortune()` 함수가 호출되면
**Then** `/api/v1/fortune/daily` API가 호출되고 결과가 `fortune` ref에 저장된다
**And** 로딩 상태가 `isLoading` ref로 관리된다
**And** 에러 상태가 `error` ref로 관리된다

**Given** API 호출이 진행 중일 때
**When** `isLoading`을 확인하면
**Then** `true`가 반환되고, 완료 시 `false`로 변경된다

**Given** API 호출이 실패할 때
**When** 에러가 발생하면
**Then** `error` ref에 에러 메시지가 저장된다
**And** `fortune`은 `null` 상태를 유지한다

**Given** 기간별 운세 조회 시
**When** `fetchFortune(type: 'daily' | 'weekly' | 'monthly' | 'yearly')` 호출 시
**Then** 해당 기간의 운세 API가 호출된다

**기술 참조:**
- Vue 3 Composition API
- 기존 TanStack Query (useQuery) 활용 - 이미 frontend에 적용됨
- TypeScript 타입 정의 필수
- `composables/useFortune.ts` 생성

---

#### Story 3.2: 일일 운세 페이지

As a **로그인한 사용자**,
I want **일일 운세 결과를 보기 좋은 UI로 확인 (FR10)**,
So that **오늘의 운세를 한눈에 파악할 수 있다**.

**Acceptance Criteria:**

**Given** 로그인한 사용자가 `/fortune` 페이지에 접속할 때
**When** 페이지가 로드되면
**Then** 일일 운세가 FortuneCard 컴포넌트로 표시된다
**And** 총운, 애정운, 직장운, 건강운, 재물운이 각각 섹션으로 구분된다
**And** 각 운세 섹션에 적절한 아이콘이 표시된다

**Given** 운세 카드가 표시될 때
**When** 사용자가 확인하면
**Then** 오늘 날짜가 명확히 표시된다 (예: "2026년 1월 28일 화요일")
**And** 사용자의 일주(日柱) 정보가 함께 표시된다

**Given** 모바일 기기에서 접속할 때
**When** 페이지가 로드되면
**Then** 반응형 레이아웃으로 최적화되어 표시된다 (모바일 퍼스트)
**And** 터치 타겟은 최소 44px × 44px (NFR-A6)

**Given** 비로그인 사용자가 접속할 때
**When** `/fortune` 페이지에 접근하면
**Then** 로그인 페이지로 리다이렉트된다

**기술 참조:**
- Nuxt 3 페이지: `pages/fortune/index.vue`
- Tailwind CSS 모바일 퍼스트
- CSR 렌더링 (Architecture 결정)

---

#### Story 3.3: 운세 기간 탭 전환

As a **사용자**,
I want **일/주/월/연 운세를 탭으로 전환 (FR14)**,
So that **원하는 기간의 운세를 쉽게 확인할 수 있다**.

**Acceptance Criteria:**

**Given** 운세 페이지에서
**When** FortuneTabs 컴포넌트가 표시되면
**Then** "일운", "주운", "월운", "연운" 4개 탭이 표시된다
**And** 현재 활성 탭이 시각적으로 구분된다 (하이라이트)

**Given** 사용자가 "주운" 탭을 클릭할 때
**When** 탭이 전환되면
**Then** 주간 운세 API (`/api/v1/fortune/weekly`)가 호출된다
**And** 로딩 상태가 표시된 후 주간 운세가 표시된다
**And** URL이 `/fortune?type=weekly`로 변경된다 (FR11)

**Given** 사용자가 "월운" 탭을 클릭할 때
**When** 탭이 전환되면
**Then** 월간 운세가 표시된다 (FR12)

**Given** 사용자가 "연운" 탭을 클릭할 때
**When** 탭이 전환되면
**Then** 연간 운세가 표시된다 (FR13)

**Given** URL에 `?type=monthly` 쿼리가 있을 때
**When** 페이지가 로드되면
**Then** 월운 탭이 활성화되고 월간 운세가 표시된다

**Given** 키보드 사용자일 때
**When** Tab 키로 탭 간 이동 시
**Then** 포커스가 명확히 표시되고 Enter로 선택 가능하다 (NFR-A2, NFR-A3)

**Given** 모바일 기기에서 운세 카드 영역을 터치할 때
**When** 좌우로 스와이프하면
**Then** 이전/다음 기간 탭으로 자연스럽게 전환된다
**And** 스와이프 방향 피드백 애니메이션이 표시된다

**기술 참조:**
- `components/fortune/FortuneTabs.vue`
- Vue Router query params 연동
- 접근성: role="tablist", aria-selected
- 터치 제스처: @vueuse/gesture 또는 native touch events

---

#### Story 3.4: 운세 로딩/에러 UI

As a **사용자**,
I want **운세 로딩 중과 에러 상황에서 적절한 피드백**,
So that **현재 상태를 명확히 인지하고 대응할 수 있다**.

**Acceptance Criteria:**

**Given** 운세 API 호출 중일 때
**When** 로딩 상태가 표시되면
**Then** FortuneLoading 컴포넌트가 스켈레톤 UI로 표시된다
**And** "운세를 분석 중입니다..." 메시지가 표시된다
**And** 애니메이션 로딩 인디케이터가 표시된다

**Given** AI 운세 생성이 3초 이상 걸릴 때
**When** 로딩이 지속되면
**Then** "AI가 사주를 분석하고 있어요. 잠시만 기다려주세요" 메시지로 변경된다

**Given** API 호출이 실패할 때
**When** 에러가 발생하면
**Then** FortuneError 컴포넌트가 표시된다
**And** 사용자 친화적 에러 메시지가 표시된다 (예: "운세를 불러오지 못했어요")
**And** "다시 시도" 버튼이 표시된다

**Given** 사주 정보가 없는 사용자일 때
**When** 운세 페이지에 접근하면
**Then** "사주 정보를 먼저 등록해주세요" 메시지가 표시된다
**And** "사주 등록하기" 버튼이 프로필 페이지로 연결된다

**Given** 네트워크 오류 시
**When** API 호출이 실패하면
**Then** "네트워크 연결을 확인해주세요" 메시지가 표시된다
**And** 오프라인 상태 아이콘이 표시된다

**기술 참조:**
- `components/fortune/FortuneLoading.vue`
- `components/fortune/FortuneError.vue`
- 스켈레톤 UI: Tailwind animate-pulse

---

### Epic 7: 관리자 운영 도구 (AI 운세 통계 확장)

#### Story 7.1: AI 운세 통계 API

As a **관리자**,
I want **AI 운세 이용 통계를 API로 조회 (FR51)**,
So that **서비스 이용 현황을 파악하고 운영 의사결정에 활용할 수 있다**.

**Acceptance Criteria:**

**Given** 관리자 권한이 있는 사용자가 인증되었을 때
**When** `GET /api/v1/admin/fortune/statistics` API를 호출하면
**Then** AI 운세 이용 통계가 JSON 형식으로 반환된다
**And** 응답 스키마: `{ success: true, data: { period, total_requests, unique_users, by_type, by_date } }`

**Given** 기간 필터가 적용될 때
**When** `?start_date=2026-01-01&end_date=2026-01-31` 쿼리로 호출하면
**Then** 해당 기간의 통계만 집계되어 반환된다
**And** 기본값은 최근 30일이다

**Given** 통계 집계 시
**When** API가 호출되면
**Then** 다음 지표가 포함된다:
  - `total_requests`: 총 운세 요청 수
  - `unique_users`: 순 이용자 수
  - `by_type`: 기간별 분포 (daily, weekly, monthly, yearly)
  - `by_date`: 일별 추이 데이터
  - `cache_hit_rate`: 캐시 히트율
  - `avg_response_time`: 평균 응답 시간

**Given** 일반 사용자가 호출할 때
**When** 관리자 API에 접근하면
**Then** HTTP 403 Forbidden이 반환된다

**Given** 대용량 데이터 조회 시
**When** 90일 이상의 기간을 요청하면
**Then** 일별 대신 주별 집계 데이터로 반환된다
**And** 응답 시간은 p95 < 500ms를 유지한다

**기술 참조:**
- `admin-backend/src/api/v1/fortune_statistics_api.py`
- `fortune_histories` 테이블 집계 쿼리
- Redis 캐싱 (통계 결과 5분 TTL)

---

#### Story 7.2: AI 운세 통계 대시보드 UI

As a **관리자**,
I want **AI 운세 이용 통계를 시각적 대시보드로 확인 (FR51)**,
So that **서비스 성과를 한눈에 파악할 수 있다**.

**Acceptance Criteria:**

**Given** 관리자가 대시보드 페이지에 접속할 때
**When** AI 운세 통계 섹션이 로드되면
**Then** 다음 핵심 지표 카드가 표시된다:
  - 오늘 운세 요청 수
  - 이번 주 순 이용자 수
  - 캐시 히트율 (%)
  - 평균 응답 시간 (ms)

**Given** 통계 차트가 표시될 때
**When** 대시보드가 로드되면
**Then** 최근 30일 일별 요청 추이 라인 차트가 표시된다
**And** 운세 유형별(일/주/월/연) 분포 파이 차트가 표시된다

**Given** 기간 필터를 변경할 때
**When** "최근 7일", "최근 30일", "최근 90일" 중 선택하면
**Then** 차트와 지표가 해당 기간으로 업데이트된다
**And** 로딩 인디케이터가 표시된다

**Given** 통계 데이터가 없을 때
**When** 선택 기간에 데이터가 없으면
**Then** "해당 기간에 데이터가 없습니다" 메시지가 표시된다
**And** 빈 차트 대신 안내 UI가 표시된다

**Given** 통계 로딩 중일 때
**When** API 호출이 진행 중이면
**Then** 스켈레톤 UI가 표시된다
**And** 차트 영역에 로딩 애니메이션이 표시된다

**Given** 반응형 레이아웃에서
**When** 태블릿/모바일로 접근하면
**Then** 카드와 차트가 세로로 재배치된다
**And** 터치로 차트 인터랙션이 가능하다

**기술 참조:**
- `admin-front/src/views/dashboard/FortuneStatistics.vue`
- 차트 라이브러리: Chart.js 또는 ApexCharts
- 기존 대시보드 디자인 패턴 준수
