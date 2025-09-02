"""
상담사 관련 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

# 레이트 리미팅 import 추가
from src.common.middleware.rate_limit import limiter

from src.core.database import get_db_maria
from src.repositories.counselor_repository import CounselorRepository
from src.services.counselor_service import CounselorService
from src.services.auth_service import AuthService
from src.schemas.auth_schema import LoginRequest, LoginResponse
from src.common.response import APIResponse, ok, fail
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import BaseAppException

router = APIRouter(prefix="/counselors", tags=["counselors"])


# Dependency injection functions
def get_counselor_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorRepository:
    """상담사 리포지토리 의존성 주입"""
    return CounselorRepository(db)


def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()


def get_counselor_service(
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> CounselorService:
    """상담사 서비스 의존성 주입"""
    return CounselorService(counselor_repo, auth_service)


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="상담사 로그인",
    description="상담사 ID와 비밀번호로 로그인하고 JWT 토큰을 HttpOnly 쿠키에 설정",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "인증 실패"},
        403: {"description": "계정 비활성화 또는 승인되지 않음"}
    }
)
@limiter.limit("15/minute")  # 분당 15회 제한 (로그인 시도 제한)
async def login(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_maria),
    counselor_service: CounselorService = Depends(get_counselor_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """상담사 로그인"""
    log = get_logger_with_request_id()
    log.info("Counselor login attempt", counselor_id=login_request.user_id)
    
    # 로그인 처리 (예외는 전역 핸들러에서 처리)
    access_token, counselor_response = await counselor_service.login(
        counselor_id=login_request.user_id,
        password=login_request.password
    )
    
    # Refresh Token 생성
    refresh_token = auth_service.create_refresh_token(
        user_id=counselor_response.counselor_id,
        email=counselor_response.counselor_id,
        role="counselor"
    )
    
    # HttpOnly 쿠키에 JWT 토큰들 설정
    # Access Token (30분)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=30 * 60  # 30분
    )
    
    # Refresh Token (7일)  
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS에서만 전송
        samesite="lax",  # CSRF 보호
        max_age=7 * 24 * 60 * 60  # 7일
    )
    
    # 응답 데이터 생성 (토큰 만료 시간 포함)
    login_response = LoginResponse(
        user_id=counselor_response.counselor_id,
        email=counselor_response.counselor_id,  # counselor_id는 이메일 기반
        nickname=counselor_response.nickname,
        access_token_expires_in=30 * 60,  # 30분 (초 단위)
        refresh_token_expires_in=7 * 24 * 60 * 60  # 7일 (초 단위)
    )
    
    log.info("Counselor login successful", 
            counselor_id=counselor_response.counselor_id,
            nickname=counselor_response.nickname)
    
    return ok(login_response, "상담사 로그인이 성공했습니다")