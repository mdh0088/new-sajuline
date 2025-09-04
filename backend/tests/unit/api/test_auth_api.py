"""
Auth API 엔드포인트 테스트

토큰 갱신(refresh) 엔드포인트의 단위 테스트를 포함합니다.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime, timedelta

from src.exceptions.custom_exceptions import AuthenticationError


@pytest.mark.unit
class TestAuthRefreshAPI:
    """토큰 갱신 API 테스트"""

    @pytest.fixture
    def mock_redis_client(self):
        """모킹된 Redis 클라이언트"""
        redis_mock = AsyncMock()
        redis_mock.setex = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)  # 기본적으로 블랙리스트에 없음
        return redis_mock

    @pytest.fixture
    def valid_refresh_token_payload(self):
        """유효한 Refresh Token 페이로드"""
        exp_time = datetime.utcnow() + timedelta(days=7)
        return {
            "sub": "test_user_123",
            "email": "test@example.com",
            "role": "user",
            "token_type": "refresh",
            "exp": int(exp_time.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "jti": "refresh_token_jti_123"
        }

    async def test_refresh_token_success(self, async_client: AsyncClient, mock_redis_client, valid_refresh_token_payload):
        """토큰 갱신 성공 테스트"""
        # Given
        refresh_token = "valid_refresh_token"
        new_access_token = "new_access_token_123"
        new_refresh_token = "new_refresh_token_456"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService 설정
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(return_value=valid_refresh_token_payload)
            mock_auth_service.create_access_token = Mock(return_value=new_access_token)
            mock_auth_service.create_refresh_token = Mock(return_value=new_refresh_token)
            mock_auth_service.blacklist_token = AsyncMock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "토큰 갱신 성공"
            assert "access_token_expires_in" in data["data"]
            assert "refresh_token_expires_in" in data["data"]
            assert data["data"]["access_token_expires_in"] == 30 * 60  # 30분
            assert data["data"]["refresh_token_expires_in"] == 7 * 24 * 60 * 60  # 7일
            
            # 쿠키 확인
            assert "access_token" in response.cookies
            assert "refresh_token" in response.cookies
            assert response.cookies["access_token"] == new_access_token
            assert response.cookies["refresh_token"] == new_refresh_token
            
            # Mock 호출 확인
            mock_auth_service.verify_refresh_token.assert_called_once_with(refresh_token, mock_redis_client)
            mock_auth_service.create_access_token.assert_called_once_with(
                user_id="test_user_123",
                email="test@example.com", 
                role="user"
            )
            mock_auth_service.create_refresh_token.assert_called_once_with(
                user_id="test_user_123",
                email="test@example.com",
                role="user"
            )
            mock_auth_service.blacklist_token.assert_called_once()

    async def test_refresh_token_from_cookie(self, async_client: AsyncClient, mock_redis_client, valid_refresh_token_payload):
        """쿠키에서 Refresh Token 추출하여 갱신 성공 테스트"""
        # Given
        refresh_token = "cookie_refresh_token"
        new_access_token = "new_access_token_123"
        new_refresh_token = "new_refresh_token_456"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService 설정
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(return_value=valid_refresh_token_payload)
            mock_auth_service.create_access_token = Mock(return_value=new_access_token)
            mock_auth_service.create_refresh_token = Mock(return_value=new_refresh_token)
            mock_auth_service.blacklist_token = AsyncMock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # When - 쿠키에 refresh_token 포함하여 요청
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={},
                cookies={"refresh_token": refresh_token}
            )
            
            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "토큰 갱신 성공"
            
            # Mock 호출 확인 - 쿠키의 토큰이 사용되었는지 확인
            mock_auth_service.verify_refresh_token.assert_called_once_with(refresh_token, mock_redis_client)

    async def test_refresh_token_invalid_token(self, async_client: AsyncClient, mock_redis_client):
        """유효하지 않은 Refresh Token으로 갱신 실패 테스트"""
        # Given
        invalid_token = "invalid_refresh_token"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService - 토큰 검증 실패
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(
                side_effect=AuthenticationError("유효하지 않은 토큰")
            )
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": invalid_token}
            )
            
            # Then
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "유효하지 않은 토큰" in data["message"]

    async def test_refresh_token_blacklisted_token(self, async_client: AsyncClient, mock_redis_client):
        """블랙리스트된 Refresh Token으로 갱신 실패 테스트"""
        # Given
        blacklisted_token = "blacklisted_refresh_token"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService - 블랙리스트된 토큰
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(
                side_effect=AuthenticationError("이미 사용된 토큰입니다")
            )
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": blacklisted_token}
            )
            
            # Then
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "이미 사용된 토큰입니다" in data["message"]

    async def test_refresh_token_api_error_test(self, async_client: AsyncClient, mock_redis_client):
        """API 레이어 에러 테스트 (테스트용 에러 트리거)"""
        # Given
        test_error_token = "api_refresh_error_test"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service"):
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": test_error_token}
            )
            
            # Then
            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert "API layer" in data["message"]

    async def test_refresh_token_missing_token(self, async_client: AsyncClient, mock_redis_client):
        """토큰이 누락된 경우 테스트"""
        # Given - 토큰 없음
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService - None 토큰으로 검증 실패
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(
                side_effect=AuthenticationError("토큰이 제공되지 않았습니다")
            )
            mock_get_auth_service.return_value = mock_auth_service
            
            # When - 토큰 없이 요청
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={}
            )
            
            # Then
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False

    async def test_refresh_token_blacklist_functionality(self, async_client: AsyncClient, mock_redis_client, valid_refresh_token_payload):
        """기존 Refresh Token 블랙리스트 처리 기능 테스트"""
        # Given
        refresh_token = "valid_refresh_token"
        new_access_token = "new_access_token_123"
        new_refresh_token = "new_refresh_token_456"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService 설정
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(return_value=valid_refresh_token_payload)
            mock_auth_service.create_access_token = Mock(return_value=new_access_token)
            mock_auth_service.create_refresh_token = Mock(return_value=new_refresh_token)
            mock_auth_service.blacklist_token = AsyncMock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            # Then
            assert response.status_code == 200
            
            # 블랙리스트 호출 확인
            mock_auth_service.blacklist_token.assert_called_once()
            call_args = mock_auth_service.blacklist_token.call_args
            
            # 블랙리스트 호출 인자 확인
            assert call_args.kwargs["jti"] == "refresh_token_jti_123"
            assert call_args.kwargs["redis_client"] == mock_redis_client
            assert isinstance(call_args.kwargs["expires_at"], datetime)

    async def test_refresh_token_cookie_settings(self, async_client: AsyncClient, mock_redis_client, valid_refresh_token_payload):
        """쿠키 설정 검증 테스트"""
        # Given
        refresh_token = "valid_refresh_token"
        new_access_token = "new_access_token_123"
        new_refresh_token = "new_refresh_token_456"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService 설정
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(return_value=valid_refresh_token_payload)
            mock_auth_service.create_access_token = Mock(return_value=new_access_token)
            mock_auth_service.create_refresh_token = Mock(return_value=new_refresh_token)
            mock_auth_service.blacklist_token = AsyncMock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            # Then
            assert response.status_code == 200
            
            # 쿠키 값 확인
            assert response.cookies["access_token"] == new_access_token
            assert response.cookies["refresh_token"] == new_refresh_token
            
            # 응답 데이터 확인
            data = response.json()
            assert data["data"]["access_token_expires_in"] == 30 * 60
            assert data["data"]["refresh_token_expires_in"] == 7 * 24 * 60 * 60

    async def test_refresh_token_rotation_pattern(self, async_client: AsyncClient, mock_redis_client, valid_refresh_token_payload):
        """Refresh Token Rotation 패턴 전체 플로우 테스트"""
        # Given
        old_refresh_token = "old_refresh_token_123"
        new_access_token = "new_access_token_456"
        new_refresh_token = "new_refresh_token_789"
        
        with patch("src.api.v1.auth_api.get_redis") as mock_get_redis, \
             patch("src.api.v1.auth_api.get_auth_service") as mock_get_auth_service:
            
            # Mock Redis 의존성 설정
            async def mock_redis_dependency():
                yield mock_redis_client
            mock_get_redis.return_value = mock_redis_dependency()
            
            # Mock AuthService 설정
            mock_auth_service = Mock()
            mock_auth_service.verify_refresh_token = AsyncMock(return_value=valid_refresh_token_payload)
            mock_auth_service.create_access_token = Mock(return_value=new_access_token)
            mock_auth_service.create_refresh_token = Mock(return_value=new_refresh_token)
            mock_auth_service.blacklist_token = AsyncMock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # When
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": old_refresh_token}
            )
            
            # Then
            assert response.status_code == 200
            
            # 1. 기존 토큰 검증
            mock_auth_service.verify_refresh_token.assert_called_once_with(old_refresh_token, mock_redis_client)
            
            # 2. 새로운 토큰들 생성
            mock_auth_service.create_access_token.assert_called_once()
            mock_auth_service.create_refresh_token.assert_called_once()
            
            # 3. 기존 토큰 블랙리스트 처리
            mock_auth_service.blacklist_token.assert_called_once()
            
            # 4. 새로운 토큰들이 쿠키에 설정됨
            assert response.cookies["access_token"] == new_access_token
            assert response.cookies["refresh_token"] == new_refresh_token
            
            # 5. 응답 메시지 확인
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "토큰 갱신 성공"