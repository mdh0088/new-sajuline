## 사주라인 리뉴얼 프로젝트 (sajuline-new)

### 소개
AI와 전문가의 하이브리드 상담을 제공하는 사주 플랫폼의 리뉴얼 모노레포입니다. 프론트엔드는 Nuxt 4 기반 SSR 웹앱, 백엔드는 FastAPI 기반 비동기 API로 구성되며, `infra`의 Docker Compose로 통합 개발 환경을 제공합니다.

### 주요 기능
- 인증/인가: JWT 기반 로그인/토큰 관리
- 사용자 관리: 회원가입, 프로필, 계정 관리
- 상담사 영역: 상담사 전용 로그인 및 기능
- 공지사항: 공지 조회/관리
- AI 상담: OpenAI/LangChain 연동 기반 기능(선택적 플래그)
- 결제 연동: KCP 바이너리 포함(환경에 맞게 구성)
- 안정성/보안: 레이트 리미팅, CORS, Trusted Host, Sentry, 구조화 로깅

### 시스템 아키텍처 개요
- 프론트엔드: Nuxt 4 + Vue 3 + TypeScript, SSR 기본, SWR/CSR 혼합 라우트 전략
- 백엔드: FastAPI + Uvicorn, 계층형 구조(API/서비스/리포지토리/스키마)
- 데이터베이스: MariaDB(주 DB), MSSQL(ARS 연동)
- 캐시/큐: Redis(세션/캐시 등)
- 인프라: Docker Compose(개발용)로 서비스 일괄 기동 및 헬스체크

### 디렉터리 구조
```txt
./
├─ backend/            # FastAPI 백엔드 (Python 3.11)
│  ├─ src/             # API, services, repositories, models, schemas, common, config, core 등
│  ├─ tests/           # pytest 기반 단위/통합 테스트
│  ├─ alembic/         # DB 마이그레이션 스크립트
│  ├─ kcp_binaries/    # KCP 결제 관련 바이너리
│  ├─ Dockerfile
│  └─ pyproject.toml
├─ frontend/           # Nuxt 4 (Vue 3, TypeScript)
│  ├─ pages/, components/, composables/, plugins/
│  ├─ nuxt.config.ts, package.json, tailwind.config.js
│  └─ Dockerfile
├─ infra/              # 로컬 통합 개발 환경 (Docker Compose)
│  └─ docker-compose.yml (Frontend, Backend, MariaDB, Redis, MSSQL)
├─ prototype/          # 초기 프로토타입 코드/문서
├─ c2c-rules/          # 코드 품질/보안/아키텍처 가이드 문서
└─ README.md           # 본 문서
```

### 기술 스택
- 프론트엔드: Nuxt 4, Vue 3, TypeScript, Pinia, @tanstack/vue-query, Element Plus, Tailwind CSS, @vueuse, Notivue
- 백엔드: FastAPI, Uvicorn, SQLAlchemy(Async) + SQLModel, Alembic, Redis, Pydantic v2, SlowAPI, Sentry, Loguru, HTTPX/AioHTTP, OpenAI/LangChain
- 데이터: MariaDB(MySQL 호환), MSSQL(ARS), Redis
- 인프라: Docker, Docker Compose(개발용), 헬스체크/브리지 네트워크/볼륨
- 품질: pytest, coverage, black, isort, flake8, mypy, pre-commit

### API 개요
- 기본 경로: `/api/v1/*`
- 헬스: `GET /health`, 준비상태: `GET /readiness`
- 도큐먼트: `GET /docs`, `GET /redoc` (디버그 모드에서 노출)
- 대표 도메인: `auth`, `users`, `counselors`, `notices`

### 개발/실행 개요
- 통합 개발(권장): `infra/docker-compose.yml`에서 프론트/백/DB/Redis/MSSQL 기동
- 수동 실행: 각 폴더(`frontend`, `backend`)에서 일반적인 개발 명령 사용
  - 프론트: `npm run dev` (Nuxt)
  - 백엔드: `uvicorn src.main:app --reload`

### 운영/가시성
- 로깅: Loguru + JSON 구조화, `backend/logs/` 보관
- 모니터링/추적: Sentry 연동
- 신뢰성: 레이트 리미팅(SlowAPI), CORS, Trusted Host 적용

### 라이선스/문의
- 라이선스: Proprietary (사내 전용)
- 문의: dev@sajuline.com
## Backend Configuration

### 구성 개요
- **중앙 설정 모듈**: `backend/src/config/settings.py`
  - Pydantic `BaseSettings` 기반 단일 소스(Single Source of Truth)
  - 인스턴스: `settings = Settings()` (모듈 하단)
- **환경파일**: `backend/.env.development`, `backend/.env.production`
  - 선택 규칙: `ENVIRONMENT=development`면 `.env.development`, 그 외 `.env.production`
- **전역 사용 패턴**: 각 모듈에서 `from src.config.settings import settings` 후 `settings.*` 접근

