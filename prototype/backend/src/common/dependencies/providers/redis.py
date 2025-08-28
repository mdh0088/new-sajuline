from __future__ import annotations
from typing import Optional
import redis.asyncio as redis
from src.common.config.settings import get_settings

_redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
	global _redis_client
	if _redis_client is None:
		settings = get_settings()
		_redis_client = await redis.from_url(
			settings.REDIS_URL,
			encoding="utf-8",
			decode_responses=True,
			max_connections=getattr(settings, "REDIS_MAX_CONNECTIONS", 50),
			socket_timeout=getattr(settings, "REDIS_SOCKET_TIMEOUT", 5),
			socket_connect_timeout=getattr(settings, "REDIS_CONNECT_TIMEOUT", 5),
		)
	return _redis_client

async def close_redis() -> None:
	global _redis_client
	if _redis_client is not None:
		await _redis_client.close()
		_redis_client = None
