"""
사용자 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request

# 레이트 리미팅 import 추가
from src.common.middleware.rate_limit import limiter

from src.core.redis import get_redis
from src.core.dependencies import (
    UserServiceDep, AuthServiceDep, NotificationServiceDep, InquiryServiceDep,
    UserBookmarkServiceDep, ConsultationReviewServiceDep, PaymentServiceDep,
    GradeServiceDep, PointTransactionServiceDep, Tm60UsersServiceDep,
    Tm60ChatlogServiceDep, Tm60ChatlogRepositoryDep, CounselorRepositoryDep,
    PaymentRepositoryDep, MariaSessionDep
)
from src.services.auth_service import AuthService, get_current_user, TokenPayload, KST
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
    FindIdRequest, FindIdResponse, FindPasswordRequest, FindPasswordResponse,
    PasswordChangeRequest, PasswordChangeResponse,
    WithdrawRequest, UserOutResponse
)
from src.common.utils.auth_utils import verify_user_role
from src.schemas.user_bookmark_schema import UserBookmarkResponse
from src.schemas.auth_schema import LoginRequest, LoginResponse
from src.common.response import APIResponse, APIResponseBuilder, ok, fail
from src.schemas.inquiry_schema import UserInquiryCreateRequest, InquiryResponse, UserAdminInquiryCreateRequest
from src.common.logging import logger, get_logger_with_request_id
from src.common.utils.client_info import extract_client_info
from src.exceptions.custom_exceptions import BaseAppException

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/inquiries",
    response_model=APIResponse,
    summary="사용자 → 관리자 문의 목록 조회"
)
async def get_user_admin_inquiries_api(
    inquiry_service: InquiryServiceDep,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user)
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
    inquiry_service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    inquiry_service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    inquiry_service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    user_service: UserServiceDep,
    notification_service: NotificationServiceDep
) -> APIResponse[UserResponse]:
    """통합 회원가입 - 일반/소셜 가입 통합 처리"""
    log = get_logger_with_request_id()

    if not signup_data.phone_chk:
        raise BaseAppException("휴대폰 인증이 필요합니다.", status_code=400)

    result = await user_service.signup(signup_data)

    # 회원가입 알림톡 발송 (실패해도 회원가입은 성공)
    try:
        await notification_service.user_join_alert(
            phone=result.phone,
            nick_name=result.nickname,
            user_id=result.user_id
        )
        log.info("Signup Kakao AlimTalk sent successfully", user_id=result.user_id)
    except Exception as e:
        log.warning("Signup Kakao AlimTalk failed but signup succeeded",
                   user_id=result.user_id, error=str(e))

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
    user_service: UserServiceDep,
    notification_service: NotificationServiceDep
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

    # 회원가입 알림톡 발송 (실패해도 회원가입은 성공)
    try:
        await notification_service.user_join_alert(
            phone=result.phone,
            nick_name=result.nickname,
            user_id=result.user_id
        )
        log.info("Social signup Kakao AlimTalk sent successfully", user_id=result.user_id)
    except Exception as e:
        log.warning("Social signup Kakao AlimTalk failed but signup succeeded",
                   user_id=result.user_id, error=str(e))

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
#     user_service: UserServiceDep
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
    user_service: UserServiceDep
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
    db: MariaSessionDep,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep
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
    auth_service: AuthServiceDep,
    current_user: TokenPayload = Depends(get_current_user),
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
            access_expires = datetime.fromtimestamp(current_user.exp, tz=KST)
            await auth_service.blacklist_token(
                jti=current_user.jti,
                expires_at=access_expires,
                redis_client=redis_client
            )
        
        # Refresh Token 블랙리스트 처리
        if refresh_token:
            try:
                refresh_payload = await auth_service.verify_refresh_token(refresh_token, redis_client)
                refresh_expires = datetime.fromtimestamp(refresh_payload["exp"], tz=KST)
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
    user_service: UserServiceDep,
    value: str = Query(..., description="검사할 이메일")
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
    user_service: UserServiceDep,
    value: str = Query(..., description="검사할 사용자 ID")
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
    user_service: UserServiceDep,
    value: str = Query(..., description="검사할 전화번호")
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
    user_service: UserServiceDep,
    value: str = Query(..., description="검사할 닉네임")
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
    user_service: UserServiceDep
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
    user_service: UserServiceDep
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
    user_service: UserServiceDep,
    bookmark_service: UserBookmarkServiceDep,
    review_service: ConsultationReviewServiceDep,
    payment_service: PaymentServiceDep,
    grade_service: GradeServiceDep,
    tm60_chatlog_service: Tm60ChatlogServiceDep,
    tm60_users_service: Tm60UsersServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    review_service: ConsultationReviewServiceDep,
    tm60_chatlog_repo: Tm60ChatlogRepositoryDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    review_service: ConsultationReviewServiceDep,
    tm60_chatlog_repo: Tm60ChatlogRepositoryDep,
    counselor_repo: CounselorRepositoryDep,
    searchtype: str = Query("my_reviews"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user)
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
    review_service: ConsultationReviewServiceDep,
    tm60_chatlog_repo: Tm60ChatlogRepositoryDep,
    counselor_repo: CounselorRepositoryDep,
    tm60_users_service: Tm60UsersServiceDep,
    point_tx_service: PointTransactionServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    review_service: ConsultationReviewServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    review_service: ConsultationReviewServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    user_service: UserServiceDep,
    payment_repo: PaymentRepositoryDep,
    tm60_chatlog_repo: Tm60ChatlogRepositoryDep,
    counselor_repo: CounselorRepositoryDep,
    start_dt: str = Query(..., description="시작일 (yyyy-mm-dd)"),
    end_dt: str = Query(..., description="종료일 (yyyy-mm-dd)"),
    search_type: SearchType = Query(...),
    order_type: OrderType = Query("latest"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user)
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
    bookmark_service: UserBookmarkServiceDep,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    current_user: TokenPayload = Depends(get_current_user)
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
    bookmark_service: UserBookmarkServiceDep,
    counselor_id: str = Query(..., description="상담사 ID"),
    current_user: TokenPayload = Depends(get_current_user)
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
    bookmark_service: UserBookmarkServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
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
    bookmark_service: UserBookmarkServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[bool]:
    verify_user_role(current_user)
    removed = await bookmark_service.remove_bookmark(current_user.sub, counselor_id)
    return ok(data=removed, message="즐겨찾기 삭제 성공")


@router.put(
    "/password",
    response_model=APIResponse[PasswordChangeResponse],
    summary="비밀번호 변경",
    description="로그인한 사용자의 비밀번호를 변경합니다. 일반 가입 사용자만 가능합니다.",
    responses={
        200: {"description": "비밀번호 변경 성공"},
        400: {"description": "유효하지 않은 요청 또는 소셜 로그인 사용자"},
        401: {"description": "현재 비밀번호 불일치"},
        404: {"description": "사용자를 찾을 수 없음"},
        429: {"description": "요청 한도 초과"}
    }
)
async def change_password(
    request_obj: Request,  # Rate Limiting 필수
    password_change_request: PasswordChangeRequest,
    user_service: UserServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[PasswordChangeResponse]:
    """
    비밀번호 변경

    - 일반 가입 사용자만 가능 (소셜 로그인 사용자는 불가)
    - 현재 비밀번호 확인 필수
    - 새 비밀번호는 8자 이상
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub
    log.info("API: Password change request", user_id=user_id)

    verify_user_role(current_user)

    result = await user_service.change_password(user_id, password_change_request)

    log.info("API: Password changed successfully", user_id=user_id)

    return ok(data=result, message="비밀번호가 성공적으로 변경되었습니다.")


