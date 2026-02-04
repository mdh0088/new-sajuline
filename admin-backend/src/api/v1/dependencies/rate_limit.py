"""
Rate Limit FastAPI 의존성.

Stories: 3-4
FRs: FR28
"""
from typing import TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, Request, status

from src.services.ai.audit.audit_logger import AIAuditLogger
from src.services.ai.audit.rate_limiter import AIRateLimiter, AIRole

if TYPE_CHECKING:
    import redis.asyncio as redis

    from src.models.admin_model import Admin


def get_admin_ai_role(admin: "Admin") -> AIRole:
    """
    관리자 역할을 AIRole로 변환.

    Args:
        admin: Admin 모델 인스턴스

    Returns:
        AIRole: AI 서비스 역할
    """
    role_mapping = {
        "super_admin": AIRole.SUPER_ADMIN,
        "admin": AIRole.ADMIN,
        "viewer": AIRole.VIEWER,
    }
    return role_mapping.get(admin.role, AIRole.VIEWER)


async def rate_limit_dependency(
    request: Request,
    current_admin: "Admin",
    redis_client: Any,  # redis.Redis from redis.asyncio
) -> "Admin":
    """
    Rate limit 검증 의존성.

    Args:
        request: FastAPI Request
        current_admin: 현재 로그인한 관리자
        redis_client: Redis 클라이언트

    Returns:
        Admin: 인증된 관리자 (rate limit 통과 시)

    Raises:
        HTTPException: 429 (Rate limit 초과)
    """
    # 관리자 역할 확인
    role = get_admin_ai_role(current_admin)

    # Rate limiter 생성 및 확인
    limiter = AIRateLimiter(redis_client)
    result = await limiter.check_rate_limit(current_admin.id, role)

    # Rate limit 초과
    if not result.allowed:
        # 감사 로그 기록
        await AIAuditLogger.log_rate_limit_exceeded(
            admin_id=current_admin.id,
            admin_role=role.value,
            current_count=result.current_count,
            limit=result.limit,
        )

        # 429 HTTPException 발생
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"요청 한도를 초과했습니다. {result.retry_after}초 후 다시 시도해주세요.",
                "code": "AIBI_RATE_LIMITED",
                "retry_after": result.retry_after,
            },
            headers={
                "Retry-After": str(result.retry_after),
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(result.window_reset),
            },
        )

    # Rate limit 허용 - 헤더 정보 설정
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(result.limit),
        "X-RateLimit-Remaining": str(result.limit - result.current_count),
        "X-RateLimit-Reset": str(result.window_reset),
    }

    return current_admin
