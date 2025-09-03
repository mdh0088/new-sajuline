"""클라이언트 정보 추출 유틸리티"""

import re
from typing import Optional, Tuple
from fastapi import Request
from user_agents import parse

from src.schemas.user_activity_log_schema import DeviceType


def get_client_ip(request: Request) -> Optional[str]:
    """클라이언트 IP 주소 추출"""
    # Proxy 환경에서 실제 IP 추출
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For: client, proxy1, proxy2 형태
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # 직접 연결인 경우
    if request.client:
        return request.client.host
    
    return None


def get_user_agent(request: Request) -> Optional[str]:
    """User-Agent 헤더 추출"""
    return request.headers.get("User-Agent")


def get_device_type(user_agent: Optional[str]) -> Optional[DeviceType]:
    """User-Agent를 통한 디바이스 타입 판별"""
    if not user_agent:
        return None
    
    try:
        parsed_ua = parse(user_agent)
        
        if parsed_ua.is_mobile:
            return DeviceType.MOBILE
        elif parsed_ua.is_tablet:
            return DeviceType.TABLET
        elif parsed_ua.is_pc:
            return DeviceType.DESKTOP
        else:
            # 기본값으로 데스크톱 처리
            return DeviceType.DESKTOP
            
    except Exception:
        # User-Agent 파싱 실패 시 기본값
        return DeviceType.DESKTOP


def extract_client_info(request: Request) -> Tuple[Optional[str], Optional[str], Optional[DeviceType]]:
    """클라이언트 정보 일괄 추출
    
    Returns:
        Tuple[ip_address, user_agent, device_type]
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    device_type = get_device_type(user_agent)
    
    return ip_address, user_agent, device_type