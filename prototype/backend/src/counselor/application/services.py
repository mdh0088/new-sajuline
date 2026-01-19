"""
Counselor 애플리케이션 서비스

상담사 관련 유즈케이스 구현
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from ..domain.entities import (
    CounselorLoginRequest, CounselorLoginResponse, CounselorTokenPair,
    CounselorInfo, SpecialtyInfo
)
from ..domain.services import CounselorValidationService
from ..domain.ports import CounselorRepositoryPort
from ...auth.domain.services import PasswordService
from ...common.services import TokenService
from ...common.services.token_service import TokenType
from ...common.config.settings import get_settings
from ...common.exceptions.custom import (
    AuthenticationException, AccountInactiveException, ValidationException
)


class CounselorAuthApplicationService:
    """상담사 인증 애플리케이션 서비스"""
    
    def __init__(self, counselor_repository: CounselorRepositoryPort) -> None:
        self.counselor_repository: CounselorRepositoryPort = counselor_repository
        self.password_service: PasswordService = PasswordService()
        self.settings = get_settings()
        
        # TokenService 초기화 (공통 모듈 사용)
        self.token_service = TokenService(
            secret_key=self.settings.SECRET_KEY,
            algorithm="HS256",
            access_token_expire_minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    def _create_jwt_token(self, counselor_id: str, email: str, counselor_nickname: str,
                         token_type: str, expires_delta: Optional[timedelta] = None) -> str:
        """상담사용 JWT 토큰 생성 (공통 TokenService 사용)"""
        # TokenType enum 변환
        token_type_enum = TokenType.ACCESS if token_type == "access" else TokenType.REFRESH
        
        # 공통 TokenService를 사용하여 토큰 생성
        return self.token_service.create_jwt_token(
            user_id=counselor_id,
            email=email,
            token_type=token_type_enum,
            role="counselor",  # 상담사 역할 명시
            expires_delta=expires_delta
        )

    def _verify_jwt_token(self, token: str) -> dict:
        """JWT 토큰 검증 (공통 TokenService 사용)"""
        try:
            # 공통 TokenService를 사용하여 토큰 검증
            token_payload = self.token_service.verify_jwt_token(token)
            
            # 상담사 역할 확인
            if token_payload.role != "counselor":
                raise AuthenticationException(message="유효하지 않은 상담사 토큰입니다.")
            
            # dict 형태로 변환하여 반환 (기존 코드와 호환성 유지)
            return {
                "sub": token_payload.sub,
                "email": token_payload.email,
                "role": token_payload.role,
                "exp": token_payload.exp,
                "type": token_payload.type,
                "jti": token_payload.jti
            }
            
        except AuthenticationException:
            raise
        except Exception:
            raise AuthenticationException(message="유효하지 않은 토큰입니다.")

    async def login(self, login_request: CounselorLoginRequest,
                   client_ip: Optional[str] = None,
                   user_agent: Optional[str] = None) -> CounselorLoginResponse:
        """상담사 로그인"""
        # 상담사 조회
        counselor = await self.counselor_repository.get_counselor_by_email(login_request.email)
        if not counselor:
            raise AuthenticationException(message="이메일 또는 비밀번호가 올바르지 않습니다.")
        
        # 비밀번호 검증
        if not self.password_service.verify_password(login_request.password, counselor.password_hash):
            raise AuthenticationException(message="이메일 또는 비밀번호가 올바르지 않습니다.")
        
        # 승인 상태 확인
        if not counselor.is_authorized:
            raise AccountInactiveException(
                message="관리자 승인이 필요한 계정입니다. 승인을 기다려주세요."
            )
        
        # 토큰 생성
        access_token = self._create_jwt_token(
            str(counselor.counselor_id), 
            counselor.email, 
            counselor.counselor_nickname,
            "access"
        )
        refresh_token = self._create_jwt_token(
            str(counselor.counselor_id), 
            counselor.email, 
            counselor.counselor_nickname,
            "refresh"
        )
        
        # 응답 생성
        tokens = CounselorTokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_service.access_token_expire_minutes * 60
        )
        
        # 전문분야 정보 변환
        specialties = [
            SpecialtyInfo(
                specialty_id=str(spec.specialty_id),
                specialty_code=spec.specialty_code,
                specialty_name=spec.specialty_name,
                description=spec.description
            )
            for spec in counselor.specialties
        ]
        
        counselor_info = CounselorInfo(
            counselor_id=str(counselor.counselor_id),
            email=counselor.email,
            counselor_nickname=counselor.counselor_nickname,
            counselor_code=counselor.counselor_code,
            name=counselor.name,
            profile_image_url=counselor.profile_image_url,
            introduction=counselor.introduction or "",
            specialties=specialties,
            price_per_minute=counselor.price_per_minute,
            counselor_status=counselor.counselor_status,
            counselor_status_text=counselor.counselor_status_text,
            is_online=counselor.is_online,
            is_authorized=counselor.is_authorized,
            rating_avg=float(counselor.rating_avg),
            rating_count=counselor.rating_count,
            created_at=counselor.created_at
        )
        
        return CounselorLoginResponse(tokens=tokens, counselor=counselor_info)

    async def get_current_counselor(self, access_token: str) -> CounselorInfo:
        """현재 상담사 정보 조회"""
        # 토큰 검증
        token_payload = self._verify_jwt_token(access_token)
        
        # 상담사 조회
        counselor = await self.counselor_repository.get_counselor_by_id(token_payload["sub"])
        if not counselor:
            raise AuthenticationException(message="상담사를 찾을 수 없습니다.")
        
        # 계정 상태 확인
        if not counselor.is_authorized:
            raise AccountInactiveException(message="승인되지 않은 상담사 계정입니다.")
        
        # 전문분야 정보 변환
        specialties = [
            SpecialtyInfo(
                specialty_id=str(spec.specialty_id),
                specialty_code=spec.specialty_code,
                specialty_name=spec.specialty_name,
                description=spec.description
            )
            for spec in counselor.specialties
        ]
        
        return CounselorInfo(
            counselor_id=str(counselor.counselor_id),
            email=counselor.email,
            counselor_nickname=counselor.counselor_nickname,
            counselor_code=counselor.counselor_code,
            name=counselor.name,
            profile_image_url=counselor.profile_image_url,
            introduction=counselor.introduction or "",
            specialties=specialties,
            price_per_minute=counselor.price_per_minute,
            counselor_status=counselor.counselor_status,
            counselor_status_text=counselor.counselor_status_text,
            is_online=counselor.is_online,
            is_authorized=counselor.is_authorized,
            rating_avg=float(counselor.rating_avg),
            rating_count=counselor.rating_count,
            created_at=counselor.created_at
        )

    async def validate_token(self, token: str) -> Optional[str]:
        """토큰 검증 및 상담사 ID 반환 (간편 버전)"""
        try:
            token_payload = self._verify_jwt_token(token)
            return token_payload["sub"]
        except (AuthenticationException, AccountInactiveException, ValidationException):
            return None 