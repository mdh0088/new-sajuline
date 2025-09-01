"""
글로벌 테스트 픽스처 및 설정

FastAPI 애플리케이션 테스트를 위한 공통 픽스처들을 정의합니다.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.repositories.user_repository import UserRepository


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """전체 테스트 세션용 이벤트 루프"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_session() -> Mock:
    """모킹된 데이터베이스 세션
    
    실제 DB 연결 없이 테스트할 수 있도록 Mock 객체를 제공합니다.
    """
    session_mock = Mock(spec=AsyncSession)
    session_mock.commit = AsyncMock()
    session_mock.rollback = AsyncMock()
    session_mock.close = AsyncMock()
    return session_mock


@pytest.fixture
def mock_user_repository(mock_db_session) -> Mock:
    """모킹된 사용자 리포지토리"""
    repo_mock = Mock(spec=UserRepository)
    repo_mock.db = mock_db_session
    
    # 기본 메서드들을 AsyncMock으로 설정
    repo_mock.create = AsyncMock()
    repo_mock.get_by_id = AsyncMock()
    repo_mock.get_by_email = AsyncMock()
    repo_mock.update = AsyncMock()
    repo_mock.delete = AsyncMock()
    repo_mock.exists_by_email = AsyncMock(return_value=False)
    repo_mock.exists_by_user_id = AsyncMock(return_value=False)
    
    return repo_mock


@pytest.fixture
def mock_auth_service() -> Mock:
    """모킹된 인증 서비스"""
    auth_mock = Mock(spec=AuthService)
    
    # 기본 메서드들 설정
    auth_mock.hash_password = Mock(return_value="hashed_password_123")
    auth_mock.verify_password = Mock(return_value=True)
    auth_mock.create_access_token = Mock(return_value="test_jwt_token")
    auth_mock.verify_token = Mock(return_value={
        "sub": "test_user",
        "email": "test@example.com",
        "role": "user"
    })
    
    return auth_mock


@pytest.fixture
def mock_user_service(mock_user_repository, mock_auth_service) -> Mock:
    """모킹된 사용자 서비스"""
    service_mock = Mock(spec=UserService)
    service_mock.user_repository = mock_user_repository
    service_mock.auth_service = mock_auth_service
    
    # 기본 메서드들을 AsyncMock으로 설정
    service_mock.create_user = AsyncMock()
    service_mock.get_user = AsyncMock()
    service_mock.update_user = AsyncMock()
    service_mock.delete_user = AsyncMock()
    service_mock.authenticate_user = AsyncMock()
    service_mock.login = AsyncMock()
    
    return service_mock


# 테스트 마커 설정
pytestmark = [
    pytest.mark.asyncio,  # 모든 테스트를 비동기로 실행
]


def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )