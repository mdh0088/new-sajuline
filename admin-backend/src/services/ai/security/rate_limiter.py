"""
AI 어시스턴트 Rate Limiter

Redis 기반 sliding window 알고리즘으로 역할별 요청 제한 적용
"""

from datetime import datetime
from typing import Tuple

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status

from .rbac import ROLE_RATE_LIMITS, AIPermission, AIRole


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
    ) -> Tuple[bool, int | None]:
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

        # Redis 키: ai_rate_limit:{admin_id}:{현재 분}
        current_minute = datetime.utcnow().minute
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
            return False, ttl if ttl > 0 else self.window_size

        # 허용
        return True, None


async def rate_limit_dependency(
    permission: AIPermission,
    redis_client: redis.Redis = Depends(lambda: None),  # DI 플레이스홀더
) -> None:
    """
    FastAPI Rate Limit 의존성

    Args:
        permission: AI 권한 정보
        redis_client: Redis 클라이언트

    Raises:
        HTTPException: Rate limit 초과 시 429 에러
    """
    # Redis 클라이언트가 None이면 skip (테스트용)
    if redis_client is None:
        return

    limiter = AIRateLimiter(redis_client)

    allowed, retry_after = await limiter.check_rate_limit(
        admin_id=permission["admin_id"], role=permission["role"]
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"요청 한도를 초과했습니다. {retry_after}초 후 다시 시도해주세요.",
            headers={"Retry-After": str(retry_after)},
        )
