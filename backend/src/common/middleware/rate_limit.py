"""
레이트 리미팅 미들웨어 설정
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from src.config.settings import settings


def get_client_identifier(request: Request) -> str:
    """
    클라이언트 식별자 반환 (IP 기반)
    프록시/로드밸런서 환경 대응
    """
    # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 대응)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 첫 번째 IP가 실제 클라이언트 IP
        return forwarded_for.split(",")[0].strip()
    
    # X-Real-IP 헤더 확인 (Nginx 등)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # 직접 연결인 경우
    return get_remote_address(request)


# 글로벌 리미터 인스턴스
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}/2",  # DB 2번 사용
    default_limits=["1000/hour"]  # 기본값: 시간당 1000회 (매우 관대)
)