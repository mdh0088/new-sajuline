"""
등급 서비스 클래스
비즈니스 로직과 트랜잭션 관리
"""
from typing import Optional

from src.exceptions.custom_exceptions import NotFoundError, ValidationError
from src.common.logging import logger, get_logger_with_request_id

from src.models.grade_model import Grade
from src.schemas.grade_schema import GradeResponse, NextGradeInfo
from src.repositories.grade_repository import GradeRepository


class GradeService:
    """등급 비즈니스 로직 서비스"""
    
    def __init__(self, grade_repo: GradeRepository):
        self.grade_repo = grade_repo
    
    async def get_grade_by_code(self, grade_code: str) -> GradeResponse:
        """
        등급 코드로 등급 정보 조회
        - 사용자의 grade_code 값으로 등급 정보 조회
        """
        log = get_logger_with_request_id()
        log.info("Getting grade by code", grade_code=grade_code)
        
        if not grade_code:
            log.warning("Grade code is empty")
            raise ValidationError("등급 코드가 필요합니다.")
        
        grade = await self.grade_repo.get_by_code(grade_code)
        if not grade:
            log.warning("Grade not found", grade_code=grade_code)
            raise NotFoundError(f"등급 코드 '{grade_code}'를 찾을 수 없습니다.")
        
        log.info("Grade found successfully", grade_code=grade_code, grade_name=grade.grade_name)
        return GradeResponse.model_validate(grade)
    
    async def get_next_grade_info(self, current_grade_code: str) -> NextGradeInfo:
        """
        현재 등급 코드로 다음 등급 정보 조회
        - 현재 등급 정보와 다음 등급 정보를 함께 반환
        - 최고 등급인 경우 next_grade는 None
        """
        log = get_logger_with_request_id()
        log.info("Getting next grade info", current_grade_code=current_grade_code)
        
        if not current_grade_code:
            log.warning("Current grade code is empty")
            raise ValidationError("현재 등급 코드가 필요합니다.")
        
        # 현재 등급 정보 조회
        current_grade = await self.grade_repo.get_by_code(current_grade_code)
        if not current_grade:
            log.warning("Current grade not found", grade_code=current_grade_code)
            raise NotFoundError(f"등급 코드 '{current_grade_code}'를 찾을 수 없습니다.")
        
        # 다음 등급 정보 조회
        next_grade = await self.grade_repo.get_next_grade_by_level(current_grade_code)
        
        # 응답 데이터 생성
        current_grade_response = GradeResponse.model_validate(current_grade)
        next_grade_response = None
        required_amount = None
        
        if next_grade:
            next_grade_response = GradeResponse.model_validate(next_grade)
            # 다음 등급까지 필요한 구매 금액 계산 (다음 등급 최소 구매 금액 - 현재 등급 최소 구매 금액)
            required_amount = next_grade.min_purchase_amount - current_grade.min_purchase_amount
            log.info("Next grade found", 
                    current_grade=current_grade.grade_name,
                    next_grade=next_grade.grade_name,
                    required_amount=required_amount)
        else:
            log.info("Already at highest grade", current_grade=current_grade.grade_name)
        
        return NextGradeInfo(
            current_grade=current_grade_response,
            next_grade=next_grade_response,
            required_amount=required_amount
        )