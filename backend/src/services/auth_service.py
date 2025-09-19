"""
JWT 기반 공통 인증 서비스 및 의존성
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request, Depends

from src.config.settings import settings
from src.exceptions.custom_exceptions import AuthenticationError, ValidationError
from src.common.logging import get_logger_with_request_id

# 한국 시간대 (UTC+9) 정의
KST = timezone(timedelta(hours=9))


class AuthService:
    """공통 인증 서비스 (JWT 토큰 관리 및 비밀번호 처리)"""
    
    def __init__(self):
        # PHP 호환 bcrypt 설정 (prototype과 동일)
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__default_ident="2y",    # PHP 호환 식별자
            bcrypt__default_rounds=10      # PHP와 동일한 라운드 수
        )
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 비밀번호 검증 오류
        if plain_password == "password_verify_error_test":
            raise ValidationError("Auth service layer: 비밀번호 검증 처리 실패 테스트")
        
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            log.error("Password verification failed", error=str(e))
            raise ValidationError("비밀번호 검증 중 오류가 발생했습니다")
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 비밀번호 해싱 오류
        if password == "password_hash_error_test":
            raise ValidationError("Auth service layer: 비밀번호 해싱 처리 실패 테스트")
        
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            log.error("Password hashing failed", error=str(e))
            raise ValidationError("비밀번호 해싱 중 오류가 발생했습니다")
    
    def create_access_token(self, user_id: str, email: str, role: str = "user") -> str:
        """JWT 액세스 토큰 생성"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 토큰 생성 오류
        if user_id == "token_create_error_test":
            raise ValidationError("Auth service layer: JWT 토큰 생성 실패 테스트")
        
        try:
            now = datetime.now(KST)
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
            
            payload = {
                "sub": user_id,
                "email": email,
                "role": role,
                "exp": int(expire.timestamp()),
                "iat": int(now.timestamp()),
                "jti": str(uuid.uuid4()),
                "token_type": "access"
            }
            
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            log.error("JWT token creation failed", user_id=user_id, email=email, error=str(e))
            raise ValidationError("토큰 생성 중 오류가 발생했습니다")
    
    def create_refresh_token(self, user_id: str, email: str, role: str = "user") -> str:
        """JWT 리프레시 토큰 생성"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 토큰 생성 오류
        if user_id == "refresh_token_create_error_test":
            raise ValidationError("Auth service layer: JWT 리프레시 토큰 생성 실패 테스트")
        
        try:
            now = datetime.now(KST)
            expire = now + timedelta(days=self.refresh_token_expire_days)
            
            payload = {
                "sub": user_id,
                "email": email,
                "role": role,
                "exp": int(expire.timestamp()),
                "iat": int(now.timestamp()),
                "jti": str(uuid.uuid4()),
                "token_type": "refresh"
            }
            
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            log.error("JWT refresh token creation failed", user_id=user_id, email=email, error=str(e))
            raise ValidationError("리프레시 토큰 생성 중 오류가 발생했습니다")
    
    def verify_token(self, token: str) -> Dict[str, any]:
        """JWT 토큰 검증"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 인증 서비스 레이어 오류 발생
        if token == "auth_service_error_test":
            raise AuthenticationError("Auth service layer: JWT 토큰 검증 실패 테스트")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 필수 필드 확인
            if not payload.get("sub") or not payload.get("email"):
                log.warning("Invalid JWT token: missing required fields", 
                           has_sub=bool(payload.get("sub")), 
                           has_email=bool(payload.get("email")))
                raise AuthenticationError("토큰이 유효하지 않습니다")
            
            return payload
            
        except JWTError as jwt_error:
            log.warning("JWT decode failed", error=str(jwt_error))
            raise AuthenticationError("토큰이 유효하지 않습니다")
    
    async def verify_refresh_token(self, token: str, redis_client=None) -> Dict[str, any]:
        """JWT 리프레시 토큰 검증"""
        log = get_logger_with_request_id()
        
        # 테스트용 강제 리프레시 토큰 검증 오류
        if token == "refresh_token_verify_error_test":
            raise AuthenticationError("Auth service layer: 리프레시 토큰 검증 실패 테스트")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 필수 필드 확인
            if not payload.get("sub") or not payload.get("email"):
                log.warning("Invalid refresh token: missing required fields", 
                           has_sub=bool(payload.get("sub")), 
                           has_email=bool(payload.get("email")))
                raise AuthenticationError("리프레시 토큰이 유효하지 않습니다")
            
            # 토큰 타입 확인
            if payload.get("token_type") != "refresh":
                log.warning("Invalid token type for refresh", token_type=payload.get("token_type"))
                raise AuthenticationError("리프레시 토큰이 아닙니다")
            
            # 블랙리스트 확인
            if redis_client:
                jti = payload.get("jti")
                if jti and await self.is_token_blacklisted(jti, redis_client):
                    log.warning("Blacklisted refresh token used", jti=jti)
                    raise AuthenticationError("이미 사용된 토큰입니다")
            
            return payload
            
        except JWTError as jwt_error:
            log.warning("Refresh token decode failed", error=str(jwt_error))
            raise AuthenticationError("리프레시 토큰이 유효하지 않습니다")
    
    async def blacklist_token(self, jti: str, expires_at: datetime, redis_client):
        """
        토큰 블랙리스트 등록 - 보안을 위한 토큰 무효화
        
        목적:
        - 토큰 갱신시: 기존 refresh token 재사용 방지
        - 로그아웃시: 현재 토큰들 무효화로 보안 강화
        - 보안 사고시: 특정 토큰 즉시 무효화
        
        JWT는 무상태(stateless)라 서버에서 직접 취소 불가하므로
        Redis 블랙리스트로 탈취된 토큰의 지속적 사용을 차단
        """
        log = get_logger_with_request_id()
        
        try:
            # TTL 계산 (만료 시간까지 남은 시간)
            ttl = int((expires_at - datetime.now(KST)).total_seconds())
            if ttl > 0:
                # Redis에 블랙리스트 등록 (TTL 설정으로 자동 만료)
                await redis_client.setex(f"blacklist:{jti}", ttl, "1")
                log.info("Token blacklisted", jti=jti, ttl=ttl)
        except Exception as e:
            log.error("Failed to blacklist token", jti=jti, error=str(e))
            # 블랙리스트 실패해도 예외 발생 안함 (서비스 연속성)
    
    async def is_token_blacklisted(self, jti: str, redis_client) -> bool:
        """토큰 블랙리스트 확인 - 무효화된 토큰 사용 차단"""
        try:
            result = await redis_client.get(f"blacklist:{jti}")
            return result is not None
        except Exception:
            # Redis 연결 실패시 false 반환 (서비스 연속성)
            return False


