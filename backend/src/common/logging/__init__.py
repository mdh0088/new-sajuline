"""
공통 로깅 모듈 - Loguru 기반 간소화된 구조
"""
from loguru import logger
import sys
import os
from contextlib import contextmanager

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


def get_scheduler_logger():
    """스케줄러 전용 로거 반환 (scheduler.log에만 기록)"""
    from .config import get_request_id
    return logger.bind(request_id=get_request_id() or "scheduler")


@contextmanager
def scheduler_logging_context():
    """스케줄러 로깅 컨텍스트 매니저

    사용 예시:
        with scheduler_logging_context():
            log = get_scheduler_logger()
            log.info("스케줄러 작업 시작")
            # ... 스케줄러 로직 ...
            log.info("스케줄러 작업 완료")
    """
    from .config import set_scheduler_context
    set_scheduler_context(True)
    try:
        yield
    finally:
        set_scheduler_context(False)


# 편의를 위한 export
__all__ = [
    "logger",
    "get_logger_with_request_id",
    "get_scheduler_logger",
    "scheduler_logging_context",
]