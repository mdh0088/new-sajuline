"""
1:1 문의 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query

from src.core.dependencies import InquiryServiceDep, InquiryServiceForCounselorDep
from src.common.response import APIResponse, APIResponseBuilder, ok
from src.common.logging import get_logger_with_request_id
from src.services.auth_service import get_current_user, TokenPayload
from src.schemas.inquiry_schema import (
    UserInquiryCreateRequest,
    UserAdminInquiryCreateRequest,
    CounselorReplyRequest,
    CounselorAdminInquiryCreateRequest,
    InquiryResponse,
    InquirySummary,
)
from src.exceptions.custom_exceptions import ForbiddenError

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


# ==================== 사용자 엔드포인트 ====================

@router.post(
    "/user-to-counselor",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 상담사 문의 등록",
    description="로그인한 사용자가 특정 상담사에게 1:1 문의를 등록합니다. 상담사에게 카카오 알림톡이 발송됩니다."
)
async def create_user_inquiry(
    payload: UserInquiryCreateRequest,
    service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[InquiryResponse]:
    if current_user.role != "user":
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Creating user inquiry", user_id=current_user.sub, counselor_id=payload.counselor_id)

    result = await service.create_user_inquiry(
        user_id=current_user.sub,
        payload=payload
    )
    return ok(data=result, message="문의가 등록되었습니다.")


@router.post(
    "/user-to-admin",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 관리자 문의 등록",
    description="로그인한 사용자가 관리자에게 1:1 문의를 등록합니다."
)
async def create_user_admin_inquiry(
    payload: UserAdminInquiryCreateRequest,
    service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[InquiryResponse]:
    if current_user.role != "user":
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Creating user admin inquiry", user_id=current_user.sub)

    result = await service.create_user_admin_inquiry(
        user_id=current_user.sub,
        payload=payload
    )
    return ok(data=result, message="문의가 등록되었습니다.")


@router.get(
    "/user-to-admin",
    response_model=APIResponse,
    summary="사용자 → 관리자 문의 목록 조회"
)
async def get_user_admin_inquiries(
    service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
) -> APIResponse:
    if current_user.role != "user":
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Getting user admin inquiries", user_id=current_user.sub, page=page, limit=limit)

    inquiries, page, limit, total = await service.get_user_admin_inquiries(
        user_id=current_user.sub,
        page=page,
        limit=limit
    )
    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="문의 목록 조회 성공"
    )


@router.get(
    "/user-to-admin/{inquiry_id}",
    response_model=APIResponse[InquiryResponse],
    summary="사용자 → 관리자 문의 상세 조회"
)
async def get_user_admin_inquiry_detail(
    inquiry_id: int,
    service: InquiryServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[InquiryResponse]:
    if current_user.role != "user":
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Getting user admin inquiry detail", user_id=current_user.sub, inquiry_id=inquiry_id)

    result = await service.get_user_admin_inquiry_detail(
        inquiry_id=inquiry_id,
        user_id=current_user.sub
    )
    return ok(data=result, message="문의 상세 조회 성공")


# ==================== 상담사 엔드포인트 ====================

@router.get(
    "/counselor/from-users",
    response_model=APIResponse,
    summary="상담사 수신 사용자 문의 목록 조회"
)
async def get_counselor_user_inquiries(
    service: InquiryServiceForCounselorDep,
    current_user: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
) -> APIResponse:
    if current_user.role != "counselor":
        raise ForbiddenError("상담사만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Getting counselor user inquiries", counselor_id=current_user.sub, page=page, limit=limit)

    inquiries, page, limit, total = await service.get_counselor_user_inquiries(
        counselor_id=current_user.sub,
        page=page,
        limit=limit
    )
    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="사용자 문의 목록 조회 성공"
    )


@router.post(
    "/counselor/reply/{inquiry_id}",
    response_model=APIResponse[InquiryResponse],
    summary="상담사 → 사용자 문의 답변",
    description="상담사가 사용자 문의에 답변합니다. 사용자에게 카카오 알림톡이 발송됩니다."
)
async def reply_to_user_inquiry(
    inquiry_id: int,
    payload: CounselorReplyRequest,
    service: InquiryServiceForCounselorDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[InquiryResponse]:
    if current_user.role != "counselor":
        raise ForbiddenError("상담사만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Counselor replying to inquiry", counselor_id=current_user.sub, inquiry_id=inquiry_id)

    result = await service.reply_to_user_inquiry(
        inquiry_id=inquiry_id,
        counselor_id=current_user.sub,
        reply_content=payload.reply_content
    )
    return ok(data=result, message="답변이 등록되었습니다.")


@router.get(
    "/counselor/to-admin",
    response_model=APIResponse,
    summary="상담사 → 관리자 문의 목록 조회"
)
async def get_counselor_admin_inquiries(
    service: InquiryServiceForCounselorDep,
    current_user: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
) -> APIResponse:
    if current_user.role != "counselor":
        raise ForbiddenError("상담사만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Getting counselor admin inquiries", counselor_id=current_user.sub, page=page, limit=limit)

    inquiries, page, limit, total = await service.get_counselor_admin_inquiries(
        counselor_id=current_user.sub,
        page=page,
        limit=limit
    )
    return APIResponseBuilder.paginated(
        data=inquiries,
        page=page,
        limit=limit,
        total=total,
        message="관리자 문의 목록 조회 성공"
    )


@router.post(
    "/counselor/to-admin",
    response_model=APIResponse[InquiryResponse],
    summary="상담사 → 관리자 문의 등록"
)
async def create_counselor_admin_inquiry(
    payload: CounselorAdminInquiryCreateRequest,
    service: InquiryServiceForCounselorDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[InquiryResponse]:
    if current_user.role != "counselor":
        raise ForbiddenError("상담사만 접근 가능합니다.")

    log = get_logger_with_request_id()
    log.info("API: Creating counselor admin inquiry", counselor_id=current_user.sub)

    result = await service.create_counselor_admin_inquiry(
        counselor_id=current_user.sub,
        payload=payload
    )
    return ok(data=result, message="문의가 등록되었습니다.")
