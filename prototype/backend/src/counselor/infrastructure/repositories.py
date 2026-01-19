"""
Counselor 인프라스트럭처 리포지토리

상담사 관련 데이터 접근 구현
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from ..domain.models import Counselor, CounselorSpecialty
from ..domain.entities import CounselorEntity, CounselorSpecialtyEntity
from ..domain.ports import CounselorRepositoryPort as ICounselorRepositoryPort
from ...common.exceptions.custom import DatabaseError


# Deprecated ABC 제거 (Protocol로 대체)


class MariaDBCounselorRepository(ICounselorRepositoryPort):
    """MariaDB Counselor 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_counselor_by_email(self, email: str) -> Optional[CounselorEntity]:
        """이메일로 상담사 조회 (전문분야 포함)"""
        try:
            result = await self.session.execute(
                select(Counselor)
                .options(selectinload(Counselor.specialties))
                .where(Counselor.email == email)
            )
            orm_obj = result.scalar_one_or_none()
            return self._to_entity(orm_obj) if orm_obj else None
        except SQLAlchemyError as e:
            # 테이블 존재하지 않음 오류 처리
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            # 기타 데이터베이스 오류
            raise DatabaseError("상담사 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    async def get_counselor_by_id(self, counselor_id: str) -> Optional[CounselorEntity]:
        """ID로 상담사 조회 (전문분야 포함)"""
        try:
            result = await self.session.execute(
                select(Counselor)
                .options(selectinload(Counselor.specialties))
                .where(Counselor.counselor_id == counselor_id)
            )
            orm_obj = result.scalar_one_or_none()
            return self._to_entity(orm_obj) if orm_obj else None
        except SQLAlchemyError as e:
            # 테이블 존재하지 않음 오류 처리
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            # 기타 데이터베이스 오류
            raise DatabaseError("상담사 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    async def get_counselor_by_code(self, counselor_code: str) -> Optional[CounselorEntity]:
        """코드로 상담사 조회"""
        try:
            result = await self.session.execute(
                select(Counselor)
                .options(selectinload(Counselor.specialties))
                .where(Counselor.counselor_code == counselor_code)
            )
            orm_obj = result.scalar_one_or_none()
            return self._to_entity(orm_obj) if orm_obj else None
        except SQLAlchemyError as e:
            # 테이블 존재하지 않음 오류 처리
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            # 기타 데이터베이스 오류
            raise DatabaseError("상담사 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    async def get_counselor_by_nickname(self, nickname: str) -> Optional[CounselorEntity]:
        """닉네임으로 상담사 조회"""
        try:
            result = await self.session.execute(
                select(Counselor)
                .options(selectinload(Counselor.specialties))
                .where(Counselor.nickname == nickname)
            )
            orm_obj = result.scalar_one_or_none()
            return self._to_entity(orm_obj) if orm_obj else None
        except SQLAlchemyError as e:
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            raise DatabaseError("상담사 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    async def get_active_specialties(self) -> List[dict]:
        """활성 전문분야 목록 조회 (MariaDB 실제 구조 - 코드 기반)"""
        try:
            # MariaDB에서는 specialty가 별도 테이블이 아니라 CounselorSpecialty에 직접 저장됨
            from src.counselor.domain.models import SPECIALTY_MAPPING
            
            # 실제 사용 중인 specialty_code들을 조회
            result = await self.session.execute(
                select(CounselorSpecialty.specialty_code)
                .distinct()
                .order_by(CounselorSpecialty.specialty_code)
            )
            used_codes = [row[0] for row in result.fetchall()]
            
            # 매핑 테이블에서 활성 specialty 반환
            active_specialties = []
            for code, name in SPECIALTY_MAPPING.items():
                active_specialties.append({
                    "specialty_code": code,
                    "specialty_name": name,
                    "is_active": True,
                    "in_use": code in used_codes
                })
            
            return active_specialties
        except SQLAlchemyError as e:
            # 기타 데이터베이스 오류
            raise DatabaseError("전문분야 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    async def update_counselor_status(self, counselor_id: str, status: str) -> None:
        """상담사 상태 업데이트 (MariaDB: status는 문자열)"""
        try:
            result = await self.session.execute(
                select(Counselor).where(Counselor.counselor_id == counselor_id)
            )
            orm_obj = result.scalar_one_or_none()
            if orm_obj:
                orm_obj.counselor_status = status
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            # 테이블 존재하지 않음 오류 처리
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            # 기타 데이터베이스 오류
            raise DatabaseError("상담사 상태를 업데이트하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    async def update_online_status(self, counselor_id: str, is_online: bool) -> None:
        """온라인 상태 업데이트 (MariaDB: counselor_status로 관리)"""
        try:
            result = await self.session.execute(
                select(Counselor).where(Counselor.counselor_id == counselor_id)
            )
            orm_obj = result.scalar_one_or_none()
            if orm_obj:
                # MariaDB에서는 is_online 필드가 없으므로 counselor_status로 관리
                orm_obj.counselor_status = "WAITING" if is_online else "ABSENT"
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            # 테이블 존재하지 않음 오류 처리
            if "does not exist" in str(e).lower():
                raise DatabaseError("데이터베이스 설정에 문제가 있습니다. 시스템 관리자에게 문의해주세요.")
            # 기타 데이터베이스 오류
            raise DatabaseError("온라인 상태를 업데이트하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.") 

    def _to_entity(self, orm: Counselor) -> CounselorEntity:
        specialties: List[CounselorSpecialtyEntity] = [
            CounselorSpecialtyEntity(
                specialty_id=str(s.specialty_id) if hasattr(s, "specialty_id") else "",
                specialty_code=s.specialty_code,
                specialty_name=s.specialty_name,
                description=getattr(s, "description", None),
            )
            for s in (orm.specialties or [])
        ]
        return CounselorEntity(
            counselor_id=str(orm.counselor_id),
            email=getattr(orm, "email", ""),
            password_hash=getattr(orm, "password_hash", ""),
            counselor_nickname=getattr(orm, "nickname", getattr(orm, "counselor_nickname", "")),
            counselor_code=orm.counselor_code,
            name=orm.name,
            profile_image_url=orm.profile_image_url,
            introduction=orm.introduction or "",
            specialties=specialties,
            price_per_minute=orm.price_per_minute,
            counselor_status=orm.counselor_status,
            counselor_status_text=orm.counselor_status_text,
            is_online=orm.is_online,
            is_authorized=orm.is_authorized,
            rating_avg=float(orm.rating_avg) if orm.rating_avg is not None else 0.0,
            rating_count=int(orm.rating_count) if orm.rating_count is not None else 0,
            created_at=orm.created_at,
        )