"""
Checkpointer 단위 테스트
"""
import pytest
from unittest.mock import patch, MagicMock
from src.services.ai.utils.checkpointer import create_checkpointer


def test_create_checkpointer_success(mock_redis_url):
    """Checkpointer 생성 성공 테스트"""
    with patch('src.services.ai.utils.checkpointer.RedisSaver') as mock_saver:
        mock_instance = MagicMock()
        mock_saver.from_conn_string.return_value = mock_instance
        
        result = create_checkpointer(mock_redis_url, ttl=1800)
        
        assert result is not None
        mock_saver.from_conn_string.assert_called_once_with(mock_redis_url)


def test_create_checkpointer_failure(mock_redis_url):
    """Checkpointer 생성 실패 테스트"""
    with patch('src.services.ai.utils.checkpointer.RedisSaver') as mock_saver:
        mock_saver.from_conn_string.side_effect = Exception("Connection failed")
        
        result = create_checkpointer(mock_redis_url)
        
        assert result is None


def test_create_checkpointer_with_custom_ttl(mock_redis_url):
    """Custom TTL로 Checkpointer 생성 테스트"""
    with patch('src.services.ai.utils.checkpointer.RedisSaver') as mock_saver:
        mock_instance = MagicMock()
        mock_saver.from_conn_string.return_value = mock_instance
        
        result = create_checkpointer(mock_redis_url, ttl=3600)
        
        assert result is not None
