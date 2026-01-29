"""
ARS tm60_users 스키마 (MSSQL)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Tm60UsersBase(BaseModel):
    """tm60_users 기본 스키마"""
    u_id: str
    u_tel: str
    u_kname: str
    u_memcd: str
    u_login: str
    u_state: str
    u_point: int
    u_memo: str = ""


class Tm60UsersResponse(Tm60UsersBase):
    """tm60_users 응답 스키마"""
    idx: int
    u_fdate: Optional[datetime] = None
    u_rdate: Optional[datetime] = None
    regdate: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Tm60UsersListResponse(BaseModel):
    """tm60_users 목록 응답 스키마"""
    items: list[Tm60UsersResponse]
    total: int
