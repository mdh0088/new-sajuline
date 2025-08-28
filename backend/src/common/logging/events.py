"""
로깅 이벤트 정의 (간소화됨)
특별한 경우에만 사용, 대부분은 @logger.catch와 get_logger_with_request_id() 사용
"""
from typing import Optional
from loguru import logger
from .config import get_request_id


class SystemEvents:
    """시스템 레벨 로깅 이벤트 (필수 유지)"""
    
    @classmethod
    def application_started(cls, **kwargs) -> None:
        """애플리케이션 시작"""
        logger.bind(request_id=get_request_id()).info("Application Started", **kwargs)
    
    @classmethod
    def application_shutdown(cls, **kwargs) -> None:
        """애플리케이션 종료"""
        logger.bind(request_id=get_request_id()).info("Application Shutdown", **kwargs)