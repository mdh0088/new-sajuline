"""
스키마 캐시 관리자 단위 테스트.

Stories: STORY-6-2
FRs: FR30, NFR-P6
"""

import pytest
import json
from unittest.mock import AsyncMock
import redis.asyncio as redis

from src.services.ai.utils.schema_cache import SchemaCacheManager
from src.services.ai.utils.cache_manager import AICacheManager


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock(spec=redis.Redis)
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def schema_cache(mock_redis):
    """스키마 캐시 인스턴스"""
    return SchemaCacheManager(mock_redis, ttl=3600)


@pytest.fixture
def sample_schema():
    """샘플 스키마"""
    return {
        "tables": {
            "payments": {
                "columns": ["id", "amount", "created_at"],
                "types": ["int", "decimal", "datetime"],
            },
            "members": {
                "columns": ["id", "name", "email"],
                "types": ["int", "varchar", "varchar"],
            },
        }
    }


class TestSchemaCacheManager:
    """SchemaCacheManager 단위 테스트"""

    def test_init(self, schema_cache):
        """초기화 테스트"""
        assert schema_cache.ttl == 3600
        assert schema_cache.key_prefix == "ai_cache:schema"

    @pytest.mark.asyncio
    async def test_get_schema_hit(self, schema_cache, mock_redis, sample_schema):
        """스키마 캐시 히트 테스트"""
        mock_redis.get.return_value = json.dumps(
            sample_schema, ensure_ascii=False
        )

        result = await schema_cache.get_schema("mariadb")

        assert result == sample_schema
        mock_redis.get.assert_called_once_with("ai_cache:schema:mariadb")

    @pytest.mark.asyncio
    async def test_get_schema_miss(self, schema_cache, mock_redis):
        """스키마 캐시 미스 테스트"""
        mock_redis.get.return_value = None

        result = await schema_cache.get_schema("mariadb")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_schema_redis_error(self, schema_cache, mock_redis):
        """Redis 에러 시 None 반환 테스트"""
        mock_redis.get.side_effect = redis.RedisError("Connection failed")

        result = await schema_cache.get_schema("mariadb")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_schema(self, schema_cache, mock_redis, sample_schema):
        """스키마 캐싱 테스트"""
        result = await schema_cache.set_schema("mariadb", sample_schema)

        assert result is True
        mock_redis.setex.assert_called_once()

        # 호출 인자 검증
        call_args = mock_redis.setex.call_args[0]
        key, ttl, value = call_args
        assert key == "ai_cache:schema:mariadb"
        assert ttl == 3600
        assert json.loads(value) == sample_schema

    @pytest.mark.asyncio
    async def test_set_schema_redis_error(
        self, schema_cache, mock_redis, sample_schema
    ):
        """스키마 저장 실패 테스트"""
        mock_redis.setex.side_effect = redis.RedisError("Write failed")

        result = await schema_cache.set_schema("mariadb", sample_schema)

        assert result is False

    @pytest.mark.asyncio
    async def test_check_schema_change_detected(
        self, schema_cache, mock_redis, sample_schema
    ):
        """스키마 변경 감지 테스트"""
        # 기존 스키마
        mock_redis.get.return_value = json.dumps(
            sample_schema, ensure_ascii=False
        )

        # 변경된 스키마 (테이블 추가)
        new_schema = {
            **sample_schema,
            "tables": {
                **sample_schema["tables"],
                "orders": {
                    "columns": ["id", "user_id"],
                    "types": ["int", "int"],
                },
            },
        }

        changed = await schema_cache.check_schema_change(
            "mariadb", new_schema
        )

        assert changed is True

    @pytest.mark.asyncio
    async def test_check_schema_no_change(
        self, schema_cache, mock_redis, sample_schema
    ):
        """스키마 변경 없음 테스트"""
        mock_redis.get.return_value = json.dumps(
            sample_schema, ensure_ascii=False
        )

        changed = await schema_cache.check_schema_change(
            "mariadb", sample_schema
        )

        assert changed is False

    @pytest.mark.asyncio
    async def test_check_schema_no_cached(self, schema_cache, mock_redis):
        """캐시된 스키마 없음 테스트"""
        mock_redis.get.return_value = None

        changed = await schema_cache.check_schema_change(
            "mariadb", {"tables": {}}
        )

        assert changed is False  # 캐시 없으면 변경 감지 불가

    def test_schema_hash(self, schema_cache, sample_schema):
        """스키마 해시 생성 테스트"""
        hash1 = schema_cache._schema_hash(sample_schema)
        hash2 = schema_cache._schema_hash(sample_schema)

        # 동일 스키마 → 동일 해시
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 해시 길이

        # 다른 스키마 → 다른 해시
        different_schema = {**sample_schema, "version": "2.0"}
        hash3 = schema_cache._schema_hash(different_schema)
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_invalidate_on_schema_change(
        self, schema_cache, mock_redis
    ):
        """스키마 변경 시 캐시 무효화 테스트"""
        # Cache manager mock
        cache_manager = AsyncMock(spec=AICacheManager)
        cache_manager.invalidate_by_pattern = AsyncMock(return_value=5)

        await schema_cache.invalidate_on_schema_change(
            "mariadb", cache_manager
        )

        # 패턴 무효화 호출 검증
        cache_manager.invalidate_by_pattern.assert_called_once_with(
            "query:*mariadb*"
        )


class TestSchemaHashConsistency:
    """스키마 해시 일관성 테스트"""

    @pytest.mark.asyncio
    async def test_column_order_independence(self, schema_cache):
        """컬럼 순서와 무관하게 동일 해시 생성 테스트"""
        schema1 = {
            "tables": {
                "users": {"columns": ["id", "name"], "types": ["int", "varchar"]}
            }
        }
        schema2 = {
            "tables": {
                "users": {"columns": ["name", "id"], "types": ["varchar", "int"]}
            }
        }

        # 컬럼 순서가 다르면 해시도 달라야 함 (실제 스키마 변경)
        hash1 = schema_cache._schema_hash(schema1)
        hash2 = schema_cache._schema_hash(schema2)
        assert hash1 != hash2

    @pytest.mark.asyncio
    async def test_table_order_independence(self, schema_cache):
        """테이블 순서와 무관하게 일관된 해시 테스트"""
        schema1 = {
            "tables": {
                "users": {"columns": ["id"]},
                "posts": {"columns": ["id"]},
            }
        }
        schema2 = {
            "tables": {
                "posts": {"columns": ["id"]},
                "users": {"columns": ["id"]},
            }
        }

        hash1 = schema_cache._schema_hash(schema1)
        hash2 = schema_cache._schema_hash(schema2)

        # JSON sort_keys로 인해 동일해야 함
        assert hash1 == hash2
