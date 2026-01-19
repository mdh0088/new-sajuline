"""
로깅 미들웨어

모든 HTTP 요청/응답을 구조화된 로그로 기록
성능 모니터링 및 디버깅을 위한 상세 정보 수집
"""

import time
import uuid
import json
import logging
from typing import Callable, Optional, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.common.logging.config import set_trace_id, reset_trace_id, set_user_id, reset_user_id

logger = logging.getLogger(__name__)


MASK_KEYS = {
    "password", "token", "refresh_token", "id_token",
    "authorization", "cookie", "api_key", "client-secret",
    "ssn", "email"
}
MAX_BODY_LOG_BYTES = 2 * 1024  # 2KB


def _is_multipart(content_type: Optional[str]) -> bool:
    return bool(content_type and "multipart/form-data" in content_type.lower())


def _mask_dict(d: dict[str, Any]) -> dict[str, Any]:
    try:
        return {k: ("****" if k.lower() in MASK_KEYS else v) for k, v in d.items()}
    except Exception:
        return {}


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청/응답 로깅 미들웨어
    
    각 요청에 대해 다음 정보를 로깅:
    - 요청 ID (UUID)
    - HTTP 메서드, URL, 헤더
    - 응답 상태 코드, 처리 시간
    - 사용자 정보 (인증된 경우)
    - 에러 정보 (실패한 경우)
    """
    
    def __init__(self, app: ASGIApp, exclude_paths: list[str] | None = None) -> None:
        """
        미들웨어 초기화
        
        Args:
            app: FastAPI 애플리케이션
            exclude_paths: 로깅에서 제외할 경로 목록
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 처리 및 로깅
        
        Args:
            request: HTTP 요청 객체
            call_next: 다음 미들웨어 또는 엔드포인트
            
        Returns:
            Response: HTTP 응답 객체
        """
        # 요청 ID: 헤더 수용 또는 생성
        incoming_request_id = request.headers.get("X-Request-ID")
        request_id = incoming_request_id or str(uuid.uuid4())
        request.state.request_id = request_id
        trace_token = set_trace_id(request_id)
        
        # 제외 경로 체크
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 요청 시작 시간
        start_time = time.perf_counter()
        
        # 요청 로깅 (바디는 2KB 이하, multipart 제외)
        await self._log_request(request, request_id)
        
        # 요청 처리
        try:
            response = await call_next(request)
            
            # 성공 응답 로깅
            await self._log_response(
                request, 
                response, 
                request_id, 
                start_time
            )
            
            return response
            
        except Exception as exc:
            # 에러 응답 로깅
            await self._log_error(
                request, 
                exc, 
                request_id, 
                start_time
            )
            raise
        finally:
            # 컨텍스트 정리
            try:
                reset_trace_id(trace_token)
                token_in_state = getattr(request.state, "user_token", None)
                if token_in_state:
                    reset_user_id(token_in_state)
            except Exception:
                pass
    
    async def _log_request(self, request: Request, request_id: str) -> None:
        """
        HTTP 요청의 시작을 로깅합니다.
        
        요청의 메서드, 경로, 요청 ID, 클라이언트 정보를 포함하여 HTTP 요청이 시작됨을 기록합니다. 민감한 헤더 값은 마스킹 처리됩니다.
        """
        # 민감한 헤더 필터링
        headers = dict(request.headers)
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        filtered_headers = {
            k: "***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }
        
        # 클라이언트 IP 추출 (프록시 환경 고려)
        client_ip = self._get_client_ip(request, headers)
        
        # 클라이언트 정보
        client_info = {
            "host": client_ip,
            "port": request.client.port if request.client else None,
            "user_agent": headers.get("user-agent"),
            "referer": headers.get("referer")
        }
        
        # 요청 바디 로깅 시도 (JSON만, 2KB 제한)
        req_body_snippet: Optional[str] = None
        try:
            content_type = headers.get("content-type", "")
            if not _is_multipart(content_type):
                raw = await request.body()
                if raw and len(raw) <= MAX_BODY_LOG_BYTES:
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict):
                            parsed = _mask_dict(parsed)
                        req_body_snippet = json.dumps(parsed, ensure_ascii=False)
                    except Exception:
                        # json 아님 → 생략
                        req_body_snippet = None
        except Exception:
            req_body_snippet = None

        logger.info(
            "http_request",
            extra={
                "http.method": request.method,
                "http.path": request.url.path,
                "client.ip": client_ip,
                "request.body": req_body_snippet,
            },
        )
    
    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        start_time: float
    ) -> None:
        """
        HTTP 응답 정보를 로깅하고 응답 헤더에 요청 ID와 처리 시간을 추가합니다.
        
        응답 상태 코드에 따라 적절한 로그 레벨로 요청 완료 메시지를 기록하며, 처리 시간과 요청 ID를 응답 헤더에 포함시킵니다. 인증된 사용자인 경우 사용자 ID도 로그에 포함됩니다.
        """
        # 처리 시간 계산
        process_time = time.perf_counter() - start_time
        
        # 응답 헤더에 요청 ID 추가 (유입분 보존)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(int(process_time * 1000))
        
        # 로그 레벨 결정: 5xx=error, 4xx=warning, else=info
        log_level = (
            "error" if response.status_code >= 500 else "warning" if response.status_code >= 400 else "info"
        )
        
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "duration_ms": int(process_time * 1000),
            "response_size": response.headers.get("content-length"),
            "content_type": response.headers.get("content-type")
        }
        
        # 사용자 정보 추가 (인증된 경우)
        if hasattr(request.state, "user_id"):
            log_data["user_id"] = request.state.user_id
        
        if log_level == "error":
            logger.error(
                "http_response",
                extra=log_data,
            )
        elif log_level == "warning":
            logger.warning(
                "http_response",
                extra=log_data,
            )
        else:
            logger.info(
                "http_response",
                extra=log_data,
            )
    
    async def _log_error(
        self,
        request: Request,
        exception: Exception,
        request_id: str,
        start_time: float
    ) -> None:
        """
        HTTP 요청 처리 중 발생한 예외를 에러 로그로 기록합니다.
        
        Parameters:
            request (Request): 처리 중인 HTTP 요청 객체
            exception (Exception): 발생한 예외 객체
            request_id (str): 요청을 식별하는 고유 ID
            start_time (float): 요청이 시작된 시간(초 단위, UNIX 타임스탬프)
        """
        # 처리 시간 계산
        process_time = time.perf_counter() - start_time

        logger.error(
            "http_exception",
            extra={
                "http.method": request.method,
                "http.path": request.url.path,
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
                "duration_ms": int(process_time * 1000),
                "trace_id": request_id,
            },
            exc_info=True,
        )
    
    def _get_client_ip(self, request: Request, headers: dict) -> Optional[str]:
        """
        프록시 환경을 고려한 클라이언트 IP 추출
        
        Args:
            request: HTTP 요청 객체
            headers: 요청 헤더 딕셔너리
            
        Returns:
            str: 클라이언트 IP 주소
        """
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        x_forwarded_for = headers.get("x-forwarded-for")
        if x_forwarded_for:
            # 첫 번째 IP가 실제 클라이언트 IP
            return x_forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인 (일부 프록시에서 사용)
        x_real_ip = headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip.strip()
        
        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else None