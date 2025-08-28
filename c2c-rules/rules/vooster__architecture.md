# Technical Requirements Document (TRD)

## 1. Executive Technical Summary
- 프로젝트 개요: Nuxt 3.18 기반 SSR 프론트엔드와 FastAPI 백엔드로 구성된 단일 단순 아키텍처. Docker Compose로 개발/스테이징/초기 운영을 일원화. MariaDB를 주 데이터 저장소로, 외부 연동용 MSSQL 2005 읽기/동기화, Redis 캐시/세션, Socket.IO 기반 실시간 상담, OpenAI GPT-4 계열 API 연동을 최소 구성으로 구현.
- 코어 기술 스택: Nuxt 3.18 + TypeScript + TailwindCSS, FastAPI(Python 3.11) + SQLAlchemy 2 + Redis 7 + MariaDB 10.6, python-socketio, OpenAI API, Payletter, KCP 본인확인, Kakao/Naver OAuth, AWS S3, Sentry, GA4.
- 핵심 기술 목표:
  - 성능: AI 응답 3초 이내, p95 API 300ms 이내, 실시간 채팅 왕복 200ms 이내, LCP 2.5s 이하.
  - 확장성: 단일 노드 기준으로 시작, Redis 준비를 통한 수평 확장 가능성 확보.
  - 신뢰성: 가용률 99.9%, 결제/포인트 정합성 보장(이중 장부), 채팅 로그 내구적 보관.
- 주요 기술 가정:
  - 초기 배포는 Docker Compose 단일 VM 또는 소규모 서버로 운영.
  - MSSQL 2005는 읽기 중심(참조/동기화)으로 사용, 핵심 트랜잭션은 MariaDB 일원화.
  - AES-256-GCM으로 민감 데이터 애플리케이션 계층 암호화, 비밀번호는 Argon2id 해시.
  - 소셜 로그인은 Kakao/Naver만 MVP 범위, Google은 이후 단계.

## 2. Tech Stack

