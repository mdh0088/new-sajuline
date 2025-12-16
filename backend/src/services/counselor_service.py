"""
상담사 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Tuple, Optional, List
from datetime import datetime

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

        # 상태별 정렬: 상담중(2) → 대기중(1) → 부재중(3) 순서
        status_priority = {'2': 0, '1': 1, '3': 2}
        filtered_codes.sort(key=lambda c: status_priority.get(state_map.get(c, '3'), 3))

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
        - tm60_member.m_state 조회 (counselor_code = m_code)
        - 제공 필드: 요청 명세에 따른 요약정보
        """
        log = get_logger_with_request_id()
        log.info("Getting counselor mypage info", counselor_id=counselor_id)

        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        response = CounselorResponse.model_validate(counselor)

        # tm60_member.m_state 조회 (counselor_code = m_code)
        if self.tm60_member_service and counselor.counselor_code:
            m_state = await self.tm60_member_service.get_state_by_code(counselor.counselor_code)
            response.m_state = m_state
            log.info("tm60_member m_state retrieved", counselor_code=counselor.counselor_code, m_state=m_state)

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
            response = CounselorResponse.model_validate(counselor)
            # m_state 조회
            if self.tm60_member_service and counselor.counselor_code:
                response.m_state = await self.tm60_member_service.get_state_by_code(counselor.counselor_code)
            return response

        # 최신 데이터 반환
        counselor = await self.counselor_repo.get_by_id(counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        # 상태가 변경된 경우 MSSQL tm60_member.m_state 동기화 (counselor_code = m_code)
        if updates.counselor_status is not None:
            if self.tm60_member_service is not None and counselor.counselor_code:
                await self.tm60_member_service.sync_state_from_counselor_status(
                    counselor.counselor_code, updates.counselor_status.value
                )

        response = CounselorResponse.model_validate(counselor)
        # m_state 조회
        if self.tm60_member_service and counselor.counselor_code:
            response.m_state = await self.tm60_member_service.get_state_by_code(counselor.counselor_code)
        return response

    async def sync_all_counselor_status(self, notification_wait_service) -> dict:
        """
        전체 상담사 상태 동기화 (tm60_member → t_counselor)
        1. tm60_member에서 전체 m_code, m_state 조회
        2. 각 m_code로 t_counselor.counselor_code 매칭
        3. counselor_status 업데이트 (m_state: 1=WAITING, 2=CONSULTING, 3=ABSENT)
        4. WAITING으로 변경된 상담사에 대해 알림 발송 처리
        """
        log = get_logger_with_request_id()
        log.info("Starting counselor status sync")

        result = {
            "total_members": 0,
            "updated_count": 0,
            "notification_sent_count": 0,
            "errors": []
        }

        if not self.tm60_member_service:
            log.warning("tm60_member_service is not available")
            return result

        # 1. MSSQL에서 전체 tm60_member 상태 조회
        members = await self.tm60_member_service.get_all_members_state()
        result["total_members"] = len(members)

        if not members:
            log.info("No tm60_members found")
            return result

        # 2. 각 멤버에 대해 상태 동기화
        for member in members:
            m_code = member.get("m_code")
            m_state = member.get("m_state")

            if not m_code or not m_state:
                continue

            # m_state → counselor_status 매핑
            # m_state: 1=대기중(WAITING), 2=상담중(CONSULTING), 3=부재중(ABSENT)
            if m_state == "1":
                new_status = "WAITING"
            elif m_state == "2":
                new_status = "CONSULTING"
            elif m_state == "3":
                new_status = "ABSENT"
            else:
                log.warning("Unknown m_state value", m_code=m_code, m_state=m_state)
                continue

            try:
                # 상태 업데이트 (이전 상태도 반환)
                success, old_status = await self.counselor_repo.update_status_by_code(
                    counselor_code=m_code,
                    new_status=new_status
                )

                if not success:
                    continue

                # 실제 변경이 있는 경우만 카운트
                if old_status != new_status:
                    result["updated_count"] += 1
                    log.info(
                        "Counselor status updated",
                        m_code=m_code,
                        old_status=old_status,
                        new_status=new_status
                    )

                    # 3. WAITING으로 변경된 경우 알림 발송 처리 (별도 try-except로 분리)
                    if new_status == "WAITING" and old_status in ("ABSENT", "CONSULTING"):
                        try:
                            counselor_id = await self.counselor_repo.get_counselor_id_by_code(m_code)
                            if counselor_id:
                                sent_count = await notification_wait_service.send_notifications_for_counselor(
                                    counselor_id
                                )
                                result["notification_sent_count"] += sent_count
                                log.info(
                                    "Notifications sent for counselor",
                                    counselor_id=counselor_id,
                                    sent_count=sent_count
                                )
                        except Exception as notify_err:
                            log.warning(
                                "Failed to send notifications but status update succeeded",
                                m_code=m_code,
                                error=str(notify_err)
                            )

            except Exception as e:
                error_msg = f"Failed to sync status for m_code={m_code}: {str(e)}"
                result["errors"].append(error_msg)
                log.error(error_msg)

        # 커밋
        await self.counselor_repo.db.commit()

        log.info(
            "Counselor status sync completed",
            total_members=result["total_members"],
            updated_count=result["updated_count"],
            notification_sent_count=result["notification_sent_count"],
            error_count=len(result["errors"])
        )

        return result