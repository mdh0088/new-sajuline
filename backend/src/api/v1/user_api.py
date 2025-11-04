"""
사용자 관련 API 엔드포인트
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

# 레이트 리미팅 import 추가
from src.common.middleware.rate_limit import limiter

from src.core.database import get_db_maria, get_db_mssql
from src.core.redis import get_redis
from src.repositories.user_repository import UserRepository
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.event_repository import EventRepository
from src.repositories.point_transaction_repository import PointTransactionRepository
from src.repositories.user_activity_log_repository import UserActivityLogRepository
from src.repositories.ars.tm60_users_repository import Tm60UsersRepository
from src.services.ars.tm60_users_service import Tm60UsersService
from src.repositories.user_bookmark_repository import UserBookmarkRepository
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.grade_repository import GradeRepository
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.services.user_service import UserService
from src.services.auth_service import AuthService, get_current_user, TokenPayload
from src.services.event_service import EventService
from src.services.point_transaction_service import PointTransactionService
from src.services.user_activity_log_service import UserActivityLogService
from src.services.user_bookmark_service import UserBookmarkService
from src.services.consultation_review_service import ConsultationReviewService
from src.services.payment_service import PaymentService
from src.services.grade_service import GradeService
from src.services.ars.tm60_chatlog_service import Tm60ChatlogService
from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.services.point_transaction_service import PointTransactionService
from src.schemas.consultation_review_schema import (
    UserReviewSummary,
    UserReviewList,
    PendingReviewList,
    UserReviewCreateRequest,
    UserReviewUpdateRequest,
    ConsultationReviewResponse,
)
from src.schemas.user_schema import (
    UserResponse, UserSignup, UserMypageResponse, SearchType, OrderType,
    FindIdRequest, FindIdResponse, FindPasswordRequest, FindPasswordResponse
)
from src.common.utils.auth_utils import verify_user_role
from src.schemas.user_bookmark_schema import UserBookmarkResponse
from src.schemas.counselor_schema import CounselorSearchItem
from src.schemas.auth_schema import LoginRequest, LoginResponse
from src.common.response import APIResponse,APIResponseBuilder, ok, fail
from src.repositories.inquiry_repository import InquiryRepository
from src.services.inquiry_service import InquiryService
from src.schemas.inquiry_schema import UserInquiryCreateRequest, InquiryResponse, UserAdminInquiryCreateRequest
from src.common.logging import logger, get_logger_with_request_id
from src.common.utils.client_info import extract_client_info
from src.exceptions.custom_exceptions import BaseAppException
router = APIRouter(prefix="/users", tags=["users"])


# Dependency injection functions
def get_user_repository(db: AsyncSession = Depends(get_db_maria)) -> UserRepository:
    """사용자 리포지토리 의존성 주입"""
    return UserRepository(db)


def get_counselor_repository(db: AsyncSession = Depends(get_db_maria)) -> CounselorRepository:
    """상담사 리포지토리 의존성 주입"""
    return CounselorRepository(db)


def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()


def get_event_repository(db: AsyncSession = Depends(get_db_maria)) -> EventRepository:
    """이벤트 리포지토리 의존성 주입"""
    return EventRepository(db)


def get_point_transaction_repository(db: AsyncSession = Depends(get_db_maria)) -> PointTransactionRepository:
    """포인트 거래 리포지토리 의존성 주입"""
    return PointTransactionRepository(db)


def get_tm60_users_service():
    """TM60 사용자 서비스 의존성 주입"""
    for mssql_session in get_db_mssql():
        repo = Tm60UsersRepository(mssql_session)
        return Tm60UsersService(repo)


def get_user_activity_log_repository(db: AsyncSession = Depends(get_db_maria)) -> UserActivityLogRepository:
    """사용자 활동 로그 리포지토리 의존성 주입"""
    return UserActivityLogRepository(db)


def get_point_transaction_service(
    point_transaction_repo: PointTransactionRepository = Depends(get_point_transaction_repository)
) -> PointTransactionService:
    """포인트 거래 서비스 의존성 주입"""
    return PointTransactionService(point_transaction_repo)


def get_user_activity_log_service(
    activity_log_repo: UserActivityLogRepository = Depends(get_user_activity_log_repository)
) -> UserActivityLogService:
    """사용자 활동 로그 서비스 의존성 주입"""
    return UserActivityLogService(activity_log_repo)


def get_event_service(
    event_repo: EventRepository = Depends(get_event_repository),
    point_transaction_service: PointTransactionService = Depends(get_point_transaction_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> EventService:
    """이벤트 서비스 의존성 주입"""
    return EventService(event_repo, point_transaction_service, tm60_users_service)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
    event_service: EventService = Depends(get_event_service),
    activity_log_service: UserActivityLogService = Depends(get_user_activity_log_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> UserService:
    """사용자 서비스 의존성 주입"""
    return UserService(user_repo, counselor_repo, auth_service, activity_log_service, event_service, tm60_users_service)


# 마이페이지용 추가 의존성 주입 함수들
def get_user_bookmark_repository(db: AsyncSession = Depends(get_db_maria)) -> UserBookmarkRepository:
    """사용자 북마크 리포지토리 의존성 주입"""
    return UserBookmarkRepository(db)


def get_consultation_review_repository(db: AsyncSession = Depends(get_db_maria)) -> ConsultationReviewRepository:
    """상담 후기 리포지토리 의존성 주입"""
    return ConsultationReviewRepository(db)


def get_inquiry_repository(db: AsyncSession = Depends(get_db_maria)) -> InquiryRepository:
    return InquiryRepository(db)


def get_inquiry_service(
    inquiry_repo: InquiryRepository = Depends(get_inquiry_repository)
) -> InquiryService:
    return InquiryService(inquiry_repo)


def get_payment_repository(db: AsyncSession = Depends(get_db_maria)) -> PaymentRepository:
    """결제 리포지토리 의존성 주입"""
    return PaymentRepository(db)


def get_grade_repository(db: AsyncSession = Depends(get_db_maria)) -> GradeRepository:
    """등급 리포지토리 의존성 주입"""
    return GradeRepository(db)


def get_tm60_chatlog_repository():
    """TM60 채팅로그 리포지토리 의존성 주입"""
    for mssql_session in get_db_mssql():
        return Tm60ChatlogRepository(mssql_session)


def get_user_bookmark_service(
    bookmark_repo: UserBookmarkRepository = Depends(get_user_bookmark_repository),
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> UserBookmarkService:
    """사용자 북마크 서비스 의존성 주입 (후기 리포지토리 포함)"""
    return UserBookmarkService(bookmark_repo, review_repo)


def get_consultation_review_service(
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> ConsultationReviewService:
    """상담 후기 서비스 의존성 주입"""
    return ConsultationReviewService(review_repo)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repository)
) -> PaymentService:
    """결제 서비스 의존성 주입"""
    return PaymentService(payment_repo)


def get_grade_service(
    grade_repo: GradeRepository = Depends(get_grade_repository)
) -> GradeService:
    """등급 서비스 의존성 주입"""
    return GradeService(grade_repo)


def get_tm60_chatlog_service() -> Tm60ChatlogService:
    """TM60 채팅로그 서비스 의존성 주입"""
    for mssql_session in get_db_mssql():
        return Tm60ChatlogService(mssql_session)

def get_tm60_chatlog_repository():
    for mssql_session in get_db_mssql():
        return Tm60ChatlogRepository(mssql_session)




@router.get(
    "/inquiries",
    response_model=APIResponse,
    summary="사용자 → 관리자 문의 목록 조회"
)
async def get_user_admin_inquiries_api(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse:
    """
    사용자 → 관리자 문의 목록을 조회합니다.
    inquirer_id=#{user_id} AND category='USER_TO_ADMIN'

    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub
    log.info("API: Getting user admin inquiries",
            user_id=user_id,
            page=page,
            limit=limit)

    # 서비스 호출 (tuple 반환)
    inquiries, page, limit, total = await inquiry_service.get_user_admin_inquiries(
        user_id=user_id,
        page=page,
        limit=limit
    )

    log.info("API: User admin inquiries retrieved successfully",
            user_id=user_id,
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
        message="사용자 문의 목록 조회 성공"
    )


