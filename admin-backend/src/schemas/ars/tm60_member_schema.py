"""
ARS tm60_member 스키마 (MSSQL)
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Tm60MemberResponse(BaseModel):
    idx: int
    m_dnis: str
    m_code: str
    m_name: str
    m_nickname: str
    m_tel: str
    m_tel1: str
    m_tel2: str
    m_mobile: str
    m_state: str
    m_nextstate: str
    m_counselling: str
    m_id: str
    m_memo: Optional[str] = ""
    last_chat: str
    chat_level: str
    class_: str = Field(alias="class")
    turn: str
    bang: str
    holdoff: str
    m_bunho: str
    m_writer: int
    m_prate: int
    m_fdate: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


