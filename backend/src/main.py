"""
사주라인 리뉴얼 프로젝트 - FastAPI 메인 애플리케이션
"""

# Sentry 초기화 (FastAPI 앱 생성 전에 실행)
from src.common.monitoring.sentry_config import initialize_sentry
initialize_sentry()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 레이트 리미팅 관련 import
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config.settings import settings
from src.api.v1.user_api import router as user_router
from src.api.v1.counselor_api import router as counselor_router
from src.common.response import fail
from src.exceptions.custom_exceptions import BaseAppException
from src.common.logging.config import setup_logging
from src.common.logging.events import SystemEvents
from src.common.logging import logger, get_logger_with_request_id
from src.common.middleware.logging import LoggingMiddleware
from src.common.middleware.rate_limit import limiter

# 로깅 시스템 초기화
setup_logging()

# FastAPI 앱 생성
app = FastAPI(
    title="사주라인 리뉴얼 API",
    description="AI와 전문가의 하이브리드 사주 상담 서비스",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    debug=settings.debug,
    openapi_tags=[
        {
            "name": "users",
            "description": "사용자 관리 - 회원가입, 로그인, 프로필 관리",
        },
        {
            "name": "counselors",
            "description": "상담사 관리 - 로그인, 상담사 전용 기능",
        },
        {
            "name": "health",
            "description": "시스템 상태 체크 - 헬스체크, 준비상태 확인",
        },
    ],
)

# 레이트 리미팅 설정 (가장 먼저 추가)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host 미들웨어
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts_list
)

# 로깅 미들웨어 (가장 먼저 추가)
app.add_middleware(LoggingMiddleware)

# 전역 예외 핸들러
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """커스텀 애플리케이션 예외 처리"""
    # 간단한 에러 로깅 (스택 트레이스 없음)
    log = get_logger_with_request_id()
    
    # status_code에 따른 로그 레벨 구분
    # 에러 발생 위치 정보 추가
    import traceback
    tb = traceback.extract_tb(exc.__traceback__)
    error_location = None
    app_frames = []
    
    if tb:
        # 모든 traceback 프레임 분석 (디버그용)
        for frame in tb:
            if '/app/src/' in frame.filename:  # 애플리케이션 코드만
                app_frames.append(f"{frame.filename.split('/')[-1]}:{frame.lineno}:{frame.name}")
        
        # 실제 에러 발생 위치 (애플리케이션 코드 중 마지막)
        if app_frames:
            error_location = app_frames[-1]
        elif tb:
            # fallback: 전체 tb 중 마지막
            last_frame = tb[-1]
            error_location = f"{last_frame.filename.split('/')[-1]}:{last_frame.lineno}:{last_frame.name}"
    
    # Request body 및 User-Agent 정보 가져오기 (미들웨어에서 저장한 것)
    request_body = getattr(request.state, 'request_body', None)
    user_agent_info = getattr(request.state, 'user_agent_info', {})
    
    if exc.status_code >= 500:
        log.error(f"{type(exc).__name__}: {exc.message}",
                 path=request.url.path,
                 method=request.method,
                 status_code=exc.status_code,
                 client_ip=request.client.host,
                 user_agent=request.headers.get("user-agent", "unknown"),
                 device=user_agent_info.get("device", "unknown"),
                 browser=user_agent_info.get("browser", "unknown"),
                 os=user_agent_info.get("os", "unknown"),
                 error_location=error_location,
                 call_stack=app_frames if len(app_frames) > 1 else None,
                 request_body=request_body)
    else:
        log.warning(f"{type(exc).__name__}: {exc.message}",
                   path=request.url.path,
                   method=request.method,
                   status_code=exc.status_code,
                   client_ip=request.client.host,
                   device=user_agent_info.get("device", "unknown"),
                   browser=user_agent_info.get("browser", "unknown"),
                   os=user_agent_info.get("os", "unknown"),
                   error_location=error_location,
                   call_stack=app_frames if len(app_frames) > 1 else None,
                   request_body=request_body)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(message=exc.message).model_dump(mode='json')
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """예상치 못한 예외 처리"""
    import sentry_sdk
    
    # Sentry에 예외 전송 (사용자 컨텍스트와 함께)
    with sentry_sdk.configure_scope() as scope:
        scope.set_context("request", {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None
        })
        sentry_sdk.capture_exception(exc)
    
    # 시스템 에러 로깅 (기존 로직 유지)
    logger.exception(f"Unhandled Exception: {str(exc)}", 
                    path=request.url.path,
                    method=request.method,
                    exception_type=type(exc).__name__)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "서버 내부 오류가 발생했습니다",
            "data": None,
            "error": {"code": "INTERNAL_SERVER_ERROR"},
            "meta": {"timestamp": None, "request_id": None, "pagination": None}
        }
    )

# API 라우터 등록
app.include_router(user_router, prefix="/api/v1")
app.include_router(counselor_router, prefix="/api/v1")


class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    message: str
    version: str


class ReadinessResponse(BaseModel):
    """준비 상태 체크 응답 모델"""
    status: str
    services: dict


@app.get("/", tags=["health"])
async def root():
    """루트 엔드포인트"""
    return {"message": "사주라인 리뉴얼 API 서버", "version": "0.1.0"}


@app.get("/health", response_model=HealthResponse, tags=["health"], summary="헬스 체크")
async def health_check():
    """API 서버 상태 확인"""
    return HealthResponse(
        status="healthy",
        message="API 서버가 정상적으로 동작 중입니다.",
        version="0.1.0"
    )


@app.get("/readiness", response_model=ReadinessResponse, tags=["health"], summary="준비 상태 체크")
async def readiness_check():
    """의존성 서비스 상태 확인 - DB, Redis, 외부 API"""
    services = {
        "database": "healthy",  # TODO: 실제 DB 연결 상태 체크
        "redis": "healthy",     # TODO: 실제 Redis 연결 상태 체크
        "external_apis": "healthy"  # TODO: 외부 API 상태 체크
    }
    
    return ReadinessResponse(
        status="ready",
        services=services
    )


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 이벤트"""
    SystemEvents.application_started(
        environment="development" if settings.is_development else "production",
        debug=settings.debug,
        log_level=settings.log_level
    )


@app.on_event("shutdown") 
async def shutdown_event():
    """애플리케이션 종료 이벤트"""
    SystemEvents.application_shutdown()


def main():
    """메인 함수 - 개발 서버 실행"""
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        reload_dirs=["src"] if settings.is_development else None,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()