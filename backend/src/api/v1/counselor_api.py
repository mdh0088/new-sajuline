"""
상담사 관련 API 엔드포인트
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

# 레이트 리미팅 import 추가
from src.common.middleware.rate_limit import limiter

from src.core.database import get_db_maria, get_db_mssql
from src.core.redis import get_redis
from src.repositories.counselor_repository import CounselorRepository
from src.repositories.user_activity_log_repository import UserActivityLogRepository
from src.repositories.consultation_review_repository import ConsultationReviewRepository
from src.repositories.inquiry_repository import InquiryRepository
from src.repositories.ars.tm60_member_repository import Tm60MemberRepository
from src.services.counselor_service import CounselorService
from src.services.auth_service import AuthService, get_current_user, TokenPayload
from src.services.user_activity_log_service import UserActivityLogService
from src.services.consultation_review_service import ConsultationReviewService
from src.services.inquiry_service import InquiryService
from src.services.ars.tm60_member_service import Tm60MemberService
from src.services.ars.tm60_chatlog_service import Tm60ChatlogService
from src.schemas.auth_schema import LoginRequest, LoginResponse
from src.schemas.counselor_schema import CounselorResponse, CounselorMypageUpdate, CounselorSearchItem
from src.schemas.user_activity_log_schema import UserType, DeviceType
from src.common.response import APIResponse, APIResponseBuilder, ok, fail
from src.common.logging import logger, get_logger_with_request_id
from src.common.utils.client_info import extract_client_info
from src.common.utils.auth_utils import verify_counselor_role
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


def get_tm60_member_service(mssql = Depends(get_db_mssql)) -> Tm60MemberService:
    repo = Tm60MemberRepository(mssql)
    return Tm60MemberService(repo)

def get_tm60_chatlog_service() -> Tm60ChatlogService:
    for mssql in get_db_mssql():
        return Tm60ChatlogService(mssql)


def get_counselor_service(
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    auth_service: AuthService = Depends(get_auth_service),
    tm60_member_service: Tm60MemberService = Depends(get_tm60_member_service),
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository)
) -> CounselorService:
    """상담사 서비스 의존성 주입"""
    return CounselorService(counselor_repo, auth_service, tm60_member_service, review_repo)


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="상담사 로그인",
    description="상담사 닉네임과 비밀번호로 로그인하고 JWT 토큰을 HttpOnly 쿠키에 설정",
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
    """상담사 로그인 (닉네임 사용)"""
    log = get_logger_with_request_id()
    log.info("Counselor login attempt", nickname=login_request.user_id)

    # 클라이언트 정보 추출
    ip_address, user_agent, device_type = extract_client_info(request)

    # 로그인 처리 (예외는 전역 핸들러에서 처리)
    access_token, counselor_response = await counselor_service.login(
        nickname=login_request.user_id,
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


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="상담사 로그아웃",
    description="현재 로그인한 상담사를 로그아웃하고 JWT 토큰 쿠키를 삭제"
)
async def logout(
    request: Request,
    response: Response,
    current_user: TokenPayload = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    redis_client = Depends(get_redis)
):
    """상담사 로그아웃"""
    log = get_logger_with_request_id()
    # 역할 확인: 상담사만 접근
    try:
        verify_counselor_role(current_user)
    except Exception:
        # 역할 불일치 시에도 쿠키는 삭제하여 보안상 세션을 종료
        pass

    try:
        # 현재 토큰들을 블랙리스트에 추가 (보안 강화)
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        # Access Token 블랙리스트 처리
        if access_token:
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

    log.info("Counselor logout successful", counselor_id=current_user.sub, email=current_user.email)
    return ok(data=None, message="로그아웃 성공")


@router.get("/inquiries/reviews", response_model=APIResponse, summary="상담사별 후기 목록 조회")
async def get_counselor_reviews(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    visible_only: bool = Query(True, description="공개 후기만 조회"),
    current_user: TokenPayload = Depends(get_current_user),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service)
) -> APIResponse:
    """
    상담사별 후기 목록을 조회합니다. (현재 로그인한 상담사 기준)
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    - **visible_only**: 공개 후기만 조회 여부 (기본값: true)
    """
    # 권한 확인: 상담사만 접근
    verify_counselor_role(current_user)
    target_counselor_id = current_user.sub
    
    log = get_logger_with_request_id()
    log.info("API: Getting counselor reviews", 
            counselor_id=target_counselor_id, 
            page=page, 
            limit=limit, 
            visible_only=visible_only)
    
    # 서비스 호출 (tuple 반환)
    reviews, page, limit, total = await review_service.get_counselor_reviews(
        counselor_id=target_counselor_id,
        page=page,
        limit=limit,
        visible_only=visible_only
    )
    
    log.info("API: Counselor reviews retrieved successfully", 
            counselor_id=target_counselor_id,
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
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse:
    """
    상담문의 목록을 조회합니다.
    inquirer_type='USER' AND counselor_id=#{counselor_id}
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    # 권한 확인: 상담사만 접근
    verify_counselor_role(current_user)
    counselor_id = current_user.sub
    
    log = get_logger_with_request_id()
    log.info("API: Getting counselor user inquiries", 
            counselor_id=counselor_id,
            page=page, 
            limit=limit)
    
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
    current_user: TokenPayload = Depends(get_current_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service)
) -> APIResponse:
    """
    관리자 문의 목록을 조회합니다.
    inquirer_type='COUNSELOR' AND inquirer_id=#{counselor_id}
    
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    # 권한 확인: 상담사만 접근
    verify_counselor_role(current_user)
    counselor_id = current_user.sub
    
    log = get_logger_with_request_id()
    log.info("API: Getting counselor admin inquiries", 
            counselor_id=counselor_id,
            page=page, 
            limit=limit)
    
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


@router.get(
    "/mypage",
    response_model=APIResponse[CounselorResponse],
    summary="상담사 마이페이지 정보",
    description="현재 로그인한 상담사의 요약 정보를 반환합니다."
)
async def get_counselor_mypage(
    current_user: TokenPayload = Depends(get_current_user),
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    상담사 마이페이지 정보 조회 (t_counselor 단일 행 반환)
    - counselor_id, nickname, profile_image_url, introduction_short, greeting_message,
      career_info, counselor_status, grade, specialty_types, keywords, work_time,
      rating_avg, rating_count, consultation_count, consultation_time_total,
      after_amount, before_amount
    """
    verify_counselor_role(current_user)
    counselor_id = current_user.sub
    log = get_logger_with_request_id()
    log.info("API: Getting counselor mypage info", counselor_id=counselor_id)

    data = await counselor_service.get_mypage_info(counselor_id)
    return ok(data=data, message="상담사 마이페이지 조회 성공")


