"""
Python logging 표준 설정 (T-070)

환경변수와 settings를 기반으로 dictConfig 초기화 및 get_logger 제공
콘솔/파일 동시 출력 및 텍스트/JSON 포맷 토글 구조
"""

from __future__ import annotations

# stdlib
import contextvars
import datetime
import logging
import logging.config
import os
from typing import Any, Dict

# third-party
from pythonjsonlogger import jsonlogger

# local
from src.common.config.settings import get_settings


# ContextVar for per-request correlation
trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
# Optional user id for logs (set by auth dependency or middleware)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)

def set_trace_id(trace_id: str) -> contextvars.Token:
    """요청별 trace ID 설정 (미들웨어 연동용)"""
    return trace_id_var.set(trace_id)

def reset_trace_id(token: contextvars.Token) -> None:
    """trace ID 복원 (미들웨어 연동용)"""
    try:
        trace_id_var.reset(token)
    except Exception:
        pass


def set_user_id(user_id: str | None) -> contextvars.Token:
    """요청 사용자 ID 설정 (없으면 None)."""
    return user_id_var.set(user_id)


def reset_user_id(token: contextvars.Token) -> None:
    """요청 사용자 ID 복원."""
    try:
        user_id_var.reset(token)
    except Exception:
        pass


def _ensure_log_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass


def _build_handlers(settings) -> Dict[str, Any]:
    log_level = settings.LOG_LEVEL.upper()
    to_stdout = settings.LOG_TO_STDOUT
    to_file = settings.LOG_TO_FILE
    log_dir = settings.LOG_DIR
    log_file = settings.LOG_FILE_NAME

    handlers: Dict[str, Any] = {}

    if to_stdout:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "text",
            "stream": "ext://sys.stdout",
        }

    if to_file:
        _ensure_log_dir(log_dir)
        handlers["file"] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": log_level,
            "formatter": "text",
            "filename": os.path.join(log_dir, log_file),
            "when": "midnight",
            "interval": 1,
            # backupCount: number of rotated files to keep (daily rotation)
            "backupCount": int(os.getenv("LOG_BACKUP_COUNT", "7")),
            "encoding": "utf-8",
        }

    if not handlers:
        # 최소 한 개는 존재하도록
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "text",
            "stream": "ext://sys.stdout",
        }

    return handlers


def build_dict_config() -> Dict[str, Any]:
    settings = get_settings()
    log_level = settings.LOG_LEVEL.upper()
    
    service_name = settings.SERVICE_NAME
    service_version = settings.SERVICE_VERSION
    env = settings.ENVIRONMENT
    
    default_json = "true" if env.lower() in {"prod", "production", "staging"} else "false"
    json_enabled = os.getenv("LOG_JSON", default_json).lower() == "true"

    text_format = (
        "%(asctime)s %(levelname)s %(name)s | %(message)s | "
        "trace_id=%(trace_id)s user_id=%(user_id)s "
        "service=%(service)s env=%(env)s version=%(version)s"
    )

    class RequestIdFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
            record.trace_id = trace_id_var.get()
            record.user_id = user_id_var.get()
            record.service = service_name
            record.env = env
            record.version = service_version
            return True

    class UTCJsonFormatter(jsonlogger.JsonFormatter):
        def formatTime(self, record, datefmt=None):  # noqa: D401
            return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        def add_fields(self, log_record, record, message_dict):  # noqa: D401
            super().add_fields(log_record, record, message_dict)
            log_record.setdefault("timestamp", self.formatTime(record))
            log_record.setdefault("level", record.levelname)
            log_record.setdefault("logger", record.name)
            log_record.setdefault("service", service_name)
            log_record.setdefault("env", env)
            log_record.setdefault("version", service_version)
            rid = getattr(record, "trace_id", None)
            if rid:
                log_record.setdefault("trace_id", rid)
            uid = getattr(record, "user_id", None)
            if uid:
                log_record.setdefault("user_id", uid)

    formatters: Dict[str, Any] = {
        "text": {
            "format": text_format,
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "()": logging.Formatter,
        }
    }

    if json_enabled:
        formatters["json"] = {"()": UTCJsonFormatter}

    handlers = _build_handlers(settings)

    # json 포맷 요청 시 콘솔/파일 포맷터 교체
    if json_enabled:
        for h in handlers.values():
            h["formatter"] = "json"

    # 필터 등록 및 모든 핸들러에 연결
    filters = {
        "request_context": {"()": RequestIdFilter},
    }
    for h in handlers.values():
        h.setdefault("filters", []).append("request_context")

    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "filters": filters,
        "handlers": handlers,
        "loggers": {
            # 루트 로거
            "": {
                "level": log_level,
                "handlers": list(handlers.keys()),
            },
            # 애플리케이션 네임스페이스 예시
            "app": {"level": log_level, "propagate": True},
            # Uvicorn 로거들을 통일된 핸들러/포맷으로 설정
            "uvicorn": {"level": log_level, "handlers": list(handlers.keys()), "propagate": False},
            "uvicorn.error": {"level": log_level, "handlers": list(handlers.keys()), "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": list(handlers.keys()), "propagate": False},
        },
    }

    return config


def configure_logging() -> None:
    logging.config.dictConfig(build_dict_config())


def get_logger(name: str) -> logging.Logger:
    """네임스페이스 로거 획득 유틸."""
    return logging.getLogger(name)


