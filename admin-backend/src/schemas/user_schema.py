"""
관리자 백엔드 사용자/ARS 스키마
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserListParams(BaseModel):
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    search_type: str = Field(default="all", description="검색 타입: all|nickname|email|phone")
    search_name: Optional[str] = Field(default=None, description="검색 키워드")
    join_type: Optional[str] = Field(default=None, description="가입유형: COMMON|NAVER|KAKAO")
    grade: Optional[str] = Field(default=None, description="등급코드")
    start_dt: Optional[str] = Field(default=None, description="생성일 범위 시작 yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="생성일 범위 종료 yyyy-mm-dd")


class UserListItem(BaseModel):
    user_id: str
    email: str
    nickname: str
    phone: str
    join_type: str
    grade_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Tm60UserBrief(BaseModel):
    idx: int
    u_id: str
    u_tel: str
    u_kname: str
    u_memcd: str
    u_login: str
    u_state: str
    u_point: int
    u_fdate: Optional[datetime] = None
    u_rdate: Optional[datetime] = None
    regdate: Optional[datetime] = None
    u_memo: str


class UserWithTm60Response(BaseModel):
    user: UserListItem
    tm60_users: List[Tm60UserBrief] = Field(default_factory=list, description="해당 user_id로 매칭된 tm60_users 전체 목록")


class UserDetailResponse(BaseModel):
    """회원 상세 응답: t_user 전체 + tm60_users 전체 목록"""
    user: dict = Field(..., description="t_user 모든 필드")
    tm60_users: List[Tm60UserBrief] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    """회원 수정 요청"""
    user_id: str = Field(..., description="회원 ID")
    nickname: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, description="평문 비밀번호")
    grade: Optional[str] = Field(default=None, description="등급코드")
    birth_date: Optional[str] = Field(default=None)

class UserUpdateResponse(BaseModel):
    user_id: str
    updated: bool


class UserPointAdjustRequest(BaseModel):
    user_id: str = Field(...)
    amount: int = Field(..., ge=1, description="증감 기준 절대값")
    type: str = Field(..., pattern="^(plus|minus)$")


class UserPointAdjustResponse(BaseModel):
    user_id: str
    amount: int = Field(..., description="적용된 서명 금액(차감은 음수)")
    balance_after: int



