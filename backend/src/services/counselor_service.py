"""
상담사 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Tuple
from datetime import datetime

from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, AuthenticationError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.counselor_model import Counselor, CounselorStatus
from src.schemas.counselor_schema import CounselorResponse
from src.repositories.counselor_repository import CounselorRepository
from src.services.auth_service import AuthService


class CounselorService:
    """상담사 비즈니스 로직 서비스"""
    
    def __init__(self, counselor_repo: CounselorRepository, auth_service: AuthService):
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
    
    async def authenticate_counselor(self, counselor_id: str, password: str) -> CounselorResponse:
        """
        상담사 인증 비즈니스 로직
        - 상담사 ID로 조회 (이메일 기반)
        - 비밀번호 검증
        - 계정 활성화 및 승인 상태 확인
        """
        # 상담사 조회
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        
        if not counselor:
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")
        
        # 탈퇴 여부 확인
        if counselor.is_out == "Y":
            raise AuthenticationError("탈퇴한 상담사 계정입니다")
        
        # 승인 상태 확인 (approved_at이 있으면 승인됨)
        if counselor.approved_at is None:
            raise AuthenticationError("승인되지 않은 상담사 계정입니다")
        
        # 비밀번호 검증
        if not counselor.password_hash or not self.auth_service.verify_password(password, counselor.password_hash):
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")
        
        return CounselorResponse.model_validate(counselor)
    
    async def login(self, counselor_id: str, password: str) -> Tuple[str, CounselorResponse]:
        """
        상담사 로그인 비즈니스 로직
        - 상담사 인증
        - JWT 토큰 생성
        - 마지막 로그인 시간 업데이트
        """
        log = get_logger_with_request_id()
        log.info("Counselor login attempt", counselor_id=counselor_id)
        
        # 상담사 인증
        try:
            counselor_response = await self.authenticate_counselor(counselor_id, password)
        except AuthenticationError as auth_error:
            log.warning("Counselor authentication failed", counselor_id=counselor_id, reason=str(auth_error))
            raise  # 원래 예외 다시 발생
        
        # JWT 토큰 생성
        access_token = self.auth_service.create_access_token(
            user_id=counselor_response.counselor_id,
            email=counselor_response.counselor_id,  # counselor_id는 이메일 기반
            role="counselor"
        )
        
        # 마지막 로그인 시간 업데이트
        await self.counselor_repo.update_last_login(counselor_response.counselor_id)
        
        log.info("Counselor login successful", counselor_id=counselor_response.counselor_id)
        return access_token, counselor_response