### 환경파일 로딩 규칙 (명시적)
- 참조 소스: `backend/src/config/settings.py` 내 `class Config`
  - `env_file = ".env.development" if os.getenv("ENVIRONMENT", "development") == "development" else ".env.production"`
  - OS 환경변수 `ENVIRONMENT`가 없으면 기본값 `development`로 동작

### 설정 사용처 (대표)
- `backend/src/main.py`
  - `settings.debug`, `settings.cors_origins_list`, `settings.trusted_hosts_list` 등으로 앱/미들웨어 구성
- `backend/src/core/database.py`
  - MariaDB: `settings.mariadb_url`, `mariadb_pool_size`/`max_overflow`/`echo`
  - MSSQL: `settings.mssql_*` 이용하여 연결 URL/엔진 생성
- `backend/src/core/redis.py`
  - `settings.redis_url`/`redis_password`로 클라이언트 생성
- `backend/src/common/middleware/rate_limit.py`
  - 레이트리밋 저장소: `redis://{settings.redis_host}:{settings.redis_port}/2`
- `backend/src/common/monitoring/sentry_config.py`
  - `settings.sentry_dsn`, `settings.service_name`/`service_version`/`environment` 활용
- `backend/src/common/logging/config.py`
  - `settings.log_level`/`settings.is_development`로 Loguru 구성

### 주요 설정 그룹 (요약)
- 애플리케이션: `environment`, `debug`, `host`, `port`, `log_level`
- 보안/JWT: `secret_key`, `access_token_expire_minutes`, `refresh_token_expire_days`, `algorithm`
- CORS/호스트: `cors_origins`(→ `cors_origins_list`), `frontend_url`, `trusted_hosts`(→ `trusted_hosts_list`)
- MariaDB: `mariadb_*` 일체, `mariadb_url` 프로퍼티 제공
- MSSQL: `mssql_*` 일체, 드라이버(개발/운영) 분기
- Redis: `redis_url`, `redis_db`, `redis_password` (+ 파생: `redis_host`, `redis_port`)
- AI: `openai_api_key`, `openai_model`, `ai_cache_ttl`
- AWS S3: `aws_*`, `s3_bucket_name`
- 소셜로그인: `kakao_client_id`, `naver_client_id`, `naver_client_secret`
- 결제: `payment_gateway_url`, `payment_gateway_key`
- 모니터링: `sentry_dsn`
- 기능플래그: `enable_ai_features`, `enable_social_login`, `enable_webhooks`
- Docker: `docker_env`
- KCP: `kcp_*`, `api_base_url`
- 관리자: `admin_email`, `admin_password`
- 로깅: `log_json`, `log_to_stdout`, `log_to_file`, `service_name`, `service_version`

### 권장 사용 패턴 (Best Practice)
1) 설정 추가
   - `backend/src/config/settings.py`의 `Settings` 클래스에 `Field(..., env="ENV_NAME")` 추가
   - 두 환경파일 모두(`.env.development`, `.env.production`)에 키 추가 및 값 설정
2) 사용
   - 각 코드에서 오직 `from src.config.settings import settings` 후 `settings.YOUR_FIELD`로 접근
3) 파생값이 필요하면
   - `@property`로 계산 필드(예: `mariadb_url`, `redis_host`, `redis_port`)를 `Settings`에 추가

### 금지/주의 (중복/분산 접근 방지)
- `os.getenv()`로 직접 읽지 말 것. 중앙 설정(`settings`)만 사용
- 설정 초기화/로깅 구성은 한 곳에서만 수행

### 현재 불일치/중복 포인트와 조치
- 로깅 초기화 이중화 가능성
  - 파일: `backend/src/common/logging/__init__.py`가 직접 `os.getenv("LOG_LEVEL")`로 초기화 수행
  - 동시에 `backend/src/common/logging/config.py`의 `setup_logging()`도 초기화 수행
  - 권장: 초기화는 `setup_logging()` 단일 경로로 통일하고, `__init__.py`는 헬퍼만 노출하도록 축소
- 프로덕션 환경파일 DB 변수명 불일치
  - 파일: `backend/.env.production`이 `DATABASE_URL|DATABASE_*` 키를 사용
  - 코드: `Settings`는 `MARIADB_*` 키를 사용하여 URL을 구성
  - 권장: 운영 파일을 `MARIADB_*` 키로 정렬(개발과 동일)하거나, 코드에 `DATABASE_*` 대응 필드를 추가하되 한 체계로 표준화

### 새 설정 추가 체크리스트
- `Settings`에 필드 추가 → 두 환경파일에 값 추가 → 코드에서 `settings`로만 접근 → 필요시 `@property` 제공 → 문서(본 섹션) 업데이트

### 사용 예시
```python
from src.config.settings import settings

def build_service_url(path: str) -> str:
    base = settings.api_base_url.rstrip('/')
    return f"{base}/{path.lstrip('/')}"

if settings.is_production:
    # 프로덕션 전용 동작
    pass
```


