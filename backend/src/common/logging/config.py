"""
로깅 구성 설정
Loguru 기반 구조화 로깅 시스템
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from contextvars import ContextVar

from src.config.settings import settings

# 스케줄러 컨텍스트 변수 (스케줄러 로그 분리용)
scheduler_context_var: ContextVar[bool] = ContextVar('is_scheduler', default=False)


def set_scheduler_context(is_scheduler: bool) -> None:
    """스케줄러 컨텍스트 설정"""
    scheduler_context_var.set(is_scheduler)


def get_scheduler_context() -> bool:
    """스케줄러 컨텍스트 반환"""
    return scheduler_context_var.get()


class LoguruConfig:
    """Loguru 로깅 설정 클래스"""
    
    def __init__(self):
        self.log_level = settings.log_level
        self.is_development = settings.is_development
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def configure(self) -> None:
        """로깅 설정 초기화"""
        # 기본 핸들러 제거
        logger.remove()
        
        # 콘솔 핸들러 추가 (개발환경)
        if self.is_development:
            logger.add(
                sys.stdout,
                level=self.log_level,
                format=self._get_console_format(),
                colorize=True,
                backtrace=True,
                diagnose=True,
                filter=RequestContextFilter()
            )
        else:
            # 프로덕션에서는 JSON 포맷
            logger.add(
                sys.stdout,
                level=self.log_level,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
                serialize=True,
                filter=RequestContextFilter()
            )
        
        # 파일 핸들러 추가 (간결한 형태) - 스케줄러 로그 제외
        logger.add(
            self.log_dir / "app.log",
            level="INFO",
            format=self._get_file_format(),
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            serialize=False,  # JSON 형태 비활성화
            filter=SchedulerContextFilter(scheduler_only=False)  # 스케줄러 로그 제외
        )
        
        # 에러 파일 핸들러 (간결한 형태)
        logger.add(
            self.log_dir / "error.log",
            level="ERROR",
            format=self._get_file_format(),
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            serialize=False,  # JSON 형태 비활성화
            filter=RequestContextFilter()
        )

        # 스케줄러 전용 파일 핸들러 (scheduler.log)
        logger.add(
            self.log_dir / "scheduler.log",
            level="INFO",
            format=self._get_scheduler_format(),
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            serialize=False,
            filter=SchedulerContextFilter(scheduler_only=True)
        )

        logger.info("Logging system initialized", extra={
            "log_level": self.log_level,
            "environment": "development" if self.is_development else "production"
        })
    
    def _get_console_format(self) -> str:
        """개발환경 콘솔 포맷"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<yellow>[{extra[request_id]}]</yellow> | "
            "<level>{message}</level>"
        )
    
    def _get_json_format(self) -> str:
        """JSON 포맷 (파일 로깅용)"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
    
    def _get_file_format(self) -> str:
        """간결한 파일 포맷"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message} | "
            "{extra}"
        )

    def _get_scheduler_format(self) -> str:
        """스케줄러 전용 간결한 포맷"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{message} | "
            "{extra}"
        )


def setup_logging() -> None:
    """로깅 시스템 설정"""
    config = LoguruConfig()
    config.configure()


def get_logger(name: str) -> Any:
    """로거 인스턴스 반환"""
    return logger.bind(logger_name=name)


# Request ID 컨텍스트 변수
from contextvars import ContextVar
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


def get_request_id() -> str:
    """현재 요청 ID 반환"""
    return request_id_var.get('')


def set_request_id(request_id: str) -> None:
    """요청 ID 설정"""
    request_id_var.set(request_id)


class RequestContextFilter:
    """Request ID를 로그에 추가하는 필터"""

    def __call__(self, record: Dict[str, Any]) -> bool:
        record["extra"]["request_id"] = get_request_id()
        return True


class SchedulerContextFilter:
    """스케줄러 로그 분리를 위한 필터

    - scheduler_only=True: 스케줄러 로그만 통과 (scheduler.log용)
    - scheduler_only=False: 스케줄러 로그 제외 (app.log용)
    """

    def __init__(self, scheduler_only: bool = False):
        self.scheduler_only = scheduler_only

    def __call__(self, record: Dict[str, Any]) -> bool:
        record["extra"]["request_id"] = get_request_id()
        is_scheduler = get_scheduler_context()

        if self.scheduler_only:
            # scheduler.log: 스케줄러 로그만 기록
            return is_scheduler
        else:
            # app.log: 스케줄러 로그 제외
            return not is_scheduler