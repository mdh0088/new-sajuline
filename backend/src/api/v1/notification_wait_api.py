"""
알림톡 발송 대기 API
상담사 접속 알림 신청 관련 엔드포인트
"""
from fastapi import APIRouter, Depends

from src.core.dependencies import NotificationWaitServiceDep
from src.common.response import APIResponse, ok
from src.services.auth_service import get_current_user, TokenPayload
from src.schemas.notification_wait_schema import (
    NotificationWaitCreate,
    NotificationWaitResponse,
)

router = APIRouter(prefix="/notification-wait", tags=["알림 대기"])


@router.post(
    "",
    response_model=APIResponse[NotificationWaitResponse],
    summary="알림 대기 등록",
    description="상담사 접속 시 알림을 받도록 등록합니다."
)
async def register_notification_wait(
    request: NotificationWaitCreate,
    service: NotificationWaitServiceDep,
    current_user: TokenPayload = Depends(get_current_user)
) -> APIResponse[NotificationWaitResponse]:
    if current_user.role != "user":
        from src.exceptions.custom_exceptions import ForbiddenError
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    result = await service.register_notification_wait(
        user_id=current_user.sub,
        counselor_id=request.counselor_id
    )
    return ok(data=result, message="알림 신청이 등록되었습니다.")
