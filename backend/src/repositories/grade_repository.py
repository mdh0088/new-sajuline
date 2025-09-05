"""
등급 Repository 클래스
데이터 액세스 레이어 - 순수한 CRUD 작업만 담당
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, asc

from src.models.grade_model import Grade
from src.common.logging import logger, get_logger_with_request_id


class GradeRepository:
    """등급 데이터 액세스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @logger.catch(reraise=True)
    async def get_by_code(self, grade_code: str) -> Optional[Grade]:
        """등급 코드로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up grade by code", grade_code=grade_code)
        
        stmt = select(Grade).where(Grade.grade_code == grade_code)
        result = await self.db.execute(stmt)
        grade = result.scalar_one_or_none()
        
        log.info("Grade lookup completed", grade_code=grade_code, found=grade is not None)
        return grade
    
    @logger.catch(reraise=True)
    async def get_by_level(self, grade_level: int) -> Optional[Grade]:
        """등급 레벨로 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up grade by level", grade_level=grade_level)
        
        stmt = select(Grade).where(Grade.grade_level == grade_level)
        result = await self.db.execute(stmt)
        grade = result.scalar_one_or_none()
        
        log.info("Grade lookup by level completed", grade_level=grade_level, found=grade is not None)
        return grade
    
    @logger.catch(reraise=True)
    async def get_next_grade_by_level(self, grade_code: str) -> Optional[Grade]:
        """현재 등급 코드보다 한 단계 높은 등급 조회"""
        log = get_logger_with_request_id()
        log.info("Looking up next grade by code", grade_code=grade_code)
        
        # 먼저 현재 등급의 레벨을 조회
        current_grade = await self.get_by_code(grade_code)
        if not current_grade:
            log.warning("Current grade not found", grade_code=grade_code)
            return None
        
        # 현재 등급 레벨보다 한 단계 높은 등급 조회
        stmt = (
            select(Grade)
            .where(and_(Grade.grade_level > current_grade.grade_level, Grade.is_active == True))
            .order_by(asc(Grade.grade_level))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        next_grade = result.scalar_one_or_none()
        
        log.info("Next grade lookup completed", 
                grade_code=grade_code, 
                current_level=current_grade.grade_level,
                found=next_grade is not None)
        return next_grade