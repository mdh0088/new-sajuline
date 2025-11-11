"""
상담사 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Tuple, Optional, List
from datetime import datetime
import random

from src.exceptions.custom_exceptions import NotFoundError, DuplicateError, AuthenticationError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.counselor_model import Counselor, CounselorStatus
from src.schemas.counselor_schema import CounselorResponse, CounselorMypageUpdate
from sqlalchemy.orm import Session
from src.services.ars.tm60_member_service import Tm60MemberService
from src.repositories.counselor_repository import CounselorRepository
from src.services.auth_service import AuthService
from src.repositories.consultation_review_repository import ConsultationReviewRepository


class CounselorService:
    """상담사 비즈니스 로직 서비스"""
    
    def __init__(self, counselor_repo: CounselorRepository, auth_service: AuthService, tm60_member_service: Tm60MemberService | None = None, review_repo: ConsultationReviewRepository | None = None):
        self.counselor_repo = counselor_repo
        self.auth_service = auth_service
        self.tm60_member_service = tm60_member_service
        self.review_repo = review_repo
    
    async def authenticate_counselor(self, nickname: str, password: str) -> CounselorResponse:
        """
        상담사 인증 비즈니스 로직
        - 상담사 닉네임으로 조회
        - 비밀번호 검증
        - 계정 활성화 및 승인 상태 확인
        """
        log = get_logger_with_request_id()

        # 상담사 조회 (닉네임으로만 조회)
        counselor = await self.counselor_repo.get_by_nickname(nickname)

        if not counselor:
            log.warning("Counselor not found", nickname=nickname)
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        log.info("Counselor found", counselor_id=counselor.counselor_id, is_out=counselor.is_out, approved_at=counselor.approved_at)

        # 탈퇴 여부 확인 (Boolean 타입)
        if counselor.is_out:
            log.warning("Counselor is out", counselor_id=counselor.counselor_id)
            raise AuthenticationError("탈퇴한 상담사 계정입니다")

        # 승인 상태 확인 (approved_at이 있으면 승인됨)
        if counselor.approved_at is None:
            log.warning("Counselor not approved", counselor_id=counselor.counselor_id)
            raise AuthenticationError("승인되지 않은 상담사 계정입니다")

        # 비밀번호 검증
        if not counselor.password_hash:
            log.warning("Counselor has no password hash", counselor_id=counselor.counselor_id)
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        if not self.auth_service.verify_password(password, counselor.password_hash):
            log.warning("Password verification failed", counselor_id=counselor.counselor_id)
            raise AuthenticationError("아이디 또는 비밀번호가 올바르지 않습니다")

        log.info("Counselor authenticated successfully", counselor_id=counselor.counselor_id)
        return CounselorResponse.model_validate(counselor)

    async def search_public(
        self,
        *,
        page: int,
        limit: int,
        cs_status: Optional[str] = None,
        is_best: Optional[bool] = None,
        is_new: Optional[bool] = None,
        cs_specialties: Optional[List[str]] = None,
        cs_keywords: Optional[List[str]] = None,
        search_name: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """공개 상담사 검색 서비스 (게스트)"""
        # 1) t_counselor 필터로 사전 코드 목록 수집
        code_id_rows = await self.counselor_repo.find_codes_by_filters(
            is_best=is_best,
            is_new=is_new,
            cs_specialties=cs_specialties,
            cs_keywords=cs_keywords,
            search_name=search_name,
        )
        if not code_id_rows:
            return [], 0

        all_codes = [row["counselor_code"] for row in code_id_rows]

        # 2) TM60 상태 매핑 (필터 적용)
        state_map: dict[str, str] = {}
        if self.tm60_member_service is not None:
            state_map = await self.tm60_member_service.get_state_map_by_codes(all_codes, m_state=cs_status)

        # cs_status 지정 시 해당 상태 코드만
        filtered_codes = [c for c in all_codes if (c in state_map)] if cs_status is not None else all_codes
        if not filtered_codes:
            return [], 0

        # 랜덤 셔플: 매 호출마다 다른 순서로 노출 (필터 내에서만 랜덤)
        random.shuffle(filtered_codes)

        total = len(filtered_codes)
        start = max(0, (page - 1) * limit)
        end = min(total, start + limit)
        page_codes = filtered_codes[start:end]

        code_to_counselor = await self.counselor_repo.get_by_counselor_codes(page_codes)

        # 3) 리뷰 카운트/평균
        from json import loads
        items: list[dict] = []
        for code in page_codes:
            c = code_to_counselor.get(code)
            if not c:
                continue
            avg_rating = 0.0
            review_count = 0
            if self.review_repo is not None:
                avg_rating = await self.review_repo.get_average_rating_by_counselor_id(c.counselor_id, visible_only=True)
                review_count = await self.review_repo.get_count_by_counselor_id(c.counselor_id, is_visible=True)
            # specialty_types 파싱
            sp_list = None
            try:
                if isinstance(c.specialty_types, str) and c.specialty_types:
                    parsed = loads(c.specialty_types)
                    if isinstance(parsed, list):
                        sp_list = [x for x in parsed if x]
            except Exception:
                sp_list = None
            items.append({
                "counselor_id": c.counselor_id,
                "counselor_code": c.counselor_code,
                "nickname": c.nickname,
                "profile_image_url": c.profile_image_url,
                "introduction_short": c.introduction_short,
                "specialty_types": sp_list,
                "keywords": c.keywords,
                "after_amount": c.after_amount,
                "rating_avg": avg_rating,
                "review_count": review_count,
                "m_state": state_map.get(code) if state_map else None,
            })
        return items, total
    
    async def login(self, nickname: str, password: str) -> Tuple[str, CounselorResponse]:
        """
        상담사 로그인 비즈니스 로직
        - 상담사 인증 (닉네임)
        - JWT 토큰 생성
        - 마지막 로그인 시간 업데이트
        """
        log = get_logger_with_request_id()
        log.info("Counselor login attempt", nickname=nickname)

        # 상담사 인증
        try:
            counselor_response = await self.authenticate_counselor(nickname, password)
        except AuthenticationError as auth_error:
            log.warning("Counselor authentication failed", nickname=nickname, reason=str(auth_error))
            raise  # 원래 예외 다시 발생

        # JWT 토큰 생성
        access_token = self.auth_service.create_access_token(
            user_id=counselor_response.counselor_id,
            email=counselor_response.counselor_id,  # counselor_id는 이메일 기반
            role="counselor"
        )

        # 마지막 로그인 시간 업데이트
        await self.counselor_repo.update_last_login(counselor_response.counselor_id)

        log.info("Counselor login successful", counselor_id=counselor_response.counselor_id, nickname=counselor_response.nickname)
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