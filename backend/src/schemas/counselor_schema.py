"""
상담사 관련 Pydantic 스키마
"""
from datetime import datetime, date
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import json

from src.models.counselor_model import CounselorStatus, CounselorGrade


class CounselorBase(BaseModel):
    """상담사 기본 스키마"""
    counselor_code: str = Field(..., min_length=1, max_length=20, description="상담사 코드")
    name: str = Field(..., min_length=2, max_length=50, description="상담사 이름")
    nickname: str = Field(..., min_length=2, max_length=50, description="상담사 닉네임")
    phone: str = Field(..., min_length=1, max_length=20, description="전화번호")
    introduction_short: Optional[str] = Field(None, description="짧은 소개")
    greeting_message: Optional[str] = Field(None, description="인사말")
    career_info: Optional[str] = Field(None, description="경력사항")
    counselor_status: CounselorStatus = Field(default=CounselorStatus.WAITING, description="상담사 상태")
    grade: Optional[CounselorGrade] = Field(default=CounselorGrade.BRONZE, description="상담사 등급")
    specialty_types: Optional[List[str]] = Field(None, description="전문 분야 (예: ['TARO', 'SAJU'])")
    keywords: Optional[str] = Field(None, description="키워드")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지")
    work_time: Optional[str] = Field(None, description="업무 시간")


class CounselorSignup(CounselorBase):
    """상담사 회원가입 요청 스키마"""
    counselor_id: str = Field(..., min_length=4, max_length=100, description="상담사 ID (이메일 기반)")
    password: str = Field(..., min_length=8, max_length=128, description="비밀번호")
    
    # 약관 동의 (필수)
    agree_terms: bool = Field(True, description="이용약관 동의")
    agree_privacy: bool = Field(True, description="개인정보처리방침 동의")


class CounselorResponse(CounselorBase):
    """상담사 정보 응답 스키마"""
    counselor_id: str = Field(..., description="상담사 ID")
    rating_avg: Optional[Decimal] = Field(None, description="평점 평균")
    rating_count: Optional[int] = Field(None, description="평점 개수")
    consultation_count: Optional[int] = Field(None, description="총 상담 횟수")
    consultation_time_total: Optional[int] = Field(None, description="총 상담 시간(분)")
    is_out: str = Field(..., description="탈퇴 여부")
    is_show: str = Field(..., description="노출 여부")
    is_new: Optional[str] = Field(None, description="신규 상담사 여부")
    approved_at: Optional[datetime] = Field(None, description="승인일시")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    last_login_at: Optional[datetime] = Field(None, description="마지막 로그인")
    withdrawn_at: Optional[datetime] = Field(None, description="탈퇴일시")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('specialty_types', mode='before')
    @classmethod
    def parse_specialty_types(cls, v: Any) -> Optional[List[str]]:
        """DB에서 JSON 문자열로 저장된 specialty_types를 파싱"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                # 빈 문자열 필터링
                if isinstance(parsed, list):
                    return [item for item in parsed if item]
                return parsed
            except (json.JSONDecodeError, TypeError):
                return None
        if isinstance(v, list):
            # 빈 문자열 필터링
            return [item for item in v if item]
        return v


# TODO: 추후 필요시 참고용 스키마들
# 부분 업데이트 요청 스키마 (마이페이지 편집)
class CounselorMypageUpdate(BaseModel):
    """상담사 마이페이지 부분 업데이트 요청 스키마"""
    counselor_status: Optional[CounselorStatus] = Field(None, description="상담사 상태: WAITING/CONSULTING/ABSENT")
    work_time: Optional[str] = Field(None, description="업무 시간")
    introduction_short: Optional[str] = Field(None, description="짧은 소개")
    greeting_message: Optional[str] = Field(None, description="인사말")
    career_info: Optional[str] = Field(None, description="경력사항")

# class CounselorLogin(BaseModel):
#     """상담사 로그인 요청 스키마"""  
#     counselor_id: str = Field(..., description="상담사 ID")
#     password: str = Field(..., description="비밀번호")
#
# class CounselorUpdate(BaseModel):
#     """상담사 정보 수정 스키마"""
#     nickname: Optional[str] = Field(None, min_length=2, max_length=50, description="상담사 닉네임")
#     phone: Optional[str] = Field(None, min_length=1, max_length=20, description="전화번호")
#     introduction: Optional[str] = Field(None, description="상담사 소개")
#     specialties: Optional[str] = Field(None, description="전문 분야")
#
# class PasswordChange(BaseModel):
#     """비밀번호 변경 스키마"""
#     current_password: str = Field(..., description="현재 비밀번호")
#     new_password: str = Field(..., min_length=8, description="새 비밀번호")
#
# class CounselorListResponse(BaseModel):
#     """상담사 목록 응답 스키마"""
#     counselors: list[CounselorResponse] = Field(..., description="상담사 목록")
#     total: int = Field(..., description="전체 상담사 수") 
#     page: int = Field(..., description="현재 페이지")
#     size: int = Field(..., description="페이지 크기")