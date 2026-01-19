"""
Counselor 인터페이스 라우터
상담사 관리 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from ...common.exceptions.custom import AuthUnauthorizedException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..domain.entities import (
    CounselorLoginRequest, CounselorLoginResponse, CounselorInfo,
    UpdateCounselorStatusRequest, UpdateOnlineStatusRequest,
    SpecialtyListResponse, SpecialtyInfo
)
from ..application.services import CounselorAuthApplicationService
from ..infrastructure.providers import get_counselor_auth_service as provide_counselor_auth_service
from ...common.utils.client_info import get_client_ip, get_user_agent
from ...common.response import APIResponse
from ...common.decorators.error_handler import handle_api_errors

# FastAPI Router 설정
router = APIRouter(
    prefix="/api/v1/counselors",
    tags=["상담사"],
    responses={
        400: {"description": "잘못된 요청"},
        401: {"description": "인증 실패"},
        403: {"description": "권한 없음"},
        404: {"description": "상담사를 찾을 수 없음"},
        422: {"description": "검증 오류"},
        500: {"description": "서버 오류"}
    }
)

# Auth Router 설정 (상담사 로그인 전용)
auth_router = APIRouter(
    prefix="/api/v1/auth/counselor",
    tags=["상담사 인증"],
    responses={
        400: {"description": "잘못된 요청"},
        401: {"description": "인증 실패"},
        403: {"description": "권한 없음 또는 승인 필요"},
        422: {"description": "검증 오류"},
        500: {"description": "서버 오류"}
    }
)

# JWT Bearer 토큰 스킴
security = HTTPBearer()


async def get_counselor_auth_service(
    service: CounselorAuthApplicationService = Depends(provide_counselor_auth_service),
) -> CounselorAuthApplicationService:
    return service


async def get_current_counselor_dependency(
    request: Request,
    counselor_auth_service: CounselorAuthApplicationService = Depends(get_counselor_auth_service)
) -> CounselorInfo:
    """현재 상담사 의존성 주입 (쿠키 기반)"""
    try:
        # 쿠키에서 토큰 추출
        access_token = request.cookies.get("counselor_access_token")
        
        if not access_token:
            raise AuthUnauthorizedException(message="로그인이 필요합니다.")
        
        return await counselor_auth_service.get_current_counselor(access_token)
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        # 내부 오류 로깅
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"상담사 인증 확인 오류: {str(e)}", exc_info=True)
        
        # 사용자에게는 일반적인 오류 메시지만 반환
        raise AuthUnauthorizedException(message="인증 정보를 확인할 수 없습니다. 다시 로그인해주세요.")


@auth_router.post(
    "/login",
    response_model=APIResponse[CounselorLoginResponse],
    summary="상담사 로그인",
    description="이메일과 비밀번호로 상담사 로그인하여 JWT 토큰을 발급받습니다. 관리자 승인이 필요합니다.",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "잘못된 인증 정보"},
        403: {"description": "계정 비활성화 또는 승인 필요"},
        500: {"description": "서버 내부 오류"}
    }
)
@handle_api_errors
async def counselor_login(
    login_request: CounselorLoginRequest,
    request: Request,
    response: Response,
    counselor_auth_service: CounselorAuthApplicationService = Depends(get_counselor_auth_service)
) -> APIResponse[CounselorLoginResponse]:
    """상담사 로그인"""
    try:
        # 클라이언트 정보 추출
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        login_response = await counselor_auth_service.login(login_request, client_ip, user_agent)
        
        # httpOnly 쿠키로 JWT 토큰 설정
        if login_response.success:
            # Access Token 쿠키 설정 (짧은 만료 시간)
            response.set_cookie(
                key="counselor_access_token",
                value=login_response.tokens.access_token,
                max_age=30 * 60,  # 30분
                httponly=True,
                secure=True,  # HTTPS에서만 전송
                samesite="strict"  # CSRF 공격 방지
            )
            
            # Refresh Token 쿠키 설정 (긴 만료 시간)
            response.set_cookie(
                key="counselor_refresh_token", 
                value=login_response.tokens.refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7일
                httponly=True,
                secure=True,
                samesite="strict"
            )
        
        return login_response
        
    except HTTPException:
        # HTTPException은 그대로 다시 발생시켜 원래 상태 코드 유지 
        raise
        
    except Exception as e:
        # 예상치 못한 내부 오류만 500으로 변환
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"상담사 로그인 예상치 못한 오류: {str(e)}", exc_info=True)
        
        # 사용자에게는 일반적인 오류 메시지만 반환
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


@auth_router.post(
    "/logout",
    summary="상담사 로그아웃",
    description="상담사 로그아웃하고 쿠키를 삭제합니다."
)
async def counselor_logout(
    request: Request,
    response: Response,
    counselor_auth_service: CounselorAuthApplicationService = Depends(get_counselor_auth_service)
):
    """상담사 로그아웃"""
    try:
        # 현재 상담사 정보 확인 (토큰 검증)
        access_token = request.cookies.get("counselor_access_token")
        if access_token:
            # 서버 측에서 토큰 무효화 처리 (선택사항)
            await counselor_auth_service.get_current_counselor(access_token)
    except HTTPException:
        # 토큰이 이미 유효하지 않더라도 쿠키는 삭제
        pass
    
    # 쿠키 삭제
    response.delete_cookie(
        key="counselor_access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    response.delete_cookie(
        key="counselor_refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {"success": True, "message": "로그아웃되었습니다."}


@auth_router.get(
    "/me",
    response_model=APIResponse[CounselorInfo],
    summary="상담사 정보 조회",
    description="현재 로그인한 상담사의 정보를 조회합니다."
)
@handle_api_errors
async def get_counselor_me(
    current_counselor: CounselorInfo = Depends(get_current_counselor_dependency)
) -> APIResponse[CounselorInfo]:
    """상담사 정보 조회"""
    return current_counselor


@auth_router.patch(
    "/status",
    summary="상담사 상태 업데이트",
    description="상담사의 상담 상태를 업데이트합니다. (1=대기중, 2=상담중, 3=부재중)"
)
async def update_counselor_status(
    status_request: UpdateCounselorStatusRequest,
    current_counselor: CounselorInfo = Depends(get_current_counselor_dependency),
    counselor_auth_service: CounselorAuthApplicationService = Depends(get_counselor_auth_service)
):
    """상담사 상태 업데이트"""
    await counselor_auth_service.counselor_repository.update_counselor_status(
        current_counselor.counselor_id,
        status_request.counselor_status.value
    )
    return {"success": True, "message": "상담사 상태가 업데이트되었습니다."}


@router.get(
    "/specialties",
    response_model=APIResponse[SpecialtyListResponse],
    summary="전문분야 목록 조회",
    description="활성화된 전문분야 목록을 조회합니다."
)
@handle_api_errors
async def get_specialties(
    counselor_auth_service: CounselorAuthApplicationService = Depends(get_counselor_auth_service)
) -> APIResponse[SpecialtyListResponse]:
    """전문분야 목록 조회"""
    specialties = await counselor_auth_service.counselor_repository.get_active_specialties()
    
    specialty_list = [
        SpecialtyInfo(
            specialty_id=str(spec["specialty_code"]),  # MariaDB에서는 code를 ID로 사용
            specialty_code=spec["specialty_code"],
            specialty_name=spec["specialty_name"],
            description=f"{spec['specialty_name']} 전문분야" + (" (사용중)" if spec["in_use"] else "")
        )
        for spec in specialties
    ]
    
    return SpecialtyListResponse(specialties=specialty_list)


@router.get(
    "/health",
    summary="Counselor 서비스 상태 확인",
    description="Counselor 서비스의 상태를 확인합니다.",
    include_in_schema=False
)
async def health_check():
    """Counselor 서비스 헬스체크"""
    return {
        "status": "healthy",
        "service": "counselor",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@auth_router.get(
    "/health",
    summary="Counselor Auth 서비스 상태 확인",
    include_in_schema=False
)
async def auth_health_check():
    """Counselor Auth 서비스 헬스체크"""
    return {
        "status": "healthy",
        "service": "counselor-auth",
        "timestamp": "2024-01-01T00:00:00Z"
    } 