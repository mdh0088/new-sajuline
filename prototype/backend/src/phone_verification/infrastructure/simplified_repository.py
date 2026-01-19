"""
Simplified Phone Verification Repository

KCP 인증 결과를 DB에 저장하는 간소화된 Repository.
세션 관리는 Redis에서 하고, DB에는 인증 완료 정보만 저장.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from ..domain.simplified_model import SimplifiedPhoneVerification

logger = logging.getLogger(__name__)


class SimplifiedPhoneVerificationRepository:
    """간소화된 핸드폰 인증 Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_ci(self, ci: str) -> Optional[SimplifiedPhoneVerification]:
        """
        CI로 인증 정보 조회 (중복가입 확인용)
        
        Args:
            ci: 연계정보
            
        Returns:
            인증 정보 또는 None
        """
        try:
            result = await self.session.execute(
                select(SimplifiedPhoneVerification).where(
                    SimplifiedPhoneVerification.ci == ci
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding verification by CI: {e}")
            return None
    
    async def find_by_di(self, di: str) -> Optional[SimplifiedPhoneVerification]:
        """
        DI로 인증 정보 조회 (사이트별 중복 확인용)
        
        Args:
            di: 중복가입확인정보
            
        Returns:
            인증 정보 또는 None
        """
        try:
            result = await self.session.execute(
                select(SimplifiedPhoneVerification).where(
                    SimplifiedPhoneVerification.di == di
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error finding verification by DI: {e}")
            return None
    
    async def find_by_phone(
        self,
        phone_no: str,
        limit: int = 10
    ) -> list[SimplifiedPhoneVerification]:
        """
        전화번호로 인증 이력 조회
        
        Args:
            phone_no: 전화번호
            limit: 최대 조회 개수
            
        Returns:
            인증 이력 리스트
        """
        try:
            result = await self.session.execute(
                select(SimplifiedPhoneVerification)
                .where(SimplifiedPhoneVerification.phone_no == phone_no)
                .order_by(SimplifiedPhoneVerification.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error finding verifications by phone: {e}")
            return []
    
    async def save_verification(
        self,
        phone_no: str,
        user_name: str,
        birth_date: str,
        ci: str,
        di: str,
        cert_no: Optional[str] = None,
        res_cd: str = "0000"
    ) -> SimplifiedPhoneVerification:
        """
        인증 정보 저장
        
        Args:
            phone_no: 전화번호
            user_name: 이름
            birth_date: 생년월일
            ci: 연계정보
            di: 중복가입확인정보
            cert_no: KCP 인증번호
            res_cd: 결과 코드
            
        Returns:
            저장된 인증 정보
        """
        try:
            # CI 중복 체크
            existing = await self.find_by_ci(ci)
            if existing:
                # 이미 존재하면 업데이트
                existing.phone_no = phone_no
                existing.user_name = user_name
                existing.birth_date = birth_date
                existing.di = di
                existing.cert_no = cert_no or existing.cert_no
                existing.res_cd = res_cd
                existing.created_at = datetime.utcnow()
                await self.session.commit()
                return existing
            
            # 새로 생성
            verification = SimplifiedPhoneVerification(
                phone_no=phone_no,
                user_name=user_name,
                birth_date=birth_date,
                ci=ci,
                di=di,
                cert_no=cert_no,
                res_cd=res_cd,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            
            self.session.add(verification)
            await self.session.commit()
            await self.session.refresh(verification)
            
            return verification
            
        except Exception as e:
            logger.error(f"Error saving verification: {e}")
            await self.session.rollback()
            raise
    
    async def check_duplicate(self, ci: str, di: str) -> dict:
        """
        중복가입 확인
        
        Args:
            ci: 연계정보
            di: 중복가입확인정보
            
        Returns:
            중복 여부 및 정보
        """
        try:
            ci_check = await self.find_by_ci(ci)
            di_check = await self.find_by_di(di)
            
            return {
                "has_ci_duplicate": ci_check is not None,
                "has_di_duplicate": di_check is not None,
                "ci_info": ci_check.to_dict() if ci_check else None,
                "di_info": di_check.to_dict() if di_check else None
            }
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return {
                "has_ci_duplicate": False,
                "has_di_duplicate": False,
                "ci_info": None,
                "di_info": None
            }

