"""
Rate Limiting 서비스
Redis를 사용한 API 요청 제한 구현
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import redis.asyncio as redis
from ...common.config.settings import get_settings


class RateLimiter:
    """Rate Limiting 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
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
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        cost: int = 1
    ) -> Tuple[bool, int, float]:
        """
        Rate limit 확인 (Sliding Window Counter 알고리즘)
        
        Args:
            key: Rate limit을 적용할 고유 키 (예: "user:123", "ip:192.168.1.1")
            max_requests: 허용되는 최대 요청 수
            window_seconds: 시간 윈도우 (초)
            cost: 이 요청의 비용 (기본값: 1)
            
        Returns:
            (허용 여부, 남은 요청 수, 리셋까지 남은 시간(초))
        """
        try:
            await self.connect()
            
            now = datetime.now()
            window_start = now - timedelta(seconds=window_seconds)
            
            # Redis key
            redis_key = f"rate_limit:{key}"
            
            # 트랜잭션으로 원자적 실행
            pipe = self.redis_client.pipeline()
            
            # 만료된 항목 제거
            pipe.zremrangebyscore(redis_key, 0, window_start.timestamp())
            
            # 현재 윈도우 내 요청 수 확인
            pipe.zcard(redis_key)
            
            # 새 요청 추가 (비용 반영)
            for _ in range(cost):
                pipe.zadd(redis_key, {f"{now.timestamp()}:{id(now)}": now.timestamp()})
            
            # TTL 설정
            pipe.expire(redis_key, window_seconds + 1)
            
            results = await pipe.execute()
            current_count = results[1]  # zcard 결과
            
            # 한도 초과 확인
            if current_count + cost > max_requests:
                # 한도 초과 시 추가한 항목 제거
                pipe = self.redis_client.pipeline()
                for _ in range(cost):
                    pipe.zremrangebyscore(redis_key, now.timestamp(), now.timestamp())
                await pipe.execute()
                
                # 가장 오래된 요청 시간 확인
                oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    reset_time = oldest[0][1] + window_seconds
                    time_until_reset = max(0, reset_time - now.timestamp())
                else:
                    time_until_reset = 0
                
                return False, 0, time_until_reset
            
            remaining = max(0, max_requests - current_count - cost)
            return True, remaining, 0
            
        except Exception as e:
            print(f"Rate limit check error: {e}")
            # Redis 오류 시 요청 허용 (fail open)
            return True, max_requests, 0
    
    async def get_rate_limit_info(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[int, int, float]:
        """
        현재 rate limit 정보 조회
        
        Returns:
            (사용된 요청 수, 남은 요청 수, 리셋까지 남은 시간)
        """
        try:
            await self.connect()
            
            now = datetime.now()
            window_start = now - timedelta(seconds=window_seconds)
            redis_key = f"rate_limit:{key}"
            
            # 만료된 항목 제거
            await self.redis_client.zremrangebyscore(redis_key, 0, window_start.timestamp())
            
            # 현재 요청 수
            current_count = await self.redis_client.zcard(redis_key)
            
            # 가장 오래된 요청 시간
            oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
            if oldest and current_count >= max_requests:
                reset_time = oldest[0][1] + window_seconds
                time_until_reset = max(0, reset_time - now.timestamp())
            else:
                time_until_reset = 0
            
            remaining = max(0, max_requests - current_count)
            return current_count, remaining, time_until_reset
            
        except Exception as e:
            print(f"Rate limit info error: {e}")
            return 0, max_requests, 0


# Rate limit 프리셋
class RateLimitPresets:
    """일반적인 rate limit 설정"""
    
    # API 엔드포인트별 설정
    LOGIN = {"max_requests": 5, "window_seconds": 300}  # 5분에 5회
    SIGNUP = {"max_requests": 3, "window_seconds": 3600}  # 1시간에 3회
    AI_FORTUNE = {"max_requests": 10, "window_seconds": 3600}  # 1시간에 10회
    PASSWORD_RESET = {"max_requests": 3, "window_seconds": 3600}  # 1시간에 3회
    
    # 전역 설정
    GLOBAL_PER_IP = {"max_requests": 100, "window_seconds": 60}  # 1분에 100회
    GLOBAL_PER_USER = {"max_requests": 1000, "window_seconds": 3600}  # 1시간에 1000회


# 싱글톤 인스턴스
rate_limiter = RateLimiter()