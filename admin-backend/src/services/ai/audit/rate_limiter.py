"""
AI 서비스 Rate Limiter (Sliding Window).

Redis 기반으로 역할별 요청 빈도를 제한합니다.

Stories: 3-4
FRs: FR28
"""
from typing import TYPE_CHECKING
from datetime import datetime, UTC
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    import redis.asyncio as redis


class AIRole(str, Enum):
    """AI 어시스턴트 역할 (순환 참조 방지용 로컬 정의)"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"


# 역할별 분당 요청 제한 (AC 4)
# - Super Admin: 고급 분석 및 복잡한 쿼리 허용
# - Admin: 일반 운영 업무 수행
# - Viewer: 읽기 전용 조회 제한
RATE_LIMITS = {
    AIRole.SUPER_ADMIN: 60,  # 60 req/min
    AIRole.ADMIN: 30,  # 30 req/min
    AIRole.VIEWER: 10,  # 10 req/min
}

# 시간당 제한 (향후 확장용)
# 현재는 분당 제한만 적용, 시간당 제한은 추후 구현 예정
HOURLY_LIMITS = {
    AIRole.SUPER_ADMIN: 600,  # 600 req/hour
    AIRole.ADMIN: 300,  # 300 req/hour
    AIRole.VIEWER: 100,  # 100 req/hour
}


@dataclass
class RateLimitResult:
    """Rate Limit 확인 결과"""

    allowed: bool
    current_count: int
    limit: int
    retry_after: int | None = None
    window_reset: int | None = None


class AIRateLimiter:
    """AI 서비스 Rate Limiter (Sliding Window Counter)"""

    WINDOW_SIZE = 60  # 1분 (초)

    def __init__(self, redis_client):
        """
        Rate Limiter 초기화.

        Args:
            redis_client: Redis 클라이언트
        """
        self.redis = redis_client

    async def check_rate_limit(
        self,
        admin_id: int,
        role: AIRole,
    ) -> RateLimitResult:
        """
        Rate limit 확인 (Sliding Window Counter).

        Args:
            admin_id: 관리자 ID
            role: 관리자 역할 (AIRole)

        Returns:
            RateLimitResult: Rate limit 확인 결과
        """
        # 역할별 제한 조회
        limit = RATE_LIMITS.get(role, 10)

        # 현재 분(minute) 계산
        now = datetime.now(UTC)
        current_minute = now.strftime("%Y%m%d%H%M")

        # Redis 키: ai_ratelimit:{admin_id}:{minute}
        key = f"ai_ratelimit:{admin_id}:{current_minute}"

        # 현재 카운트 증가
        current = await self.redis.incr(key)

        # 첫 요청이면 만료 설정 (60초 + 10초 여유)
        if current == 1:
            await self.redis.expire(key, self.WINDOW_SIZE + 10)

        # 제한 초과 확인
        if current > limit:
            # TTL 조회
            ttl = await self.redis.ttl(key)
            retry_after = max(ttl, 1)  # 최소 1초

            return RateLimitResult(
                allowed=False,
                current_count=current,
                limit=limit,
                retry_after=retry_after,
                window_reset=retry_after,
            )

        # 허용
        return RateLimitResult(
            allowed=True,
            current_count=current,
            limit=limit,
            window_reset=self.WINDOW_SIZE,
        )

    async def get_usage_stats(
        self,
        admin_id: int,
        role: AIRole,
    ) -> dict:
        """
        사용량 통계 조회.

        Args:
            admin_id: 관리자 ID
            role: 관리자 역할

        Returns:
            dict: 사용량 통계
        """
        now = datetime.now(UTC)
        current_minute = now.strftime("%Y%m%d%H%M")
        key = f"ai_ratelimit:{admin_id}:{current_minute}"

        # 현재 카운트 조회
        current = await self.redis.get(key)
        limit = RATE_LIMITS.get(role, 10)

        current_count = int(current) if current else 0

        return {
            "current": current_count,
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset_seconds": self.WINDOW_SIZE,
        }
