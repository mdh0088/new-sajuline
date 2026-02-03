"""
데이터베이스 스키마 로더

MariaDB 테이블 스키마 정보를 조회하고 캐싱합니다.

Stories: AI-002
FRs: FR-011, FR-012
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.logging import get_logger
from src.config.settings import Settings

logger = get_logger(__name__)


class SchemaLoader:
    """데이터베이스 스키마 로더

    테이블별 스키마 정보를 조회하고 캐싱하여
    Text-to-SQL 프롬프트에 포함할 수 있도록 합니다.

    Attributes:
        _schema_cache: 테이블 스키마 캐시 {table_name: (schema_info, cached_at)}
        _cache_ttl_seconds: 캐시 유효 시간 (기본 1시간)
        _cache_lock: 캐시 동시성 제어를 위한 Lock
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        cache_ttl_seconds: Optional[int] = None,
    ):
        """SchemaLoader 초기화

        Args:
            settings: 애플리케이션 설정 (DI 패턴)
            cache_ttl_seconds: 캐시 유효 시간 (초). 기본 3600초 (1시간)
        """
        self._schema_cache: dict[str, tuple[str, datetime]] = {}
        self._cache_ttl_seconds = cache_ttl_seconds or 3600
        self._cache_lock = asyncio.Lock()  # 동시성 제어

    async def load_schema(
        self,
        db_session: AsyncSession,
        table_names: list[str],
        force_refresh: bool = False,
    ) -> str:
        """테이블 스키마 정보를 Markdown 형식으로 로드

        Args:
            db_session: SQLAlchemy 비동기 세션
            table_names: 로드할 테이블 이름 목록
            force_refresh: True시 캐시 무시하고 DB에서 재조회

        Returns:
            str: Markdown 형식의 스키마 정보

        Examples:
            >>> loader = SchemaLoader()
            >>> schema_info = await loader.load_schema(db_session, ["users", "payments"])
            >>> print(schema_info)
            ## Table: users
            | Column | Type | Nullable | Key | Comment |
            |--------|------|----------|-----|---------|
            | id | INT | NO | PRI | 사용자 ID |
            | username | VARCHAR(50) | NO | UNI | 사용자명 |
            ...
        """
        schema_parts = []

        for table_name in table_names:
            # 캐시 확인 (Lock으로 동시성 보호)
            async with self._cache_lock:
                if not force_refresh and table_name in self._schema_cache:
                    cached_schema, cached_at = self._schema_cache[table_name]
                    if datetime.now() - cached_at < timedelta(
                        seconds=self._cache_ttl_seconds
                    ):
                        schema_parts.append(cached_schema)
                        logger.debug(
                            f"schema_cache_hit",
                            extra={
                                "event": "schema_cache_hit",
                                "table": table_name,
                                "cached_at": cached_at.isoformat(),
                            },
                        )
                        continue

            # DB에서 스키마 조회
            schema_info = await self._load_table_schema(db_session, table_name)

            if schema_info:
                # 캐시 저장 (Lock으로 동시성 보호)
                async with self._cache_lock:
                    self._schema_cache[table_name] = (schema_info, datetime.now())
                schema_parts.append(schema_info)

                logger.debug(
                    f"schema_loaded",
                    extra={
                        "event": "schema_loaded",
                        "table": table_name,
                        "schema_length": len(schema_info),
                    },
                )
            else:
                logger.warning(
                    f"schema_not_found",
                    extra={
                        "event": "schema_not_found",
                        "table": table_name,
                    },
                )

        return "\n\n".join(schema_parts)

    async def _load_table_schema(
        self, db_session: AsyncSession, table_name: str
    ) -> Optional[str]:
        """단일 테이블 스키마 정보 조회

        INFORMATION_SCHEMA.COLUMNS를 사용하여 테이블 구조를 조회합니다.

        Args:
            db_session: SQLAlchemy 비동기 세션
            table_name: 테이블 이름

        Returns:
            Optional[str]: Markdown 형식의 테이블 스키마 또는 None (테이블 없음)
        """
        query = text("""
            SELECT
                COLUMN_NAME,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                COLUMN_DEFAULT,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
        """)

        try:
            result = await db_session.execute(query, {"table_name": table_name})
            columns = result.fetchall()

            if not columns:
                return None

            # Markdown 테이블 생성
            markdown = [f"## Table: {table_name}"]
            markdown.append("| Column | Type | Nullable | Key | Default | Comment |")
            markdown.append("|--------|------|----------|-----|---------|---------|")

            for col in columns:
                column_name = col[0]
                column_type = col[1]
                is_nullable = "YES" if col[2] == "YES" else "NO"
                column_key = col[3] or "-"
                column_default = col[4] or "-"
                column_comment = col[5] or "-"

                markdown.append(
                    f"| {column_name} | {column_type} | {is_nullable} | "
                    f"{column_key} | {column_default} | {column_comment} |"
                )

            return "\n".join(markdown)

        except Exception as e:
            logger.error(
                "schema_load_error",
                extra={
                    "event": "schema_load_error",
                    "table": table_name,
                    "error": str(e),
                },
                exc_info=True,
            )
            return None

    async def clear_cache(self, table_name: Optional[str] = None):
        """스키마 캐시 초기화

        Args:
            table_name: 특정 테이블 캐시만 초기화. None시 전체 초기화
        """
        async with self._cache_lock:
            if table_name:
                self._schema_cache.pop(table_name, None)
                logger.info(
                    "schema_cache_cleared",
                    extra={
                        "event": "schema_cache_cleared",
                        "table": table_name,
                    },
                )
            else:
                self._schema_cache.clear()
                logger.info(
                    "schema_cache_cleared_all",
                    extra={
                        "event": "schema_cache_cleared_all",
                    },
                )
