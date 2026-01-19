"""
데이터베이스 세션 관리

비동기 SQLAlchemy 세션 생성 및 의존성 주입
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.common.config.settings import get_settings

settings = get_settings()

# 비동기 엔진 생성 (MariaDB 최적화)
if settings.is_docker_environment:
    # Docker 환경에서는 NullPool 사용 (pool 매개변수 제거)
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,  # MariaDB 연결 재활용 (1시간)
        poolclass=NullPool
    )
else:
    # 로컬 환경에서는 일반 연결 풀 사용
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600  # MariaDB 연결 재활용 (1시간)
    )

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션 의존성
    
    FastAPI 의존성 주입에서 사용
    자동으로 세션을 생성하고 종료
    
    Yields:
        AsyncSession: 비동기 데이터베이스 세션
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


async def init_db() -> None:
    """
    데이터베이스 초기화
    
    테이블 생성 및 초기 데이터 설정
    주의: 프로덕션에서는 Alembic 마이그레이션 사용 권장
    """
    from src.common.database.base import Base
    
    async with async_engine.begin() as conn:
        # 개발 환경에서만 사용 (프로덕션에서는 Alembic 사용)
        if settings.is_development:
            # 모든 테이블 삭제 후 재생성 (주의!)
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    데이터베이스 연결 종료
    
    애플리케이션 종료 시 호출
    """
    await async_engine.dispose()


# 별칭 (하위 호환성을 위해)
get_async_session = get_db 


# 배경 작업용 세션 팩토리 (T-068)
async def get_db_session_for_background() -> AsyncGenerator[AsyncSession, None]:
    """
    백그라운드 태스크 전용 비동기 세션 의존성
    - 요청 스코프와 분리된 독립 세션을 보장
    - 커밋/롤백은 호출 측 정책에 따라 수행 (여기서는 자동 커밋/롤백 제공)
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