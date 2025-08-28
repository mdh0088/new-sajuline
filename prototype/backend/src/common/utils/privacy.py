"""
개인정보보호 유틸리티
IP 주소 마스킹, 데이터 암호화, 민감정보 처리
"""
import hashlib
import hmac
from typing import Optional
from cryptography.fernet import Fernet
from ...common.config.settings import get_settings


class PrivacyProtector:
    """개인정보보호 처리 클래스"""
    
    def __init__(self):
        self.settings = get_settings()
        
    @staticmethod
    def mask_ip_address(ip_address: str) -> str:
        """
        IP 주소 마스킹 (마지막 옥텟 제거)
        
        Args:
            ip_address: 원본 IP 주소
            
        Returns:
            마스킹된 IP 주소
        """
        if not ip_address or ip_address == "unknown":
            return "unknown"
        
        try:
            # IPv4 처리
            if '.' in ip_address and ':' not in ip_address:
                parts = ip_address.split('.')
                if len(parts) == 4:
                    return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
            
            # IPv6 처리
            elif ':' in ip_address:
                parts = ip_address.split(':')
                if len(parts) >= 4:
                    return ':'.join(parts[:4]) + ':xxxx:xxxx:xxxx:xxxx'
            
            # 기타 경우 해싱 처리
            return f"hashed_{hashlib.sha256(ip_address.encode()).hexdigest()[:8]}"
            
        except Exception:
            return "masked"
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
        """
        민감한 데이터 해싱 (SHA-256 + Salt)
        
        Args:
            data: 해싱할 데이터
            salt: 솔트 (없으면 자동 생성)
            
        Returns:
            해싱된 데이터
        """
        if not data:
            return ""
        
        if not salt:
            salt = "sajuline_privacy_salt_2024"
        
        return hashlib.sha256((data + salt).encode()).hexdigest()
    
    def encrypt_personal_data(self, data: str) -> Optional[str]:
        """
        개인정보 암호화
        
        Args:
            data: 암호화할 데이터
            
        Returns:
            암호화된 데이터 또는 None
        """
        if not data or not self.settings.DATA_ENCRYPTION_ENABLED:
            return data
        
        try:
            encryption_key = self.settings.ENCRYPTION_KEY
            if not encryption_key:
                return data
            
            # Fernet 키 생성 (Base64 인코딩 필요)
            key = hashlib.sha256(encryption_key.encode()).digest()
            key_b64 = Fernet.generate_key() if len(key) != 32 else key
            
            fernet = Fernet(key_b64)
            encrypted_data = fernet.encrypt(data.encode())
            
            return encrypted_data.decode()
            
        except Exception as e:
            print(f"Encryption error: {e}")
            return data
    
    def decrypt_personal_data(self, encrypted_data: str) -> Optional[str]:
        """
        개인정보 복호화
        
        Args:
            encrypted_data: 암호화된 데이터
            
        Returns:
            복호화된 데이터 또는 원본
        """
        if not encrypted_data or not self.settings.DATA_ENCRYPTION_ENABLED:
            return encrypted_data
        
        try:
            encryption_key = self.settings.ENCRYPTION_KEY
            if not encryption_key:
                return encrypted_data
            
            key = hashlib.sha256(encryption_key.encode()).digest()
            key_b64 = Fernet.generate_key() if len(key) != 32 else key
            
            fernet = Fernet(key_b64)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            
            return decrypted_data.decode()
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_data
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """
        이메일 익명화 (부분 마스킹)
        
        Args:
            email: 원본 이메일
            
        Returns:
            익명화된 이메일
        """
        if not email or '@' not in email:
            return "anonymous@domain.com"
        
        try:
            local, domain = email.split('@')
            
            # 로컬 부분 마스킹
            if len(local) <= 2:
                local_masked = local[0] + '*'
            else:
                local_masked = local[0] + '*' * (len(local) - 2) + local[-1]
            
            # 도메인 부분도 부분 마스킹
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                domain_masked = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1)
                domain_masked += '.' + '.'.join(domain_parts[1:])
            else:
                domain_masked = domain
            
            return f"{local_masked}@{domain_masked}"
            
        except Exception:
            return "anonymous@domain.com"
    
    @staticmethod
    def anonymize_phone(phone: str) -> str:
        """
        전화번호 익명화
        
        Args:
            phone: 원본 전화번호
            
        Returns:
            익명화된 전화번호
        """
        if not phone:
            return "***-****-****"
        
        # 숫자만 추출
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) >= 11:
            # 010-****-1234 형태로 마스킹
            return f"{digits[:3]}-****-{digits[-4:]}"
        elif len(digits) >= 8:
            # ***-1234 형태로 마스킹
            return f"***-{digits[-4:]}"
        else:
            return "***-****"
    
    @staticmethod
    def is_sensitive_data(field_name: str) -> bool:
        """
        민감한 데이터 필드인지 확인
        
        Args:
            field_name: 필드명
            
        Returns:
            민감한 데이터 여부
        """
        sensitive_fields = {
            'password', 'password_hash', 'phone', 'email',
            'birth_date', 'birth_time', 'ssn', 'social_security',
            'credit_card', 'bank_account', 'ip_address',
            'address', 'real_name', 'id_number'
        }
        
        return field_name.lower() in sensitive_fields or any(
            sensitive in field_name.lower() for sensitive in sensitive_fields
        )


# 싱글톤 인스턴스
privacy_protector = PrivacyProtector()


# 편의 함수들
def mask_ip(ip_address: str) -> str:
    """IP 주소 마스킹 편의 함수"""
    return PrivacyProtector.mask_ip_address(ip_address)


def hash_sensitive(data: str) -> str:
    """민감 데이터 해싱 편의 함수"""
    return PrivacyProtector.hash_sensitive_data(data)


def anonymize_email(email: str) -> str:
    """이메일 익명화 편의 함수"""
    return PrivacyProtector.anonymize_email(email)


def anonymize_phone(phone: str) -> str:
    """전화번호 익명화 편의 함수"""
    return PrivacyProtector.anonymize_phone(phone)