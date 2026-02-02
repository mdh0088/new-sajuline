"""
AI Settings 단위 테스트
"""
import pytest
from src.config.settings import settings


def test_ai_settings_defaults():
    """AI 설정 기본값 테스트"""
    # 기본값은 환경 변수에서 로드되므로 존재 여부만 확인
    assert hasattr(settings, 'openai_api_key')
    assert hasattr(settings, 'ai_redis_url')
    assert hasattr(settings, 'ai_session_ttl')
    assert hasattr(settings, 'ai_llm_model')
    assert hasattr(settings, 'ai_llm_timeout')
    assert hasattr(settings, 'ai_llm_fallback_model')


def test_ai_redis_url_format():
    """AI Redis URL 형식 테스트"""
    assert isinstance(settings.ai_redis_url, str)
    assert settings.ai_redis_url.startswith('redis://')


def test_ai_session_ttl_type():
    """AI Session TTL 타입 테스트"""
    assert isinstance(settings.ai_session_ttl, int)
    assert settings.ai_session_ttl > 0


def test_ai_llm_timeout_type():
    """AI LLM Timeout 타입 테스트"""
    assert isinstance(settings.ai_llm_timeout, int)
    assert settings.ai_llm_timeout > 0
