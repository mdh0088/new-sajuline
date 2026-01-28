# Project Structure & Boundaries

### Complete Project Directory Structure

```
new-sajuline/
├── frontend/                    # Nuxt 4 사용자 웹 (SSR)
│   ├── nuxt.config.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── .env.development
│   ├── .env.production
│   ├── pages/
│   │   ├── index.vue            # 메인 페이지
│   │   ├── fortune/             # 🆕 AI 운세 (MVP)
│   │   │   └── index.vue
│   │   ├── counselors/          # 상담사 목록
│   │   ├── mypage/              # 마이페이지
│   │   └── chat/                # 채팅
│   ├── app/
│   │   ├── components/
│   │   │   ├── Fortune/         # 🆕 운세 컴포넌트
│   │   │   │   ├── FortuneTabs.vue
│   │   │   │   ├── FortuneCard.vue
│   │   │   │   ├── FortuneLoading.vue
│   │   │   │   └── FortuneError.vue
│   │   │   ├── Chat/
│   │   │   ├── Counselor/
│   │   │   └── Common/
│   │   ├── composables/
│   │   │   ├── useFortune.ts    # 🆕 운세 API 훅
│   │   │   ├── useAuth.ts
│   │   │   └── useChat.ts
│   │   └── assets/
│   ├── stores/
│   │   ├── fortune.ts           # 🆕 운세 스토어
│   │   ├── auth.ts
│   │   └── chat.ts
│   ├── types/
│   │   └── fortune.d.ts         # 🆕 운세 타입
│   ├── server/                  # Nuxt 서버 API
│   └── public/
│
├── backend/                     # FastAPI 사용자 API
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env.development
│   ├── .env.production
│   ├── ecosystem.production.config.js
│   ├── alembic/                 # DB 마이그레이션
│   │   ├── versions/
│   │   │   └── xxxx_add_fortune_histories.py  # 🆕
│   │   └── env.py
│   └── src/
│       ├── main.py
│       ├── api/v1/
│       │   ├── fortune_api.py   # 🆕 운세 API
│       │   ├── auth_api.py
│       │   ├── user_api.py
│       │   ├── counselor_api.py
│       │   ├── chat_api.py
│       │   └── payment_api.py
│       ├── services/
│       │   ├── fortune_service.py  # 🆕 운세 로직
│       │   ├── openai_service.py   # 🆕 OpenAI 연동
│       │   ├── auth_service.py
│       │   └── chat_service.py
│       ├── repositories/
│       │   ├── fortune_repository.py  # 🆕 운세 DB
│       │   ├── user_repository.py
│       │   └── counselor_repository.py
│       ├── models/
│       │   ├── fortune_model.py   # 🆕 운세 모델
│       │   ├── user_model.py
│       │   └── counselor_model.py
│       ├── schemas/
│       │   ├── fortune_schema.py  # 🆕 운세 스키마
│       │   └── user_schema.py
│       └── common/
│           ├── middleware/
│           ├── utils/
│           └── exceptions/
│
├── admin-front/                 # Vue 3 관리자 웹 (SPA)
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── views/
│       │   └── fortune/         # 🆕 운세 통계 (관리자)
│       ├── api/
│       └── stores/
│
├── admin-backend/               # FastAPI 관리자 API
│   └── src/
│       ├── api/v1/
│       │   └── fortune_api.py   # 🆕 운세 통계 API
│       └── services/
│
├── docs/                        # 프로젝트 문서
│   ├── index.md
│   ├── ARCHITECTURE.md
│   ├── TECH-STACK.md
│   ├── API-REFERENCE.md
│   ├── DATA-MODELS.md
│   └── DEPLOYMENT.md
│
├── .github/
│   └── workflows/
│       ├── deploy-all.yml
│       └── deploy-admin-all.yml
│
└── _bmad-output/                # BMAD 산출물
    └── planning-artifacts/
        ├── prd.md
        ├── architecture.md      # 이 문서
        └── product-brief-*.md
```

### Architectural Boundaries

**API Boundaries:**
| 경계 | 엔드포인트 | 인증 |
|------|-----------|------|
| 사용자 API | `/api/v1/*` (backend:8000) | JWT |
| 관리자 API | `/api/v1/*` (admin-backend:8001) | Admin JWT |
| WebSocket | `/socket.io/` (backend:8000) | JWT |

**Service Boundaries:**
```
Frontend Layer
    ↓ HTTP/WebSocket
Backend Layer (API → Service → Repository)
    ↓ SQL/Cache
Data Layer (MariaDB + Redis)
```

**Data Flow (AI 운세):**
```
1. 사용자 요청 → /api/v1/fortune/daily
2. Redis 캐시 확인 → 히트 시 반환
3. 미스 시 → OpenAI API 호출
4. 결과 → Redis 캐시 저장 + DB 기록
5. 응답 반환
```

### Requirements to Structure Mapping

**FR 영역 → 디렉토리 매핑:**

| FR 카테고리 | Backend | Frontend |
|------------|---------|----------|
| 사용자 계정 (FR1-9) | `auth_api.py`, `user_api.py` | `pages/auth/`, `stores/auth.ts` |
| AI 운세 (FR10-16) | 🆕 `fortune_api.py`, `openai_service.py` | 🆕 `pages/fortune/`, `useFortune.ts` |
| 상담 서비스 (FR17-25) | `counselor_api.py`, `chat_api.py` | `pages/counselors/`, `pages/chat/` |
| 결제/포인트 (FR26-33) | `payment_api.py` | `pages/payment/` |
| 관리자 (FR43-52) | `admin-backend/` | `admin-front/` |

### Integration Points

**외부 서비스 연동 위치:**
| 서비스 | 연동 파일 | 용도 |
|--------|----------|------|
| OpenAI | `services/openai_service.py` | AI 운세 생성 |
| Payletter | `services/payment_service.py` | 결제 처리 |
| KCP | `services/auth_service.py` | 본인인증 |
| Kakao/Naver OAuth | `services/oauth_service.py` | 소셜 로그인 |
| MSSQL (ARS) | `repositories/ars/` | 레거시 연동 |

### MVP 신규 파일 목록

**Backend (6개 파일):**
1. `src/api/v1/fortune_api.py` - API 엔드포인트
2. `src/services/fortune_service.py` - 비즈니스 로직
3. `src/services/openai_service.py` - OpenAI 연동
4. `src/repositories/fortune_repository.py` - DB 접근
5. `src/models/fortune_model.py` - SQLAlchemy 모델
6. `src/schemas/fortune_schema.py` - Pydantic 스키마

**Frontend (7개 파일):**
1. `pages/fortune/index.vue` - 운세 페이지
2. `app/components/Fortune/FortuneTabs.vue` - 탭 컴포넌트
3. `app/components/Fortune/FortuneCard.vue` - 결과 카드
4. `app/components/Fortune/FortuneLoading.vue` - 로딩 UI
5. `app/components/Fortune/FortuneError.vue` - 에러 UI
6. `app/composables/useFortune.ts` - API 훅
7. `stores/fortune.ts` - 상태 스토어

**Database (1개 마이그레이션):**
1. `alembic/versions/xxxx_add_fortune_histories.py`

---
