"""
JWT 토큰 블랙리스트 관리
Redis를 사용한 토큰 무효화 시스템
"""
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis
from ...common.config.settings import get_settings


class TokenBlacklistService:
    """JWT 토큰 블랙리스트 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.blacklist_prefix = "blacklist:token:"
        
    async def connect(self):
        """Redis 연결"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def blacklist_token(self, jti: str, exp: datetime) -> bool:
        """
        토큰을 블랙리스트에 추가
        
        Args:
            jti: JWT Token ID (토큰의 고유 식별자)
            exp: 토큰 만료 시간
            
        Returns:
            성공 여부
        """
        try:
            await self.connect()
            
            # 토큰의 남은 유효 시간 계산
            remaining_time = exp - datetime.utcnow()
            if remaining_time <= timedelta(0):
                # 이미 만료된 토큰은 블랙리스트에 추가할 필요 없음
                return True
            
            # Redis에 토큰 ID 저장 (TTL은 토큰의 남은 유효 시간)
            key = f"{self.blacklist_prefix}{jti}"
            ttl_seconds = int(remaining_time.total_seconds())
            
            await self.redis_client.setex(
                key,
                ttl_seconds,
                "blacklisted"
            )
            
            return True
            
        except Exception as e:
            print(f"Error blacklisting token: {e}")
            return False
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        토큰이 블랙리스트에 있는지 확인
        
        Args:
            jti: JWT Token ID
            
        Returns:
            블랙리스트 여부
        """
        try:
            await self.connect()
            
            key = f"{self.blacklist_prefix}{jti}"
            result = await self.redis_client.exists(key)
            
            return bool(result)
            
        except Exception as e:
            print(f"Error checking token blacklist: {e}")
            # Redis 오류 시 안전하게 처리 (토큰을 유효한 것으로 간주)
            return False
    
    async def clear_expired_tokens(self):
        """
        만료된 토큰 정리 (Redis TTL이 자동으로 처리하므로 일반적으로 불필요)
        디버깅이나 수동 정리가 필요한 경우 사용
        """
        # Redis의 TTL 기능이 자동으로 만료된 키를 제거하므로
        # 별도의 정리 작업은 필요하지 않음
        pass


# 싱글톤 인스턴스
token_blacklist_service = TokenBlacklistService()