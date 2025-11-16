"""
사용자 관련 Pydantic 스키마
"""
from datetime import datetime, date, timedelta, timezone
from typing import Optional, List, Literal
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.user_model import JoinType, UserStatus, Gender
from src.schemas.grade_schema import NextGradeInfo

# 한국 시간대 (UTC+9) 정의
KST = timezone(timedelta(hours=9))


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr = Field(..., description="이메일")
    nickname: str = Field(..., min_length=2, max_length=50, description="닉네임")
    phone: str = Field(..., min_length=1, max_length=15, description="전화번호")
    join_type: JoinType = Field(default=JoinType.COMMON, description="가입 유형")
    social_provider: Optional[str] = Field(None, description="소셜 제공자")
    social_id: Optional[str] = Field(None, description="소셜 고유 ID")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    birth_date: Optional[str] = Field(None, description="생년월일시 (YYYY-MM-DD HH:MM 형식)")
    gender: Optional[Gender] = Field(None, description="성별")
    mileage_point: int = Field(default=0, ge=0, description="마일리지 포인트")
    is_marketing_agreed: bool = Field(default=False, description="마케팅 동의")


class UserSignup(UserBase):
    """통합 회원가입 요청 스키마 (일반 + 소셜)"""
    user_id: str = Field(..., min_length=4, max_length=20, description="사용자 ID")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="비밀번호 (일반 회원가입시 필수)")
    phone_chk: bool = Field(..., description="휴대폰 인증 완료 여부 (필수)")

    # 필수 약관 동의는 프론트엔드에서만 검증, 서버로는 전송하지 않음
    # is_marketing_agreed, social_provider, social_id는 UserBase에서 상속


class UserResponse(UserBase):
    """사용자 정보 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    user_status: UserStatus = Field(..., description="사용자 상태")
    grade_code: str = Field(..., description="등급코드")
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


class UserMypageResponse(BaseModel):
    """사용자 마이페이지 통합 응답 스키마"""
    
    # 1. 기본 사용자 정보
    user_info: UserResponse = Field(..., description="사용자 기본 정보")
    
    # 2. 상담 관련 통계
    total_consultation_count: int = Field(..., ge=0, description="총 상담 수 (tm60_chatlog)")
    
    # 3. 즐겨찾기 통계
    total_bookmark_count: int = Field(..., ge=0, description="총 즐겨찾기 수 (t_user_bookmark)")
    
    # 4. 후기 통계
    total_review_count: int = Field(..., ge=0, description="총 후기 작성 수 (t_consultation_review)")
    
    # 5. 포인트 정보
    current_points: int = Field(..., ge=0, description="현재 보유 포인트 (tm60_users)")
    
    # 6. 등급 정보
    grade_info: NextGradeInfo = Field(..., description="현재 등급 및 다음 등급 정보 (t_grade)")
    
    # 7. 결제 정보
    monthly_payment_total: Decimal = Field(..., ge=0, description="이번 달 결제 총액 (t_payment)")
    
    # 통계 요약 정보
    data_updated_at: datetime = Field(default_factory=datetime.utcnow, description="데이터 조회 시점")


# 포인트 내역 스키마 (사용자 도메인 귀속)
SearchType = Literal["point_charge", "point_use"]
OrderType = Literal["latest", "highest", "lowest"]


class CounselorBrief(BaseModel):
    counselor_code: str = Field(..., description="상담사 코드")
    nickname: Optional[str] = Field(None, description="상담사 닉네임")
    name: Optional[str] = Field(None, description="상담사 실명")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")


class PointChargeHistoryItem(BaseModel):
    paid_at: Optional[datetime] = Field(None, description="결제 일시")
    product_name: Optional[str] = Field(None, description="결제 상품명")
    point_amount: int = Field(..., description="충전 포인트")


class PointUseHistoryItem(BaseModel):
    chatstart: Optional[str] = Field(None, description="채팅 시작")
    chatend: Optional[str] = Field(None, description="채팅 종료")
    realchattm: Optional[int] = Field(None, description="실제 채팅 시간")
    counselor: Optional[CounselorBrief] = Field(None, description="상담사 정보")
    usepoint: int = Field(..., description="사용 포인트")


class PointHistoryResponse(BaseModel):
    search_type: SearchType = Field(..., description="조회 유형")
    items_charge: Optional[List[PointChargeHistoryItem]] = Field(None, description="충전 내역 목록")
    items_use: Optional[List[PointUseHistoryItem]] = Field(None, description="사용 내역 목록")


class FindIdRequest(BaseModel):
    """ID 찾기 요청"""
    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="본인인증된 전화번호"
    )

    model_config = ConfigDict(from_attributes=True)


class FindIdResponse(BaseModel):
    """ID 찾기 응답"""
    user_id: str = Field(..., description="사용자 ID")
    created_at: datetime = Field(..., description="가입일시")

    model_config = ConfigDict(from_attributes=True)


class FindPasswordRequest(BaseModel):
    """비밀번호 찾기 요청"""
    user_id: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="사용자 ID"
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="본인인증된 전화번호"
    )

    model_config = ConfigDict(from_attributes=True)


class FindPasswordResponse(BaseModel):
    """비밀번호 찾기 응답"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="임시 비밀번호가 전송된 이메일 (마스킹)")
    message: str = Field(..., description="안내 메시지")

    model_config = ConfigDict(from_attributes=True)


class WithdrawRequest(BaseModel):
    """회원탈퇴 요청 스키마"""
    password: Optional[str] = Field(None, description="비밀번호 확인 (소셜 로그인 사용자는 null)")

    model_config = ConfigDict(from_attributes=True)


class UserOutResponse(BaseModel):
    """회원탈퇴 응답 스키마"""
    out_idx: int = Field(..., description="탈퇴 고유 식별자")
    user_id: Optional[str] = Field(None, description="탈퇴한 사용자 ID")
    nickname: Optional[str] = Field(None, description="탈퇴한 사용자 닉네임")
    phone: Optional[str] = Field(None, description="탈퇴한 사용자 전화번호")
    email: Optional[str] = Field(None, description="탈퇴한 사용자 이메일")
    created_at: datetime = Field(..., description="탈퇴 일시")

    model_config = ConfigDict(from_attributes=True)


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