"""
User 인터페이스 라우터
사용자 프로필, 설정, 포인트 관리 API 엔드포인트
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...common.exceptions.custom import AuthUnauthorizedException
from ...common.response import APIResponse
from ...common.decorators.error_handler import handle_api_errors
from ...common.logging.config import set_user_id
from ...auth.application.services import AuthApplicationService
from ...auth.infrastructure.providers import get_auth_service as provide_auth_service
from ..domain.entities import (
    UserProfile, UpdateProfileRequest, UpdateProfileResponse,
    AddPointsRequest, UsePointsRequest, PointTransactionResponse, PointTransaction,
    UserSettings, UserSettingsRequest, UserStatsResponse,
    DeleteAccountRequest, DeleteAccountResponse
)
from ..application.services import UserApplicationService
from ..infrastructure.providers import get_user_service as provide_user_service

# FastAPI Router 설정
router = APIRouter(
    prefix="/api/v1/users",
    tags=["사용자"],
    responses={
        400: {"description": "잘못된 요청"},
        401: {"description": "인증 실패"},
        404: {"description": "사용자를 찾을 수 없음"},
        422: {"description": "검증 오류"},
        500: {"description": "서버 오류"}
    }
)

# JWT Bearer 토큰 스킴
security = HTTPBearer()


async def get_auth_service(
    service: AuthApplicationService = Depends(provide_auth_service),
) -> AuthApplicationService:
    return service


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthApplicationService = Depends(get_auth_service)
) -> str:
    """현재 사용자 ID 추출"""
    if not credentials:
        raise AuthUnauthorizedException(message="인증 토큰이 필요합니다.")
    
    user_id = await auth_service.validate_token(credentials.credentials)
    if not user_id:
        raise AuthUnauthorizedException(message="유효하지 않은 토큰입니다.")
    
    # 요청 컨텍스트 및 로깅 컨텍스트 설정
    try:
        request.state.user_id = user_id
        request.state.user_token = set_user_id(user_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "로깅을 위한 사용자 컨텍스트 설정 실패: %s", e, exc_info=False
        )
    return user_id


@router.get(
    "/me",
    response_model=APIResponse[UserProfile],
    summary="내 프로필 조회",
    description="현재 로그인된 사용자의 프로필 정보를 조회합니다.",
    responses={
        200: {"description": "프로필 조회 성공"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자 프로필을 찾을 수 없음"},
    }
)
@handle_api_errors
async def get_my_profile(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[UserProfile]:
    """내 프로필 조회"""
    return await user_service.get_user_profile(current_user_id)


@router.put(
    "/me",
    response_model=APIResponse[UpdateProfileResponse],
    summary="내 프로필 업데이트",
    description="현재 로그인된 사용자의 프로필 정보를 업데이트합니다.",
    responses={
        200: {"description": "프로필 업데이트 성공"},
        400: {"description": "중복된 닉네임 또는 전화번호"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def update_my_profile(
    update_request: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[UpdateProfileResponse]:
    """내 프로필 업데이트"""
    return await user_service.update_profile(current_user_id, update_request)


@router.post(
    "/points/add",
    response_model=APIResponse[PointTransactionResponse],
    summary="포인트 추가",
    description="사용자 계정에 포인트를 추가합니다.",
    responses={
        200: {"description": "포인트 추가 성공"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def add_points(
    add_request: AddPointsRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[PointTransactionResponse]:
    """포인트 추가"""
    return await user_service.add_points(current_user_id, add_request)


@router.post(
    "/points/use",
    response_model=APIResponse[PointTransactionResponse],
    summary="포인트 사용",
    description="사용자 계정의 포인트를 사용합니다.",
    responses={
        200: {"description": "포인트 사용 성공"},
        400: {"description": "포인트 잔액 부족"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def use_points(
    use_request: UsePointsRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[PointTransactionResponse]:
    """포인트 사용"""
    return await user_service.use_points(current_user_id, use_request)


@router.get(
    "/points/transactions",
    response_model=APIResponse[List[PointTransaction]],
    summary="포인트 거래 내역",
    description="사용자의 포인트 거래 내역을 조회합니다.",
    responses={
        200: {"description": "거래 내역 조회 성공"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def get_point_transactions(
    limit: int = Query(20, ge=1, le=100, description="조회할 거래 수"),
    offset: int = Query(0, ge=0, description="건너뛸 거래 수"),
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[List[PointTransaction]]:
    """포인트 거래 내역 조회"""
    return await user_service.get_point_transactions(current_user_id, limit, offset)


@router.get(
    "/settings",
    response_model=APIResponse[UserSettings],
    summary="사용자 설정 조회",
    description="현재 사용자의 설정을 조회합니다.",
    responses={
        200: {"description": "설정 조회 성공"},
        401: {"description": "인증되지 않은 사용자"},
    }
)
@handle_api_errors
async def get_user_settings(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[UserSettings]:
    """사용자 설정 조회"""
    return await user_service.get_user_settings(current_user_id)


@router.put(
    "/settings",
    response_model=APIResponse[UserSettings],
    summary="사용자 설정 업데이트",
    description="현재 사용자의 설정을 업데이트합니다.",
    responses={
        200: {"description": "설정 업데이트 성공"},
        401: {"description": "인증되지 않은 사용자"},
    }
)
@handle_api_errors
async def update_user_settings(
    settings_request: UserSettingsRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[UserSettings]:
    """사용자 설정 업데이트"""
    return await user_service.update_user_settings(current_user_id, settings_request)


@router.get(
    "/stats",
    response_model=APIResponse[UserStatsResponse],
    summary="사용자 통계",
    description="현재 사용자의 이용 통계를 조회합니다.",
    responses={
        200: {"description": "통계 조회 성공"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def get_user_stats(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[UserStatsResponse]:
    """사용자 통계 조회"""
    return await user_service.get_user_stats(current_user_id)


@router.delete(
    "/me",
    response_model=APIResponse[DeleteAccountResponse],
    summary="계정 삭제",
    description="현재 사용자의 계정을 삭제합니다.",
    responses={
        200: {"description": "계정 삭제 성공"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
    }
)
@handle_api_errors
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(provide_user_service)
) -> APIResponse[DeleteAccountResponse]:
    """계정 삭제"""
    return await user_service.delete_account(current_user_id, delete_request)


@router.get(
    "/health",
    response_model=APIResponse[dict],
    summary="User 서비스 상태 확인",
    description="User 서비스의 상태를 확인합니다.",
    include_in_schema=False  # Swagger 문서에서 숨김
)
@handle_api_errors
async def health_check() -> APIResponse[dict]:
    """User 서비스 헬스체크"""
    import datetime
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "user",
            "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        error=None,
        meta=None,
    ) 