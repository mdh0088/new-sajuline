"""
로깅 구성 설정
Loguru 기반 구조화 로깅 시스템
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger

from src.config.settings import settings


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

        # 파일 핸들러 추가 (관리자 로그)
        logger.add(
            self.log_dir / "admin.log",
            level="INFO",
            format=self._get_file_format(),
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            serialize=False,
            filter=RequestContextFilter()
        )

        # 에러 파일 핸들러
        logger.add(
            self.log_dir / "admin_error.log",
            level="ERROR",
            format=self._get_file_format(),
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            serialize=False,
            filter=RequestContextFilter()
        )

        # 감사 로그 (관리자 전용)
        if settings.enable_audit_log:
            logger.add(
                self.log_dir / "audit.log",
                level="INFO",
                format=self._get_audit_format(),
                rotation="50 MB",
                retention=f"{settings.audit_log_retention_days} days",
                compression="gz",
                serialize=False,
                filter=lambda record: record.get("extra", {}).get("audit", False)
            )

        logger.info("Admin logging system initialized", extra={
            "log_level": self.log_level,
            "environment": settings.app_env,
            "audit_enabled": settings.enable_audit_log
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

    def _get_file_format(self) -> str:
        """간결한 파일 포맷"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message} | "
            "{extra}"
        )

    def _get_audit_format(self) -> str:
        """감사 로그 포맷"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "AUDIT | "
            "{extra[admin_id]} | "
            "{extra[action]} | "
            "{extra[resource]} | "
            "{extra[ip]} | "
            "{message}"
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