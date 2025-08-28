"""
사주라인 백엔드 메인 애플리케이션

FastAPI 기반의 사주 상담 플랫폼 백엔드 서버
Hexagonal Architecture 패턴 적용
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sentry_sdk

from src.common.config.settings import get_settings
from src.common.exceptions.handlers import setup_exception_handlers
from src.common.middleware.logging import LoggingMiddleware
from src.common.logging.config import configure_logging, build_dict_config
from src.common.middleware.rate_limit import RateLimitMiddleware


# 환경설정 로드 및 검증
settings = get_settings()


def validate_startup_requirements():
    """
    애플리케이션 시작 시 필수 요구사항 검증
    
    Raises:
        SystemExit: 필수 요구사항이 충족되지 않은 경우
    """
    logger = logging.getLogger("app.bootstrap")
    logger.info("startup_requirements_validation_start")
    
    try:
        # 환경 변수 검증
        settings.validate_required_settings()
        logger.info("env_ready", extra={"environment": settings.ENVIRONMENT})
        logger.info("database_ready", extra={"database": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'})
        logger.info("redis_ready", extra={"redis_url": settings.REDIS_URL})
        logger.info("cors_ready", extra={"cors_origins_count": len(settings.CORS_ORIGINS)})
        
        # 프로덕션 환경 추가 검증
        if settings.is_production:
            if settings.DEBUG:
                logger.warning("debug_mode_in_production")
            
            if not settings.SENTRY_DSN:
                logger.warning("sentry_dsn_not_configured")
        
        logger.info("startup_requirements_validation_success")
        
    except ValueError as e:
        logger.error("startup_validation_failed", extra={"error": str(e)})
        logger.info("check_environment_variables")
        raise SystemExit(1)
    except Exception as e:
        logger.error("startup_validation_unexpected_error", extra={"error": str(e)})
        raise SystemExit(1)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    애플리케이션 생명주기 관리
    
    시작 시:
    - 환경 변수 검증
    - 데이터베이스 연결 초기화
    - Redis 연결 초기화
    - AI 모델 준비
    
    종료 시:
    - 모든 연결 정리
    """
    # 시작 시 초기화
    logger = logging.getLogger("app.bootstrap")
    logger.info("server_start")
    
    # 환경 변수 및 필수 요구사항 검증
    validate_startup_requirements()
    
    # 앱 스코프 싱글톤 리소스 초기화 (T-068)
    from src.common.dependencies.providers.redis import get_redis, close_redis
    from src.common.dependencies.providers.s3 import get_s3
    from src.common.dependencies.providers.ai import get_ai_client

    try:
        # Redis (async)
        app.state.redis = await get_redis()
    except Exception as e:  # noqa: BLE001
        logger.error("redis_initialization_failed", extra={"error": str(e)})
        app.state.redis = None

    try:
        # S3 (sync client)
        app.state.s3 = get_s3()
    except Exception as e:  # noqa: BLE001
        logger.warning("s3_initialization_skipped", extra={"error": str(e)})
        app.state.s3 = None

    try:
        # OpenAI (sync client object)
        app.state.ai = get_ai_client()
    except Exception as e:  # noqa: BLE001
        logger.warning("ai_client_initialization_skipped", extra={"error": str(e)})
        app.state.ai = None

    logger.info("initialization_complete")
    
    yield
    
    # 종료 시 정리
    logger.info("server_shutdown")
    # 앱 스코프 싱글톤 리소스 정리 (T-068)
    try:
        await close_redis()
    except Exception:
        pass
    # S3, AI는 별도의 종료 루틴이 필요하지 않음 (GC 대상)
    app.state.redis = None
    app.state.s3 = None
    app.state.ai = None
    
    logger.info("cleanup_complete")


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성 및 설정
    
    Returns:
        FastAPI: 설정된 FastAPI 애플리케이션 인스턴스
    """
    

    # Sentry 초기화 (환경변수/설정 기반)
    try:
        dsn = getattr(settings, "SENTRY_DSN", None)
        if dsn and settings.ENVIRONMENT != "development":
            service = os.getenv("SERVICE_NAME", "sajuline-api")
            version = os.getenv("SERVICE_VERSION", "dev")
            sentry_sdk.init(
                dsn=dsn,
                environment=settings.ENVIRONMENT,
                release=f"{service}@{version}",
                send_default_pii=True,
            )
    except Exception as e:  # noqa: BLE001
        logging.getLogger("app.bootstrap").warning("Sentry initialization skipped: %s", e)

    app = FastAPI(
        title="사주라인 API",
        description="AI와 전문가가 만나는 온라인 사주 상담 플랫폼",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )
    
    # CORS 설정 (최상위에 두어 모든 응답에 헤더 포함)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
    
    # 신뢰할 수 있는 호스트 설정
    if settings.TRUSTED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=settings.TRUSTED_HOSTS
        )
    
    # 커스텀 미들웨어
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # 보안 헤더 미들웨어 추가
    from src.common.middleware.security_headers import APISecurityHeadersMiddleware
    app.add_middleware(APISecurityHeadersMiddleware)
    
    # 예외 핸들러 설정
    setup_exception_handlers(app)
    
    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health_check():
        """
        헬스체크 엔드포인트
        
        Returns:
            dict: 서비스 상태 정보
        """
        return {
            "status": "healthy",
            "service": "sajuline-backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    @app.get("/")
    async def root():
        """
        루트 엔드포인트
        
        Returns:
            dict: 기본 정보
        """
        return {
            "message": "사주라인 백엔드 API",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
            "health": "/health"
        }
    
    # DB 헬스체크 (MSSQL)
    @app.get("/health/db")
    async def health_db():
        from src.common.database.mssql_session import test_mssql_connection_async
        ok, msg = await test_mssql_connection_async()
        return {"ok": ok, "message": msg}

    # Providers 상태 점검 예제 엔드포인트
    @app.get("/health/providers")
    async def health_providers():
        from src.common.dependencies.providers import get_redis, get_s3, get_ai_client
        result = {"redis": False, "s3": False, "ai": False}
        # Redis 체크
        try:
            redis_client = await get_redis()
            pong = await redis_client.ping()
            result["redis"] = bool(pong)
        except Exception as e:  # noqa: BLE001
            result["redis_error"] = str(e)
        # S3 체크
        try:
            s3 = get_s3()
            # 가벼운 호출: region 조회 시도(네트워크 없이 구성만 확인)
            _ = s3.meta.region_name if hasattr(s3, "meta") else True
            result["s3"] = True
        except Exception as e:  # noqa: BLE001
            result["s3_error"] = str(e)
        # AI 클라이언트 체크
        try:
            ai = get_ai_client()
            result["ai"] = ai is not None
        except Exception as e:  # noqa: BLE001
            result["ai_error"] = str(e)
        return result

    # 라우터 등록 (일관된 /v1 prefix 패턴)
    
    # Auth 도메인 라우터 (Hexagonal Architecture)
    from src.auth.interface.routers import router as auth_router
    app.include_router(auth_router, tags=["인증"])
    
    # User 도메인 라우터 (Hexagonal Architecture)
    from src.user.interface.routers import router as user_router
    app.include_router(user_router, tags=["사용자"])
    
    
    # 추가 도메인별 라우터 등록 (Hexagonal Architecture)
    from src.counselor.interface.routers import router as counselor_router, auth_router as counselor_auth_router
    
    app.include_router(counselor_router, tags=["상담사"])
    app.include_router(counselor_auth_router, tags=["상담사 인증"])  # 상담사 로그인 라우터 추가
    
    # 핸드폰 인증 도메인 라우터 (레거시/간소화 모두 복구)
    from src.phone_verification.interface.routers import router as phone_verification_router
    app.include_router(phone_verification_router, tags=["핸드폰 인증 (Legacy)"])
    
    from src.phone_verification.interface.simplified_routers import router as sms_router
    app.include_router(sms_router, tags=["SMS 인증"])
    
    from src.phone_verification.interface.kcp_callback_router import router as kcp_router
    app.include_router(kcp_router, tags=["KCP Callback"])
    
    return app


# 앱 인스턴스 생성
app = create_app()


def main() -> None:
    """
    개발 서버 실행용 메인 함수
    """
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        log_config=build_dict_config(),
        access_log=True,
        use_colors=True,
        loop="uvloop",
    )


if __name__ == "__main__":
    main() 