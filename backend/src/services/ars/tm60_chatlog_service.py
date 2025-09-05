"""
TM60 채팅로그 Service 클래스
ARS 시스템 연동 - MSSQL tm60_chatlog 테이블 비즈니스 로직 처리
"""
from sqlalchemy.orm import Session

from src.repositories.ars.tm60_chatlog_repository import Tm60ChatlogRepository
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError


class Tm60ChatlogService:
    """TM60 채팅로그 비즈니스 로직 처리 클래스"""
    
    def __init__(self, mssql_session: Session):
        """의존성 주입: MSSQL 세션"""
        self.repository = Tm60ChatlogRepository(mssql_session)
    
    async def get_user_consultation_count(self, user_id: str) -> int:
        """
        사용자의 상담 내역 수 조회
        
        Args:
            user_id (str): 사용자 ID
            
        Returns:
            int: 상담 내역 수 (usepoint >= 0 조건)
            
        Raises:
            ValidationError: 잘못된 사용자 ID
        """
        log = get_logger_with_request_id()
        log.info("Getting user consultation count", user_id=user_id)
        
        # 입력값 검증
        if not user_id or not user_id.strip():
            log.warning("Invalid user_id provided", user_id=user_id)
            raise ValidationError("사용자 ID가 올바르지 않습니다.")
        
        # Repository를 통해 조회
        count = await self.repository.get_consultation_count_by_user_id(user_id.strip())
        
        log.info(
            "User consultation count retrieved successfully",
            user_id=user_id,
            count=count
        )
        
        return count