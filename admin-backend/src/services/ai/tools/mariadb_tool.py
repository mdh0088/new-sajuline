"""
MariaDB 연결 풀 관리.

싱글톤 패턴으로 MariaDB 연결 풀을 관리합니다.

Stories: 2-3
FRs: FR-011, NFR-I1
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiomysql

from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class MariaDBConnectionPool:
    """MariaDB 연결 풀 관리 (싱글톤)

    aiomysql Pool을 싱글톤으로 관리하여 연결 누수를 방지합니다.

    TODO: src/core/database.py의 get_db()와 통합하여 연결 풀 중복 생성 방지
    TODO: AI BI 전용 읽기 전용 계정(ai_bi_maria_ro) 사용 (settings.py에 추가 필요)
    """

    # 연결 풀 설정 상수
    MIN_POOL_SIZE = 5
    MAX_POOL_SIZE = 20
    CONNECT_TIMEOUT = 10  # 초

    _pool: aiomysql.Pool | None = None
    _initialized: bool = False

    @classmethod
    async def get_pool(cls) -> aiomysql.Pool:
        """연결 풀 반환 (싱글톤)

        연결 풀이 없으면 새로 생성하고, 있으면 재사용합니다.

        Returns:
            aiomysql.Pool: MariaDB 연결 풀

        Raises:
            Exception: 연결 풀 생성 실패 시
        """
        # 연결 풀이 없거나 종료된 경우 재생성
        needs_new_pool = False
        if cls._pool is None:
            needs_new_pool = True
        else:
            # private 속성(_closed) 직접 접근 대신 예외 처리로 상태 확인
            try:
                # Pool이 닫혔는지 확인 (size 접근 시 에러 발생)
                _ = cls._pool.size
            except (AttributeError, RuntimeError):
                # Pool이 닫혔거나 유효하지 않음
                needs_new_pool = True

        if needs_new_pool:
            settings = get_settings()

            logger.info(
                "creating_mariadb_pool",
                extra={
                    "event": "creating_mariadb_pool",
                    "host": settings.maria_host,
                    "port": settings.maria_port,
                    "database": settings.maria_database,
                    "min_size": cls.MIN_POOL_SIZE,
                    "max_size": cls.MAX_POOL_SIZE,
                },
            )

            cls._pool = await aiomysql.create_pool(
                host=settings.maria_host,
                port=settings.maria_port,
                user=settings.maria_user,
                password=settings.maria_password.get_secret_value(),
                db=settings.maria_database,
                minsize=cls.MIN_POOL_SIZE,
                maxsize=cls.MAX_POOL_SIZE,
                autocommit=True,
                charset="utf8mb4",
                connect_timeout=cls.CONNECT_TIMEOUT,
            )

            cls._initialized = True

            logger.info(
                "mariadb_pool_created",
                extra={
                    "event": "mariadb_pool_created",
                    "pool_size": cls._pool.size,
                    "free_size": cls._pool.freesize,
                },
            )

        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        """연결 풀 종료

        애플리케이션 종료 시 연결 풀을 안전하게 종료합니다.
        """
        if cls._pool is not None:
            try:
                # Pool이 유효한지 확인
                pool_size = cls._pool.size

                logger.info(
                    "closing_mariadb_pool",
                    extra={
                        "event": "closing_mariadb_pool",
                        "pool_size": pool_size,
                    },
                )

                cls._pool.close()
                await cls._pool.wait_closed()
            except (AttributeError, RuntimeError):
                # Pool이 이미 닫혔거나 유효하지 않음 - 무시
                pass
            finally:
                cls._pool = None
                cls._initialized = False

                logger.info(
                    "mariadb_pool_closed",
                    extra={"event": "mariadb_pool_closed"},
                )

    @classmethod
    @asynccontextmanager
    async def connection(cls) -> AsyncGenerator[aiomysql.Connection, None]:
        """연결 풀에서 연결을 가져오는 컨텍스트 매니저

        Yields:
            aiomysql.Connection: MariaDB 연결

        Example:
            ```python
            async with MariaDBConnectionPool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            ```
        """
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            try:
                yield conn
            except Exception as e:
                logger.exception(
                    "mariadb_connection_error",
                    extra={
                        "event": "mariadb_connection_error",
                        "error": str(e),
                    },
                )
                raise


# FastAPI 라이프사이클 이벤트용 헬퍼
async def init_mariadb_pool() -> None:
    """FastAPI 시작 시 연결 풀 초기화

    애플리케이션 시작 시 MariaDB 연결 풀을 미리 생성하여
    첫 쿼리 실행 시 레이턴시를 줄입니다.

    Returns:
        None

    Raises:
        Exception: 연결 풀 생성 실패 시

    Example:
        ```python
        # main.py에서 lifespan 이벤트로 등록
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_mariadb_pool()
            yield
            await close_mariadb_pool()
        ```
    """
    await MariaDBConnectionPool.get_pool()
    logger.info("MariaDB 연결 풀 초기화 완료")


async def close_mariadb_pool() -> None:
    """FastAPI 종료 시 연결 풀 종료

    애플리케이션 종료 시 MariaDB 연결 풀을 안전하게 종료하여
    리소스를 정리합니다.

    Returns:
        None
    """
    await MariaDBConnectionPool.close_pool()
    logger.info("MariaDB 연결 풀 종료 완료")
