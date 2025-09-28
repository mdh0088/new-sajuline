"""
관리자 백엔드 상담사 목록 스키마
"""
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CounselorListParams(BaseModel):
    """상담사 목록 조회 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    search_type: str = Field(default="all", description="검색 타입: all|name|nickname|counselor_id")
    search_name: Optional[str] = Field(default=None, description="검색 키워드")
    specialties: Optional[List[str]] = Field(default=None, description="전문 분야 필터 (예: ['TARO','SAJU'])")
    is_show: Optional[bool] = Field(default=None, description="노출 여부 필터")
    is_out: Optional[bool] = Field(default=None, description="탈퇴 여부 필터")
    start_dt: Optional[str] = Field(default=None, description="생성일 범위 시작 yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="생성일 범위 종료 yyyy-mm-dd")


class CounselorListItem(BaseModel):
    """상담사 목록 아이템 (m_state 포함)"""
    counselor_id: str
    counselor_code: str
    name: str
    nickname: str
    is_show: bool
    is_out: bool
    created_at: datetime
    specialty_types: Optional[List[str]] = None
    m_state: Optional[str] = Field(default=None, description="tm60_member.m_state")

    model_config = ConfigDict(from_attributes=True)


