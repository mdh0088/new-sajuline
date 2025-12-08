"""
알림톡 발송 대기 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from src.exceptions.custom_exceptions import ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.schemas.notification_wait_schema import (
    NotificationWaitResponse,
    NotificationWaitCheckResponse,
)
from src.repositories.notification_wait_repository import NotificationWaitRepository


class NotificationWaitService:
    """알림톡 발송 대기 비즈니스 로직 서비스"""

    def __init__(self, notification_wait_repo: NotificationWaitRepository):
        self.notification_wait_repo = notification_wait_repo

    async def register_notification_wait(
        self, user_id: str, counselor_id: str
    ) -> NotificationWaitResponse:
        """
        알림 대기 등록
        - 중복 등록 시 에러 발생
        """
        log = get_logger_with_request_id()
        log.info("Registering notification wait", user_id=user_id, counselor_id=counselor_id)

        if not user_id or not counselor_id:
            raise ValidationError("사용자 ID와 상담사 ID가 필요합니다.")

        # 중복 체크
        if await self.notification_wait_repo.exists(user_id, counselor_id):
            raise ValidationError("이미 알림 신청이 등록되어 있습니다.")

        # 등록
        created = await self.notification_wait_repo.create(user_id, counselor_id)
        await self.notification_wait_repo.db.commit()

        log.info("Notification wait registered", wait_idx=created.wait_idx)
        return NotificationWaitResponse.model_validate(created)

    async def cancel_notification_wait(
        self, user_id: str, counselor_id: str
    ) -> bool:
        """
        알림 대기 취소 (삭제)
        - 삭제된 건이 없으면 False 반환
        """
        log = get_logger_with_request_id()
        log.info("Canceling notification wait", user_id=user_id, counselor_id=counselor_id)

        if not user_id or not counselor_id:
            raise ValidationError("사용자 ID와 상담사 ID가 필요합니다.")

        affected = await self.notification_wait_repo.delete(user_id, counselor_id)
        await self.notification_wait_repo.db.commit()

        log.info("Notification wait canceled", affected=affected)
        return affected > 0

    async def check_notification_wait(
        self, user_id: str, counselor_id: str
    ) -> NotificationWaitCheckResponse:
        """
        알림 대기 등록 여부 확인
        """
        log = get_logger_with_request_id()
        log.info("Checking notification wait", user_id=user_id, counselor_id=counselor_id)

        if not user_id or not counselor_id:
            raise ValidationError("사용자 ID와 상담사 ID가 필요합니다.")

        is_registered = await self.notification_wait_repo.exists(user_id, counselor_id)

        log.info("Notification wait check completed", is_registered=is_registered)
        return NotificationWaitCheckResponse(
            is_registered=is_registered,
            wait_idx=None
        )

    async def send_notifications_for_counselor(self, counselor_id: str) -> int:
        """
        상담사 접속 시 알림 발송 및 완료 처리
        - 해당 상담사의 모든 미발송 알림을 발송 완료 처리
        - 반환: 발송 완료 처리된 건수
        """
        log = get_logger_with_request_id()
        log.info("Sending notifications for counselor", counselor_id=counselor_id)

        if not counselor_id:
            raise ValidationError("상담사 ID가 필요합니다.")

        # 미발송 목록 조회 (알림톡 발송용)
        notifications = await self.notification_wait_repo.get_list_by_counselor(counselor_id)

        # TODO: 실제 알림톡 발송 로직 (KakaoTalk API 호출)
        # for notification in notifications:
        #     await send_kakao_notification(notification.user_id, counselor_id)

        # 모두 발송 완료 처리
        count = await self.notification_wait_repo.mark_all_as_sent(counselor_id)
        await self.notification_wait_repo.db.commit()

        log.info("Notifications sent for counselor", counselor_id=counselor_id, count=count)
        return count
