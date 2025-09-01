"""
Redis 서비스 단위 테스트

TokenBlacklistService의 토큰 블랙리스트 등록/확인 기능과
로깅, 에러 처리가 올바르게 작동하는지 테스트합니다.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import AsyncGenerator

from src.core.redis import (
    get_redis, 
    close_redis, 
    TokenBlacklistService,
    get_token_blacklist_service
)
from src.exceptions.custom_exceptions import ValidationError


@pytest.mark.unit
class TestRedisConnection:
    """Redis 연결 관련 테스트"""

    @patch('src.core.redis.redis')
    async def test_get_redis_success(self, mock_redis):
        """Redis 연결 성공 테스트"""
        # Given
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_redis.from_url.return_value = mock_client
        
        # When
        async for redis_client in get_redis():
            # Then
            assert redis_client is not None
            mock_redis.from_url.assert_called_once()
            mock_client.ping.assert_called_once()
            break

    @patch('src.core.redis.redis')
    @patch('src.core.redis.get_logger_with_request_id')
    async def test_get_redis_connection_failed(self, mock_logger, mock_redis):
        """Redis 연결 실패 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(side_effect=Exception("Connection failed"))
        mock_redis.from_url.return_value = mock_client
        
        # When & Then
        with pytest.raises(ValidationError, match="Redis 연결에 실패했습니다"):
            async for _ in get_redis():
                break
        
        # 에러 로그가 기록되었는지 확인
        mock_log.error.assert_called_once()
        assert "Redis connection failed" in str(mock_log.error.call_args)

    async def test_close_redis(self):
        """Redis 연결 종료 테스트"""
        # Given
        import src.core.redis as redis_module
        mock_client = AsyncMock()
        redis_module._redis_client = mock_client
        
        # When
        await close_redis()
        
        # Then
        mock_client.close.assert_called_once()
        assert redis_module._redis_client is None