@router.post(
    "/inquiries",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 관리자 문의 등록",
    status_code=status.HTTP_201_CREATED
)
async def create_user_admin_inquiry_api(
    payload: UserAdminInquiryCreateRequest,
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse[InquiryResponse]:
    """
    로그인 사용자 기준으로 관리자에게 문의 등록

    - **inquiry_type**: PAY(결제문의), ACCOUNT(계정문의), CS(상담문의), EVENT(이벤트문의), ETC(기타문의)
    - **title**: 제목 (선택)
    - **content**: 문의 내용 (필수)
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub
    log.info("API: Creating user admin inquiry",
            user_id=user_id,
            inquiry_type=payload.inquiry_type)

    result = await inquiry_service.create_user_admin_inquiry(
        user_id=user_id,
        payload=payload
    )

    log.info("API: User admin inquiry created successfully",
            user_id=user_id,
            inquiry_id=result.inquiry_id)

    return ok(data=result, message="문의가 등록되었습니다.")


@router.get(
    "/inquiries/{inquiry_id}",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 관리자 문의 상세 조회"
)
async def get_user_admin_inquiry_detail_api(
    inquiry_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse[InquiryResponse]:
    """
    사용자 → 관리자 문의 상세 조회

    - **inquiry_id**: 문의 ID
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub
    log.info("API: Getting user admin inquiry detail",
            user_id=user_id,
            inquiry_id=inquiry_id)

    result = await inquiry_service.get_user_admin_inquiry_detail(
        inquiry_id=inquiry_id,
        user_id=user_id
    )

    log.info("API: User admin inquiry detail retrieved successfully",
            user_id=user_id,
            inquiry_id=inquiry_id)

    return ok(data=result, message="문의 상세 조회 성공")


@router.post(
    "/inquiries/counselor",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 상담사 문의 등록",
    status_code=status.HTTP_201_CREATED
)
async def create_user_inquiry_api(
    payload: UserInquiryCreateRequest,
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse[InquiryResponse]:
    """로그인 사용자 기준으로 상담사에게 문의 등록"""
    result = await inquiry_service.create_user_inquiry(user_id=current_user.sub, payload=payload)
    return ok(data=result, message="문의가 등록되었습니다.")

@router.post(
    "/signup",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="통합 회원가입",
    description="이메일과 비밀번호로 일반 회원가입 또는 소셜 정보로 소셜 회원가입을 처리합니다.",
    responses={
        201: {"description": "회원가입 성공"},
        400: {"description": "중복된 사용자 정보 또는 유효하지 않은 입력"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("20/hour")  # 시간당 20회 제한 (어뷰징 방지)
async def signup(
    request: Request,  # Rate Limiting 필수
    signup_data: UserSignup,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """통합 회원가입 - 일반/소셜 가입 통합 처리"""
    if not signup_data.phone_chk:
        raise BaseAppException("휴대폰 인증이 필요합니다.", status_code=400)

    result = await user_service.signup(signup_data)
    return ok(data=result, message="회원가입이 완료되었습니다.")


@router.post(
    "/social/signup",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="소셜 회원가입 (자동 로그인)",
    description="소셜 회원가입과 동시에 자동 로그인 처리하여 JWT 토큰을 HttpOnly 쿠키에 설정합니다.",
    responses={
        201: {"description": "회원가입 및 로그인 성공"},
        400: {"description": "중복된 사용자 정보 또는 유효하지 않은 입력"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("20/hour")  # 시간당 20회 제한 (어뷰징 방지)
async def social_signup_with_login(
    request: Request,  # Rate Limiting 필수
    response: Response,
    signup_data: UserSignup,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """소셜 회원가입 + 자동 로그인"""
    log = get_logger_with_request_id()
    log.info("Social signup with auto-login attempt", user_id=signup_data.user_id, provider=signup_data.social_provider)

    # 휴대폰 인증 검증
    if not signup_data.phone_chk:
        raise BaseAppException("휴대폰 인증이 필요합니다.", status_code=400)

    # 소셜 정보 필수 검증
    if not signup_data.social_provider or not signup_data.social_id:
        raise BaseAppException("소셜 회원가입에는 social_provider와 social_id가 필수입니다.", status_code=400)

    # 회원가입 처리
    result = await user_service.signup(signup_data)
    
    # 자동 로그인을 위한 JWT 토큰들 생성
    auth_service = AuthService()
    access_token = auth_service.create_access_token(
        user_id=result.user_id,
        email=result.email,
        role="user"
    )
    
    refresh_token = auth_service.create_refresh_token(
        user_id=result.user_id,
        email=result.email,
        role="user"
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
    
    # 마지막 로그인 시간 업데이트
    await user_service.user_repo.update_last_login(result.user_id)
    
    log.info("Social signup with auto-login completed with refresh token", user_id=result.user_id, provider=signup_data.social_provider)
    return ok(data=result, message="소셜 회원가입 및 로그인이 완료되었습니다.")











# TODO: 사용자 목록 조회 - 추후 참고용
# @router.get(
#     "/", 
#     response_model=UserListResponse,
#     summary="사용자 목록 조회",
#     description="페이지네이션과 상태 필터 지원"
# )
# async def get_user_list(
#     page: int = Query(1, ge=1, description="페이지 번호"),
#     size: int = Query(20, ge=1, le=100, description="페이지 크기"),
#     user_status: Optional[str] = Query(None, description="사용자 상태 필터"),
#     user_service: UserService = Depends(get_user_service)
# ):
#     """사용자 목록 조회 - 페이징 및 상태별 필터링"""
#     return await user_service.get_user_list(page, size, user_status)


@router.post(
    "/authenticate", 
    response_model=UserResponse,
    summary="사용자 인증",
    responses={
        401: {"description": "인증 실패"},
        423: {"description": "계정 잠금"}
    }
)
@limiter.limit("10/minute")  # 분당 10회 제한 (브루트포스 공격 방지)
async def authenticate_user(
    request: Request,
    login_data: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 인증 - ID/이메일 및 비밀번호 검증"""
    return await user_service.authenticate_user(login_data.user_id, login_data.password)


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="사용자 로그인",
    description="사용자 ID와 비밀번호로 로그인하고 JWT 토큰을 HttpOnly 쿠키에 설정",
    responses={
        200: {"description": "로그인 성공"},
        401: {"description": "인증 실패"},
        403: {"description": "계정 비활성화"},
        423: {"description": "계정 잠금"}
    }
)
@limiter.limit("15/minute")  # 분당 15회 제한 (로그인 시도 제한)
async def login(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_maria),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """사용자 로그인"""
    log = get_logger_with_request_id()
    log.info("Login attempt", user_id=login_request.user_id)
    
    # 테스트용 강제 API 레이어 오류 발생  
    if login_request.user_id == "api_error_test":
        raise BaseAppException("API layer: 예상치 못한 시스템 오류 테스트", status_code=500)
    
    # 클라이언트 정보 추출
    client_ip, user_agent, device_type = extract_client_info(request)
    
    # 로그인 처리 (예외는 전역 핸들러에서 처리)
    access_token, user_response = await user_service.login(
        user_id_or_email=login_request.user_id,
        password=login_request.password,
        client_ip=client_ip,
        user_agent=user_agent,
        device_type=device_type
    )
    
    # Refresh Token 생성
    refresh_token = auth_service.create_refresh_token(
        user_id=user_response.user_id,
        email=user_response.email,
        role="user"
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
        user_id=user_response.user_id,
        email=user_response.email,
        nickname=user_response.nickname,
        access_token_expires_in=30 * 60,  # 30분 (초 단위)
        refresh_token_expires_in=7 * 24 * 60 * 60  # 7일 (초 단위)
    )
    
    log.info("Authentication successful with refresh token", user_id=user_response.user_id)
    return ok(data=login_response, message="로그인 성공")


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="사용자 로그아웃",
    description="현재 로그인된 사용자를 로그아웃하고 JWT 토큰 쿠키를 삭제",
    responses={200: {"description": "로그아웃 성공"}}
)
async def logout(
    request: Request,
    response: Response,
    current_user: TokenPayload = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    redis_client = Depends(get_redis)
):
    """사용자 로그아웃"""
    log = get_logger_with_request_id()
    
    try:
        # 현재 토큰들을 블랙리스트에 추가 (보안 강화)
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        # Access Token 블랙리스트 처리
        if access_token:
            from datetime import datetime
            access_expires = datetime.fromtimestamp(current_user.exp)
            await auth_service.blacklist_token(
                jti=current_user.jti,
                expires_at=access_expires,
                redis_client=redis_client
            )
        
        # Refresh Token 블랙리스트 처리
        if refresh_token:
            try:
                refresh_payload = await auth_service.verify_refresh_token(refresh_token, redis_client)
                refresh_expires = datetime.fromtimestamp(refresh_payload["exp"])
                await auth_service.blacklist_token(
                    jti=refresh_payload["jti"],
                    expires_at=refresh_expires,
                    redis_client=redis_client
                )
            except Exception as e:
                # refresh token이 이미 만료되었거나 유효하지 않은 경우
                log.warning("Failed to blacklist refresh token during logout", 
                           user_id=current_user.sub, error=str(e))
    
    except Exception as e:
        # 블랙리스트 처리 실패해도 로그아웃은 진행 (쿠키 삭제)
        log.warning("Token blacklist failed during logout", 
                   user_id=current_user.sub, error=str(e))
    
    # HttpOnly 쿠키에서 JWT 토큰들 삭제
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    log.info("User logout successful", user_id=current_user.sub, email=current_user.email)
    return ok(data=None, message="로그아웃 성공")


# 중복 검사 API들
@router.get(
    "/check-availability/email",
    response_model=APIResponse[bool],
    summary="이메일 중복 검사",
    description="입력된 이메일이 사용 가능한지 확인합니다.",
    responses={
        200: {"description": "검사 완료"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한 (실시간 검증용)
async def check_email_availability(
    request: Request,
    value: str = Query(..., description="검사할 이메일"),
    user_service: UserService = Depends(get_user_service)
):
    """이메일 중복 검사"""
    available = await user_service.check_email_availability(value)
    message = "사용 가능한 이메일입니다." if available else "이미 사용 중인 이메일입니다."
    return ok(data=available, message=message)


@router.get(
    "/check-availability/user-id",
    response_model=APIResponse[bool],
    summary="사용자 ID 중복 검사",
    description="입력된 사용자 ID가 사용 가능한지 확인합니다.",
    responses={
        200: {"description": "검사 완료"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한 (실시간 검증용)
async def check_user_id_availability(
    request: Request,
    value: str = Query(..., description="검사할 사용자 ID"),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 ID 중복 검사"""
    available = await user_service.check_user_id_availability(value)
    message = "사용 가능한 ID입니다." if available else "이미 사용 중인 ID입니다."
    return ok(data=available, message=message)


@router.get(
    "/check-availability/phone",
    response_model=APIResponse[bool],
    summary="전화번호 중복 검사",
    description="입력된 전화번호가 사용 가능한지 확인합니다.",
    responses={
        200: {"description": "검사 완료"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한 (실시간 검증용)
async def check_phone_availability(
    request: Request,
    value: str = Query(..., description="검사할 전화번호"),
    user_service: UserService = Depends(get_user_service)
):
    """전화번호 중복 검사"""
    available = await user_service.check_phone_availability(value)
    message = "사용 가능한 전화번호입니다." if available else "이미 사용 중인 전화번호입니다."
    return ok(data=available, message=message)


@router.get(
    "/check-availability/nickname",
    response_model=APIResponse[bool],
    summary="닉네임 중복 검사",
    description="입력된 닉네임이 사용 가능한지 확인합니다.",
    responses={
        200: {"description": "검사 완료"},
        429: {"description": "요청 한도 초과"}
    }
)
@limiter.limit("30/minute")  # 분당 30회 제한 (실시간 검증용)
async def check_nickname_availability(
    request: Request,
    value: str = Query(..., description="검사할 닉네임"),
    user_service: UserService = Depends(get_user_service)
):
    """닉네임 중복 검사"""
    available = await user_service.check_nickname_availability(value)
    message = "사용 가능한 닉네임입니다." if available else "이미 사용 중인 닉네임입니다."
    return ok(data=available, message=message)


@router.post(
    "/find-id",
    response_model=APIResponse[FindIdResponse],
    summary="사용자 ID 찾기",
    description="핸드폰 본인인증을 통해 등록된 사용자 ID를 찾습니다.",
    responses={
        200: {"description": "ID 찾기 성공"},
        404: {"description": "사용자를 찾을 수 없음"}
    }
)
async def find_user_id(
    find_id_data: FindIdRequest,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[FindIdResponse]:
    """핸드폰 본인인증 기반 ID 찾기"""
    log = get_logger_with_request_id()
    log.info("Find ID attempt", phone=find_id_data.phone)

    result = await user_service.find_user_id(find_id_data.phone)

    log.info("Find ID successful", user_id=result.user_id)
    return ok(data=result, message="아이디를 찾았습니다.")


@router.post(
    "/find-password",
    response_model=APIResponse[FindPasswordResponse],
    summary="비밀번호 찾기 (임시 비밀번호 발급)",
    description="사용자 ID와 핸드폰 본인인증을 통해 임시 비밀번호를 이메일로 전송합니다. (일반 회원가입 회원만 가능)",
    responses={
        200: {"description": "임시 비밀번호 발급 및 이메일 전송 성공"},
        404: {"description": "사용자를 찾을 수 없음 (정보 불일치 또는 SNS 가입 회원)"},
        400: {"description": "이메일 전송 실패"}
    }
)
async def find_password(
    find_password_data: FindPasswordRequest,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[FindPasswordResponse]:
    """비밀번호 찾기 - 임시 비밀번호 발급 및 이메일 전송"""
    log = get_logger_with_request_id()
    log.info("Find password attempt", user_id=find_password_data.user_id, phone=find_password_data.phone)

    result = await user_service.find_password(find_password_data)

    log.info("Find password successful", user_id=result.user_id, email=result.email)
    return ok(data=result, message=result.message)


@router.get(
    "/mypage",
    response_model=APIResponse[UserMypageResponse],
    summary="사용자 마이페이지 정보 조회",
    description="로그인한 사용자의 마이페이지에 필요한 통합 정보를 조회합니다.",
    responses={
        200: {"description": "마이페이지 정보 조회 성공"},
        401: {"description": "인증 필요"},
        404: {"description": "사용자 정보 없음"},
        500: {"description": "서버 오류"}
    }
)
@limiter.limit("100/minute")  # 분당 100회 제한 (마이페이지는 자주 조회될 수 있음)
async def get_user_mypage(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    bookmark_service: UserBookmarkService = Depends(get_user_bookmark_service),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
    payment_service: PaymentService = Depends(get_payment_service),
    grade_service: GradeService = Depends(get_grade_service),
    tm60_chatlog_service: Tm60ChatlogService = Depends(get_tm60_chatlog_service),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service)
) -> APIResponse[UserMypageResponse]:
    """사용자 마이페이지 통합 정보 조회"""
    log = get_logger_with_request_id()
    user_id = current_user.sub
    log.info("Getting user mypage info", user_id=user_id)
    
    try:
        # 1. 기본 사용자 정보 조회
        user_info = await user_service.user_repo.get_by_id(user_id)
        if not user_info:
            log.warning("User not found for mypage", user_id=user_id)
            raise BaseAppException("사용자 정보를 찾을 수 없습니다.", status_code=404)
        
        user_response = UserResponse.model_validate(user_info)
        
        # 2. 상담 수 조회 (tm60_chatlog)
        consultation_count = await tm60_chatlog_service.get_user_consultation_count(user_id)
        
        # 3. 즐겨찾기 수 조회 (t_user_bookmark)
        bookmark_count_response = await bookmark_service.get_bookmark_count_by_user(user_id)
        bookmark_count = bookmark_count_response.bookmark_count
        
        # 4. 후기 수 조회 (t_consultation_review)
        review_count_response = await review_service.get_user_review_count(user_id)
        review_count = review_count_response.review_count
        
        # 5. 포인트 조회 (tm60_users)
        current_points = await tm60_users_service.get_user_points(user_id)
        
        # 6. 등급 정보 조회 (t_grade)
        grade_info = await grade_service.get_next_grade_info(user_info.grade_code)
        
        # 7. 이번 달 결제 총액 조회 (t_payment)
        monthly_payment_total = await payment_service.get_user_monthly_total_payment_amount(user_id)
        
        # 8. 통합 응답 생성
        mypage_response = UserMypageResponse(
            user_info=user_response,
            total_consultation_count=consultation_count,
            total_bookmark_count=bookmark_count,
            total_review_count=review_count,
            current_points=current_points,
            grade_info=grade_info,
            monthly_payment_total=monthly_payment_total
        )
        
        log.info("User mypage info retrieved successfully", 
                user_id=user_id,
                consultation_count=consultation_count,
                bookmark_count=bookmark_count,
                review_count=review_count,
                current_points=current_points,
                current_grade=grade_info.current_grade.grade_name,
                monthly_payment=monthly_payment_total)
        
        return ok(data=mypage_response, message="마이페이지 정보 조회 성공")

        
    except BaseAppException:
        # 이미 정의된 예외는 그대로 재발생
        raise
    except Exception as e:
        log.warning("Mypage info retrieval failed", 
                   user_id=user_id, 
                   error=str(e))
        raise BaseAppException(f"마이페이지 정보 조회 중 오류가 발생했습니다: {str(e)}", status_code=500)


# =====================================================
# User Reviews APIs (/user/review 요구사항)
# =====================================================

@router.get(
    "/reviews/summary",
    response_model=APIResponse[UserReviewSummary],
    summary="사용자 후기 요약 정보",
)
async def get_user_review_summary_api(
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
    tm60_chatlog_repo: Tm60ChatlogRepository = Depends(get_tm60_chatlog_repository),
) -> APIResponse[UserReviewSummary]:
    data = await review_service.get_user_review_summary(
        user_id=current_user.sub,
        chatlog_repo=tm60_chatlog_repo,
    )
    return ok(data=data, message="후기 요약 조회 성공")


@router.get(
    "/reviews",
    response_model=APIResponse,
    summary="사용자 후기 목록 조회 (작성/대기)",
    description="searchtype = my_reviews | pending_reviews, page/limit 기반"
)
async def get_user_reviews_api(
    searchtype: str = Query("my_reviews"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
    tm60_chatlog_repo: Tm60ChatlogRepository = Depends(get_tm60_chatlog_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
):
    if searchtype == "my_reviews":
        data, total = await review_service.get_my_reviews_detailed(
            user_id=current_user.sub,
            page=page,
            limit=limit,
            chatlog_repo=tm60_chatlog_repo,
            counselor_repo=counselor_repo,
        )
        return APIResponseBuilder.paginated(
            data=data.items,
            page=page,
            limit=limit,
            total=total,
            message="작성한 후기 목록 조회 성공",
        )

    if searchtype == "pending_reviews":
        data, total = await review_service.get_pending_reviews(
            user_id=current_user.sub,
            page=page,
            limit=limit,
            chatlog_repo=tm60_chatlog_repo,
            counselor_repo=counselor_repo,
        )
        return APIResponseBuilder.paginated(
            data=data.items,
            page=page,
            limit=limit,
            total=total,
            message="작성 대기 목록 조회 성공",
        )

    raise BaseAppException("유효하지 않은 searchtype 입니다. my_reviews | pending_reviews", status_code=400)


@router.post(
    "/reviews",
    response_model=APIResponse[ConsultationReviewResponse],
    summary="사용자 후기 생성 (포인트 지급 포함)",
)
async def create_user_review_api(
    payload: UserReviewCreateRequest,
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
    tm60_chatlog_repo: Tm60ChatlogRepository = Depends(get_tm60_chatlog_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    tm60_users_service: Tm60UsersService = Depends(get_tm60_users_service),
    point_tx_service: PointTransactionService = Depends(get_point_transaction_service),
) -> APIResponse[ConsultationReviewResponse]:
    result = await review_service.create_user_review_with_award(
        user_id=current_user.sub,
        payload=payload,
        chatlog_repo=tm60_chatlog_repo,
        counselor_repo=counselor_repo,
        tm60_users_service=tm60_users_service,
        point_transaction_service=point_tx_service,
    )
    return ok(data=result, message="후기 작성 성공")


@router.put(
    "/reviews",
    response_model=APIResponse[ConsultationReviewResponse],
    summary="사용자 후기 수정 (세션 기준)",
)
async def update_user_review_api(
    payload: UserReviewUpdateRequest,
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
) -> APIResponse[ConsultationReviewResponse]:
    updated = await review_service.update_user_review_by_session(
        user_id=current_user.sub,
        payload=payload,
    )
    return ok(data=updated, message="후기 수정 성공")


@router.delete(
    "/reviews/{review_id}",
    response_model=APIResponse[bool],
    summary="사용자 후기 삭제 (상담사 답변 존재 시 불가)",
)
async def delete_user_review_api(
    review_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
) -> APIResponse[bool]:
    success = await review_service.delete_user_review_with_check(review_id=review_id, user_id=current_user.sub)
    return ok(data=success, message="후기 삭제 성공")

@router.get(
    "/points/history",
    response_model=APIResponse,
    summary="사용자 포인트 내역 조회",
    description=(
        "search_type=point_charge → t_payment + t_point_product 조인하여 (paid_at, product_name, point_amount) 반환.\n"
        "search_type=point_use → tm60_chatlog에서 (chatstart, chatend, 상담사정보, usepoint) 반환."
    ),
)
async def get_point_history(
    start_dt: str = Query(..., description="시작일 (yyyy-mm-dd)"),
    end_dt: str = Query(..., description="종료일 (yyyy-mm-dd)"),
    search_type: SearchType = Query(...),
    order_type: OrderType = Query("latest"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    tm60_chatlog_repo: Tm60ChatlogRepository = Depends(get_tm60_chatlog_repository),
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
) -> APIResponse:
    """사용자 포인트 내역 조회"""
    data, total = await user_service.get_point_history(
        user_id=current_user.sub,
        start_dt=start_dt,
        end_dt=end_dt,
        search_type=search_type,
        order_type=order_type,
        payment_repo=payment_repo,
        chatlog_repo=tm60_chatlog_repo,
        counselor_repo=counselor_repo,
        page=page,
        limit=limit,
    )
    # 페이지네이션 메타 포함 응답
    
    return APIResponseBuilder.paginated(
        data=data.items_charge if search_type == 'point_charge' else data.items_use or [],
        page=page,
        limit=limit,
        total=total,
        message="포인트 내역 조회 성공"
    )


# =====================
# 즐겨찾기 API
# =====================

@router.get(
    "/bookmarks",
    response_model=APIResponse,
    summary="사용자 즐겨찾기 상담사 목록",
    description=(
        "t_user_bookmark ⋈ t_counselor (counselor_id) 조인으로 상담사 목록 반환.\n"
        "조건: t_counselor.is_out = false AND t_counselor.is_show = true.\n"
        "정렬: t_user_bookmark.created_at DESC. 페이지네이션 지원"
    ),
)
async def list_bookmarks(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user),
    bookmark_service: UserBookmarkService = Depends(get_user_bookmark_service),
):
    verify_user_role(current_user)
    items, total = await bookmark_service.get_favorite_counselors(
        user_id=current_user.sub,
        page=page,
        limit=limit,
    )
    return APIResponseBuilder.paginated(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message="즐겨찾기 상담사 목록 조회 성공",
    )

@router.get(
    "/bookmarks/check",
    response_model=APIResponse[bool],
    summary="사용자 즐겨찾기 여부 조회"
)
async def check_bookmark(
    counselor_id: str = Query(..., description="상담사 ID"),
    current_user: TokenPayload = Depends(get_current_user),
    bookmark_service: UserBookmarkService = Depends(get_user_bookmark_service)
) -> APIResponse[bool]:
    # 권한: 일반 사용자만
    verify_user_role(current_user)
    is_marked = await bookmark_service.is_bookmarked(current_user.sub, counselor_id)
    return ok(data=is_marked, message="즐겨찾기 여부 조회 성공")


@router.post(
    "/bookmarks",
    response_model=APIResponse[UserBookmarkResponse],
    summary="사용자 즐겨찾기 등록"
)
async def add_bookmark(
    counselor_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    bookmark_service: UserBookmarkService = Depends(get_user_bookmark_service)
) -> APIResponse[UserBookmarkResponse]:
    verify_user_role(current_user)
    created = await bookmark_service.add_bookmark(current_user.sub, counselor_id)
    return ok(data=created, message="즐겨찾기 등록 성공")


@router.delete(
    "/bookmarks",
    response_model=APIResponse[bool],
    summary="사용자 즐겨찾기 삭제"
)
async def remove_bookmark(
    counselor_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    bookmark_service: UserBookmarkService = Depends(get_user_bookmark_service)
) -> APIResponse[bool]:
    verify_user_role(current_user)
    removed = await bookmark_service.remove_bookmark(current_user.sub, counselor_id)
    return ok(data=removed, message="즐겨찾기 삭제 성공")
