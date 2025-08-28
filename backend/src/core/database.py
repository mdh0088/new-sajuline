"""
데이터베이스 연결 설정
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

# 비동기 엔진 생성
async_engine = create_async_engine(
    settings.mariadb_url,
    echo=settings.mariadb_echo,
    pool_size=settings.mariadb_pool_size,
    max_overflow=settings.mariadb_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,  # MariaDB 연결 재활용 (1시간)
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_maria() -> AsyncGenerator[AsyncSession, None]:
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


def get_db_mssql() -> Generator[Session, None, None]:
    """
    MSSQL 동기 세션 의존성 (외부 ARS 시스템 연동용)
    
    필요할 때마다 엔진과 세션을 생성
    """
    # MSSQL 엔진 생성
    driver = settings.mssql_prod_driver if settings.is_production else settings.mssql_dev_driver
    url = _build_mssql_url(
        settings.mssql_host,
        settings.mssql_port,
        settings.mssql_db,
        settings.mssql_user,
        settings.mssql_password,
        driver
    )
    
    connect_args = {}
    if driver.lower() == "pymssql" and settings.is_production:
        connect_args = {"tds_version": "7.1", "login_timeout": 30, "timeout": 30}
    
    engine = create_engine(
        url,
        echo=settings.mariadb_echo,
        pool_size=settings.mariadb_pool_size,
        max_overflow=settings.mariadb_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args=connect_args,
    )
    
    # 세션 팩토리 생성 및 세션 제공
    SessionLocal = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        engine.dispose()


async def close_db() -> None:
    """
    데이터베이스 연결 종료
    애플리케이션 종료 시 호출
    """
    await async_engine.dispose()


# 별칭 (명확한 네이밍)
get_maria_db = get_db_maria
get_mssql_db = get_db_mssql