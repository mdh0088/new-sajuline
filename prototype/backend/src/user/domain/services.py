"""
User 도메인 서비스
사용자 관련 비즈니스 로직과 검증
"""
from typing import Optional, Dict, Any
import re
from datetime import datetime


class UserValidationService:
    """사용자 정보 검증 서비스"""
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """전화번호 형식 검증"""
        if not phone:
            return False
        # 한국 전화번호 형식: 010-XXXX-XXXX 또는 01012345678
        pattern = r'^01[0-9]-?\d{3,4}-?\d{4}$'
        return bool(re.match(pattern, phone.replace(' ', '')))
    
    @staticmethod
    def validate_nickname(nickname: str) -> bool:
        """닉네임 유효성 검증"""
        if not nickname:
            return False
        # 2-50자 길이 체크
        if len(nickname) < 2 or len(nickname) > 50:
            return False
        # 특수문자 제한 (한글, 영문, 숫자, 일부 특수문자만 허용)
        pattern = r'^[가-힣a-zA-Z0-9_\-\.]+$'
        return bool(re.match(pattern, nickname))
    
    @staticmethod
    def validate_profile_update(update_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """프로필 업데이트 데이터 검증"""
        errors = []
        
        # 닉네임 검증
        if 'nickname' in update_data:
            if not UserValidationService.validate_nickname(update_data['nickname']):
                errors.append("올바른 닉네임 형식이 아닙니다.")
        
        # 전화번호 검증
        if 'phone' in update_data:
            if not UserValidationService.validate_phone_format(update_data['phone']):
                errors.append("올바른 전화번호 형식이 아닙니다.")
        
        # 성별 검증
        if 'gender' in update_data:
            if update_data['gender'] not in ['M', 'F', None]:
                errors.append("성별은 M(남성), F(여성) 중 하나여야 합니다.")
        
        return len(errors) == 0, errors


class UserPointService:
    """사용자 포인트 관련 서비스"""
    
    @staticmethod
    def calculate_point_expiry(added_at: datetime) -> datetime:
        """포인트 만료일 계산 (1년)"""
        from datetime import timedelta
        return added_at + timedelta(days=365)
    
    @staticmethod
    def validate_point_transaction(current_balance: int, amount: int, 
                                  transaction_type: str) -> tuple[bool, Optional[str]]:
        """포인트 거래 유효성 검증"""
        if transaction_type == 'USE':
            if amount <= 0:
                return False, "사용 포인트는 0보다 커야 합니다."
            if current_balance < amount:
                return False, f"포인트가 부족합니다. (현재: {current_balance}P)"
        elif transaction_type == 'ADD':
            if amount <= 0:
                return False, "추가 포인트는 0보다 커야 합니다."
        else:
            return False, "올바른 거래 유형이 아닙니다."
        
        return True, None
    
    @staticmethod
    def calculate_new_balance(current_balance: int, amount: int, 
                            transaction_type: str) -> int:
        """새로운 포인트 잔액 계산"""
        if transaction_type == 'ADD':
            return current_balance + amount
        elif transaction_type == 'USE':
            return current_balance - amount
        else:
            return current_balance


class UserStatusService:
    """사용자 상태 관리 서비스"""
    
    @staticmethod
    def can_use_premium_features(user) -> bool:
        """프리미엄 기능 사용 가능 여부"""
        return user.is_premium and user.is_active
    
    @staticmethod
    def can_make_purchase(user) -> bool:
        """구매 가능 여부 확인"""
        return user.is_active and not user.is_deleted
    
    @staticmethod
    def should_show_onboarding(user) -> bool:
        """온보딩 표시 여부"""
        # 가입 후 7일 이내이고 첫 구매가 없는 경우
        from datetime import timedelta
        days_since_join = (datetime.utcnow() - user.created_at).days
        return days_since_join <= 7 and user.point_balance == 0


class UserPrivacyService:
    """사용자 개인정보 관련 서비스"""
    
    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """전화번호 마스킹"""
        if not phone or len(phone) < 8:
            return phone
        # 010-1234-5678 -> 010-****-5678
        if '-' in phone:
            parts = phone.split('-')
            if len(parts) == 3:
                return f"{parts[0]}-****-{parts[2]}"
        # 01012345678 -> 010****5678
        else:
            return phone[:3] + '****' + phone[-4:]
    
    @staticmethod
    def mask_email(email: str) -> str:
        """이메일 마스킹"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[:2] + '*' * (len(local) - 2)
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def prepare_public_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """공개 프로필용 데이터 준비 (민감정보 제거)"""
        public_fields = ['user_id', 'nickname', 'gender', 'created_at', 'is_premium']
        return {k: v for k, v in user_data.items() if k in public_fields}