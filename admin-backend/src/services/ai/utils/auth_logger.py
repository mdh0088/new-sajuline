"""
AI 서비스 인증 로거

Stories: 1-2
FRs: FR-012
"""

from datetime import datetime, timezone
from typing import Optional

import structlog

# 구조화 로깅 (JSON 형식)
logger = structlog.get_logger("ai.auth")


async def log_ai_access(
    admin_id: str,
    endpoint: str,
    status: str,
    error_code: Optional[str] = None,
) -> None:
    """
    AI 서비스 접근 로그 기록 (structlog 기반 JSON 로깅)

    Args:
        admin_id: 관리자 ID
        endpoint: 접근한 엔드포인트
        status: 접근 상태 (success/failure)
        error_code: 에러 코드 (실패 시)
    """
    # Mask token in admin_id if it looks like a token (길이 > 20)
    masked_admin_id = admin_id
    if len(admin_id) > 20:
        masked_admin_id = f"***{admin_id[-4:]}"

    log_data = {
        "event": "ai_access",
        "admin_id": masked_admin_id,
        "endpoint": endpoint,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if error_code:
        log_data["error_code"] = error_code

    if status == "success":
        logger.info("ai_access_successful", **log_data)
    else:
        logger.warning("ai_access_failed", **log_data)
