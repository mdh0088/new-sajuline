"""
Phone Verification Repository

핸드폰 인증 리포지토리 (데이터베이스 접근)
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, desc
from ..domain.models import PhoneVerification
from ..domain.entities import VerificationStatus


class PhoneVerificationRepository:
    """핸드폰 인증 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, verification: PhoneVerification) -> PhoneVerification:
        """인증 정보 생성"""
        self.session.add(verification)
        await self.session.flush()
        return verification
    
    async def get_by_session_id(self, session_id: str) -> Optional[PhoneVerification]:
        """세션 ID로 조회"""
        result = await self.session.execute(
            select(PhoneVerification).where(PhoneVerification.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self,
        user_id: str,
        status: Optional[VerificationStatus] = None
    ) -> List[PhoneVerification]:
        """사용자 ID로 조회"""
        query = select(PhoneVerification).where(PhoneVerification.user_id == user_id)
        
        if status:
            query = query.where(PhoneVerification.status == status)
        
        query = query.order_by(desc(PhoneVerification.created_at))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_recent_by_phone(
        self,
        phone_no: str,
        minutes: int = 30
    ) -> Optional[PhoneVerification]:
        """
        전화번호로 최근 인증 조회
        중복 인증 방지용
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        result = await self.session.execute(
            select(PhoneVerification).where(
                and_(
                    PhoneVerification.phone_no == phone_no,
                    PhoneVerification.status == VerificationStatus.COMPLETED,
                    PhoneVerification.verified_at >= since
                )
            ).order_by(desc(PhoneVerification.verified_at))
        )
        return result.scalar_one_or_none()
    
    async def get_by_ci(self, ci: str) -> Optional[PhoneVerification]:
        """CI로 조회 (중복 가입 확인용)"""
        result = await self.session.execute(
            select(PhoneVerification).where(
                and_(
                    PhoneVerification.ci == ci,
                    PhoneVerification.status == VerificationStatus.COMPLETED
                )
            ).order_by(desc(PhoneVerification.verified_at))
        )
        return result.scalar_one_or_none()
    
    async def get_by_di(self, di: str) -> Optional[PhoneVerification]:
        """DI로 조회 (중복 가입 확인용)"""
        result = await self.session.execute(
            select(PhoneVerification).where(
                and_(
                    PhoneVerification.di == di,
                    PhoneVerification.status == VerificationStatus.COMPLETED
                )
            ).order_by(desc(PhoneVerification.verified_at))
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self,
        session_id: str,
        status: VerificationStatus,
        **kwargs
    ) -> Optional[PhoneVerification]:
        """상태 업데이트"""
        verification = await self.get_by_session_id(session_id)
        if not verification:
            return None
        
        verification.status = status
        verification.updated_at = datetime.utcnow()
        
        # 추가 필드 업데이트
        for key, value in kwargs.items():
            if hasattr(verification, key):
                setattr(verification, key, value)
        
        await self.session.flush()
        return verification
    
    async def update_verification_result(
        self,
        session_id: str,
        cert_no: str,
        decrypted_data: dict
    ) -> Optional[PhoneVerification]:
        """인증 결과 업데이트"""
        verification = await self.get_by_session_id(session_id)
        if not verification:
            return None
        
        # 인증 결과 저장
        verification.cert_no = cert_no
        verification.comm_id = decrypted_data.get("comm_id")
        verification.phone_no = decrypted_data.get("phone_no")
        verification.verified_name = decrypted_data.get("user_name")
        verification.verified_birth = decrypted_data.get("birth_day")
        verification.sex_code = decrypted_data.get("sex_code")
        verification.local_code = decrypted_data.get("local_code")
        verification.ci = decrypted_data.get("ci_url")
        verification.di = decrypted_data.get("di_url")
        verification.res_cd = decrypted_data.get("res_cd")
        verification.res_msg = decrypted_data.get("res_msg")
        
        # 상태 및 시간 업데이트
        verification.status = VerificationStatus.COMPLETED
        verification.verified_at = datetime.utcnow()
        verification.updated_at = datetime.utcnow()
        
        await self.session.flush()
        return verification
    
    async def cleanup_expired(self, before: Optional[datetime] = None) -> int:
        """만료된 인증 정보 정리"""
        if not before:
            before = datetime.utcnow()
        
        result = await self.session.execute(
            update(PhoneVerification)
            .where(
                and_(
                    PhoneVerification.status.in_([
                        VerificationStatus.PENDING,
                        VerificationStatus.IN_PROGRESS
                    ]),
                    PhoneVerification.expires_at < before
                )
            )
            .values(status=VerificationStatus.EXPIRED)
        )
        
        await self.session.flush()
        return result.rowcount
    
    async def delete_old_records(self, days: int = 30) -> int:
        """오래된 레코드 삭제"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(PhoneVerification).where(
                PhoneVerification.created_at < cutoff_date
            )
        )
        
        records = result.scalars().all()
        for record in records:
            await self.session.delete(record)
        
        await self.session.flush()
        return len(records)