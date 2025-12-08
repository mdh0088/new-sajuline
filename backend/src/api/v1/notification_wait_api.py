"""
알림톡 발송 대기 API
상담사 접속 알림 신청 관련 엔드포인트
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_maria
from src.common.response import APIResponse, ok
from src.services.auth_service import get_current_user, TokenPayload
from src.repositories.notification_wait_repository import NotificationWaitRepository
from src.services.notification_wait_service import NotificationWaitService
from src.schemas.notification_wait_schema import (
    NotificationWaitCreate,
    NotificationWaitResponse,
)

router = APIRouter(prefix="/notification-wait", tags=["알림 대기"])


def get_notification_wait_repository(
    db: AsyncSession = Depends(get_db_maria)
) -> NotificationWaitRepository:
    return NotificationWaitRepository(db)


def get_notification_wait_service(
    repo: NotificationWaitRepository = Depends(get_notification_wait_repository)
) -> NotificationWaitService:
    return NotificationWaitService(repo)


@router.post(
    "",
    response_model=APIResponse[NotificationWaitResponse],
    summary="알림 대기 등록",
    description="상담사 접속 시 알림을 받도록 등록합니다."
)
async def register_notification_wait(
    request: NotificationWaitCreate,
    current_user: TokenPayload = Depends(get_current_user),
    service: NotificationWaitService = Depends(get_notification_wait_service)
) -> APIResponse[NotificationWaitResponse]:
    if current_user.role != "user":
        from src.exceptions.custom_exceptions import ForbiddenError
        raise ForbiddenError("일반 사용자만 접근 가능합니다.")

    result = await service.register_notification_wait(
        user_id=current_user.sub,
        counselor_id=request.counselor_id
    )
    return ok(data=result, message="알림 신청이 등록되었습니다.")
