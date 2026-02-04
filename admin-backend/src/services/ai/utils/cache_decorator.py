"""
캐시 데코레이터.

함수에 캐싱 기능을 추가하는 데코레이터를 제공합니다.

Usage Example:
    ```python
    from src.services.ai.utils.cache_manager import AICacheManager
    from src.services.ai.utils.cache_decorator import cacheable

    # Redis 클라이언트 생성
    redis_client = redis.from_url("redis://localhost:6379")
    cache_manager = AICacheManager(redis_client)

    # 함수에 캐싱 적용
    @cacheable(cache_manager)
    async def execute_query(question: str, db_scope: str, admin_role: str):
        # 실제 쿼리 실행 로직
        return {"answer": "...", "data": [...]}

    # 첫 호출: LLM 실행 + 캐싱
    result1 = await execute_query("오늘 매출", "mariadb", "admin")
    # result1 = {"answer": "...", "from_cache": False}

    # 두 번째 호출: 캐시에서 반환 (5분 내)
    result2 = await execute_query("오늘 매출", "mariadb", "admin")
    # result2 = {"answer": "...", "from_cache": True, "cached_at": "..."}
    ```

Stories: STORY-6-2
FRs: FR30, NFR-P6
"""

from functools import wraps
from typing import Callable
import time


def cacheable(cache_manager, key_params: list[str] = ["question", "db_scope"]):
    """
    캐시 데코레이터.

    함수 실행 전 캐시를 조회하고, 캐시 미스 시 함수를 실행한 후 결과를 캐싱합니다.

    Args:
        cache_manager: AICacheManager 인스턴스
        key_params: 캐시 키 생성에 사용할 파라미터 목록

    Returns:
        데코레이터 함수
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 파라미터 추출
            question = kwargs.get("question", "")
            db_scope = kwargs.get("db_scope", "mariadb")
            admin_role = kwargs.get("admin_role", "admin")

            start_time = time.time()

            # 캐시 조회
            cached = await cache_manager.get_cached_response(
                question=question, db_scope=db_scope, admin_role=admin_role
            )

            if cached:
                response_time = (time.time() - start_time) * 1000
                await cache_manager.record_response_time(response_time, from_cache=True)
                return {
                    **cached.data,
                    "from_cache": True,
                    "cached_at": cached.created_at,
                }

            # 실제 함수 실행
            result = await func(*args, **kwargs)

            response_time = (time.time() - start_time) * 1000
            await cache_manager.record_response_time(response_time, from_cache=False)

            # 결과 캐싱
            await cache_manager.set_cached_response(
                question=question,
                db_scope=db_scope,
                admin_role=admin_role,
                response=result,
            )

            return {**result, "from_cache": False}

        return wrapper

    return decorator
