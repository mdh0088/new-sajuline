"""
요청 로깅 미들웨어
Request ID 생성 및 요청/응답 로깅
"""
import time
import uuid
import json
import re
from typing import Callable, Dict, Any
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
        
        # # 민감한 필드 (로깅에서 마스킹) - 주석처리
        # self.sensitive_fields = {
        #     "password", "passwd", "pwd", "password_hash",
        #     "token", "access_token", "refresh_token", "jwt",
        #     "api_key", "secret", "key", "private_key",
        #     "ssn", "social_security_number", "card_number",
        #     "cvv", "pin", "otp", "verification_code"
        # }
    
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
        user_agent_info = self._parse_user_agent(user_agent)
        
        # Request Body 로깅
        request_body = await self._get_request_body(request)
        
        # Request에 body 정보와 user agent 정보 저장 (에러 핸들러에서 사용)
        request.state.request_body = request_body
        request.state.user_agent_info = user_agent_info
        
        log = get_logger_with_request_id()
        log.info("Request started", 
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params) if request.query_params else None,
                client_ip=client_ip,
                user_agent=user_agent,
                device=user_agent_info["device"],
                browser=user_agent_info["browser"],
                os=user_agent_info["os"],
                request_body=request_body)
        
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
    
    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """User-Agent 정보 파싱"""
        if not user_agent:
            return {"device": "unknown", "browser": "unknown", "os": "unknown"}
        
        # 디바이스 타입 판별
        device = "desktop"
        if re.search(r'Mobile|Android|iPhone|iPad', user_agent, re.IGNORECASE):
            if re.search(r'iPad', user_agent, re.IGNORECASE):
                device = "tablet"
            else:
                device = "mobile"
        elif re.search(r'Tablet', user_agent, re.IGNORECASE):
            device = "tablet"
        
        # 브라우저 판별
        browser = "unknown"
        if re.search(r'Chrome/(\d+)', user_agent):
            if re.search(r'Edg/', user_agent):
                browser = "edge"
            elif re.search(r'OPR/', user_agent):
                browser = "opera"
            else:
                browser = "chrome"
        elif re.search(r'Firefox/(\d+)', user_agent):
            browser = "firefox"
        elif re.search(r'Safari/(\d+)', user_agent) and not re.search(r'Chrome', user_agent):
            browser = "safari"
        elif re.search(r'MSIE|Trident', user_agent):
            browser = "ie"
        
        # OS 판별
        os_name = "unknown"
        if re.search(r'Windows NT (\d+\.\d+)', user_agent):
            os_match = re.search(r'Windows NT (\d+\.\d+)', user_agent)
            if os_match:
                version = os_match.group(1)
                os_name = f"windows-{version}"
        elif re.search(r'Mac OS X (\d+[._]\d+)', user_agent):
            os_match = re.search(r'Mac OS X (\d+[._]\d+)', user_agent)
            if os_match:
                version = os_match.group(1).replace('_', '.')
                os_name = f"macos-{version}"
        elif re.search(r'iPhone OS (\d+[._]\d+)', user_agent):
            os_match = re.search(r'iPhone OS (\d+[._]\d+)', user_agent)
            if os_match:
                version = os_match.group(1).replace('_', '.')
                os_name = f"ios-{version}"
        elif re.search(r'Android (\d+\.\d+)', user_agent):
            os_match = re.search(r'Android (\d+\.\d+)', user_agent)
            if os_match:
                version = os_match.group(1)
                os_name = f"android-{version}"
        elif re.search(r'Linux', user_agent):
            os_name = "linux"
        
        return {"device": device, "browser": browser, "os": os_name}
    
    async def _get_request_body(self, request: Request) -> Dict[str, Any]:
        """Request Body를 추출 (마스킹 없음)"""
        try:
            # Content-Type 확인
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # JSON 요청 처리
                body_bytes = await request.body()
                if body_bytes:
                    body_json = json.loads(body_bytes)
                    # return self._mask_sensitive_data(body_json)  # 마스킹 주석처리
                    return body_json  # 원본 그대로 반환
            
            elif "application/x-www-form-urlencoded" in content_type:
                # Form 데이터 처리
                form_data = await request.form()
                body_dict = dict(form_data)
                # return self._mask_sensitive_data(body_dict)  # 마스킹 주석처리
                return body_dict  # 원본 그대로 반환
            
            return {"content_type": content_type, "body_logged": False}
        
        except Exception as e:
            return {"error": f"Failed to parse request body: {str(e)}"}

    # def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """민감한 데이터를 마스킹 - 주석처리"""
    #     if not isinstance(data, dict):
    #         return data
    #     
    #     masked_data = {}
    #     for key, value in data.items():
    #         key_lower = key.lower()
    #         if any(sensitive in key_lower for sensitive in self.sensitive_fields):
    #             masked_data[key] = "***MASKED***"
    #         elif isinstance(value, dict):
    #             masked_data[key] = self._mask_sensitive_data(value)
    #         else:
    #             masked_data[key] = value
    #     
    #     return masked_data