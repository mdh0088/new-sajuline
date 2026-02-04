"""
AI 감사 로깅 설정.

90일 보관 정책과 함께 구조화된 JSON 로깅을 제공합니다.

Stories: 3-4
FRs: FR17, NFR-S5
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler


def configure_ai_audit_logging():
    """
    AI 감사 로깅 설정 (AC 3: 90일 보관).

    - 파일: logs/ai_audit.log
    - 로테이션: 매일 자정 (midnight)
    - 보관 기간: 90일 (backupCount=90)
    - 포맷: JSON 구조화 로그

    Note: AC 3 부분 구현
    - TimedRotatingFileHandler의 backupCount=90은 최대 90개의 백업 파일 유지
    - 매일 로테이션하므로 약 90일간 보관됨
    - 완전한 90일 보장을 위해서는 별도 정리 작업(cron/scheduler) 필요
    - 현재 구현: 간단한 파일 개수 기반 보관 (프로덕션에서는 추가 스케줄러 권장)
    """
    # logs 디렉토리 생성
    os.makedirs("logs", exist_ok=True)

    # AI 감사 전용 로거
    logger = logging.getLogger("ai.audit")
    logger.setLevel(logging.INFO)

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()

    # 파일 핸들러 (90일 보관)
    file_handler = TimedRotatingFileHandler(
        filename="logs/ai_audit.log",
        when="midnight",  # 매일 자정 로테이션
        interval=1,  # 1일마다
        backupCount=90,  # 최대 90개 백업 파일 (≈90일)
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    # 포맷터 설정 (JSON은 audit_logger에서 처리)
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)

    return logger
