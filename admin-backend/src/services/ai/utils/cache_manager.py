"""
AI 응답 캐시 관리자.

Redis 기반 캐싱으로 동일 질의에 대한 응답 속도 향상 및 LLM 비용 절감.

Stories: STORY-6-2
FRs: FR30, NFR-P5, NFR-P6, NFR-I3
"""

from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timezone
import hashlib
import json
import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


@dataclass
class CacheConfig:
    """캐시 설정"""

    query_ttl: int = 300  # 쿼리 캐시 TTL (5분)
    schema_ttl: int = 3600  # 스키마 캐시 TTL (1시간)
    stats_ttl: int = 86400  # 통계 TTL (24시간)
    prefix: str = "ai_cache"


@dataclass
class CacheEntry:
    """캐시 항목"""

    data: Any
    created_at: str
    hit_count: int = 0
    from_cache: bool = False


@dataclass
class CacheStats:
    """캐시 통계"""

    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    avg_response_time_cached: float
    avg_response_time_uncached: float


class AICacheManager:
    """AI 응답 캐시 관리자"""

    def __init__(self, redis_client: redis.Redis, config: Optional[CacheConfig] = None):
        self.redis = redis_client
        self.config = config or CacheConfig()
        self._connected = True

    def _generate_cache_key(self, question: str, db_scope: str, admin_role: str) -> str:
        """캐시 키 생성 (질문 + DB + 역할 기반 해시)

        정규화 규칙:
        - 연속 공백 → 단일 공백
        - 대소문자 무시 (소문자 변환)

        해시 충돌 방지:
        - SHA-256 해시의 32자(128bit) 사용
        - 충돌 확률: 2^64 요청 후 50%

        Returns:
            캐시 키 형식: {prefix}:{db_scope}:query:{hash}
            예: ai_cache:mariadb:query:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
        """
        # 정규화: 공백 정리, 소문자 변환
        normalized = " ".join(question.lower().split())
        key_source = f"{normalized}:{db_scope}:{admin_role}"
        # 32자 해시 사용으로 충돌 확률 최소화 (16자 → 32자)
        hash_value = hashlib.sha256(key_source.encode()).hexdigest()[:32]
        # db_scope를 키에 포함하여 스키마 변경 시 무효화 가능하도록
        return f"{self.config.prefix}:{db_scope}:query:{hash_value}"

    async def get_cached_response(
        self, question: str, db_scope: str, admin_role: str
    ) -> Optional[CacheEntry]:
        """캐시된 응답 조회"""
        if not self._connected:
            return None

        try:
            key = self._generate_cache_key(question, db_scope, admin_role)
            cached = await self.redis.get(key)

            if cached:
                # decode_responses=True이므로 cached는 str
                data = json.loads(cached)
                # 히트 카운트 증가
                await self.redis.hincrby(f"{self.config.prefix}:stats", "hits", 1)

                logger.info("cache_hit", key=key, question_preview=question[:50])

                return CacheEntry(
                    data=data["response"],
                    created_at=data["created_at"],
                    hit_count=data.get("hit_count", 0) + 1,
                    from_cache=True,
                )

            # 미스 카운트 증가
            await self.redis.hincrby(f"{self.config.prefix}:stats", "misses", 1)
            return None

        except redis.RedisError as e:
            logger.warning("cache_get_error", error=str(e))
            self._connected = False
            return None

    async def set_cached_response(
        self, question: str, db_scope: str, admin_role: str, response: dict
    ) -> bool:
        """응답 캐싱"""
        if not self._connected:
            return False

        try:
            key = self._generate_cache_key(question, db_scope, admin_role)
            cache_data = {
                "response": response,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "db_scope": db_scope,
                "hit_count": 0,
            }

            await self.redis.setex(
                key,
                self.config.query_ttl,
                json.dumps(cache_data, ensure_ascii=False, default=str),
            )

            logger.info("cache_set", key=key, ttl=self.config.query_ttl)
            return True

        except redis.RedisError as e:
            logger.warning("cache_set_error", error=str(e))
            self._connected = False
            return False

    async def invalidate_by_pattern(self, pattern: str) -> int:
        """패턴 기반 캐시 무효화 (배치 처리로 성능 최적화)

        Args:
            pattern: 무효화할 패턴 (예: "mariadb:query:", "query:")

        Returns:
            삭제된 캐시 개수

        Note:
            100개씩 배치 처리하여 Redis 블로킹 최소화
        """
        if not self._connected:
            return 0

        try:
            deleted = 0
            batch = []
            batch_size = 100  # 100개씩 배치 처리

            async for key in self.redis.scan_iter(
                match=f"{self.config.prefix}:{pattern}*"
            ):
                batch.append(key)
                if len(batch) >= batch_size:
                    deleted += await self.redis.delete(*batch)
                    batch = []

            # 남은 키 처리
            if batch:
                deleted += await self.redis.delete(*batch)

            if deleted > 0:
                logger.info("cache_invalidated", pattern=pattern, deleted_count=deleted)
            return deleted

        except redis.RedisError as e:
            logger.warning("cache_invalidate_error", error=str(e))
            return 0

    async def invalidate_all(self) -> int:
        """전체 캐시 무효화"""
        return await self.invalidate_by_pattern("query:")

    async def get_stats(self) -> CacheStats:
        """캐시 통계 조회

        Returns:
            CacheStats: 캐시 통계 (히트율, 평균 응답 시간 등)

        Note:
            평균 응답 시간은 누적 합계를 카운트로 나눈 값입니다.
            decode_responses=True이므로 stats의 값은 str입니다.
        """
        try:
            stats = await self.redis.hgetall(f"{self.config.prefix}:stats")
            # decode_responses=True이므로 키/값 모두 str
            hits = int(stats.get("hits", "0"))
            misses = int(stats.get("misses", "0"))
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0.0

            # 평균 응답 시간 계산: 누적 합계 / 카운트
            cached_sum = float(stats.get("avg_cached_time", "0"))
            cached_count = int(stats.get("avg_cached_time_count", "1"))
            avg_cached = cached_sum / cached_count if cached_count > 0 else 0.0

            uncached_sum = float(stats.get("avg_uncached_time", "0"))
            uncached_count = int(stats.get("avg_uncached_time_count", "1"))
            avg_uncached = uncached_sum / uncached_count if uncached_count > 0 else 0.0

            return CacheStats(
                total_requests=total,
                cache_hits=hits,
                cache_misses=misses,
                hit_rate=round(hit_rate, 2),
                avg_response_time_cached=round(avg_cached, 2),
                avg_response_time_uncached=round(avg_uncached, 2),
            )

        except redis.RedisError as e:
            logger.warning("cache_stats_error", error=str(e))
            return CacheStats(
                total_requests=0,
                cache_hits=0,
                cache_misses=0,
                hit_rate=0.0,
                avg_response_time_cached=0.0,
                avg_response_time_uncached=0.0,
            )

    async def record_response_time(self, response_time_ms: float, from_cache: bool):
        """응답 시간 기록"""
        try:
            key = "avg_cached_time" if from_cache else "avg_uncached_time"
            count_key = f"{key}_count"

            async with self.redis.pipeline() as pipe:
                await pipe.hincrbyfloat(
                    f"{self.config.prefix}:stats", key, response_time_ms
                )
                await pipe.hincrby(f"{self.config.prefix}:stats", count_key, 1)
                await pipe.execute()

        except redis.RedisError:
            pass  # 통계 실패는 무시

    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            await self.redis.ping()
            self._connected = True
            return True
        except redis.RedisError:
            self._connected = False
            return False
