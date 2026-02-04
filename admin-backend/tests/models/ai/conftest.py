"""
AI 모델 테스트용 fixtures
"""
import pytest
import pytest_asyncio
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.database import Base
# Import all models to ensure they are registered with Base.metadata
from src.models.admin_model import Admin  # noqa: F401
from src.models.ai.ai_query_history_model import AIQueryHistory  # noqa: F401
from src.models.ai.ai_feedback_model import AIFeedback  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """테스트용 인메모리 데이터베이스 세션"""
    # 인메모리 SQLite 데이터베이스 사용 (aiomysql 대신)
    # StaticPool을 사용하여 연결 유지
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 세션 팩토리 생성
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # 세션 생성 및 반환
    async with async_session_factory() as session:
        yield session

    # 정리
    await engine.dispose()