| Category | Technology / Library | Reasoning (Why it's chosen for this project) |
| --- | --- | --- |
| 프론트엔드 프레임워크 | Nuxt 3.18 (Vue 3) | SSR/SEO, 모바일 퍼스트, 라우팅/상태/번들 최적화 기본 제공 |
| 언어/타입 | TypeScript 5.4 | 안정성/유지보수성 향상 |
| 스타일 | Tailwind CSS 3.4 | 일관된 디자인 시스템, 개발 속도 |
| 상태 관리 | Pinia | 가벼운 상태 관리, Nuxt 통합 용이 |
| API 통신 | Axios | 직관적 HTTP 클라이언트, 인터셉터로 토큰/에러 처리 용이 |
| 실시간 클라이언트 | socket.io-client | Socket.IO 서버와 호환, 자동 재연결 |
| 백엔드 프레임워크 | FastAPI 0.115 | 비동기/성능, 타입 기반 검증, 문서화 자동화 |
| 런타임/서버 | Python 3.11, Uvicorn | 최신 성능/호환성, ASGI 서버 |
| 실시간 서버 | python-socketio 5.x | FastAPI와 통합, 실시간 채팅 구현 |
| 데이터베이스 | MariaDB 10.6 LTS | 주 데이터 저장소, 비용/성능/호환성 |
| ORM/마이그레이션 | SQLAlchemy 2.x, Alembic | 타입 안전 ORM, 스키마 버전 관리 |
| 외부 DB 연동 | MSSQL 2005 + pyodbc + FreeTDS | 레거시 SQL Server 2005 호환 확보 |
| 캐시/세션 | Redis 7.x, redis-py | 세션/캐시/속도, Pub/Sub 확장 발판 |
| 인증/암호화 | python-jose, argon2-cffi, cryptography | JWT 발급/검증, 안전한 패스워드, AES-256-GCM 구현 |
| 소셜 로그인 | Kakao OAuth, Naver OAuth (Authlib) | 국내 표준 소셜 로그인 지원 |
| 결제/본인확인 | Payletter REST API, KCP 본인확인 | 포인트 결제/충전, 휴대폰 본인확인 |
| 파일 스토리지 | AWS S3 + boto3 | 프로필/채팅 파일 저장, 확장성 |
| AI 연동 | OpenAI API (gpt-4o-mini, fallback gpt-4-turbo) | 3초 SLA 충족, 비용/성능 균형 |
| 모니터링/분석 | Sentry, Google Analytics 4 | 오류 추적/사용자 분석 |
| 리버스 프록시 | Nginx (선택) | 정적 자산/업로드, 프록시, SSL 종단 (운영 시) |
| 컨테이너 | Docker, docker-compose v2 | 환경 일원화, 초기 운영 단순화 |
| 테스트 | Pytest, Vitest | 백/프론트 단위 테스트 최소 구성 |

## 3. System Architecture Design

### Top-Level building blocks
- 프론트엔드 웹앱
  - Nuxt 3 SSR/CSR 하이브리드
  - 인증/상태 핸들링(Pinia), SEO/LCP 최적화
- 백엔드 API
  - FastAPI RESTful 엔드포인트
  - 도메인 서비스/리포지토리/스키마 계층화
  - AES-256-GCM 암호화, JWT 인증
- 실시간 채팅 서비스
  - python-socketio ASGI 애플리케이션
  - 메시지 영속화(MariaDB), 첨부파일 S3
- 데이터 계층
  - MariaDB: 사용자/상담/결제/포인트/후기/커뮤니티/로그
  - Redis: 세션/캐시/레이트 리밋/임시 토큰
  - MSSQL 2005: 외부 상담사/포인트 참조(읽기/주기 동기화)
- 외부 연동
  - OpenAI API, Kakao/Naver OAuth, Payletter, KCP 본인확인, AWS S3
- 관측/운영
  - Sentry, GA4, 구조화 로그, 헬스체크, Docker Compose 오케스트레이션

### Top-Level Component Interaction Diagram
```mermaid
graph TD
    U[User (Web/Mobile Web)] --> FE[Nuxt 3 (SSR/CSR)]
    FE -->|REST/JSON| BE[FastAPI (API)]
    FE -->|Socket.IO| RT[FastAPI + Socket.IO]
    BE --> MDB[MariaDB]
    BE --> RDS[Redis]
    BE --> S3[(AWS S3)]
    BE --> OAI[OpenAI API]
    BE --> KAKAO[Kakao OAuth]
    BE --> NAVER[Naver OAuth]
    BE --> KCP[KCP Identity]
    BE --> PAY[Payletter]
    BE --> MSSQL[MSSQL 2005 (External)]
```

- 사용자는 Nuxt 프론트엔드에 접속하며 SSR로 초기 렌더링 후 CSR 전환.
- 프론트엔드는 REST로 FastAPI와 통신, 실시간 기능은 Socket.IO로 별도 네임스페이스와 연결.
- 백엔드는 MariaDB/Redis/S3와 상호작용하며 외부 서비스(OAuth/AI/본인확인/결제/MSSQL)와 통합.
- MSSQL 2005는 읽기/동기화 전용으로 주기적으로 MariaDB에 반영.

### Code Organization & Convention
도메인 중심 조직 전략
- 도메인 분리: auth, user, counselor, matching, reservation, chat, payment, points, review, community, support, notification 등으로 경계 설정
- 계층화 아키텍처: api(프리젠테이션)/service(도메인 로직)/repository(영속)/infrastructure(클라이언트/암호화/외부)/schemas(dto)/models(orm)
- 기능 모듈화: 각 도메인별 라우팅/서비스/리포지토리/스키마를 한 모듈로 응집
- 공용 컴포넌트: 공용 유틸, 보안, 설정, 예외, 미들웨어를 shared/infra로 집약

범용 파일/폴더 구조 (단일 레포 별도 운영, 모노레포 사용하지 않음)
```
/frontend
├── .env.development
├── .env.production
├── nuxt.config.ts
├── package.json
├── src/
│   ├── assets/
│   ├── components/
│   ├── composables/
│   ├── pages/
│   ├── layouts/
│   ├── store/            # Pinia stores (auth, user, points, chat)
│   ├── services/         # api clients (axios), socket client
│   ├── utils/
│   ├── middleware/
│   └── styles/
└── tests/                 # unit/e2e (선택)

/backend
├── .env.development
├── .env.production
├── docker/
│   └── freeTDS/          # MSSQL 2005용 FreeTDS 설정
├── alembic/
├── app/
│   ├── api/              # routers by domain
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── counselors.py
│   │   │   ├── reservations.py
│   │   │   ├── chat.py
│   │   │   ├── payments.py
│   │   │   ├── points.py
│   │   │   ├── reviews.py
│   │   │   ├── community.py
│   │   │   ├── support.py
│   │   │   └── admin.py
│   ├── core/             # config, security, crypto, logging, errors
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic DTOs
│   ├── services/         # domain services
│   ├── repositories/     # db access layer
│   ├── infrastructure/   # clients: openai, s3, payletter, kcp, oauth, mssql
│   ├── workers/          # schedulers (APScheduler), background tasks
│   ├── socket/           # socket.io namespaces, event handlers
│   └── main.py           # FastAPI app factory
├── tests/
└── docker-compose.yml     # 개발/스테이징용 (최상위 운영 별도 가능)
```

### Data Flow & Communication Patterns
- 클라이언트-서버 통신
  - REST/JSON, 표준 HTTP 상태코드, 에러 포맷 통일
  - SSR 초기 데이터 프리패치, 이후 CSR로 증분 갱신
  - 인증: HttpOnly 쿠키 기반 JWT(access 짧게, refresh 길게), CSRF 토큰 더블 서브밋
- 데이터베이스 상호작용
  - SQLAlchemy 2.0 ORM + 명시적 세션 범위(요청 단위)
  - 읽기/쓰기 분리는 MVP에서 단일 인스턴스, 인덱스 최적화로 대응
  - Alembic 마이그레이션으로 스키마 버전 관리
- 외부 서비스 통합
  - OpenAI/Payletter/KCP/OAuth는 백엔드에서 서버-투-서버 통신
  - 웹훅(Payletter): 서명 검증, 멱등키 처리(요청 ID 기반)
- 실시간 통신
  - Socket.IO 네임스페이스: /chat
  - JWT 검증으로 연결 인증, Redis 세션 조회
  - 자동 재연결, 오프라인 시 서버 큐 없음(단, 수신 누락 방지 위해 입장 시 최근 N개 히스토리 재전송)
- 데이터 동기화
  - MSSQL 2005 동기화: APScheduler로 주기적 읽기(예: 5분), 변경분 upsert
  - 포인트 연동: 기준 저장소는 MariaDB, 외부 포인트는 매핑/정산 규칙에 따라 배치 동기화
  - 캐시 일관성: 쓰기 시 캐시 무효화 키 전략(user:{id}:dashboard, ai:daily:{user}:{date})

## 4. Performance & Optimization Strategy
- 캐싱 우선 전략: AI 운세(일/주/월)와 상담사 리스트/프로필을 Redis로 캐시(TTL 기반), 사용자별 대시보드 캐시.
- 데이터베이스 최적화: 핵심 쿼리 인덱스(user_id, counselor_id, created_at, status), 채팅 메시지 파티셔닝(월 단위 테이블 또는 인덱스 프리픽스) 고려.
- 프론트엔드 성능: Nuxt ISR/SPA 하이드레이션 최적화, 이미지 lazyload/S3+CDN, Tailwind JIT, 라우트 기반 코드 스플리팅.
- 서버 성능: Uvicorn workers 튜닝, keep-alive, GZip/Brotli, Socket.IO 전송 압축, 백그라운드 작업 오프로딩.

## 5. Implementation Roadmap & Milestones
### Phase 1: Foundation (MVP Implementation)
- 코어 인프라: Docker Compose(backend, frontend, mariadb, redis, nginx(optional)), 환경변수 .env.* 분리, 베이스 CI(빌드/테스트).
- 필수 기능: 이메일+비밀번호 가입/로그인, KCP 본인확인(휴대폰), Kakao/Naver 로그인, 포인트 충전(Payletter 기본 결제/웹훅), 반응형 UI, AI 운세 기본(일일), 게스트 1회 체험.
- 기본 보안: JWT 쿠키, Argon2id, AES-256-GCM PII 암호화, 레이트 리밋, CORS/CSRF.
- 개발 환경: API 문서(Swagger), DB 마이그레이션, 시드 데이터, Sentry/GA4 설정.
- 타임라인: 4주.

### Phase 2: Feature Enhancement
- 고도 기능: 상담사 등록/프로필/검색/필터, 예약/캘린더, 후기/평점, 포인트 적립/선물, 커뮤니티 Q&A/공지.
- 성능 최적화: 인덱스 튜닝, 캐시 히트율 개선, SSR 프리패치 최적화.
- 보안 강화: 관리자 RBAC, 감사 로그, 비정상 로그인 탐지.
- 모니터링: SLO 대시보드(간단 메트릭), 업타임 모니터, 알림.
- 타임라인: 8주.

### Phase 3: Scaling & Optimization
- 확장성: 채팅 Socket.IO 수평 확장 대비(Sticky session, Redis Adapter 도입 준비), 파일 업로드 프록시 최적화.
- 고급 연동: AI 상세 리포트(주/월), 개인화 추천(간단 규칙+행동 로그), MSSQL 동기화 안정화.
- 엔터프라이즈: 정산 리포트, BI 기초 데이터 파이프라인(Export).
- 컴플라이언스: 개인정보 파기/익명화, 키 로테이션 절차 수립.
- 타임라인: 4주.

### Phase 4: Scale & Optimize
- 성능: p95 300ms 유지, 워커 증설 가이드, 캐시 미스 최적화.
- 보안: 침투 테스트 대응, 비밀 관리 개선(별도 보안 저장소 도입 고려).
- 분석: 리텐션 퍼널/전환 추적 고도화, 마케팅 자동화 훅.
- 타임라인: 8주.

## 6. Risk Assessment & Mitigation Strategies
### Technical Risk Analysis
- 기술 리스크: MSSQL 2005 드라이버 호환성
  - 대응: FreeTDS + pyodbc 검증, 연결 풀 타임아웃/재시도, 읽기 전용 설계.
- 성능 리스크: AI 응답 지연
  - 대응: 프롬프트 경량화, 결과 캐싱, 모델 선택(gpt-4o-mini), 타임아웃/폴백.
- 보안 리스크: JWT 탈취/CSRF
  - 대응: HttpOnly/SameSite/Lax, CSRF 토큰, 짧은 access + 롤링 refresh, 디바이스 바인딩.
- 통합 리스크: 결제 웹훅 멱등성
  - 대응: 이벤트 ID 기반 멱등 처리, 서명 검증, 재시도 안전 설계.
- 채팅 안정성: WebSocket 끊김
  - 대응: Socket.IO 자동 재연결, 백오프, 메시지 저장 후 재입장 히스토리 제공.

### Project Delivery Risks
- 일정 리스크: 외부 연동 승인 지연(KCP/Payletter)
  - 대응: 샌드박스 먼저 통합, 기능 토글로 단계적 오픈.
- 리소스 리스크: AI 프롬프트/도메인 룰 설계 역량
  - 대응: 초기 템플릿/가드레일 확보, 사용자 피드백 루프 짧게 운영.
- 품질 리스크: 테스트 커버리지 부족
  - 대응: 핵심 경로(E2E 결제/로그인/채팅/AI) 우선 테스트.
- 배포 리스크: 단일 노드 장애
  - 대응: 일일 스냅샷 백업, 장애 복구 런북, 예비 인스턴스 이미지.

---

## Technical Documentation Guidelines

### 기술 버전 및 호환성
- Node.js 20 LTS / Nuxt 3.18 / TypeScript 5.4 / Tailwind 3.4 / Pinia 최신
- Python 3.11 / FastAPI 0.115 / Uvicorn 0.30 / Pydantic v2
- SQLAlchemy 2.0.x / Alembic 1.13
- MariaDB 10.6+ / Redis 7.x
- pyodbc 5.x + FreeTDS(프로토콜 TDS 7.1) for SQL Server 2005
- python-socketio 5.x / socket.io-client 4.x
- cryptography 42+ (AES-256-GCM), argon2-cffi 최신, python-jose 3.3
- boto3 최신, openai 1.x, Authlib 1.x

### 아키텍처 패턴과 구현 세부
- 패턴: Layered + RESTful
- 경계:
  - API 레이어: 요청 검증(Pydantic), 인증/인가, DTO 변환
  - 서비스 레이어: 트랜잭션 경계, 도메인 규칙(포인트 차감/적립, 예약 상태 전이)
  - 리포지토리: ORM 쿼리, N+1 방지(선택적 eager load)
  - 인프라: 외부 API 클라이언트, 암호화/서명, 스토리지
- 트랜잭션: 포인트/결제/예약은 단일 트랜잭션, 이벤트 로그 테이블로 감사 가능성 확보

### 데이터베이스 스키마 설계 원칙
- 정규화: 3NF 준수, 고정 사전 테이블 분리(상담 카테고리/스타일 등)
- 주요 테이블(예시):
  - users(id, email unique, phone enc, password_hash, social_links, preferences enc, created_at)
  - counselors(id, profile, skills, rating_agg, status)
  - reservations(id, user_id, counselor_id, schedule_ts, status, price_per_min, created_at)
  - chats(id, session_id, sender_type, message enc, attachments, created_at, indexes: session_id+created_at)
  - chat_sessions(id, reservation_id, started_at, ended_at, duration_sec, cost_points)
  - payments(id, user_id, method, amount, status, provider_ref, created_at)
  - points_ledger(id, user_id, delta, reason, ref_type, ref_id, balance_snapshot, created_at)
  - reviews(id, reservation_id, rating, comment, created_at)
  - community_posts(id, user_id, type, title, content, created_at)
  - notifications(id, user_id, type, payload, read_at)
- 인덱스: FK, created_at, 상태 컬럼(status), 복합 인덱스(user_id, created_at)
- 파티셔닝 고려: chats/chats_sessions 월 단위 또는 보관 정책(예: 1년)
- 무결성: FK/체크 제약, ledger 멱등 제약(unique(provider_ref))

### 성능 지표 및 SLA
- API p95 300ms 이하, 채팅 RTT 200ms 이하(국내), AI 응답 3s 이하
- 가용성 99.9%, 오류율 0.1% 이하
- LCP 2.5s 이하, CLS 0.1 이하, TBT 200ms 이하

### 보안 구현 상세 및 컴플라이언스
- 인증
  - 로그인: 일반(아이디/비밀번호), 소셜(Kakao/Naver), KCP 본인확인 연동
  - 토큰: JWT RS256, access(15m), refresh(14d) 롤링, Redis 토큰 블랙리스트/세션 저장
  - 쿠키: HttpOnly, Secure, SameSite=Lax, CSRF 토큰(쿠키+헤더)
- 비밀번호/데이터 보호
  - 비밀번호: Argon2id(메모리/시간 파라미터 정책)
  - 데이터 암호화: AES-256-GCM(cryptography), 키는 환경변수(AES_MASTER_KEY)에서 로드, 키 ID/버전 관리, 주기적 로테이션 계획
  - 전송 구간: TLS 1.2+
- 접근 제어
  - RBAC(사용자/상담사/관리자), 관리자 전용 엔드포인트 보호
  - 레이트 리밋: 로그인/AI/결제 엔드포인트 중심(버킷 토큰 in Redis)
- 저장소 보안
  - S3: 프라이빗 버킷 + 프리사인드 URL, 서버사이드 암호화(SSE-S3)
- 감사/로그
  - 결제/포인트/예약 상태 변경 감사 로그
  - PII 마스킹 로깅, Sentry 샘플링
- 규정 준수
  - 개인정보 최소 수집/보관기간, 파기/익명화 배치
  - 면책/이용약관/환불정책 반영

### 모니터링 및 관측
- Sentry: 백/프론트 릴리즈 트래킹, 성능 이벤트, 사용자 세션
- GA4: 퍼널/전환/리텐션, 캠페인 파라미터
- 헬스체크: /healthz(liveness), /readyz(readiness)
- 로그: JSON 구조화, 요청 ID 상관관계, 웹훅/결제 별도 채널
- 가벼운 가용성 모니터: 외부 핑 서비스(UptimeRobot 등)

### 도메인 경계 정의(요약)
- Auth/Identity: 계정/소셜/KCP/세션/권한
- User Profile: 선호 설정/푸시 설정/개인화
- Counselor: 등록/승인/프로필/가용시간
- Matching: 추천/검색/랭킹
- Reservation: 예약/변경/취소/알림
- Chat: 세션/메시지/평가/재상담
- Points/Payment: 충전/차감/적립/선물/환불/정산
- Community: 후기/Q&A/공지/신고
- AI: 운세 분석/리포트/히스토리 캐싱
- Integration: MSSQL 동기화/Payletter/KCP/OAuth/S3/OpenAI

### 구현 가이드 및 베스트 프랙티스
- API 계약: OpenAPI 스펙 자동 생성/검증, 에러 코드 사전 정의
- 멱등성: 결제/포인트/웹훅에 멱등키 적용
- 타임존: 서버 UTC, 표시 KST, DB 타임스탬프 UTC
- 국제화: i18n 준비(프론트), 다국어 문구 분리
- 업로드: S3 프리사인드 URL 직접 업로드, 서버는 메타만 저장

### 배포/운영
- Docker Compose 서비스
  - frontend: Nuxt SSR
  - backend: FastAPI + Socket.IO
  - mariadb: 10.6
  - redis: 7
  - nginx: reverse proxy(선택), SSL 종단(운영)
- 환경변수 관리
  - 각각 디렉터리 하위 .env.development / .env.production
  - Docker는 파일 마운트로 전달(컨테이너 환경변수 직접 사용하지 않음)
- 백업
  - MariaDB 일일 덤프, S3 저장, 7/30/90 보관 정책
  - S3 버전닝/라이프사이클

### 테스트 전략
- 단위: 서비스/리포지토리/스키마 유효성(Pytest)
- 통합: OAuth/결제/웹훅 샌드박스
- E2E(선택): 핵심 플로우(가입→본인확인→충전→예약→채팅→평가)
- 부하(경량): 채팅/AI 엔드포인트 p95 확인

### 구체 성능 최적화 포인트
- AI 프롬프트 최소화, 스트리밍 응답(필요시)
- Socket.IO 압축/하트비트 주기 튜닝
- 데이터 액세스 패턴 캐시 앞단 최적화(대시보드/프로필)
- 이미지 썸네일/리사이즈 후 업로드

### 외부 연동 세부
- Kakao/Naver OAuth: 백엔드 리다이렉트 처리, 프론트는 단순 링크
- KCP 본인확인: 결과 검증 해시 검증, 검증 토큰 단발성 저장(짧은 TTL)
- Payletter: 결제 생성→리다이렉트→웹훅 승인, 포인트 적립은 웹훅 확인 후 처리, 환불 역거래 API
- OpenAI: 모델 gpt-4o-mini 기본, 타임아웃 2.5s, 실패 시 폴백 모델/재시도(지수 백오프)

### 실시간 채팅 설계
- 인증: 연결 시 JWT 검사, 예약/세션 권한 확인
- 메시지: MariaDB 영속화(텍스트 AES-256-GCM), S3 첨부, 전송 영수증 ACK
- 과금: 세션 종료 시 duration 기반 포인트 차감, 중간 하트비트로 안착
- 확장: 추후 Redis Adapter 도입 시 수평 확장 용이

### 데이터 보존/정책
- 채팅 로그: 최소 1년(암호화 저장)
- 결제/장부: 회계 기준에 따른 보존(예: 5년 이상)
- PII: 목적 달성 후 즉시 파기/익명화

### 구체적인 KPI 매핑
- DAU/MAU/리텐션: GA4+서버 이벤트
- 전환율/ARPU: 결제/장부 데이터 집계
- 상담 완료율/응답시간: 채팅 세션 메트릭
- AI 만족도/이용률: 평가/클릭/세션 로그

### 확장 로드맵 고려사항(과도 설계 지양)
- 초기에는 단일 노드/단일 DB
- 트래픽 증가 시: DB 리드 레플리카, Socket.IO Redis Adapter, 파일 CDN
- ECS/Fargate 전환은 Compose 안정화 후 단계적 고려

끝.