@pytest.mark.unit
class TestTokenBlacklistService:
    """토큰 블랙리스트 서비스 테스트"""

    @pytest.fixture
    def mock_redis_client(self):
        """모킹된 Redis 클라이언트"""
        client_mock = AsyncMock()
        client_mock.setex = AsyncMock(return_value=True)
        client_mock.get = AsyncMock(return_value=None)
        client_mock.keys = AsyncMock(return_value=[])
        return client_mock

    @pytest.fixture
    def blacklist_service(self, mock_redis_client):
        """TokenBlacklistService 인스턴스"""
        return TokenBlacklistService(mock_redis_client)

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_add_token_success(self, mock_logger, blacklist_service, mock_redis_client):
        """토큰 블랙리스트 등록 성공 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        jti = "test-jwt-id-123"
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # When
        result = await blacklist_service.add_token(jti, expires_at)
        
        # Then
        assert result is True
        
        # Redis setex 호출 확인
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        assert f"blacklist:token:{jti}" == call_args[0][0]
        assert call_args[0][2] == "1"  # value
        
        # 성공 로그 확인
        mock_log.info.assert_called()
        assert "Adding token to blacklist" in str(mock_log.info.call_args_list[0])
        assert "Token blacklisted successfully" in str(mock_log.info.call_args_list[1])

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_add_token_already_expired(self, mock_logger, blacklist_service, mock_redis_client):
        """이미 만료된 토큰 블랙리스트 등록 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        jti = "expired-jwt-id"
        expires_at = datetime.utcnow() - timedelta(hours=1)  # 이미 만료
        
        # When
        result = await blacklist_service.add_token(jti, expires_at)
        
        # Then
        assert result is True
        mock_redis_client.setex.assert_not_called()  # Redis 호출 안함
        
        # 경고 로그 확인
        mock_log.warning.assert_called()
        assert "Token already expired, skipping blacklist" in str(mock_log.warning.call_args)

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_add_token_redis_error(self, mock_logger, blacklist_service, mock_redis_client):
        """Redis 에러 시 블랙리스트 등록 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.setex.side_effect = Exception("Redis error")
        
        jti = "error-jwt-id"
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # When
        result = await blacklist_service.add_token(jti, expires_at)
        
        # Then
        assert result is False  # 실패했지만 서비스 연속성 유지
        
        # 에러 로그 확인
        mock_log.error.assert_called()
        assert "Failed to blacklist token" in str(mock_log.error.call_args)

    async def test_is_blacklisted_true(self, blacklist_service, mock_redis_client):
        """블랙리스트된 토큰 확인 테스트"""
        # Given
        mock_redis_client.get.return_value = "1"  # 블랙리스트에 존재
        jti = "blacklisted-jwt-id"
        
        # When
        result = await blacklist_service.is_blacklisted(jti)
        
        # Then
        assert result is True
        mock_redis_client.get.assert_called_once_with(f"blacklist:token:{jti}")

    async def test_is_blacklisted_false(self, blacklist_service, mock_redis_client):
        """블랙리스트되지 않은 토큰 확인 테스트"""
        # Given
        mock_redis_client.get.return_value = None  # 블랙리스트에 없음
        jti = "clean-jwt-id"
        
        # When
        result = await blacklist_service.is_blacklisted(jti)
        
        # Then
        assert result is False
        mock_redis_client.get.assert_called_once_with(f"blacklist:token:{jti}")

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_is_blacklisted_redis_error(self, mock_logger, blacklist_service, mock_redis_client):
        """Redis 에러 시 블랙리스트 확인 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.get.side_effect = Exception("Redis connection lost")
        
        jti = "error-jwt-id"
        
        # When
        result = await blacklist_service.is_blacklisted(jti)
        
        # Then
        assert result is False  # 에러 시 false 반환 (서비스 연속성)
        
        # 에러 로그 확인
        mock_log.error.assert_called()
        assert "Failed to check blacklist" in str(mock_log.error.call_args)

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_get_stats_success(self, mock_logger, blacklist_service, mock_redis_client):
        """블랙리스트 통계 조회 성공 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.keys.return_value = [
            "blacklist:token:jwt1", 
            "blacklist:token:jwt2", 
            "blacklist:token:jwt3"
        ]
        
        # When
        stats = await blacklist_service.get_stats()
        
        # Then
        assert stats["total_blacklisted"] == 3
        assert stats["pattern"] == "blacklist:token:*"
        assert stats["redis_connected"] is True
        
        # 성공 로그 확인
        mock_log.info.assert_called()
        assert "Blacklist stats retrieved" in str(mock_log.info.call_args)

    @patch('src.core.redis.get_logger_with_request_id')
    async def test_get_stats_redis_error(self, mock_logger, blacklist_service, mock_redis_client):
        """Redis 에러 시 통계 조회 테스트"""
        # Given
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_redis_client.keys.side_effect = Exception("Redis keys error")
        
        # When
        stats = await blacklist_service.get_stats()
        
        # Then
        assert stats["total_blacklisted"] == 0
        assert stats["redis_connected"] is False
        
        # 에러 로그 확인
        mock_log.error.assert_called()
        assert "Failed to get blacklist stats" in str(mock_log.error.call_args)

    def test_factory_function(self, mock_redis_client):
        """팩토리 함수 테스트"""
        # When
        service = get_token_blacklist_service(mock_redis_client)
        
        # Then
        assert isinstance(service, TokenBlacklistService)
        assert service.redis is mock_redis_client
        assert service.prefix == "blacklist:token:"


@pytest.mark.integration
class TestRedisServiceIntegration:
    """Redis 서비스 통합 테스트 (실제 Redis 연결 필요)"""
    
    @pytest.mark.skip(reason="실제 Redis 서버가 필요한 통합 테스트")
    async def test_full_blacklist_workflow(self):
        """전체 블랙리스트 워크플로우 통합 테스트"""
        # 실제 Redis 서버 연결이 필요한 테스트
        # CI/CD에서는 Redis 컨테이너와 함께 실행
        pass


@pytest.mark.unit  
class TestLoggerCatchDecorator:
    """@logger.catch 데코레이터 동작 테스트"""
    
    @patch('src.core.redis.logger')
    async def test_logger_catch_reraise(self, mock_logger, mock_redis_client):
        """@logger.catch(reraise=True) 동작 테스트"""
        # Given
        service = TokenBlacklistService(mock_redis_client)
        mock_redis_client.setex.side_effect = Exception("Test error")
        
        jti = "test-jwt"
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # When & Then
        # 예외가 재발생되어야 하지만 logger.catch가 로그를 남겨야 함
        result = await service.add_token(jti, expires_at)
        
        # logger.catch가 동작하여 예외가 로깅되고 서비스는 False 반환
        assert result is False