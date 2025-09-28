# 사주라인 관리자 백엔드 API

## 프로젝트 개요
사주라인 관리자 백엔드 API 서버 - FastAPI 기반의 관리자 전용 시스템

## 기술 스택
- **Python**: 3.11+
- **FastAPI**: 0.110.0
- **SQLAlchemy**: 2.0.28 (비동기)
- **Pydantic**: 2.6.4
- **uvicorn**: 0.27.1
- **데이터베이스**: MariaDB (주), MSSQL (외부 연동)

## 환경 설정

### 1. UV 환경 설정 (권장)
```bash
# 의존성 설치
uv sync --extra dev

# 개발 서버 실행
uv run uvicorn src.main:app --reload --port 8001
```

### 2. 가상환경 설정 (대안)
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -e ".[dev]"

# 개발 서버 실행
uvicorn src.main:app --reload --port 8001
```

## 환경 변수 설정
`.env.development` 파일 확인 필요:
- DATABASE_URL: MariaDB 연결 정보
- MSSQL_* : MSSQL ARS 데이터베이스 연결 정보
- SECRET_KEY: JWT 토큰 암호화 키
- SENTRY_DSN: 에러 추적 (선택사항)

## API 엔드포인트

### 헬스체크
- `GET /` - 루트 엔드포인트
- `GET /health` - API 서버 상태 확인
- `GET /readiness` - 의존성 서비스 상태 확인

### 인증 API
- `GET /api/v1/auth/test` - 인증 API 테스트 엔드포인트

### API 문서
- 개발 모드에서 자동 생성: http://localhost:8001/docs (Swagger UI)
- ReDoc: http://localhost:8001/redoc

## 개발 도구

### 코드 품질 검사
```bash
# 포매팅
uv run black src/
uv run isort src/

# 린팅
uv run flake8 src/
uv run mypy src/

# 테스트
uv run pytest --cov=src tests/
```

## 포트 설정
- **관리자 백엔드**: 8001
- **메인 백엔드**: 8000 (구분을 위해)
- **프론트엔드**: 3000

## 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
uv run alembic revision --autogenerate -m "description"

# 마이그레이션 적용
uv run alembic upgrade head
```

## 문제 해결
1. **Python 버전 오류**: Python 3.11+ 필수
2. **의존성 설치 실패**: `uv sync --extra dev` 재실행
3. **포트 충돌**: 포트 8001 사용 중인지 확인
4. **데이터베이스 연결**: Docker Compose 서비스 실행 상태 확인