"""
사용자 관련 Pydantic 스키마
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.user_model import JoinType, UserStatus, Gender


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr = Field(..., description="이메일")
    nickname: str = Field(..., min_length=2, max_length=50, description="닉네임")
    phone: str = Field(..., min_length=1, max_length=15, description="전화번호")
    join_type: JoinType = Field(default=JoinType.COMMON, description="가입 유형")
    social_provider: Optional[str] = Field(None, description="소셜 제공자")
    social_id: Optional[str] = Field(None, description="소셜 고유 ID")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    birth_date: Optional[date] = Field(None, description="생년월일")
    gender: Optional[Gender] = Field(None, description="성별")
    is_marketing_agreed: bool = Field(default=False, description="마케팅 동의")


class UserSignup(UserBase):
    """통합 회원가입 요청 스키마 (일반 + 소셜)"""
    user_id: str = Field(..., min_length=4, max_length=20, description="사용자 ID")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="비밀번호 (일반 회원가입시 필수)")
    
    # 약관 동의 (필수)
    agree_terms: bool = Field(True, description="이용약관 동의")
    agree_privacy: bool = Field(True, description="개인정보처리방침 동의")
    # is_marketing_agreed, social_provider, social_id는 UserBase에서 상속


class UserResponse(UserBase):
    """사용자 정보 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    user_status: UserStatus = Field(..., description="사용자 상태")
    grade_code: str = Field(..., description="등급코드")
    social_provider: Optional[str] = Field(None, description="소셜 제공자")
    failed_login_count: int = Field(..., description="로그인 실패 횟수")
    locked_until: Optional[datetime] = Field(None, description="계정 잠금 해제 시간")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    last_login_at: Optional[datetime] = Field(None, description="마지막 로그인")
    
    # 회원가입 시 포인트 지급 정보 (선택적)
    signup_reward: Optional["SignupRewardInfo"] = Field(None, description="회원가입 보상 정보")
    
    model_config = ConfigDict(from_attributes=True)


class SignupRewardInfo(BaseModel):
    """회원가입 보상 정보"""
    event_name: str = Field(..., description="이벤트명")
    reward_value: int = Field(..., description="지급된 포인트")
    balance_after: int = Field(..., description="지급 후 포인트 잔액")
    message: str = Field(..., description="보상 메시지")


# TODO: 추후 필요시 참고용 스키마들
# class UserLogin(BaseModel):
#     """로그인 요청 스키마"""  
#     user_id: str = Field(..., description="사용자 ID 또는 이메일")
#     password: str = Field(..., description="비밀번호")
#
# class PasswordChange(BaseModel):
#     """비밀번호 변경 스키마"""
#     current_password: str = Field(..., description="현재 비밀번호")
#     new_password: str = Field(..., min_length=8, description="새 비밀번호")
#
# class UserListResponse(BaseModel):
#     """사용자 목록 응답 스키마"""
#     users: list[UserResponse] = Field(..., description="사용자 목록")
#     total: int = Field(..., description="전체 사용자 수") 
#     page: int = Field(..., description="현재 페이지")
#     size: int = Field(..., description="페이지 크기")