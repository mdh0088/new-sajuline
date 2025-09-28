"""
JWT 기반 인증 서비스 (관리자 백엔드)
Redis 미사용. HttpOnly 쿠키 기반 액세스/리프레시 토큰 처리.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from src.config.settings import settings
from src.exceptions.custom_exceptions import AuthenticationError, ValidationError


class AuthService:
    """공통 인증 서비스"""

    def __init__(self) -> None:
        # backend 상담사 로그인과 동일한 설정 (PHP 호환 bcrypt 2y, cost=10)
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__default_ident="2y",
            bcrypt__default_rounds=10,
        )
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            raise ValidationError("비밀번호 검증 중 오류가 발생했습니다") from e

    def hash_password(self, password: str) -> str:
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            raise ValidationError("비밀번호 해싱 중 오류가 발생했습니다") from e

    def _create_token(self, *, user_id: str, email: str, role: str, expires_delta: timedelta, token_type: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
            "jti": uuid.uuid4().hex,
            "token_type": token_type,
        }
        try:
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            raise ValidationError("토큰 생성 중 오류가 발생했습니다") from e

    def create_access_token(self, *, user_id: str, email: str, role: str) -> str:
        return self._create_token(
            user_id=user_id,
            email=email,
            role=role,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
            token_type="access",
        )

    def create_refresh_token(self, *, user_id: str, email: str, role: str) -> str:
        return self._create_token(
            user_id=user_id,
            email=email,
            role=role,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
            token_type="refresh",
        )

    def verify_token(self, token: str) -> Dict[str, any]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            raise AuthenticationError("토큰이 유효하지 않습니다") from e


