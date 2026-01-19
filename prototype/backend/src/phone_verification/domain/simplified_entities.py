"""
Simplified Phone Verification Entities

Industry-standard SMS verification request/response models.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class SendCodeRequest(BaseModel):
    """SMS 인증 코드 발송 요청"""
    
    phone: str = Field(
        ...,
        description="휴대폰 번호 (하이픈 없이)",
        example="01012345678"
    )
    name: str = Field(
        ...,
        description="사용자 이름",
        example="홍길동"
    )
    birth_date: str = Field(
        ...,
        description="생년월일 (YYYYMMDD)",
        example="19900101"
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        """휴대폰 번호 검증"""
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', v)
        
        # Check Korean mobile phone pattern
        if not re.match(r'^01[0-9]{8,9}$', phone_digits):
            raise ValueError('올바른 휴대폰 번호 형식이 아닙니다.')
        
        return phone_digits
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """생년월일 검증"""
        if not re.match(r'^\d{8}$', v):
            raise ValueError('생년월일은 YYYYMMDD 형식이어야 합니다.')
        
        # Basic date validation
        try:
            year = int(v[:4])
            month = int(v[4:6])
            day = int(v[6:8])
            
            if year < 1900 or year > datetime.now().year:
                raise ValueError('올바른 연도가 아닙니다.')
            if month < 1 or month > 12:
                raise ValueError('올바른 월이 아닙니다.')
            if day < 1 or day > 31:
                raise ValueError('올바른 일이 아닙니다.')
        except:
            raise ValueError('올바른 생년월일이 아닙니다.')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """이름 검증"""
        if not v or len(v.strip()) < 2:
            raise ValueError('이름은 2자 이상이어야 합니다.')
        if len(v) > 50:
            raise ValueError('이름이 너무 깁니다.')
        return v.strip()


class SendCodeResponse(BaseModel):
    """SMS 인증 코드 발송 응답"""
    
    session_id: str = Field(
        ...,
        description="인증 세션 ID"
    )
    expires_at: datetime = Field(
        ...,
        description="세션 만료 시간"
    )
    remaining_time: int = Field(
        ...,
        description="남은 시간 (초)"
    )
    message: str = Field(
        default="인증번호가 발송되었습니다.",
        description="응답 메시지"
    )
    up_hash: Optional[str] = Field(
        None,
        description="KCP up_hash (인증창 호출용)"
    )


class VerifyCodeRequest(BaseModel):
    """인증 코드 확인 요청"""
    
    session_id: str = Field(
        ...,
        description="인증 세션 ID"
    )
    code: str = Field(
        ...,
        description="6자리 인증 코드",
        example="123456"
    )
    
    @validator('code')
    def validate_code(cls, v):
        """인증 코드 검증"""
        # Remove any spaces or hyphens
        code_digits = re.sub(r'\D', '', v)
        
        if not re.match(r'^\d{6}$', code_digits):
            raise ValueError('인증 코드는 6자리 숫자여야 합니다.')
        
        return code_digits
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """세션 ID 검증"""
        if not v or len(v) != 32:
            raise ValueError('올바른 세션 ID가 아닙니다.')
        return v


class VerifyCodeResponse(BaseModel):
    """인증 코드 확인 응답"""
    
    verified: bool = Field(
        ...,
        description="인증 성공 여부"
    )
    token: Optional[str] = Field(
        None,
        description="인증 토큰 (성공 시)"
    )
    phone: Optional[str] = Field(
        None,
        description="인증된 전화번호"
    )
    message: str = Field(
        ...,
        description="응답 메시지"
    )
    phone_chk: Optional[str] = Field(
        None,
        description="암호화된 인증 플래그 (기존 시스템 호환용)"
    )


class CheckVerifiedRequest(BaseModel):
    """인증 확인 요청"""
    
    token: str = Field(
        ...,
        description="인증 토큰"
    )


class CheckVerifiedResponse(BaseModel):
    """인증 확인 응답"""
    
    verified: bool = Field(
        ...,
        description="인증 상태"
    )
    phone: Optional[str] = Field(
        None,
        description="인증된 전화번호"
    )
    verified_at: Optional[datetime] = Field(
        None,
        description="인증 시간"
    )
    user_info: Optional[dict] = Field(
        None,
        description="사용자 정보"
    )


class ResendCodeRequest(BaseModel):
    """인증 코드 재발송 요청"""
    
    session_id: str = Field(
        ...,
        description="기존 세션 ID"
    )


class PhoneVerificationError(BaseModel):
    """에러 응답"""
    
    error: str = Field(
        ...,
        description="에러 타입"
    )
    message: str = Field(
        ...,
        description="에러 메시지"
    )
    detail: Optional[dict] = Field(
        None,
        description="상세 정보"
    )