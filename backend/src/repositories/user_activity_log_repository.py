"""사용자 활동 로그 리포지토리"""

import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.models.user_activity_log_model import UserActivityLog
from src.schemas.user_activity_log_schema import UserActivityLogCreate
from src.common.logging import get_logger_with_request_id


class UserActivityLogRepository:
    """사용자 활동 로그 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def create(self, log_data: UserActivityLogCreate) -> UserActivityLog:
        """활동 로그 생성"""
        log = get_logger_with_request_id()
        log.info("Creating user activity log", 
                user_id=log_data.user_id, 
                activity_type=log_data.activity_type)
        
        # JSON 직렬화 처리
        activity_detail_json = None
        if log_data.activity_detail:
            try:
                activity_detail_json = json.dumps(log_data.activity_detail, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                log.warning("Failed to serialize activity_detail", error=str(e))
                activity_detail_json = json.dumps({"error": "serialization_failed"})
        
        activity_log = UserActivityLog(
            user_id=log_data.user_id,
            user_type=log_data.user_type,
            activity_type=log_data.activity_type,
            activity_detail=activity_detail_json,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            device_type=log_data.device_type
        )
        
        self.db.add(activity_log)
        await self.db.flush()
        await self.db.refresh(activity_log)
        
        log.info("User activity log created", 
                log_id=activity_log.log_id,
                user_id=log_data.user_id)
        
        return activity_log