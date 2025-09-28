"""
상담사 상태 변경 서비스 (관리자 백엔드)
- 요청 검증
- t_counselor 존재/코드 일치 확인
- MSSQL tm60_member.m_state 동기화 (m_code 매칭)
"""
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.counselor_repository import CounselorRepository
from src.services.ars.tm60_member_service import Tm60MemberService
from src.schemas.counselor_schema import CounselorStateUpdateRequest, CounselorStateUpdateResponse
from src.exceptions.custom_exceptions import ValidationError, NotFoundError


class CounselorStatusService:
    def __init__(self, db: AsyncSession, tm60_member_service_factory):
        self.db = db
        self.counselor_repo = CounselorRepository(db)
        # tm60_member_service_factory: Callable[[], Tm60MemberService]
        self.tm60_member_service_factory = tm60_member_service_factory

    async def update_state(self, payload: CounselorStateUpdateRequest) -> CounselorStateUpdateResponse:
        # 1) 기본 검증
        if payload.m_state not in {"1", "2", "3"}:
            raise ValidationError("m_state는 '1','2','3' 중 하나여야 합니다")

        # 2) 상담사 존재 및 코드 일치 확인 (MariaDB)
        counselor = await self.counselor_repo.get_by_id(payload.counselor_id)
        if not counselor:
            raise NotFoundError("상담사를 찾을 수 없습니다")

        if not counselor.counselor_code:
            raise ValidationError("상담사 코드가 설정되어 있지 않습니다")

        if counselor.counselor_code != payload.counselor_code:
            raise ValidationError("요청 counselor_code가 시스템 정보와 일치하지 않습니다")

        # 3) MSSQL tm60_member.m_code 매칭 후 m_state 업데이트
        tm60_service: Tm60MemberService = self.tm60_member_service_factory()
        updated = tm60_service.update_state_by_code(m_code=payload.counselor_code, m_state=payload.m_state)

        return CounselorStateUpdateResponse(
            counselor_id=payload.counselor_id,
            counselor_code=payload.counselor_code,
            m_state=payload.m_state,
            updated=bool(updated),
        )


