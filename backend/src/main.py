"""
사주라인 리뉴얼 프로젝트 - FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

from src.config.settings import settings
from src.api.v1.user import router as user_router

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
    allowed_hosts=settings.trusted_hosts_list
)

# API 라우터 등록
app.include_router(user_router, prefix="/api/v1")


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