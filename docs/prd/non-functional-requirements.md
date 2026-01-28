# Non-Functional Requirements

### Performance

**응답 시간 요구사항:**

| 구분 | 목표 | 측정 방법 |
|------|------|-----------|
| NFR-P1: API 응답시간 | p95 < 300ms | 서버 모니터링 |
| NFR-P2: AI 운세 응답 | < 3초 | OpenAI API 응답 추적 |
| NFR-P3: 채팅 메시지 RTT | < 200ms | WebSocket 모니터링 |
| NFR-P4: 페이지 초기 로드 | LCP < 2.5초 | Core Web Vitals |
| NFR-P5: 인터랙티브 시간 | TTI < 3.5초 | Lighthouse |

**리소스 요구사항:**
- NFR-P6: 초기 JS 번들 < 200KB (gzipped)
- NFR-P7: 전체 페이지 < 1MB
- NFR-P8: CLS (Cumulative Layout Shift) < 0.1

### Security

**데이터 보호:**
- NFR-S1: 모든 통신은 HTTPS(TLS 1.2+)로 암호화되어야 한다
- NFR-S2: 비밀번호는 Argon2id 알고리즘으로 해싱되어야 한다
- NFR-S3: 채팅 메시지는 AES-256-GCM으로 암호화 저장되어야 한다
- NFR-S4: 개인정보(사주 정보)는 암호화되어 저장되어야 한다

**인증 및 권한:**
- NFR-S5: JWT 토큰 만료 시간은 Access 15분, Refresh 7일이어야 한다
- NFR-S6: 인증 토큰은 HttpOnly 쿠키로 저장되어야 한다
- NFR-S7: CSRF 토큰으로 상태 변경 요청을 보호해야 한다

**API 보안:**
- NFR-S8: Rate Limiting이 적용되어야 한다 (100 req/min per IP)
- NFR-S9: CORS 정책이 허용된 도메인만 접근 가능해야 한다
- NFR-S10: SQL Injection, XSS 공격에 대한 방어가 적용되어야 한다

**결제 보안:**
- NFR-S11: 결제 정보는 PG사를 통해 처리되며 서버에 저장하지 않는다
- NFR-S12: 결제 웹훅은 서명 검증을 통해 인증되어야 한다

### Scalability

**용량 요구사항:**
- NFR-SC1: 동시 접속 사용자 500명을 지원해야 한다 (MVP 기준)
- NFR-SC2: 일일 AI 운세 요청 10,000건을 처리할 수 있어야 한다
- NFR-SC3: 동시 채팅 세션 100개를 지원해야 한다

**확장성 설계:**
- NFR-SC4: 수평 확장이 가능한 Stateless 아키텍처를 유지해야 한다
- NFR-SC5: 세션 데이터는 Redis에 저장하여 서버 간 공유되어야 한다
- NFR-SC6: 데이터베이스 연결 풀링을 사용해야 한다

### Reliability

**가용성:**
- NFR-R1: 서비스 가용성 99% 이상을 유지해야 한다
- NFR-R2: 계획된 유지보수는 사전 공지 후 진행해야 한다

**장애 복구:**
- NFR-R3: AI API 장애 시 캐시된 결과 또는 에러 메시지를 표시해야 한다
- NFR-R4: WebSocket 연결 끊김 시 자동 재연결되어야 한다 (exponential backoff)
- NFR-R5: 결제 실패 시 포인트 이중 차감이 발생하지 않아야 한다

**데이터 무결성:**
- NFR-R6: 포인트 거래는 트랜잭션으로 원자성을 보장해야 한다
- NFR-R7: 데이터베이스 백업을 일 1회 이상 수행해야 한다

### Accessibility

**WCAG 2.1 AA 준수:**
- NFR-A1: 텍스트와 배경의 명암비는 4.5:1 이상이어야 한다
- NFR-A2: 모든 인터랙티브 요소는 키보드로 접근 가능해야 한다
- NFR-A3: 포커스 표시자가 명확하게 보여야 한다
- NFR-A4: 폼 요소는 연결된 레이블이 있어야 한다
- NFR-A5: 이미지는 대체 텍스트를 제공해야 한다

**모바일 접근성:**
- NFR-A6: 터치 타겟 크기는 최소 44px × 44px이어야 한다
- NFR-A7: 200% 확대 시에도 레이아웃이 유지되어야 한다

### Integration

**외부 시스템 연동:**

| 연동 대상 | 요구사항 |
|-----------|----------|
| NFR-I1: OpenAI API | 타임아웃 10초, 실패 시 재시도 1회 |
| NFR-I2: Payletter (PG) | 웹훅 수신 후 5초 이내 응답 |
| NFR-I3: KCP (본인인증) | 인증 완료 결과 실시간 처리 |
| NFR-I4: Kakao/Naver OAuth | 토큰 만료 시 자동 갱신 |
| NFR-I5: MSSQL (ARS) | 읽기 전용 연결, 타임아웃 5초 |

**API 호환성:**
- NFR-I6: REST API는 JSON 형식을 사용해야 한다
- NFR-I7: API 버저닝(/api/v1/)을 지원해야 한다
- NFR-I8: 에러 응답은 일관된 형식을 따라야 한다

### Monitoring & Observability

**로깅:**
- NFR-M1: 모든 API 요청/응답은 구조화된 JSON 로그로 기록되어야 한다
- NFR-M2: 로그에는 요청 ID가 포함되어 추적 가능해야 한다
- NFR-M3: 민감 정보(비밀번호, 토큰)는 로그에 기록하지 않아야 한다

**모니터링:**
- NFR-M4: Sentry를 통해 에러가 실시간으로 수집되어야 한다
- NFR-M5: 핵심 지표(응답시간, 에러율)는 대시보드에서 확인 가능해야 한다

---
