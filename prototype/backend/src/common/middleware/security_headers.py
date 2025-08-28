"""
보안 헤더 미들웨어
XSS, Clickjacking 등 웹 보안 공격 방어를 위한 HTTP 헤더 설정
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    보안 관련 HTTP 헤더를 설정하는 미들웨어
    
    OWASP 권장 보안 헤더를 자동으로 추가하여
    다양한 웹 보안 공격으로부터 애플리케이션을 보호
    """
    
    def __init__(
        self,
        app,
        x_content_type_options: str = "nosniff",
        x_frame_options: str = "DENY",
        x_xss_protection: str = "1; mode=block",
        strict_transport_security: str = "max-age=31536000; includeSubDomains",
        content_security_policy: str = None,
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str = "geolocation=(), microphone=(), camera=()"
    ):
        """
        미들웨어 초기화
        
        Args:
            app: FastAPI 애플리케이션
            x_content_type_options: MIME 타입 스니핑 방지
            x_frame_options: Clickjacking 방지
            x_xss_protection: XSS 필터 활성화
            strict_transport_security: HTTPS 강제
            content_security_policy: 컨텐츠 보안 정책
            referrer_policy: Referrer 정책
            permissions_policy: 브라우저 기능 권한 정책
        """
        super().__init__(app)
        self.x_content_type_options = x_content_type_options
        self.x_frame_options = x_frame_options
        self.x_xss_protection = x_xss_protection
        self.strict_transport_security = strict_transport_security
        self.content_security_policy = content_security_policy or self._default_csp()
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy
    
    def _default_csp(self) -> str:
        """
        기본 Content Security Policy 설정
        
        보안 강화:
        - 'unsafe-inline'과 'unsafe-eval' 사용 최소화
        - nonce 기반 스크립트 실행 지원
        - 필요한 도메인만 명시적으로 허용
        """
        import secrets
        # 각 요청마다 고유한 nonce 생성 (필요시 활성화)
        # nonce = secrets.token_urlsafe(16)
        
        return (
            "default-src 'self'; "
            # 프로덕션에서는 'unsafe-inline'과 'unsafe-eval' 제거 권장
            # nonce 기반으로 전환: f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
            "script-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        모든 응답에 보안 헤더 추가
        
        Args:
            request: HTTP 요청 객체
            call_next: 다음 미들웨어 또는 라우트 핸들러
            
        Returns:
            보안 헤더가 추가된 HTTP 응답
        """
        # 요청 처리
        response = await call_next(request)
        
        # 보안 헤더 추가
        if self.x_content_type_options:
            response.headers["X-Content-Type-Options"] = self.x_content_type_options
        
        if self.x_frame_options:
            response.headers["X-Frame-Options"] = self.x_frame_options
        
        if self.x_xss_protection:
            response.headers["X-XSS-Protection"] = self.x_xss_protection
        
        # HTTPS 환경에서만 HSTS 헤더 추가
        if request.url.scheme == "https" and self.strict_transport_security:
            response.headers["Strict-Transport-Security"] = self.strict_transport_security
        
        # Only set CSP if not already set by the route handler
        if self.content_security_policy and "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = self.content_security_policy
        
        if self.referrer_policy:
            response.headers["Referrer-Policy"] = self.referrer_policy
        
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy
        
        # 추가 보안 헤더
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # 개발 환경에서는 CSP 위반 보고 헤더 추가 (디버깅용)
        if request.app.debug:
            response.headers["Content-Security-Policy-Report-Only"] = (
                self.content_security_policy + "; report-uri /api/csp-report"
            )
        
        return response


class APISecurityHeadersMiddleware(SecurityHeadersMiddleware):
    """
    API 전용 보안 헤더 미들웨어
    
    API 서버에 최적화된 보안 헤더 설정
    """
    
    def __init__(self, app):
        # 개발 환경인지 확인
        from src.common.config.settings import get_settings
        settings = get_settings()
        
        # 개발 환경에서는 더 관대한 CSP 정책 적용
        if settings.ENVIRONMENT == "development":
            csp_policy = "default-src 'self' http://localhost:* ws://localhost:*; connect-src 'self' http://localhost:* ws://localhost:*; frame-ancestors 'none';"
        else:
            # 프로덕션에서는 엄격한 CSP 적용
            csp_policy = "default-src 'none'; frame-ancestors 'none';"
            
        super().__init__(
            app,
            # API는 iframe에 포함될 필요 없음
            x_frame_options="DENY",
            # 환경별 CSP 정책 적용
            content_security_policy=csp_policy,
            # API는 브라우저 기능 사용하지 않음
            permissions_policy="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        )