"""
MSSQL 동기 세션 관리

MySQL/MariaDB 세션 패턴과 동일한 규격으로 의존성 제공
"""

from typing import Generator, Optional, TYPE_CHECKING

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import asyncio

from src.common.config.settings import get_settings

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.engine import Engine


settings = get_settings()


# URL 빌더 (pyodbc/pymssql 선택 지원)
def _build_mssql_url_dev(host: str, port: int, db: str, user: str, password: str) -> str:
    # ODBC Driver 18 for SQL Server, TrustServerCertificate=yes
    import urllib.parse
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


def _build_mssql_url_prod(host: str, port: int, db: str, user: str, password: str) -> str:
    # pymssql URL (tds_version은 connect_args로 지정)
    import urllib.parse
    return f"mssql+pymssql://{urllib.parse.quote_plus(user)}:{urllib.parse.quote_plus(password)}@{host}:{port}/{db}?charset=utf8"


def create_mssql_engine():
    host = settings.MSSQL_HOST
    port = settings.MSSQL_PORT
    db = settings.MSSQL_DB
    user = settings.MSSQL_USER
    password = settings.MSSQL_PASSWORD
    
    # MSSQL 비밀번호 필수 검증
    if not password:
        raise ValueError("MSSQL_PASSWORD must be set in environment variables")

    dev_driver = getattr(settings, "MSSQL_DEV_DRIVER", "pymssql").lower()
    prod_driver = getattr(settings, "MSSQL_PROD_DRIVER", "pymssql").lower()

    # URL 선택 (환경/드라이버 분기)
    if settings.is_production:
        url = _build_mssql_url_prod(host, port, db, user, password) if prod_driver == "pymssql" else _build_mssql_url_dev(host, port, db, user, password)
        connect_args = {"tds_version": "7.1", "login_timeout": 30, "timeout": 30} if prod_driver == "pymssql" else {}
    else:
        url = _build_mssql_url_prod(host, port, db, user, password) if dev_driver == "pymssql" else _build_mssql_url_dev(host, port, db, user, password)
        connect_args = {}

    # 풀 전략 (session.py와 동일한 규격)
    if settings.is_docker_environment:
        engine = create_engine(
            url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_recycle=3600,
            poolclass=NullPool,
            connect_args=connect_args,
        )
    else:
        engine = create_engine(
            url,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=connect_args,
        )

    return engine

# 동기 엔진 및 세션 팩토리
_engine = create_mssql_engine()
SyncSessionLocal = sessionmaker(
    bind=_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_mssql_db() -> Generator[Session, None, None]:
    """
    MSSQL 동기 세션 의존성 (FastAPI Depends 에서 사용)

    기존 MySQL 세션 패턴과 동일하게 commit/rollback 을 보장
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_mssql_connection(engine: Optional["Engine"] = None) -> tuple[bool, str]:
    """MSSQL 연결 헬스 체크"""
    try:
        eng = engine or _engine
        with eng.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True, "OK"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


async def test_mssql_connection_async(engine: Optional[AsyncEngine] = None) -> tuple[bool, str]:
    """MSSQL 비동기 연결 헬스 체크"""
    try:
        # 비동기 엔진이 제공되지 않은 경우 동기 연결을 스레드 풀에서 실행
        if engine is None:
            # asyncio.to_thread를 사용하여 동기 함수를 비동기로 실행
            return await asyncio.to_thread(test_mssql_connection, _engine)
        
        # 비동기 엔진이 제공된 경우 비동기 연결 사용
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True, "OK"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


# session.py와 인터페이스 유사성을 위한 보조 함수들
def init_mssql_db() -> None:
    """
    MSSQL 초기화 훅 (개발 환경에서만 사용 권장)
    - 현재는 외부 SQL 스크립트(T-043)로 스키마를 관리하므로, 연결성 확인만 수행
    """
    ok, msg = test_mssql_connection()
    if not ok:
        raise RuntimeError(f"MSSQL init failed: {msg}")


def close_mssql_db() -> None:
    """MSSQL 엔진 자원 해제"""
    try:
        _engine.dispose()
    except Exception:
        pass


# 별칭 (session.py 스타일 매칭)
get_db_mssql = get_mssql_db


def get_mssql_db_for_background() -> Generator[Session, None, None]:
    """
    백그라운드 태스크 전용 MSSQL 동기 세션 팩토리 (T-068)
    요청 스코프와 분리된 독립 세션을 제공
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


