"""
관리자 백엔드 데이터베이스 연결 설정
MariaDB (주 데이터) 및 MSSQL (외부 연동) 지원
"""
from typing import AsyncGenerator, Generator
import urllib.parse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from src.config.settings import settings

# ORM Base 클래스
Base = declarative_base()

# =============================================================================
# MariaDB 비동기 연결 (주 데이터베이스)
# =============================================================================

# 비동기 엔진 생성 (한국 시간대 설정 포함)
async_engine = create_async_engine(
    settings.mariadb_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,  # MariaDB 연결 재활용 (1시간)
    connect_args={
        "init_command": "SET time_zone='+09:00'"  # 한국 시간대 설정
    }
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    MariaDB 비동기 세션 의존성

    FastAPI 의존성 주입에서 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# =============================================================================
# MSSQL 동기 연결 (외부 ARS 시스템 연동)
# =============================================================================

def _build_mssql_url(host: str, port: int, db: str, user: str, password: str, driver: str) -> str:
    """MSSQL URL 빌더"""
    if driver.lower() == "pymssql":
        # pymssql URL
        return f"mssql+pymssql://{urllib.parse.quote_plus(user)}:{urllib.parse.quote_plus(password)}@{host}:{port}/{db}?charset=utf8"
    else:
        # ODBC Driver URL
        odbc_conn = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server=tcp:{host},{port};"
            f"Database={db};"
            f"Uid={user};"
            f"Pwd={password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes;"
            f"Connection Timeout=30;"
        )
        return f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_conn)}"


# MSSQL 엔진 및 세션 팩토리 생성 (전역, 한 번만 생성)
def _create_mssql_engine():
    """MSSQL 엔진 생성 함수"""
    url = _build_mssql_url(
        settings.mssql_server,
        settings.mssql_port,
        settings.mssql_database,
        settings.mssql_username,
        settings.mssql_password,
        settings.mssql_driver
    )

    connect_args = {}
    if settings.mssql_driver.lower() == "pymssql":
        tds_version = "7.0" if settings.is_production else "7.1"
        connect_args = {"tds_version": tds_version, "login_timeout": 30, "timeout": settings.mssql_timeout}

    return create_engine(
        url,
        echo=settings.debug,
        pool_size=10,  # MSSQL 연결 풀 크기
        max_overflow=20,  # MSSQL 최대 오버플로우
        pool_pre_ping=True,
        pool_recycle=3600,  # MSSQL 연결 재활용 (1시간)
        pool_timeout=30,    # 연결 대기 시간
        connect_args=connect_args,
    )


# 전역 MSSQL 엔진 및 세션 팩토리
mssql_engine = _create_mssql_engine()
MSSQLSessionLocal = sessionmaker(
    bind=mssql_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_db_mssql() -> Generator[Session, None, None]:
    """
    MSSQL 동기 세션 의존성 (외부 ARS 시스템 연동용)

    전역 엔진을 사용하여 세션만 생성/관리
    """
    db = MSSQLSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db() -> None:
    """
    데이터베이스 초기화
    애플리케이션 시작 시 호출
    """
    # 테이블 생성 (필요한 경우)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass


async def close_db() -> None:
    """
    데이터베이스 연결 종료
    애플리케이션 종료 시 호출
    """
    await async_engine.dispose()
    mssql_engine.dispose()  # MSSQL 엔진도 정리


# 별칭 (명확한 네이밍)
get_maria_db = get_db
get_mssql_db = get_db_mssql