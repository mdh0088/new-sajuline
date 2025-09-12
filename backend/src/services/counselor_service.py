"""
상담사 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Tuple
from datetime import datetime

from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, AuthenticationError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.counselor_model import Counselor, CounselorStatus
from src.schemas.counselor_schema import CounselorResponse, CounselorMypageUpdate
from sqlalchemy.orm import Session
from src.services.ars.tm60_member_service import Tm60MemberService
from src.repositories.counselor_repository import CounselorRepository
from src.services.auth_service import AuthService


class CounselorService:
    """상담사 비즈니스 로직 서비스"""
    
    def __init__(self, counselor_repo: CounselorRepository, auth_service: AuthService, tm60_member_service: Tm60MemberService | None = None):
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
        self.tm60_member_service = tm60_member_service
    
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

    async def get_mypage_info(self, counselor_id: str) -> CounselorResponse:
        """
        상담사 마이페이지 정보 조회
        - 단일 행 조회 (t_counselor)
        - 제공 필드: 요청 명세에 따른 요약정보
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor mypage info", counselor_id=counselor_id)

        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        response = CounselorResponse.model_validate(counselor)
        log.info("Counselor mypage info retrieved", counselor_id=counselor_id)
        return response

    async def update_mypage(self,
                            counselor_id: str,
                            updates: CounselorMypageUpdate) -> CounselorResponse:
        """마이페이지 부분 업데이트 + 필요 시 MSSQL m_state 동기화"""
        log = get_logger_with_request_id()
        log.info("Updating counselor mypage", counselor_id=counselor_id, updates=updates.model_dump(exclude_none=True))

        # MariaDB 부분 업데이트
        updated = await self.counselor_repo.partial_update(
            counselor_id,
            counselor_status=updates.counselor_status.value if updates.counselor_status is not None else None,
            work_time=updates.work_time,
            introduction_short=updates.introduction_short,
            greeting_message=updates.greeting_message,
            career_info=updates.career_info
        )

        if not updated:
            # 변경할 값이 없으면 그대로 현재 정보 반환
            log.info("No fields to update", counselor_id=counselor_id)
            counselor = await self.counselor_repo.get_by_id(counselor_id)
            if not counselor:
                raise NotFoundError("상담사를 찾을 수 없습니다")
            return CounselorResponse.model_validate(counselor)

        # 상태가 변경된 경우 MSSQL tm60_member.m_state 동기화 (주입된 서비스 사용)
        if updates.counselor_status is not None:
            if self.tm60_member_service is not None:
                await self.tm60_member_service.sync_state_from_counselor_status(counselor_id, updates.counselor_status.value)

        # 최신 데이터 반환
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")
        return CounselorResponse.model_validate(counselor)