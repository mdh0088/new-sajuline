"""
레이트 리미터 미들웨어

API 호출 빈도를 제한하여 서비스 안정성 확보
Redis를 사용한 분산 환경에서의 레이트 리미팅
"""

import time
import logging
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.common.config.settings import get_settings
from src.common.exceptions.custom import RateLimitException
from src.common.infrastructure.rate_limiter import rate_limiter, RateLimitPresets

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    API 레이트 리미터 미들웨어
    
    Redis를 사용하여 사용자별/IP별 API 호출 빈도 제한
    Sliding window 알고리즘 구현
    """
    
    def __init__(
        self,
        app,
        calls: int = None,
        period: int = None,
        exempt_paths: list = None
    ):
        """
        미들웨어 초기화
        
        Args:
            app: FastAPI 애플리케이션
            calls: 허용 호출 횟수
            period: 제한 기간(초)
            exempt_paths: 제한에서 제외할 경로 목록
        """
        super().__init__(app)
        self.calls = calls or settings.RATE_LIMIT_CALLS
        self.period = period or settings.RATE_LIMIT_PERIOD
        self.exempt_paths = exempt_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        클라이언트의 요청에 대해 레이트 리미팅을 적용하고, 제한을 초과한 경우 예외를 발생시킵니다.
        
        레이트 리미터가 비활성화되어 있거나 제외된 경로인 경우 제한 없이 요청을 처리합니다.  
        제한을 초과하면 `RateLimitException`을 발생시키며, 허용된 경우 응답 헤더에 레이트 리미트 정보를 추가합니다.
        
        Returns:
            Response: 처리된 HTTP 응답 객체
        """
        # 레이트 리미터가 비활성화된 경우 패스
        if not self.enabled:
            return await call_next(request)
        
        # 제외 경로 체크
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # 클라이언트 식별자 생성
        client_id = await self._get_client_identifier(request)
        
        # 레이트 리미트 체크
        is_allowed, retry_after = await self._check_rate_limit(client_id)
        
        if not is_allowed:
            # 레이트 리미트 초과 로깅
            logger.warning(
                f"Rate limit exceeded: {client_id} - {request.method} {request.url.path} "
                f"(limit: {self.calls}/{self.period}s, retry after: {retry_after}s)"
            )
            
            raise RateLimitException(
                message=f"API 호출 한도를 초과했습니다. {retry_after}초 후 다시 시도해주세요.",
                retry_after=retry_after
            )
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 헤더에 레이트 리미트 정보 추가
        remaining = await self._get_remaining_calls(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.period)
        
        return response
    
    async def _get_client_identifier(self, request: Request) -> str:
        """
        클라이언트 식별자 생성
        
        Args:
            request: HTTP 요청 객체
            
        Returns:
            str: 클라이언트 고유 식별자
        """
        # 인증된 사용자인 경우 사용자 ID 사용
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # 미인증 사용자인 경우 IP 주소 사용
        client_ip = request.client.host if request.client else "unknown"
        
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        레이트 리미트 확인 (Sliding Window 알고리즘)
        
        Args:
            client_id: 클라이언트 식별자
            
        Returns:
            tuple: (허용 여부, 재시도 가능 시간)
        """
        allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
            key=client_id,
            max_requests=self.calls,
            window_seconds=self.period
        )
        
        if not allowed:
            return False, int(reset_time)
        
        return True, None
    
    async def _get_remaining_calls(self, client_id: str) -> int:
        """
        남은 호출 횟수 계산
        
        Args:
            client_id: 클라이언트 식별자
            
        Returns:
            int: 남은 호출 횟수
        """
        _, remaining, _ = await self.rate_limiter.get_rate_limit_info(
            key=client_id,
            max_requests=self.calls,
            window_seconds=self.period
        )
        return remaining


class IPRateLimitMiddleware(RateLimitMiddleware):
    """
    IP 기반 레이트 리미터
    
    특정 IP에서의 과도한 요청을 방지
    """
    
    async def _get_client_identifier(self, request: Request) -> str:
        """IP 주소만을 기반으로 식별자 생성"""
        client_ip = request.client.host if request.client else "unknown"
        
        # 프록시 헤더 확인
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        return f"ip:{client_ip}"


class UserRateLimitMiddleware(RateLimitMiddleware):
    """
    사용자 기반 레이트 리미터
    
    인증된 사용자별로 API 호출 제한
    """
    
    async def _get_client_identifier(self, request: Request) -> str:
        """사용자 ID를 기반으로 식별자 생성"""
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # 미인증 사용자는 제한하지 않음
        return "anonymous"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """미인증 사용자는 레이트 리미팅 건너뛰기"""
        if not hasattr(request.state, "user_id") or not request.state.user_id:
            return await call_next(request)
        
        return await super().dispatch(request, call_next) 