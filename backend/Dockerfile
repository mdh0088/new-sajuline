# 사주라인 백엔드 Dockerfile
# Python 3.11 + FastAPI + uv 패키지 관리

# Build stage
FROM python:3.11-slim as builder

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 시스템 패키지 업데이트 및 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (Python 패키지 관리자)
RUN pip install uv

# 작업 디렉터리 설정
WORKDIR /app

# pyproject.toml 복사 및 의존성 설치
COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml

# Production stage
FROM python:3.11-slim as production

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# 시스템 패키지 업데이트 및 런타임 의존성 설치
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 비특권 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 작업 디렉터리 설정
WORKDIR /app

# 빌드 스테이지에서 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/

# KCP 바이너리 파일 복사
COPY kcp_binaries/ ./kcp_binaries/

# KCP 바이너리 실행 권한 설정
RUN chmod +x /app/kcp_binaries/32bit/ct_cli /app/kcp_binaries/64bit/ct_cli

# 로그 디렉터리 생성
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# 사용자 전환
USER appuser

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 포트 노출
EXPOSE $PORT

# 애플리케이션 실행
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM production as development

# 개발 환경 전용 설정
ENV ENVIRONMENT=development

# pyproject.toml 복사 (개발 의존성 설치용)
USER root
COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml --extra dev

# 테스트 파일 복사 (개발 환경에서만 필요)
COPY tests/ ./tests/

USER appuser

# 개발 서버 실행 (reload 활성화)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]