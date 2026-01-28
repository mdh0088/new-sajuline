# Core Architectural Decisions

### Decision Priority Analysis

**이미 결정됨 (Brownfield):**
- Database: MariaDB 10.6 + Redis 7.0
- Authentication: JWT + OAuth (Kakao/Naver)
- Frontend: Nuxt 4 + Vue 3 + Tailwind
- Backend: FastAPI + Python 3.11
- Infrastructure: AWS EC2 + S3 + CloudFront

**MVP 신규 결정 (AI 운세 서비스):**
- AI API 통합 전략
- 운세 캐싱 정책
- 에러 핸들링 전략
- 데이터 모델 설계

### Data Architecture

**Database (기존):**
- Primary: MariaDB 10.6 (ACID 트랜잭션)
- Cache: Redis 7.0 (세션, 캐시, Pub/Sub)
- Legacy: MSSQL 2005 (읽기 전용, ARS)

**AI 운세 캐싱 전략:**
| 운세 유형 | 캐시 키 | TTL | 근거 |
|----------|--------|-----|------|
| 일일 운세 | `fortune:daily:{user_id}:{date}` | 24시간 | 하루 1회 갱신 |
| 주간 운세 | `fortune:weekly:{user_id}:{week}` | 7일 | 주 1회 갱신 |
| 월간 운세 | `fortune:monthly:{user_id}:{month}` | 30일 | 월 1회 갱신 |
| 연간 운세 | `fortune:yearly:{user_id}:{year}` | 365일 | 연 1회 갱신 |

**운세 데이터 모델:**
```sql
CREATE TABLE fortune_histories (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    fortune_type ENUM('daily', 'weekly', 'monthly', 'yearly'),
    target_date DATE NOT NULL,
    content TEXT NOT NULL,
    ai_model VARCHAR(50),
    prompt_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_type_date (user_id, fortune_type, target_date)
);
```

### Authentication & Security

**인증 전략 (기존):**
- JWT: Access Token (15분) + Refresh Token (7일)
- OAuth 2.0: Kakao, Naver
- 본인인증: KCP 휴대폰 인증

**보안 결정:**
| 항목 | 결정 | 근거 |
|------|------|------|
| 토큰 저장 | HttpOnly Cookie | XSS 방어 |
| 비밀번호 | Argon2id | 최신 해싱 알고리즘 |
| 채팅 암호화 | AES-256-GCM | PII 보호 |
| API 보안 | Rate Limiting (100/min/IP) | DDoS 방어 |

### API & Communication

**REST API 설계:**
- Base URL: `/api/v1/`
- 버저닝: URL Path 방식
- 응답 형식: JSON
- 에러 형식: `{code, message, details}`

**AI 운세 API:**
```
GET  /api/v1/fortune/daily     # 일일 운세 조회
GET  /api/v1/fortune/weekly    # 주간 운세 조회
GET  /api/v1/fortune/monthly   # 월간 운세 조회
GET  /api/v1/fortune/yearly    # 연간 운세 조회
```

**OpenAI 연동 전략:**
| 항목 | 결정 | 근거 |
|------|------|------|
| Model | GPT-4o-mini | 비용 효율 + 품질 균형 |
| Timeout | 10초 | 3초 SLA + 버퍼 |
| Retry | 1회 (exponential backoff) | 장애 대응 |
| Fallback | 캐시된 이전 응답 또는 기본 메시지 | 가용성 확보 |

**에러 핸들링:**
```python
# OpenAI 에러 처리 전략
if openai_timeout:
    return cached_fortune or default_message
if openai_error:
    log_to_sentry()
    return cached_fortune or default_message
if rate_limited:
    return cached_fortune or retry_after_delay()
```

### Frontend Architecture

**렌더링 전략:**
| 페이지 | 렌더링 | 근거 |
|--------|--------|------|
| 메인, 상담사 목록 | SSR | SEO |
| 운세 페이지 | CSR | 동적 데이터 |
| 마이페이지, 채팅 | CSR | 인터랙션 |

**상태 관리:**
- Pinia: 클라이언트 상태 (auth, UI)
- TanStack Query: 서버 상태 (API 캐싱)
- Socket.IO: 실시간 상태 (채팅)

**운세 UI 컴포넌트:**
```
pages/fortune/
├── index.vue           # 탭 컨테이너
├── components/
│   ├── FortuneTabs.vue    # 일/주/월/연 탭
│   ├── FortuneCard.vue    # 운세 결과 카드
│   ├── FortuneLoading.vue # 로딩 스켈레톤
│   └── FortuneError.vue   # 에러 상태
└── composables/
    └── useFortune.ts      # 운세 API 훅
```

### Infrastructure & Deployment

**배포 전략 (기존):**
- CI/CD: GitHub Actions + Self-hosted Runner
- 프로세스: PM2 클러스터 모드
- 웹서버: Nginx 리버스 프록시

**모니터링:**
| 도구 | 용도 |
|------|------|
| Sentry | 에러 추적, 성능 모니터링 |
| PM2 | 프로세스 상태 |
| CloudWatch | AWS 리소스 |

**AI 운세 모니터링 추가:**
- OpenAI API 응답시간 추적
- 캐시 히트율 모니터링
- 에러율/타임아웃율 대시보드

### Decision Impact Analysis

**구현 순서:**
1. fortune_histories 테이블 생성 (Alembic)
2. OpenAI 서비스 레이어 구현
3. 운세 API 엔드포인트 구현
4. Redis 캐싱 레이어 구현
5. 프론트엔드 운세 페이지 구현
6. 에러 핸들링 및 폴백 구현
7. 모니터링 대시보드 설정

**컴포넌트 의존성:**
```
Frontend (useFortune.ts)
    ↓
Backend (fortune_api.py)
    ↓
Service (fortune_service.py)
    ↓
├── openai_service.py → OpenAI API
├── Redis → 캐시
└── fortune_repository.py → MariaDB
```

---
