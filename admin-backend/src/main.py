"""
사주라인 관리자 백엔드 - FastAPI 메인 애플리케이션
"""

# Sentry 초기화 (FastAPI 앱 생성 전에 실행)
from src.common.monitoring.sentry_config import initialize_sentry
initialize_sentry()

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config.settings import settings
from src.api.v1.auth_api import router as auth_router
from src.api.v1.admin_api import router as admin_router
from src.api.v1.counselor_api import router as counselor_router
from src.api.v1.counselor_application_api import router as counselor_application_router
from src.api.v1.user_api import router as user_router
from src.api.v1.grade_api import router as grade_router
from src.api.v1.point_product_api import router as point_product_router
from src.api.v1.banner_api import router as banner_router
from src.api.v1.notice_api import router as notice_router
from src.api.v1.payment_api import router as payment_router
from src.api.v1.inquiry_api import router as inquiry_router
from src.api.v1.promotion_api import router as promotion_router
from src.api.v1.exhibition_api import router as exhibition_router
from src.api.v1.mileage_api import router as mileage_router
from src.api.v1.consultation_review_api import router as consultation_review_router
from src.api.v1.dashboard_api import router as dashboard_router
from src.api.v1.ai_assistant_api import router as ai_assistant_router
from src.common.response import fail
from src.exceptions.custom_exceptions import BaseAppException
from src.common.logging.config import setup_logging
from src.common.logging.events import SystemEvents
from src.common.logging import logger, get_logger_with_request_id
from src.common.middleware.logging import LoggingMiddleware
# from src.common.middleware.audit import AuditLogMiddleware

# 로깅 시스템 초기화
setup_logging()

# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="사주라인 관리자 백엔드 API",
    version=settings.app_version,
    docs_url=settings.docs_url if settings.debug else None,
    redoc_url=settings.redoc_url if settings.debug else None,
    openapi_url=settings.openapi_url,
    debug=settings.debug,
    openapi_tags=[
        {
            "name": "auth",
            "description": "관리자 인증 - 로그인, 토큰 갱신, 2FA",
        },
        {
            "name": "admin",
            "description": "관리자 관리 - 관리자 계정, 권한 설정",
        },
        {
            "name": "dashboard",
            "description": "대시보드 - 통계, 실시간 모니터링",
        },
        {
            "name": "users",
            "description": "사용자 관리 - 회원 조회, 수정, 정지",
        },
        {
            "name": "counselors",
            "description": "상담사 관리 - 상담사 승인, 정보 관리",
        },
        {
            "name": "counselor-applications",
            "description": "상담사 신청 관리 - 신청 조회, 승인/거절 처리",
        },
        {
            "name": "payments",
            "description": "결제 관리 - 결제 내역, 환불 처리",
        },
        {
            "name": "statistics",
            "description": "통계 분석 - 매출, 사용자, 상담 통계",
        },
        {
            "name": "health",
            "description": "시스템 상태 체크 - 헬스체크, 준비상태 확인",
        },
    ],
)

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
    allowed_hosts=["*"]  # 관리자 백엔드는 모든 호스트 허용
)

# 로깅 미들웨어 (가장 먼저 추가)
app.add_middleware(LoggingMiddleware)

# 감사 로그 미들웨어 (관리자 전용) - 비활성화
# if settings.enable_audit_log:
#     app.add_middleware(AuditLogMiddleware)

# 전역 예외 핸들러
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 유효성 검사 예외 처리 (422 → 400 변환)

    Story 2-1 AC #6: 유효성 검사 실패 시 400 Bad Request 반환
    """
    log = get_logger_with_request_id()

    # 유효성 검사 에러 상세 정보 추출
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    error_detail = "; ".join(error_messages)

    log.warning(
        "validation_error",
        extra={
            "event": "validation_error",
            "path": request.url.path,
            "method": request.method,
            "error_detail": error_detail,
            "client_ip": request.client.host if request.client else None,
        },
    )

    return JSONResponse(
        status_code=400,  # 422 대신 400 반환
        content={
            "success": False,
            "message": "입력 데이터가 유효하지 않습니다.",
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "detail": error_detail,
                "errors": errors,
            },
            "meta": {"timestamp": None, "request_id": None, "pagination": None},
        },
    )


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
        # 안전한 포매팅: 키워드 충돌/KeyError 방지 위해 message를 args로 분리하지 않음
        log.error("%s: %s",
                 type(exc).__name__, exc.message,
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
        log.warning("%s: %s",
                   type(exc).__name__, exc.message,
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
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(counselor_router, prefix="/api/v1")
app.include_router(counselor_application_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(grade_router, prefix="/api/v1")
app.include_router(point_product_router, prefix="/api/v1")
app.include_router(banner_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(notice_router, prefix="/api/v1")
app.include_router(inquiry_router, prefix="/api/v1")
app.include_router(promotion_router, prefix="/api/v1")
app.include_router(exhibition_router, prefix="/api")
app.include_router(mileage_router, prefix="/api/v1")
app.include_router(consultation_review_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(ai_assistant_router, prefix="/api/v1")


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
    return {
        "message": f"{settings.app_name}",
        "version": settings.app_version,
        "environment": settings.app_env
    }


@app.get("/health", response_model=HealthResponse, tags=["health"], summary="헬스 체크")
async def health_check():
    """API 서버 상태 확인"""
    return HealthResponse(
        status="healthy",
        message="관리자 API 서버가 정상적으로 동작 중입니다.",
        version=settings.app_version
    )


@app.get("/readiness", response_model=ReadinessResponse, tags=["health"], summary="준비 상태 체크")
async def readiness_check():
    """의존성 서비스 상태 확인 - DB, 외부 API"""
    services = {
        "database": "healthy",  # TODO: 실제 DB 연결 상태 체크
        "mssql": "healthy",     # TODO: 실제 MSSQL 연결 상태 체크
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
        environment=settings.app_env,
        debug=settings.debug,
        log_level=settings.log_level
    )
    print(f"🚀 {settings.app_name} v{settings.app_version} started on port {settings.port}")
    print(f"📚 API Documentation: http://localhost:{settings.port}{settings.docs_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 이벤트"""
    SystemEvents.application_shutdown()
    print(f"👋 {settings.app_name} shutting down...")


def main():
    """메인 함수 - 개발 서버 실행"""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.is_development,
        reload_dirs=["src"] if settings.is_development else None,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()