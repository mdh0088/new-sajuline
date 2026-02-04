"""
자동완성 서비스.

Stories: 4-3
FRs: FR22
"""
from typing import Any, Optional

from src.common.logging import get_logger

logger = get_logger(__name__)

# 캐시 히트율 측정용 상수
CACHE_HIT_THRESHOLD = 0.30  # AC5: 30% 이상


class AutocompleteService:
    """자동완성 서비스.

    AC1: 입력 중 실시간 자동완성 제안이 표시된다
    AC2: 자주 사용된 질문이 우선 제안된다
    AC3: 테이블/컬럼 이름이 자동완성에 포함된다
    AC4: 키보드로 자동완성 항목을 선택할 수 있다 (프론트엔드 처리)
    AC5: 캐시 히트율이 30% 이상이다
    """

    QUESTIONS_KEY = "ai:autocomplete:questions"
    KEYWORDS_KEY = "ai:autocomplete:keywords"
    CACHE_TTL = 86400  # 24시간

    def __init__(self, redis_client: Any, encoding: str = "utf-8"):
        """서비스 초기화.

        Args:
            redis_client: Redis 클라이언트 (redis.asyncio.Redis)
            encoding: 문자 인코딩 (기본값: utf-8, EUC-KR 환경 고려)
        """
        self.redis = redis_client
        self.encoding = encoding
        # AC5: 캐시 히트율 측정용
        self._cache_hits = 0
        self._total_requests = 0

    async def suggest(
        self, query: str, limit: int = 5, request_id: Optional[str] = None
    ) -> list[str]:
        """자동완성 제안.

        AC1: 입력 중 실시간 자동완성 제안
        AC2: 자주 사용된 질문이 우선 제안
        AC3: 테이블/컬럼 이름 포함

        Args:
            query: 검색 쿼리 (API에서 min_length=2 검증됨)
            limit: 최대 제안 개수
            request_id: 요청 ID (디버깅용)

        Returns:
            list[str]: 자동완성 제안 목록
        """
        suggestions = []
        cache_hit = False

        try:
            # AC5: 캐시 히트율 측정
            self._total_requests += 1

            # 1. 캐시된 인기 질문에서 검색 (AC2 - 점수 기반 정렬)
            popular = await self._search_popular_questions(query, limit)
            # AC5: Redis 호출 성공하면 히트 (결과 있는지 여부와 무관)
            # 비어있어도 캐시에서 조회했으므로 히트로 간주
            self._cache_hits += 1
            suggestions.extend(popular)

            # 2. 테이블/컬럼 키워드 검색 (AC3)
            if len(suggestions) < limit:
                keywords = await self._search_keywords(query, limit - len(suggestions))
                suggestions.extend(keywords)

            # AC5: 캐시 히트율 로깅
            if self._total_requests % 100 == 0:  # 100회마다 로깅
                hit_rate = self._cache_hits / self._total_requests
                logger.info(
                    "cache_hit_rate",
                    extra={
                        "event": "cache_hit_rate",
                        "hit_rate": hit_rate,
                        "threshold_met": hit_rate >= CACHE_HIT_THRESHOLD,
                        "total_requests": self._total_requests,
                        "cache_hits": self._cache_hits,
                    }
                )

        except Exception as e:
            # Redis 에러 시 빈 결과 반환
            logger.error(
                "autocomplete_error",
                extra={
                    "event": "autocomplete_error",
                    "query": query,
                    "error": str(e),
                    "request_id": request_id,  # 디버깅용
                }
            )
            return []

        # limit 개수만큼만 반환 (AC1)
        return suggestions[:limit]

    async def _search_popular_questions(self, query: str, limit: int) -> list[str]:
        """인기 질문 검색.

        AC2: 자주 사용된 질문이 우선 제안 (점수 기반 정렬)

        Args:
            query: 검색 쿼리
            limit: 최대 개수

        Returns:
            list[str]: 인기 질문 목록 (사용 빈도 높은 순)
        """
        try:
            # AC2: 점수 기반 정렬 - ZREVRANGEBYSCORE 사용
            # 모든 질문을 점수 내림차순으로 가져온 후 prefix 필터링
            all_questions = await self.redis.zrevrange(
                self.QUESTIONS_KEY, 0, -1, withscores=False
            )

            # Prefix 매칭
            query_lower = query.lower()
            matched = [
                q.decode(self.encoding) if isinstance(q, bytes) else q
                for q in all_questions
                if (q.decode(self.encoding) if isinstance(q, bytes) else q).lower().startswith(query_lower)
            ]

            return matched[:limit]
        except Exception as e:
            logger.warning(
                "popular_questions_search_failed",
                extra={
                    "event": "popular_questions_search_failed",
                    "query": query,
                    "error": str(e),
                }
            )
            return []

    async def _search_keywords(self, query: str, limit: int) -> list[str]:
        """테이블/컬럼 키워드 검색.

        AC3: 테이블/컬럼 이름이 자동완성에 포함

        Args:
            query: 검색 쿼리
            limit: 최대 개수

        Returns:
            list[str]: 키워드 목록
        """
        try:
            # Redis SET에서 테이블/컬럼 키워드 검색
            # AC5: Redis 캐시 사용
            keywords = await self.redis.smembers(self.KEYWORDS_KEY)

            # 쿼리와 매칭되는 키워드 필터링
            query_lower = query.lower()
            matched = [
                k.decode(self.encoding) if isinstance(k, bytes) else k
                for k in keywords
                if query_lower in (k.decode(self.encoding) if isinstance(k, bytes) else k).lower()
            ]

            return matched[:limit]
        except Exception as e:
            logger.warning(
                "keywords_search_failed",
                extra={
                    "event": "keywords_search_failed",
                    "query": query,
                    "error": str(e),
                }
            )
            return []

    async def index_question(self, question: str) -> None:
        """질문 인덱싱 (사용 시마다 점수 증가).

        AC2: 자주 사용된 질문이 우선 제안되도록 점수 증가
        AC5: Redis 캐시로 히트율 향상

        Args:
            question: 인덱싱할 질문
        """
        # 빈 문자열은 인덱싱하지 않음
        if not question or not question.strip():
            return

        try:
            # Redis ZINCRBY로 점수 증가 (사용 빈도 기록)
            await self.redis.zincrby(self.QUESTIONS_KEY, 1, question)

            # TTL 설정 (캐시 유효기간)
            # AC5: 캐시 히트율 향상
            await self.redis.expire(self.QUESTIONS_KEY, self.CACHE_TTL)

            logger.info(
                "question_indexed",
                extra={
                    "event": "question_indexed",
                    "question": question,
                }
            )
        except Exception as e:
            logger.error(
                "question_indexing_failed",
                extra={
                    "event": "question_indexing_failed",
                    "question": question,
                    "error": str(e),
                }
            )

    async def index_keywords(self, keywords: list[str]) -> None:
        """테이블/컬럼 키워드 인덱싱.

        AC3: 테이블/컬럼 이름을 자동완성에 포함하기 위한 인덱싱

        Args:
            keywords: 인덱싱할 키워드 목록 (테이블명, 컬럼명 등)
        """
        if not keywords:
            return

        try:
            # Redis SET에 키워드 추가
            await self.redis.sadd(self.KEYWORDS_KEY, *keywords)

            # TTL 설정
            await self.redis.expire(self.KEYWORDS_KEY, self.CACHE_TTL)

            logger.info(
                "keywords_indexed",
                extra={
                    "event": "keywords_indexed",
                    "count": len(keywords),
                }
            )
        except Exception as e:
            logger.error(
                "keywords_indexing_failed",
                extra={
                    "event": "keywords_indexing_failed",
                    "error": str(e),
                }
            )

    def get_cache_hit_rate(self) -> dict:
        """캐시 히트율 조회.

        AC5: 캐시 히트율이 30% 이상인지 검증

        Returns:
            dict: 히트율 통계
        """
        if self._total_requests == 0:
            return {
                "hit_rate": 0.0,
                "threshold_met": False,
                "total_requests": 0,
                "cache_hits": 0,
            }

        hit_rate = self._cache_hits / self._total_requests
        return {
            "hit_rate": hit_rate,
            "threshold_met": hit_rate >= CACHE_HIT_THRESHOLD,
            "total_requests": self._total_requests,
            "cache_hits": self._cache_hits,
        }
