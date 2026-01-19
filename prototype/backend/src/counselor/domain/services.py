"""
Counselor 도메인 서비스

상담사 관련 비즈니스 로직 담당
"""

from typing import Optional
from datetime import datetime


class CounselorValidationService:
    """상담사 검증 서비스"""
    
    @staticmethod
    def validate_counselor_status(status: str) -> bool:
        """상담사 상태 유효성 검증"""
        valid_statuses = ['active', 'inactive', 'pending', 'suspended']
        return status in valid_statuses
    
    @staticmethod
    def can_counselor_login(is_authorized: bool, status: str) -> bool:
        """상담사 로그인 가능 여부 확인"""
        return is_authorized and status == 'active'
    
    @staticmethod
    def validate_specialty_code(specialty_code: str) -> bool:
        """전문분야 코드 유효성 검증"""
        # 전문분야 코드는 3자리 숫자
        return specialty_code.isdigit() and len(specialty_code) == 3


class CounselorStatusService:
    """상담사 상태 관리 서비스"""
    
    @staticmethod
    def should_auto_offline(last_activity: datetime) -> bool:
        """자동 오프라인 전환 여부 확인 (30분 이상 비활성)"""
        from datetime import timedelta
        if not last_activity:
            return False
        inactive_duration = datetime.utcnow() - last_activity
        return inactive_duration > timedelta(minutes=30)
    
    @staticmethod
    def calculate_rating(total_reviews: int, sum_ratings: int) -> float:
        """평균 평점 계산"""
        if total_reviews == 0:
            return 0.0
        return round(sum_ratings / total_reviews, 2)