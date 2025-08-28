"""
요청 로깅 미들웨어
Request ID 생성 및 요청/응답 로깅
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging.config import set_request_id, get_request_id
from ..logging import logger, get_logger_with_request_id


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    def __init__(self, app):
        super().__init__(app)
        # 로깅 제외할 경로
        self.exclude_paths = {
            "/health", 
            "/readiness", 
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """요청 처리 및 로깅"""
        # Request ID 생성
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        
        # Request 헤더에 ID 추가 (디버깅용)
        request.headers.__dict__.setdefault("_list", []).append(
            (b"x-request-id", request_id.encode())
        )
        
        # 로깅 제외 경로 체크
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        
        # 요청 시작 로깅
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        log = get_logger_with_request_id()
        log.info("Request started", 
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params) if request.query_params else None,
                client_ip=client_ip,
                user_agent=user_agent)
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 완료 로깅
            duration_ms = (time.time() - start_time) * 1000
            log.info("Request completed", 
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=round(duration_ms, 2),
                    client_ip=client_ip)
            
        except Exception as exc:
            # 예외 발생시 로깅
            duration_ms = (time.time() - start_time) * 1000
            log.error("Request failed", 
                     method=request.method,
                     path=request.url.path,
                     status_code=500,
                     duration_ms=round(duration_ms, 2),
                     client_ip=client_ip,
                     error=str(exc))
            raise
        
        # Response 헤더에 Request ID 추가
        response.headers["X-Request-ID"] = request_id
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # X-Forwarded-For 헤더 우선 (프록시 환경)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 직접 연결
        if request.client:
            return request.client.host
        
        return "unknown"