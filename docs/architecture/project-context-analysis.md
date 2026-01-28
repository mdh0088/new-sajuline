# Project Context Analysis

### Requirements Overview

**Functional Requirements:**

52개 FR이 7개 capability 영역에 걸쳐 정의됨:

| 영역 | FR 수 | 아키텍처 영향 |
|------|-------|--------------|
| 사용자 계정 (FR1-9) | 9 | 인증/인가, OAuth, 본인인증 연동 |
| AI 운세 (FR10-16) | 7 | OpenAI API 통합, 캐싱 전략 |
| 상담 서비스 (FR17-25) | 9 | WebSocket 실시간 통신, 상태 관리 |
| 결제/포인트 (FR26-33) | 8 | PG 연동, 트랜잭션 정합성 |
| 콘텐츠/공지 (FR34-38) | 5 | CMS, SSR/SEO |
| 알림 (FR39-42) | 4 | 비동기 메시징, 푸시 |
| 관리자 (FR43-52) | 10 | 별도 관리자 시스템, 대시보드 |

**아키텍처 핵심 이슈:**
- AI 운세 서비스: OpenAI API 의존성, 3초 SLA, 24시간 캐싱
- 실시간 채팅: Socket.IO, 연결 상태 관리, 메시지 암호화
- 하이브리드 렌더링: SSR(SEO) + CSR(인터랙션) 전략

**Non-Functional Requirements:**

35+ NFR이 다음 품질 속성을 정의:

| 품질 속성 | 주요 요구사항 |
|----------|--------------|
| Performance | API p95 < 300ms, AI < 3s, 채팅 RTT < 200ms, LCP < 2.5s |
| Security | HTTPS, JWT (15m/7d), 암호화 저장, Rate Limiting |
| Scalability | 1인 개발자 운영, 수평 확장 고려 |
| Reliability | 99%+ 가용성, 에러 핸들링, 폴백 |
| Accessibility | WCAG 2.1 AA, 모바일 우선 |
| Integration | OpenAI, Payletter, KCP, OAuth, MSSQL(읽기전용) |
| Monitoring | Sentry, 구조화 로깅, 대시보드 |

**Scale & Complexity:**

- Primary domain: Full-Stack Web Application (SaaS)
- Complexity level: Medium
- Project context: Brownfield (기존 시스템 현대화)
- Estimated architectural components: 8-10

### Technical Constraints & Dependencies

**필수 기술 제약:**
- Nuxt 4 (SSR/CSR 하이브리드) - 이미 선택됨
- FastAPI + Python 3.11 - 이미 선택됨
- MariaDB 10.6 + Redis 7 - 이미 운영 중
- MSSQL 2005 (레거시 ARS) - 읽기 전용 연동

**외부 서비스 의존성:**
| 서비스 | 용도 | 장애 영향 |
|--------|------|----------|
| OpenAI API | AI 운세 | 핵심 기능 불가 |
| Payletter | 결제 | 충전 불가 |
| KCP | 본인인증 | 가입 불가 |
| Kakao/Naver | 소셜 로그인 | 해당 로그인 불가 |
| AWS S3 | 파일 저장 | 이미지 업로드 불가 |

**인프라 제약:**
- 1인 개발자 운영 → 복잡도 최소화 필수
- AWS 기반 인프라 (EC2, CloudFront, S3)
- PM2 프로세스 관리

### Cross-Cutting Concerns Identified

**아키텍처 전반에 영향을 미치는 관심사:**

1. **인증/인가**: 모든 API, 프론트엔드에 적용
2. **에러 핸들링**: Sentry 통합, 사용자 친화적 메시지
3. **로깅/모니터링**: 구조화 JSON, 요청 ID 추적
4. **보안**: HTTPS, CORS, Rate Limiting, 암호화
5. **캐싱**: Redis (운세 24h, 세션), CDN (정적)
6. **성능**: 번들 최적화, 이미지 최적화, 지연 로딩

---
