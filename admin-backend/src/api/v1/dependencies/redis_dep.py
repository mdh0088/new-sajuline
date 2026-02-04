"""
Redis dependency for FastAPI.

Stories: STORY-6-2
FRs: FR30, NFR-I3
"""

from typing import AsyncGenerator
import redis.asyncio as redis
from fastapi import Depends

from src.config.settings import settings
from src.common.logging import get_logger

logger = get_logger(__name__)


async def get_redis_client() -> AsyncGenerator[redis.Redis | None, None]:
    """Redis 클라이언트 생성 및 반환

    Yields:
        Redis 클라이언트 인스턴스 또는 None (연결 실패 시)

    Note:
        각 요청마다 새로운 연결을 생성하지만, redis-py는 내부적으로
        연결 풀을 관리하므로 효율적입니다.

        Redis 연결 실패 시 None을 반환하여 API가 graceful하게 동작합니다.
    """
    client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,  # str로 받아서 타입 일관성 유지
    )

    try:
        # 연결 확인
        await client.ping()
        yield client
    except redis.RedisError as e:
        logger.warning(
            "redis_connection_failed", error=str(e), url=settings.REDIS_URL
        )
        # Redis 연결 실패 시에도 None을 yield하여 API가 계속 동작하도록 함
        yield None
    finally:
        # 연결 종료 (이미 닫힌 연결은 무시)
        try:
            await client.close()
        except Exception:
            pass  # 이미 닫힌 연결 무시
