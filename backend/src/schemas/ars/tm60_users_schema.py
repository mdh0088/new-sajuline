"""
ARS tm60_users 테이블 관련 Pydantic 스키마 (MSSQL 연동)

외부 상담사 시스템 연동을 위한 읽기 전용 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.ars.tm60_users_model import UserMemCode, UserLoginStatus, UserState


class Tm60UsersBase(BaseModel):
    """ARS 사용자 기본 스키마"""
    u_id: str = Field(..., description="사용자 ID")
    u_tel: str = Field(..., description="사용자 전화번호")
    u_kname: str = Field(..., description="사용자 한글 이름")
    u_memcd: str = Field(default="1", description="회원 구분 코드")
    u_login: str = Field(default="1", description="로그인 상태")
    u_state: str = Field(default="0", description="사용자 상태")
    u_point: int = Field(default=0, description="사용자 포인트")
    u_memo: str = Field(default="", description="사용자 메모")


class Tm60UsersResponse(Tm60UsersBase):
    """ARS 사용자 정보 응답 스키마"""
    idx: int = Field(..., description="사용자 고유 식별자")
    u_fdate: Optional[datetime] = Field(None, description="최초 가입일")
    u_rdate: Optional[datetime] = Field(None, description="최근 수정일")
    regdate: Optional[datetime] = Field(None, description="등록일")
    
    # 추가 속성 (계산된 필드)
    is_active: bool = Field(..., description="활성 상태")
    is_logged_in: bool = Field(..., description="로그인 상태")
    member_type: str = Field(..., description="회원 유형")
    
    model_config = ConfigDict(from_attributes=True)


class Tm60UsersListResponse(BaseModel):
    """ARS 사용자 목록 응답 스키마"""
    users: list[Tm60UsersResponse] = Field(..., description="사용자 목록")
    total: int = Field(..., description="전체 사용자 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


class Tm60UsersSearch(BaseModel):
    """ARS 사용자 검색 스키마"""
    u_id: Optional[str] = Field(None, description="사용자 ID 검색")
    u_tel: Optional[str] = Field(None, description="전화번호 검색")
    u_kname: Optional[str] = Field(None, description="이름 검색")
    u_memcd: Optional[UserMemCode] = Field(None, description="회원 구분 필터")
    u_state: Optional[UserState] = Field(None, description="사용자 상태 필터")
    min_point: Optional[int] = Field(None, description="최소 포인트")
    max_point: Optional[int] = Field(None, description="최대 포인트")
    from_date: Optional[datetime] = Field(None, description="가입일 시작일")
    to_date: Optional[datetime] = Field(None, description="가입일 종료일")