# JWT 인증 관련 스키마 (임시로 여기에 정의)
class TokenPayload:
    """JWT 토큰 페이로드"""
    def __init__(self, sub: str, email: str, role: str, exp: int, iat: int, jti: str):
        self.sub = sub
        self.email = email
        self.role = role
        self.exp = exp
        self.iat = iat
        self.jti = jti


# 의존성 함수들
def get_auth_service() -> AuthService:
    """AuthService 의존성"""
    return AuthService()


async def get_current_user_optional(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[TokenPayload]:
    """
    선택적 사용자 인증 (인증되지 않아도 오류 발생 안함)
    
    목적: 로그인하지 않아도 접근할 수 있지만, 로그인한 사용자에게는 추가 기능을 제공하는 API에 사용
    
    사용 예시:
    - 메인 페이지: 로그인 안해도 볼 수 있지만, 로그인하면 개인화된 운세 표시
    - 상품 목록: 누구나 볼 수 있지만, 로그인하면 찜한 상품 표시
    - 게시글 목록: 누구나 볼 수 있지만, 로그인하면 내가 쓴 글 하이라이트
    
    실제 사용법:
    @router.get("/fortune/daily")
    async def get_daily_fortune(
        current_user: Optional[TokenPayload] = Depends(get_current_user_optional)
    ):
        if current_user:
            return get_personalized_fortune(current_user.sub)
        else:
            return get_general_fortune()
    
    HttpOnly 쿠키에서 JWT 토큰을 읽어서 검증하되, 토큰이 없거나 유효하지 않아도 None 반환
    """
    try:
        # HttpOnly 쿠키에서 access_token 읽기
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            return None
        
        # JWT 토큰 검증
        payload = auth_service.verify_token(access_token)
        
        return TokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            role=payload.get("role", "user"),
            exp=payload["exp"],
            iat=payload["iat"],
            jti=payload["jti"]
        )
        
    except Exception:
        # 토큰이 유효하지 않아도 None 반환 (오류 발생 안함)
        return None


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenPayload:
    """
    필수 사용자 인증 (인증되지 않으면 401 오류 발생)
    
    목적: 반드시 로그인해야만 접근할 수 있는 API에 사용
    
    사용 예시:
    - 마이페이지
    - 포인트 충전  
    - 상담 예약
    - 개인정보 수정
    
    실제 사용법:
    @router.get("/mypage")
    async def get_mypage(
        current_user: TokenPayload = Depends(get_current_user)  # 로그인 안하면 401 에러
    ):
        return get_user_data(current_user.sub)
    
    HttpOnly 쿠키에서 JWT 토큰을 읽어서 검증하고, 토큰이 없거나 유효하지 않으면 401 에러 발생
    """
    try:
        # HttpOnly 쿠키에서 access_token 읽기
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 없습니다"
            )
        
        # JWT 토큰 검증
        payload = auth_service.verify_token(access_token)
        
        return TokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            role=payload.get("role", "user"),
            exp=payload["exp"],
            iat=payload["iat"],
            jti=payload["jti"]
        )
        
    except HTTPException:
        # HTTPException은 그대로 다시 발생
        raise
    except Exception:
        # 다른 예외는 401 에러로 변환
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다"
        )