@router.patch(
    "/mypage",
    response_model=APIResponse[CounselorResponse],
    summary="상담사 마이페이지 부분 수정",
    description="전달된 필드만 부분 업데이트하며, 상태 변경 시 MSSQL tm60_member.m_state를 동기화합니다."
)
async def update_counselor_mypage(
    updates: CounselorMypageUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    - 변경 대상 필드 (옵셔널):
      counselor_status, work_time, introduction_short, greeting_message, career_info
    - 상태 변경 시 MSSQL 매핑: WAITING→1, CONSULTING→2, ABSENT→3
    """
    verify_counselor_role(current_user)
    counselor_id = current_user.sub
    log = get_logger_with_request_id()
    log.info("API: Updating counselor mypage", counselor_id=counselor_id)

    data = await counselor_service.update_mypage(counselor_id, updates)
    return ok(data=data, message="상담사 마이페이지 수정 성공")


@router.get(
    "/consultation-time",
    response_model=APIResponse,
    summary="상담시간/포인트 월 합계",
    description="tm60_chatlog에서 counselor_code(m_code) 기준 yyyy, mm 조건으로 합계를 조회"
)
async def get_monthly_consultation_stats(
    yyyy: str = Query(..., min_length=4, max_length=4, description="연도 (YYYY)"),
    mm: str = Query(..., min_length=2, max_length=2, description="월 (MM)"),
    current_user: TokenPayload = Depends(get_current_user),
    counselor_service: CounselorService = Depends(get_counselor_service),
    chatlog_service: Tm60ChatlogService = Depends(get_tm60_chatlog_service)
):
    """현재 로그인 상담사의 `counselor_code`로 tm60_chatlog 집계 조회"""
    verify_counselor_role(current_user)
    counselor = await counselor_service.counselor_repo.get_by_id(current_user.sub)
    if not counselor:
        raise BaseAppException("상담사 정보를 찾을 수 없습니다", status_code=404)
    m_code = counselor.counselor_code
    sum_realchattm, sum_usepoint = await chatlog_service.get_monthly_stats_by_m_code(m_code, yyyy, mm)
    data = {
        "m_code": m_code,
        "yyyy": yyyy,
        "mm": mm,
        "sum_realchattm": sum_realchattm,
        "sum_usepoint": sum_usepoint
    }
    return ok(data=data, message="상담시간/포인트 합계 조회 성공")


# =====================
# 공개(게스트) 엔드포인트
# =====================

@router.get(
    "/public/search",
    response_model=APIResponse,
    summary="상담사 공개 검색 목록",
    description=(
        "게스트 가능. 필터: is_best, is_new, cs_specialties[], cs_keywords[], search_name. "
        "t_counselor에서 필터링 후 counselor_code 목록으로 tm60_member.m_state를 조인하여 상태 반환. "
        "또한 t_consultation_review의 is_visible=true 기준 review_count와 평균 rating을 포함. 페이징 제공."
    ),
)
async def search_public_counselors(
    request: Request,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    cs_status: Optional[str] = Query(None, description="tm60_members.m_state 값(예: '1','2','3')"),
    is_best: Optional[bool] = Query(None),
    is_new: Optional[bool] = Query(None),
    cs_specialties: Optional[list[str]] = Query(None, description="전문분야 배열"),
    cs_keywords: Optional[list[str]] = Query(None, description="키워드 배열"),
    search_name: Optional[str] = Query(None, description="상담사 닉네임 like"),
    counselor_service: CounselorService = Depends(get_counselor_service),
):
    """공개 검색 목록 (게스트)
    요구사항 요약:
    - t_counselor: is_out=false, is_show=true
    - 상태는 tm60_member.m_state 사용 (필터 cs_status 존재 시 해당 조건 적용)
    - 1차 필터: is_best, is_new, specialty_types, keywords, search_name
    - 2차: counselor_code -> tm60_member.m_code IN 검색
    - 각 항목에 리뷰 총 개수(is_visible=true)와 평균 rating 포함
    - 페이징 응답 및 전체 count 포함
    """
    log = get_logger_with_request_id()
    log.info(
        "API: Public counselor search",
        page=page,
        limit=limit,
        cs_status=cs_status,
        is_best=is_best,
        is_new=is_new,
        cs_specialties=cs_specialties,
        cs_keywords=cs_keywords,
        search_name=search_name,
    )

    items, total = await counselor_service.search_public(
        page=page,
        limit=limit,
        cs_status=cs_status,
        is_best=is_best,
        is_new=is_new,
        cs_specialties=cs_specialties,
        cs_keywords=cs_keywords,
        search_name=search_name,
    )
    return APIResponseBuilder.paginated(
        data=items,
        page=page,
        limit=limit,
        total=total,
        message="상담사 공개 검색 목록 조회 성공",
    )


@router.get(
    "/public/{counselor_code}",
    response_model=APIResponse[CounselorResponse],
    summary="상담사 공개 상세 조회",
    description="counselor_code로 상담사 상세를 조회합니다. 게스트 접근 가능"
)
async def get_public_counselor_detail(
    counselor_code: str,
    counselor_repo: CounselorRepository = Depends(get_counselor_repository),
    review_repo: ConsultationReviewRepository = Depends(get_consultation_review_repository),
    chatlog_service: Tm60ChatlogService = Depends(get_tm60_chatlog_service)
):
    """상담사 공개 상세 조회
    - 입력: counselor_code
    - 출력 필드: counselor_id, nickname, profile_image_url, introduction_short, greeting_message,
      career_info, keywords, work_time, specialty_types, after_amount, before_amount,
      rating_avg(후기 기반), consultation_count(tm60_chatlog 기반)
    """
    log = get_logger_with_request_id()
    log.info("API: Public counselor detail", counselor_code=counselor_code)

    counselor = await counselor_repo.get_by_counselor_code(counselor_code)
    if not counselor:
        raise BaseAppException("상담사를 찾을 수 없습니다", status_code=404)

    # 평균 평점 (공개 후기만)
    rating_avg = await review_repo.get_average_rating_by_counselor_id(counselor.counselor_id, visible_only=True)

    # 상담건수 (tm60_chatlog: m_code=counselor_code AND usepoint>0)
    consultation_count = await chatlog_service.get_consultation_count_by_m_code(counselor.counselor_code)

    # 응답 변환 및 보강
    resp = CounselorResponse.model_validate(counselor)
    resp.rating_avg = rating_avg
    resp.consultation_count = consultation_count

    return ok(data=resp, message="상담사 공개 상세 조회 성공")


@router.get(
    "/public/{counselor_id}/reviews",
    response_model=APIResponse,
    summary="상담사 공개 후기 목록 조회",
    description="counselor_id로 후기 목록을 조회합니다. 게스트 접근 가능"
)
async def get_public_counselor_reviews(
    counselor_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    visible_only: bool = Query(True, description="공개 후기만 조회"),
    review_service: ConsultationReviewService = Depends(get_consultation_review_service),
):
    log = get_logger_with_request_id()
    log.info("API: Public counselor reviews", counselor_id=counselor_id, page=page, limit=limit, visible_only=visible_only)

    reviews, page, limit, total = await review_service.get_counselor_reviews(
        counselor_id=counselor_id,
        page=page,
        limit=limit,
        visible_only=visible_only,
    )

    return APIResponseBuilder.paginated(
        data=reviews,
        page=page,
        limit=limit,
        total=total,
        message="상담사 공개 후기 목록 조회 성공",
    )


@router.get(
    "/public/{counselor_id}/inquiries",
    response_model=APIResponse,
    summary="상담사 공개 문의 목록 조회",
    description="counselor_id로 사용자→상담사 문의 목록을 조회합니다. 게스트 접근 가능"
)
async def get_public_counselor_user_inquiries(
    counselor_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    log = get_logger_with_request_id()
    log.info("API: Public counselor user inquiries", counselor_id=counselor_id, page=page, limit=limit)

    inquiries, page, limit, total = await inquiry_service.get_counselor_user_inquiries(
        counselor_id=counselor_id,
        page=page,
        limit=limit,
    )

    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="상담사 공개 문의 목록 조회 성공",
    )