@router.post(
    "/withdraw",
    response_model=APIResponse[UserOutResponse],
    summary="회원 탈퇴",
    description="사용자 회원 탈퇴를 처리합니다. 일반 가입자는 비밀번호 확인이 필요하며, 소셜 로그인 사용자는 비밀번호 없이 탈퇴 가능합니다.",
    responses={
        200: {"description": "회원 탈퇴 성공"},
        400: {"description": "유효하지 않은 요청 또는 이미 탈퇴한 사용자"},
        401: {"description": "비밀번호 불일치"},
        404: {"description": "사용자를 찾을 수 없음"}
    }
)
async def withdraw_user(
    request: WithdrawRequest,
    user_service: UserServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[UserOutResponse]:
    """
    회원 탈퇴 처리

    - 일반 가입자: 비밀번호 확인 필수
    - 소셜 로그인: 비밀번호 불필요
    - 탈퇴 정보는 t_user_out에 기록됨
    - 사용자 상태는 WITHDRAWN으로 변경됨
    - ARS 시스템(tm60_users)에서도 삭제됨

    프론트엔드는 응답 수신 후 로그아웃 처리 필요
    """
    log = get_logger_with_request_id()
    user_id = current_user.sub

    verify_user_role(current_user)

    log.info("API: User withdrawal request", user_id=user_id)

    result = await user_service.withdraw_user(user_id, request)

    log.info("API: User withdrawal completed successfully",
            user_id=user_id,
            out_idx=result.out_idx)

    return ok(data=result, message="회원 탈퇴가 완료되었습니다. 그동안 이용해 주셔서 감사합니다.")


# ===========================
# Public APIs (인증 불필요)
# ===========================

@router.get(
    "/public/reviews",
    response_model=APIResponse,
    summary="전체 후기 조회 (공개)",
    description="모든 공개 후기를 조회합니다. 인증 불필요.",
)
async def get_all_public_reviews_api(
    review_service: ConsultationReviewServiceDep,
    chatlog_repo: Tm60ChatlogRepositoryDep,
    counselor_repo: CounselorRepositoryDep,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
) -> APIResponse:
    """전체 공개 후기 목록 조회"""
    data, total = await review_service.get_all_public_reviews(
        page=page,
        limit=limit,
        chatlog_repo=chatlog_repo,
        counselor_repo=counselor_repo,
    )
    return APIResponseBuilder.paginated(
        data=data.items,
        page=page,
        limit=limit,
        total=total,
        message="전체 후기 조회 성공"
    )
