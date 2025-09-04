"""
Redis 연결 설정 및 공통 서비스
토큰 블랙리스트 전용 (DB 1번 사용, Rate Limit은 DB 2번)
"""
from typing import AsyncGenerator, Optional
import redis.asyncio as redis
from datetime import datetime

from src.config.settings import settings
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError


# =============================================================================
# Redis 연결 관리 (database.py와 동일한 패턴)
# =============================================================================

# Redis 클라이언트 (지연 초기화)
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Redis 비동기 클라이언트 의존성
    
    FastAPI 의존성 주입에서 사용
    토큰 블랙리스트용 (DB 1번 사용)
    """
    global _redis_client
    
    if _redis_client is None:
        log = get_logger_with_request_id()
        try:
            _redis_client = redis.from_url(
                settings.redis_url,
                db=1,  # DB 1번 (Rate Limit은 DB 2번)
                password=settings.redis_password,
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            await _redis_client.ping()
            log.info("Redis connection established", db=1)
        except Exception as e:
            log.error("Redis connection failed", error=str(e))
            raise ValidationError("Redis 연결에 실패했습니다")
    
    try:
        yield _redis_client
    except Exception as e:
        # Redis 사용 중 오류 발생해도 재연결 시도
        log = get_logger_with_request_id()
        log.error("Redis operation failed", error=str(e))
        # 예외를 다시 발생시켜 FastAPI가 적절히 처리할 수 있도록 함
        raise


async def close_redis() -> None:
    """
    Redis 연결 종료
    애플리케이션 종료 시 호출
    """
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# =============================================================================
# 토큰 블랙리스트 전용 서비스
# =============================================================================

class TokenBlacklistService:
    """토큰 블랙리스트 관리 서비스 (프로젝트 규격 준수)"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "blacklist:token:"
    
    @logger.catch(reraise=True)
    async def add_token(self, jti: str, expires_at: datetime) -> bool:
        """
        토큰 블랙리스트 등록
        
        Args:
            jti: JWT ID (토큰 고유 식별자)
            expires_at: 토큰 만료 시간
            
        Returns:
            bool: 성공 여부
        """
        log = get_logger_with_request_id()
        log.info("Adding token to blacklist", jti=jti)
        
        try:
            # TTL 계산 (만료 시간까지 남은 시간)
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            
            if ttl <= 0:
                log.warning("Token already expired, skipping blacklist", jti=jti)
                return True
            
            # Redis에 블랙리스트 등록 (TTL로 자동 만료)
            key = f"{self.prefix}{jti}"
            await self.redis.setex(key, ttl, "1")
            
            log.info("Token blacklisted successfully", jti=jti, ttl=ttl)
            return True
            
        except Exception as e:
            log.error("Failed to blacklist token", jti=jti, error=str(e))
            # 블랙리스트 실패해도 서비스 연속성 유지
            return False
    
    @logger.catch(reraise=True)
    async def is_blacklisted(self, jti: str) -> bool:
        """
        토큰 블랙리스트 확인
        
        Args:
            jti: JWT ID
            
        Returns:
            bool: 블랙리스트 여부
        """
        try:
            key = f"{self.prefix}{jti}"
            result = await self.redis.get(key)
            is_blacklisted = result is not None
            
            if is_blacklisted:
                log = get_logger_with_request_id()
                log.warning("Blacklisted token usage attempt", jti=jti)
            
            return is_blacklisted
            
        except Exception as e:
            log = get_logger_with_request_id()
            log.error("Failed to check blacklist", jti=jti, error=str(e))
            # Redis 연결 실패시 false 반환 (서비스 연속성)
            return False
    
    @logger.catch(reraise=True)
    async def get_stats(self) -> dict:
        """블랙리스트 통계 정보"""
        log = get_logger_with_request_id()
        
        try:
            pattern = f"{self.prefix}*"
            keys = await self.redis.keys(pattern)
            
            stats = {
                "total_blacklisted": len(keys),
                "pattern": pattern,
                "redis_connected": True
            }
            
            log.info("Blacklist stats retrieved", **stats)
            return stats
            
        except Exception as e:
            log.error("Failed to get blacklist stats", error=str(e))
            return {
                "total_blacklisted": 0,
                "pattern": self.prefix,
                "redis_connected": False
            }


def get_token_blacklist_service(redis_client: redis.Redis) -> TokenBlacklistService:
    """TokenBlacklistService 팩토리 함수 (의존성 주입 패턴)"""
    return TokenBlacklistService(redis_client)