"""
Redis 기반 LangGraph Checkpointing
"""

from typing import Any, Optional

try:
    from langgraph.checkpoint.redis import RedisSaver

    HAS_REDIS_CHECKPOINT = True
except ImportError:
    # langgraph 버전이 redis checkpoint를 지원하지 않는 경우
    RedisSaver = None  # type: ignore
    HAS_REDIS_CHECKPOINT = False


def create_checkpointer(redis_url: str, ttl: int = 1800) -> Optional[Any]:
    """
    Redis 기반 체크포인터 생성

    Args:
        redis_url: Redis 연결 URL
        ttl: Time-to-live (초 단위, 기본 30분)

    Returns:
        RedisSaver 인스턴스 또는 None (연결 실패 시 또는 지원하지 않는 경우)
    """
    if not HAS_REDIS_CHECKPOINT:
        print(
            "Warning: langgraph.checkpoint.redis not available. Checkpointing disabled."
        )
        return None

    try:
        checkpointer = RedisSaver.from_conn_string(redis_url)  # type: ignore
        # TTL 설정은 Redis 연결에서 처리됨
        return checkpointer
    except Exception as e:
        # 로깅은 상위 레벨에서 처리
        print(f"Redis Checkpointer 초기화 실패: {e}")
        return None
