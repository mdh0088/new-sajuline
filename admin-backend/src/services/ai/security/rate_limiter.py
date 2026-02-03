"""
AI 어시스턴트 Rate Limiter

Redis 기반 sliding window 알고리즘으로 역할별 요청 제한 적용
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status

from .audit_logger import log_rate_limit_exceeded
from .rbac import ROLE_RATE_LIMITS, AIPermission, AIRole

logger = logging.getLogger(__name__)
KST = ZoneInfo("Asia/Seoul")


class AIRateLimiter:
    """AI 어시스턴트 Rate Limiter"""

    def __init__(self, redis_client: redis.Redis):
        """
        Args:
            redis_client: Redis 클라이언트
        """
        self.redis = redis_client
        self.window_size = 60  # 1분 윈도우

    async def check_rate_limit(
        self, admin_id: int, role: AIRole
    ) -> tuple[bool, int | None]:
        """
        Rate limit 체크

        Args:
            admin_id: 관리자 ID
            role: AI 역할

        Returns:
            tuple[bool, int | None]: (허용 여부, retry_after 초)
        """
        # 역할별 limit 가져오기
        limit = ROLE_RATE_LIMITS[role]

        # Redis 키: ai_rate_limit:{admin_id}:{현재 분} (KST 기준)
        current_minute = datetime.now(KST).minute
        key = f"ai_rate_limit:{admin_id}:{current_minute}"

        # 요청 카운트 증가
        current_count = await self.redis.incr(key)

        # 첫 요청이면 TTL 설정
        if current_count == 1:
            await self.redis.expire(key, self.window_size)

        # Limit 체크
        if current_count > limit:
            # Rate limit 초과
            ttl = await self.redis.ttl(key)

            # TTL 음수 처리 (Redis 상태 이상)
            if ttl < 0:
                logger.warning(
                    f"Rate limit key TTL is negative: {ttl} for admin {admin_id}"
                )
                ttl = self.window_size

            return False, ttl

        # 허용
        return True, None


async def get_redis_client() -> redis.Redis:
    """
    Redis 클라이언트 DI

    Returns:
        redis.Redis: Redis 클라이언트 인스턴스
    """
    from src.config.settings import settings

    redis_client = redis.from_url(
        settings.ai_redis_url, decode_responses=True, socket_timeout=5
    )
    try:
        yield redis_client
    finally:
        await redis_client.close()


async def rate_limit_dependency(
    permission: AIPermission,
    redis_client: redis.Redis = Depends(get_redis_client),
) -> None:
    """
    FastAPI Rate Limit 의존성

    Args:
        permission: AI 권한 정보
        redis_client: Redis 클라이언트

    Raises:
        HTTPException: Rate limit 초과 시 429 에러
    """
    # Redis 연결 실패 시 로깅 후 우회 (가용성 우선)
    try:
        await redis_client.ping()
    except Exception as e:
        logger.error(
            f"Redis connection failed for rate limiting: {e}. "
            f"Allowing request without rate limit (availability priority)"
        )
        return

    limiter = AIRateLimiter(redis_client)

    allowed, retry_after = await limiter.check_rate_limit(
        admin_id=permission["admin_id"], role=permission["role"]
    )

    if not allowed:
        # Rate Limit 초과 로깅
        log_rate_limit_exceeded(
            admin_id=permission["admin_id"],
            role=permission["role"],
            retry_after=retry_after,
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"요청 한도를 초과했습니다. {retry_after}초 후 다시 시도해주세요.",
            headers={"Retry-After": str(retry_after)},
        )
