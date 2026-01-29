"""
운세 캐시 서비스

Story 2.3: 운세 캐시 시스템 (Redis + DB 이중 캐싱)

AC1: Redis 캐싱 + DB 영구 저장
AC2: Redis 캐시 히트 시 DB 조회 없이 반환
AC3: Redis 미스 시 DB 폴백 + 캐시 재설정
AC4: Redis 장애 시 DB 폴백으로 정상 응답
AC5: 기간별 TTL 적용
"""
from datetime import date
from typing import Optional, Tuple

import redis.asyncio as redis

from src.models.fortune_history_model import FortuneType
from src.repositories.fortune_repository import FortuneRepository
from src.schemas.fortune_schema import FortuneResponse
from src.common.logging import logger, get_logger_with_request_id


# TTL 설정 (초 단위)
FORTUNE_TTL = {
    FortuneType.DAILY: 24 * 60 * 60,       # 24시간 (86400초)
    FortuneType.WEEKLY: 7 * 24 * 60 * 60,   # 7일 (604800초)
    FortuneType.MONTHLY: 30 * 24 * 60 * 60,  # 30일 (2592000초)
    FortuneType.YEARLY: 365 * 24 * 60 * 60,  # 365일 (31536000초)
}


class FortuneCacheService:
    """
    운세 캐시 서비스 (Redis + DB 이중 캐싱)

    캐시 조회 순서: Redis → DB → None
    캐시 저장: DB (영구) + Redis (TTL)
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        repository: FortuneRepository
    ):
        self.redis = redis_client
        self.repository = repository
        self.key_prefix = "fortune:"

    @logger.catch(reraise=True)
    async def get_cached_fortune(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date
    ) -> Tuple[Optional[FortuneResponse], str]:
        """
        캐시된 운세 조회 (Redis → DB 순서)

        Args:
            user_id: 사용자 ID
            fortune_type: 운세 유형 (FortuneType Enum)
            target_date: 운세 대상 날짜

        Returns:
            tuple: (운세 데이터 또는 None, cache_status: "HIT" | "DB_HIT" | "MISS")
        """
        log = get_logger_with_request_id()
        cache_key = self._build_cache_key(user_id, fortune_type, target_date)

        # 1. Redis 조회 시도
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                log.info("Redis cache HIT", cache_key=cache_key, user_id=user_id)
                return FortuneResponse.model_validate_json(cached), "HIT"
        except Exception as e:
            log.warning(
                "Redis 조회 실패, DB 폴백",
                error=str(e),
                cache_key=cache_key
            )

        # 2. DB 조회 시도
        history = await self.repository.get_fortune_by_user_date(
            user_id=user_id,
            fortune_type=fortune_type.value,
            target_date=target_date
        )

        if history:
            log.info("DB cache HIT", user_id=user_id, history_id=history.id)
            response = self._history_to_response(history)
            # Redis 재설정 시도 (실패해도 서비스 지속)
            await self._try_set_redis(cache_key, response, fortune_type)
            return response, "DB_HIT"

        log.info("Cache MISS", user_id=user_id, fortune_type=fortune_type.value)
        return None, "MISS"

    @logger.catch(reraise=True)
    async def set_fortune_cache(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date,
        fortune_data: FortuneResponse,
        ai_model: str = "gpt-4o-mini",
        prompt_version: str = "v1.0.0"
    ) -> bool:
        """
        운세 캐시 저장 (Redis + DB 동시)

        Args:
            user_id: 사용자 ID
            fortune_type: 운세 유형
            target_date: 운세 대상 날짜
            fortune_data: 저장할 운세 데이터
            ai_model: 사용된 AI 모델
            prompt_version: 프롬프트 버전

        Returns:
            bool: 저장 성공 여부
        """
        log = get_logger_with_request_id()
        cache_key = self._build_cache_key(user_id, fortune_type, target_date)

        # 1. DB 저장 (영구)
        await self.repository.create_fortune_history(
            user_id=user_id,
            fortune_type=fortune_type.value,
            target_date=target_date,
            content=fortune_data.model_dump_json(),
            ai_model=ai_model,
            prompt_version=prompt_version
        )

        # 2. Redis 저장 (TTL)
        redis_success = await self._try_set_redis(cache_key, fortune_data, fortune_type)

        log.info(
            "Fortune cached",
            user_id=user_id,
            fortune_type=fortune_type.value,
            target_date=str(target_date),
            redis_success=redis_success
        )
        return True

    async def invalidate_cache(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date
    ) -> bool:
        """
        캐시 무효화 (선택적 기능)

        Args:
            user_id: 사용자 ID
            fortune_type: 운세 유형
            target_date: 운세 대상 날짜

        Returns:
            bool: 무효화 성공 여부
        """
        log = get_logger_with_request_id()
        cache_key = self._build_cache_key(user_id, fortune_type, target_date)

        try:
            await self.redis.delete(cache_key)
            log.info("Cache invalidated", cache_key=cache_key)
            return True
        except Exception as e:
            log.warning("Cache invalidation failed", error=str(e), cache_key=cache_key)
            return False

    async def _try_set_redis(
        self,
        cache_key: str,
        data: FortuneResponse,
        fortune_type: FortuneType
    ) -> bool:
        """
        Redis 저장 시도 (실패해도 서비스 중단 안함)

        Args:
            cache_key: Redis 캐시 키
            data: 저장할 운세 데이터
            fortune_type: 운세 유형 (TTL 결정용)

        Returns:
            bool: 저장 성공 여부
        """
        try:
            ttl = self._get_ttl(fortune_type)
            await self.redis.setex(cache_key, ttl, data.model_dump_json())
            return True
        except Exception as e:
            log = get_logger_with_request_id()
            log.error("Redis 저장 실패", error=str(e), cache_key=cache_key)
            return False

    def _build_cache_key(
        self,
        user_id: str,
        fortune_type: FortuneType,
        target_date: date
    ) -> str:
        """
        캐시 키 생성

        형식: fortune:{type}:{user_id}:{date_key}
        예: fortune:daily:user123:2026-01-29
        """
        date_key = self._get_date_key(fortune_type, target_date)
        return f"{self.key_prefix}{fortune_type.value}:{user_id}:{date_key}"

    def _get_date_key(self, fortune_type: FortuneType, target_date: date) -> str:
        """
        기간별 날짜 키 형식 반환

        - daily: 2026-01-29
        - weekly: 2026-W05
        - monthly: 2026-01
        - yearly: 2026
        """
        if fortune_type == FortuneType.DAILY:
            return target_date.isoformat()
        elif fortune_type == FortuneType.WEEKLY:
            return target_date.strftime("%Y-W%W")
        elif fortune_type == FortuneType.MONTHLY:
            return target_date.strftime("%Y-%m")
        elif fortune_type == FortuneType.YEARLY:
            return str(target_date.year)
        return target_date.isoformat()

    def _get_ttl(self, fortune_type: FortuneType) -> int:
        """
        기간별 TTL 반환 (초 단위)

        - daily: 24시간 (86400초)
        - weekly: 7일 (604800초)
        - monthly: 30일 (2592000초)
        - yearly: 365일 (31536000초)
        """
        return FORTUNE_TTL.get(fortune_type, FORTUNE_TTL[FortuneType.DAILY])

    def _history_to_response(self, history) -> FortuneResponse:
        """
        DB 이력을 응답 스키마로 변환

        Args:
            history: FortuneHistory 모델 인스턴스

        Returns:
            FortuneResponse: 변환된 응답 스키마
        """
        return FortuneResponse.model_validate_json(history.content)
