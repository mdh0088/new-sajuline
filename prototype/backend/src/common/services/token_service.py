"""
공통 JWT 토큰 서비스

모든 도메인에서 사용할 수 있는 통합 토큰 관리 서비스
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from enum import Enum

from pydantic import BaseModel
from jose import jwt, JWTError

from ..exceptions.custom import AuthenticationException


class TokenType(str, Enum):
    """토큰 타입"""
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    """토큰 페이로드"""
    sub: str  # user_id 또는 counselor_id
    email: str
    type: str  # token type
    exp: int  # expiration
    jti: str  # JWT ID
    role: Optional[str] = None  # user, counselor, admin 등


class TokenService:
    """토큰 관련 서비스"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 access_token_expire_minutes: int = 30,
                 refresh_token_expire_days: int = 7):
        """토큰 서비스 초기화
        
        Args:
            secret_key: JWT 시크릿 키
            algorithm: JWT 알고리즘 (기본값: HS256)
            access_token_expire_minutes: 액세스 토큰 만료 시간 (분)
            refresh_token_expire_days: 리프레시 토큰 만료 시간 (일)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_jwt_token(self, 
                        user_id: str, 
                        email: str, 
                        token_type: TokenType,
                        role: Optional[str] = None,
                        expires_delta: Optional[timedelta] = None) -> str:
        """JWT 토큰 생성
        
        Args:
            user_id: 사용자 ID
            email: 사용자 이메일
            token_type: 토큰 타입 (ACCESS 또는 REFRESH)
            role: 사용자 역할 (user, counselor, admin)
            expires_delta: 만료 시간 (미지정시 기본값 사용)
        
        Returns:
            생성된 JWT 토큰 문자열
        """
        now = datetime.utcnow()
        
        if expires_delta:
            expire = now + expires_delta
        elif token_type == TokenType.ACCESS:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        else:
            expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "email": email,
            "type": token_type.value,
            "exp": expire,
            "iat": now,
            "jti": self.generate_jti()
        }
        
        if role:
            payload["role"] = role
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_jwt_token(self, token: str, expected_type: Optional[TokenType] = None) -> TokenPayload:
        """JWT 토큰 검증
        
        Args:
            token: 검증할 JWT 토큰
            expected_type: 예상 토큰 타입 (선택사항)
        
        Returns:
            TokenPayload: 검증된 토큰 페이로드
        
        Raises:
            AuthenticationException: 토큰이 유효하지 않은 경우
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 필수 필드 확인
            required_fields = ["sub", "email", "type", "exp", "jti"]
            for field in required_fields:
                if field not in payload:
                    raise AuthenticationException(message=f"토큰에 필수 필드가 없습니다: {field}")
            
            # 토큰 타입 확인
            if expected_type and payload["type"] != expected_type.value:
                raise AuthenticationException(message="올바르지 않은 토큰 타입입니다.")
            
            # TokenPayload 객체 생성
            return TokenPayload(
                sub=payload["sub"],
                email=payload["email"],
                type=payload["type"],
                exp=payload["exp"],
                jti=payload["jti"],
                role=payload.get("role")
            )
            
        except JWTError:
            raise AuthenticationException(message="유효하지 않은 토큰입니다.")
    
    def create_token_pair(self, user_id: str, email: str, role: Optional[str] = None) -> Tuple[str, str]:
        """액세스 토큰과 리프레시 토큰 쌍 생성
        
        Args:
            user_id: 사용자 ID
            email: 사용자 이메일
            role: 사용자 역할
        
        Returns:
            Tuple[액세스 토큰, 리프레시 토큰]
        """
        access_token = self.create_jwt_token(user_id, email, TokenType.ACCESS, role)
        refresh_token = self.create_jwt_token(user_id, email, TokenType.REFRESH, role)
        return access_token, refresh_token
    
    @staticmethod
    def generate_user_id() -> str:
        """고유한 사용자 ID 생성"""
        return f"user_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_counselor_id() -> str:
        """고유한 상담사 ID 생성"""
        return f"counselor_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_session_id() -> str:
        """세션 ID 생성"""
        return f"sess_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_jti() -> str:
        """JWT ID 생성"""
        return uuid.uuid4().hex
    
    @staticmethod
    def generate_verification_token() -> str:
        """이메일 인증 토큰 생성"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token() -> str:
        """비밀번호 재설정 토큰 생성"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """토큰 해시화 (저장용)"""
        return hashlib.sha256(token.encode()).hexdigest()