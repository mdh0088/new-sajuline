"""
DB 스키마 캐시 및 변경 감지.

스키마 캐싱으로 불필요한 DB 메타데이터 조회를 줄이고,
스키마 변경 시 관련 쿼리 캐시를 자동 무효화합니다.

Stories: STORY-6-2
FRs: FR30, NFR-P6
"""

from typing import Any, Dict, Optional
import redis.asyncio as redis
import json
import hashlib
import structlog

logger = structlog.get_logger()


class SchemaCacheManager:
    """DB 스키마 캐시 및 변경 감지"""

    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        """
        Args:
            redis_client: Redis 클라이언트
            ttl: 스키마 캐시 TTL (기본: 1시간)
        """
        self.redis = redis_client
        self.ttl = ttl
        self.key_prefix = "ai_cache:schema"

    async def get_schema(self, db_scope: str) -> Optional[Dict[str, Any]]:
        """캐시된 스키마 조회"""
        try:
            cached = await self.redis.get(f"{self.key_prefix}:{db_scope}")
            if cached:
                return json.loads(cached)
            return None
        except redis.RedisError:
            return None

    async def set_schema(self, db_scope: str, schema: Dict[str, Any]) -> bool:
        """스키마 캐싱"""
        try:
            await self.redis.setex(
                f"{self.key_prefix}:{db_scope}",
                self.ttl,
                json.dumps(schema, ensure_ascii=False),
            )
            return True
        except redis.RedisError:
            return False

    async def check_schema_change(
        self, db_scope: str, current_schema: Dict[str, Any]
    ) -> bool:
        """스키마 변경 감지"""
        cached = await self.get_schema(db_scope)
        if cached is None:
            return False  # 캐시 없음 = 변경 감지 불가

        # 스키마 해시 비교
        cached_hash = self._schema_hash(cached)
        current_hash = self._schema_hash(current_schema)

        if cached_hash != current_hash:
            logger.warning(
                "schema_change_detected",
                db_scope=db_scope,
                cached_hash=cached_hash,
                current_hash=current_hash,
            )
            return True
        return False

    def _schema_hash(self, schema: Dict[str, Any]) -> str:
        """스키마 해시 생성

        Note:
            SHA-256 사용 (MD5는 보안 취약점으로 deprecated)
            NIST, OWASP 권고사항 준수
        """
        sorted_str = json.dumps(schema, sort_keys=True)
        return hashlib.sha256(sorted_str.encode()).hexdigest()

    async def invalidate_on_schema_change(self, db_scope: str, cache_manager: Any):
        """스키마 변경 시 관련 쿼리 캐시 무효화

        Args:
            db_scope: DB 스코프 (mariadb, mssql 등)
            cache_manager: AICacheManager 인스턴스

        Note:
            캐시 키 형식: ai_cache:{db_scope}:query:{hash}
            패턴: {db_scope}:query: 로 해당 DB의 모든 쿼리 캐시 삭제
        """
        # db_scope가 키에 포함되므로 정확한 패턴 매칭 가능
        deleted = await cache_manager.invalidate_by_pattern(f"{db_scope}:query:")
        logger.info(
            "schema_change_cache_invalidated", db_scope=db_scope, deleted_count=deleted
        )
