"""사용자 활동 로그 서비스"""

from typing import Optional

from src.repositories.user_activity_log_repository import UserActivityLogRepository
from src.schemas.user_activity_log_schema import (
    UserActivityLogCreate, 
    ActivityType, 
    UserType, 
    DeviceType
)
from src.common.logging import get_logger_with_request_id


class UserActivityLogService:
    """사용자 활동 로그 비즈니스 로직 서비스"""
    
    def __init__(self, activity_log_repo: UserActivityLogRepository):
        self.activity_log_repo = activity_log_repo
    
    async def log_login_success(
        self,
        user_id: str,
        user_type: UserType = UserType.USER,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: Optional[DeviceType] = None
    ) -> None:
        """로그인 성공 로그 기록"""
        log = get_logger_with_request_id()
        log.info("Logging successful login", user_id=user_id)
        
        activity_detail = {
            "login_method": "email_password",
            "success": True
        }
        
        log_data = UserActivityLogCreate(
            user_id=user_id,
            user_type=user_type,
            activity_type=ActivityType.LOGIN,
            activity_detail=activity_detail,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        
        await self.activity_log_repo.create(log_data)
        log.info("Login success logged", user_id=user_id)