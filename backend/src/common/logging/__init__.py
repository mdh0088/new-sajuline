"""
공통 로깅 모듈 - Loguru 기반 간소화된 구조
"""
from loguru import logger
import sys
import os

# 기본 핸들러 제거
logger.remove()

# 개발/프로덕션 환경 구분
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 콘솔 출력 설정
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {extra[request_id]} | <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# 파일 출력 설정
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {extra[request_id]} | {message}",
    level=LOG_LEVEL,
    rotation="1 day",
    retention="7 days",
    encoding="utf-8"
)

def get_logger_with_request_id():
    """Request ID가 포함된 로거 반환"""
    from .config import get_request_id
    return logger.bind(request_id=get_request_id() or "no-request-id")

# 편의를 위한 export
__all__ = ["logger", "get_logger_with_request_id"]