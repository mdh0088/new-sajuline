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
from src.repositories.user_activity_log_repository import UserActivityLogRepository
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.repositories.inquiry_repository import InquiryRepository
from src.services.counselor_service import CounselorService
from src.services.auth_service import AuthService
from src.services.user_activity_log_service import UserActivityLogService
from src.services.consultation_review_service import ConsultationReviewService
from src.services.inquiry_service import InquiryService
from src.schemas.auth_schema import LoginRequest, LoginResponse
from src.schemas.user_activity_log_schema import UserType, DeviceType
from src.common.response import APIResponse, APIResponseBuilder, ok, fail
from src.common.logging import logger, get_logger_with_request_id
from src.common.utils.client_info import extract_client_info
from src.exceptions.custom_exceptions import BaseAppException

router = APIRouter(prefix="/counselors", tags=["counselors"])


# Dependency injection functions
def get_counselor_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorRepository:
    """상담사 리포지토리 의존성 주입"""
    return CounselorRepository(db)


def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()


def get_user_activity_log_repository(db: AsyncSession = Depends(get_db_maria)) -> UserActivityLogRepository:
    """사용자 활동 로그 리포지토리 의존성 주입"""
    return UserActivityLogRepository(db)


def get_user_activity_log_service(
    activity_repo: UserActivityLogRepository = Depends(get_user_activity_log_repository)
) -> UserActivityLogService:
    """사용자 활동 로그 서비스 의존성 주입"""
    return UserActivityLogService(activity_repo)


def get_consultation_review_repository(db: AsyncSession = Depends(get_db_maria)) -> ConsultationReviewRepository:
    """상담 후기 리포지토리 의존성 주입"""
    return ConsultationReviewRepository(db)


def get_consultation_review_service(
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> ConsultationReviewService:
    """상담 후기 서비스 의존성 주입"""
    return ConsultationReviewService(review_repo)


def get_inquiry_repository(db: AsyncSession = Depends(get_db_maria)) -> InquiryRepository:
    """1:1 문의 리포지토리 의존성 주입"""
    return InquiryRepository(db)


def get_inquiry_service(
    inquiry_repo: InquiryRepository = Depends(get_inquiry_repository)
) -> InquiryService:
    """1:1 문의 서비스 의존성 주입"""
    return InquiryService(inquiry_repo)


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
    auth_service: AuthService = Depends(get_auth_service),
    activity_log_service: UserActivityLogService = Depends(get_user_activity_log_service)
):
    """상담사 로그인"""
    log = get_logger_with_request_id()
    log.info("Counselor login attempt", counselor_id=login_request.user_id)
    
    # 클라이언트 정보 추출
    ip_address, user_agent, device_type = extract_client_info(request)
    
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
    
    # 상담사 로그인 성공 활동 로그 기록
    try:
        await activity_log_service.log_login_success(
            user_id=counselor_response.counselor_id,
            user_type=UserType.COUNSELOR,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        log.info("Counselor activity log recorded", counselor_id=counselor_response.counselor_id)
    except Exception as e:
        log.warning("Counselor activity log failed but login succeeded", 
                   counselor_id=counselor_response.counselor_id, 
                   error=str(e))
    
    log.info("Counselor login successful", 
            counselor_id=counselor_response.counselor_id,
            nickname=counselor_response.nickname)
    
    return ok(login_response, "상담사 로그인이 성공했습니다")


@router.get("/{counselor_id}/reviews", response_model=APIResponse, summary="상담사별 후기 목록 조회")
async def get_counselor_reviews(
    counselor_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    visible_only: bool = Query(True, description="공개 후기만 조회"),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service)
) -> APIResponse:
    """
    상담사별 후기 목록을 조회합니다.
    
    - **counselor_id**: 상담사 ID
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    - **visible_only**: 공개 후기만 조회 여부 (기본값: true)
    """
    log = get_logger_with_request_id()
    log.info("API: Getting counselor reviews", 
            counselor_id=counselor_id, 
            page=page, 
            limit=limit, 
            visible_only=visible_only)
    
    # 서비스 호출 (tuple 반환)
    reviews, page, limit, total = await review_service.get_counselor_reviews(
        counselor_id=counselor_id,
        page=page,
        limit=limit,
        visible_only=visible_only
    )
    
    log.info("API: Counselor reviews retrieved successfully", 
            counselor_id=counselor_id,
            count=len(reviews), 
            total=total, 
            page=page, 
            limit=limit)
    
    # APIResponseBuilder.paginated 사용
    return APIResponseBuilder.paginated(
        data=reviews,
        page=page,
        limit=limit,
        total=total,
        message="상담사 후기 목록 조회 성공"
    )


@router.get("/inquiries/users", response_model=APIResponse, summary="상담문의 목록 조회")
async def get_counselor_user_inquiries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    counselor_service: CounselorService = Depends(get_counselor_service),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse:
    """
    상담문의 목록을 조회합니다.
    inquirer_type='USER' AND counselor_id=#{counselor_id}
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    log = get_logger_with_request_id()
    log.info("API: Getting counselor user inquiries", 
            page=page, 
            limit=limit)
    
    # TODO: 현재 로그인된 상담사 ID 가져오기 (JWT 토큰에서)
    # 임시로 하드코딩된 counselor_id 사용
    counselor_id = "temp_counselor_id"
    
    # 서비스 호출 (tuple 반환)
    inquiries, page, limit, total = await inquiry_service.get_counselor_user_inquiries(
        counselor_id=counselor_id,
        page=page,
        limit=limit
    )
    
    log.info("API: Counselor user inquiries retrieved successfully", 
            counselor_id=counselor_id,
            count=len(inquiries), 
            total=total, 
            page=page, 
            limit=limit)
    
    # APIResponseBuilder.paginated 사용
    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="상담문의 목록 조회 성공"
    )


@router.get("/inquiries/admin", response_model=APIResponse, summary="관리자 문의 목록 조회")
async def get_counselor_admin_inquiries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    counselor_service: CounselorService = Depends(get_counselor_service),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse:
    """
    관리자 문의 목록을 조회합니다.
    inquirer_type='COUNSELOR' AND inquirer_id=#{counselor_id}
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    log = get_logger_with_request_id()
    log.info("API: Getting counselor admin inquiries", 
            page=page, 
            limit=limit)
    
    # TODO: 현재 로그인된 상담사 ID 가져오기 (JWT 토큰에서)
    # 임시로 하드코딩된 counselor_id 사용
    counselor_id = "temp_counselor_id"
    
    # 서비스 호출 (tuple 반환)
    inquiries, page, limit, total = await inquiry_service.get_counselor_admin_inquiries(
        counselor_id=counselor_id,
        page=page,
        limit=limit
    )
    
    log.info("API: Counselor admin inquiries retrieved successfully", 
            counselor_id=counselor_id,
            count=len(inquiries), 
            total=total, 
            page=page, 
            limit=limit)
    
    # APIResponseBuilder.paginated 사용
    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="관리자 문의 목록 조회 성공"
    )