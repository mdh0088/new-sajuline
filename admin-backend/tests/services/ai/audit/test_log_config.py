"""
로깅 설정 테스트.

Stories: 3-4
"""
import pytest
from unittest.mock import Mock, patch, call
import logging
from src.services.ai.audit.log_config import configure_ai_audit_logging


class TestLogConfig:
    """로깅 설정 테스트"""

    def test_configure_creates_ai_audit_logger(self):
        """AI 감사 로거가 생성되는지 확인"""
        with patch("src.services.ai.audit.log_config.logging") as mock_logging, \
             patch("src.services.ai.audit.log_config.TimedRotatingFileHandler"), \
             patch("src.services.ai.audit.log_config.os.makedirs"):
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO  # 실제 값 사용

            configure_ai_audit_logging()

            # ai.audit 로거가 요청되었는지 확인
            mock_logging.getLogger.assert_called_once_with("ai.audit")

    def test_configure_adds_file_handler(self):
        """파일 핸들러가 추가되는지 확인"""
        with patch("src.services.ai.audit.log_config.logging") as mock_logging, \
             patch("src.services.ai.audit.log_config.TimedRotatingFileHandler") as MockHandler, \
             patch("src.services.ai.audit.log_config.os.makedirs"):
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO  # 실제 값 사용
            mock_handler = MockHandler.return_value

            configure_ai_audit_logging()

            # TimedRotatingFileHandler 생성 확인
            MockHandler.assert_called_once_with(
                filename="logs/ai_audit.log",
                when="midnight",
                interval=1,
                backupCount=90,
                encoding="utf-8",
            )

            # 핸들러가 로거에 추가되었는지 확인
            mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_configure_sets_log_level_info(self):
        """로그 레벨이 INFO로 설정되는지 확인"""
        with patch("src.services.ai.audit.log_config.logging") as mock_logging, \
             patch("src.services.ai.audit.log_config.TimedRotatingFileHandler"):
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO  # 실제 값 사용

            configure_ai_audit_logging()

            # 로거 레벨이 INFO로 설정되었는지 확인
            mock_logger.setLevel.assert_called_once_with(logging.INFO)

    def test_90_day_backup_count(self):
        """90일 보관 설정 확인"""
        with patch("src.services.ai.audit.log_config.logging") as mock_logging, \
             patch("src.services.ai.audit.log_config.TimedRotatingFileHandler") as MockHandler, \
             patch("src.services.ai.audit.log_config.os.makedirs"):
            mock_logging.INFO = logging.INFO  # 실제 값 사용
            mock_logging.getLogger.return_value = Mock()

            configure_ai_audit_logging()

            # backupCount가 90인지 확인
            call_kwargs = MockHandler.call_args[1]
            assert call_kwargs["backupCount"] == 90

    def test_logs_directory_creation(self):
        """logs 디렉토리가 생성되는지 확인"""
        with patch("src.services.ai.audit.log_config.logging") as mock_logging, \
             patch("src.services.ai.audit.log_config.TimedRotatingFileHandler"), \
             patch("src.services.ai.audit.log_config.os.makedirs") as mock_makedirs:
            mock_logging.INFO = logging.INFO  # 실제 값 사용
            mock_logging.getLogger.return_value = Mock()

            configure_ai_audit_logging()

            # logs 디렉토리 생성 확인
            mock_makedirs.assert_called_once_with("logs", exist_ok=True)
