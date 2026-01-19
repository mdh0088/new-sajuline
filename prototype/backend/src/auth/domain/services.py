"""
Auth 도메인 서비스
인증과 관련된 순수 비즈니스 로직
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any

from passlib.context import CryptContext

from .entities import AuthProvider, AuthenticatedUser
from ...common.services.token_service import TokenType, TokenPayload, TokenService


class PasswordService:
    """비밀번호 관련 서비스"""
    
    def __init__(self) -> None:
        # PHP 호환 bcrypt 설정 (기존 $2y$10$ 형태와 동일)
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__default_ident="2y",    # PHP 호환 식별자
            bcrypt__default_rounds=10      # PHP와 동일한 라운드 수
        )
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_password(self, length: int = 12) -> str:
        """안전한 임시 비밀번호 생성"""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """비밀번호 강도 검증"""
        errors = []
        
        if len(password) < 8:
            errors.append("비밀번호는 최소 8자 이상이어야 합니다.")
        
        if len(password) > 128:
            errors.append("비밀번호는 최대 128자 이하여야 합니다.")
        
        if not any(c.islower() for c in password):
            errors.append("소문자를 포함해야 합니다.")
        
        if not any(c.isupper() for c in password):
            errors.append("대문자를 포함해야 합니다.")
        
        if not any(c.isdigit() for c in password):
            errors.append("숫자를 포함해야 합니다.")
        
        # 특수문자 검사
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("특수문자를 포함해야 합니다.")
        
        return len(errors) == 0, errors


# TokenService는 common.services로 이동됨 - 임포트만 유지


class AuthValidationService:
    """인증 검증 서비스"""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """이메일 형식 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """전화번호 형식 검증"""
        import re
        pattern = r'^01[0-9]{8,9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_terms_agreement(agree_terms: bool, agree_privacy: bool) -> bool:
        """필수 약관 동의 검증"""
        return agree_terms and agree_privacy
    
    @staticmethod
    def is_account_locked(failed_attempts: int, last_failed_at: Optional[datetime] = None) -> bool:
        """계정 잠금 여부 확인"""
        MAX_FAILED_ATTEMPTS = 5
        LOCKOUT_DURATION = timedelta(minutes=30)
        
        if failed_attempts < MAX_FAILED_ATTEMPTS:
            return False
        
        if last_failed_at is None:
            return True
        
        return datetime.utcnow() - last_failed_at < LOCKOUT_DURATION
    
    @staticmethod
    def should_reset_failed_attempts(last_failed_at: Optional[datetime]) -> bool:
        """실패 횟수 리셋 여부 확인"""
        RESET_DURATION = timedelta(hours=24)
        
        if last_failed_at is None:
            return False
        
        return datetime.utcnow() - last_failed_at > RESET_DURATION


class AuthSessionService:
    """인증 세션 관리 서비스"""
    
    @staticmethod
    def create_session_info(user_id: str, device_info: Optional[str] = None, 
                          ip_address: Optional[str] = None, 
                          user_agent: Optional[str] = None) -> dict:
        """세션 정보 생성"""
        now = datetime.utcnow()
        return {
            "session_id": f"sess_{uuid.uuid4().hex[:16]}",  # 세션 ID 생성
            "user_id": user_id,
            "device_info": device_info,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now,
            "last_accessed_at": now,
            "expires_at": now + timedelta(days=30),  # 30일 후 만료
            "is_active": True
        }
    
    @staticmethod
    def is_session_valid(created_at: datetime, last_accessed_at: datetime, 
                        expires_at: Optional[datetime] = None) -> bool:
        """세션 유효성 검사"""
        now = datetime.utcnow()
        
        # 만료 시간 확인
        if expires_at and now > expires_at:
            return False
        
        # 비활성 시간 확인 (7일 동안 미접속시 만료)
        INACTIVE_DURATION = timedelta(days=7)
        if now - last_accessed_at > INACTIVE_DURATION:
            return False
        
        return True
    
    @staticmethod
    def extract_device_info(user_agent: Optional[str]) -> Optional[str]:
        """User-Agent에서 디바이스 정보 추출"""
        if not user_agent:
            return None
        
        user_agent_lower = user_agent.lower()
        
        # 모바일 디바이스 감지
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        if any(keyword in user_agent_lower for keyword in mobile_keywords):
            if 'android' in user_agent_lower:
                return "Android Mobile"
            elif 'iphone' in user_agent_lower:
                return "iPhone"
            elif 'ipad' in user_agent_lower:
                return "iPad"
            else:
                return "Mobile Device"
        
        # 데스크탑 브라우저 감지
        browser_keywords = {
            'chrome': 'Chrome',
            'firefox': 'Firefox',
            'safari': 'Safari',
            'edge': 'Edge',
            'opera': 'Opera'
        }
        
        for keyword, browser_name in browser_keywords.items():
            if keyword in user_agent_lower:
                return f"Desktop {browser_name}"
        
        return "Desktop Browser"


class SocialAuthService:
    """소셜 인증 서비스"""
    
    @staticmethod
    def generate_social_user_id(provider: AuthProvider, social_id: str) -> str:
        """소셜 로그인용 사용자 ID 생성"""
        hash_input = f"{provider.value}:{social_id}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        return f"social_{hash_value}"
    
    @staticmethod
    def validate_social_token(provider: AuthProvider, access_token: str) -> bool:
        """소셜 토큰 유효성 검증 (외부 API 호출 전 기본 검증)"""
        if not access_token or len(access_token) < 10:
            return False
        
        # 제공자별 토큰 형식 기본 검증
        if provider == AuthProvider.KAKAO:
            return access_token.startswith(('Bearer ', 'token ')) or len(access_token) > 20
        elif provider == AuthProvider.NAVER:
            return len(access_token) > 30
        elif provider == AuthProvider.GOOGLE:
            return access_token.startswith('ya29.') or len(access_token) > 50
        
        return True
    
    @staticmethod
    def extract_user_info_from_social_response(provider: AuthProvider, 
                                             social_data: dict) -> dict:
        """소셜 로그인 응답에서 사용자 정보 추출"""
        extracted_info = {
            "social_id": None,
            "email": None,
            "name": None,
            "profile_image": None
        }
        
        if provider == AuthProvider.KAKAO:
            kakao_account = social_data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            
            extracted_info.update({
                "social_id": str(social_data.get("id", "")),
                "email": kakao_account.get("email"),
                "name": profile.get("nickname"),
                "profile_image": profile.get("profile_image_url")
            })
        
        elif provider == AuthProvider.NAVER:
            response = social_data.get("response", {})
            extracted_info.update({
                "social_id": response.get("id"),
                "email": response.get("email"),
                "name": response.get("name") or response.get("nickname"),
                "profile_image": response.get("profile_image")
            })
        
        elif provider == AuthProvider.GOOGLE:
            extracted_info.update({
                "social_id": social_data.get("sub") or social_data.get("id"),
                "email": social_data.get("email"),
                "name": social_data.get("name"),
                "profile_image": social_data.get("picture")
            })
        
        return extracted_info 