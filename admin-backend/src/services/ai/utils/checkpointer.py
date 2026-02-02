"""
Redis 기반 LangGraph Checkpointing
"""

from typing import Optional

from langgraph.checkpoint.redis import RedisSaver


def create_checkpointer(redis_url: str, ttl: int = 1800) -> Optional[RedisSaver]:
    """
    Redis 기반 체크포인터 생성

    Args:
        redis_url: Redis 연결 URL
        ttl: Time-to-live (초 단위, 기본 30분)

    Returns:
        RedisSaver 인스턴스 또는 None (연결 실패 시)
    """
    try:
        checkpointer = RedisSaver.from_conn_string(redis_url)
        # TTL 설정은 Redis 연결에서 처리됨
        return checkpointer
    except Exception as e:
        # 로깅은 상위 레벨에서 처리
        print(f"Redis Checkpointer 초기화 실패: {e}")
        return None
