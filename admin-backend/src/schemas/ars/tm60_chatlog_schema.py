"""
ARS tm60_chatlog 스키마 (MSSQL)
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Tm60ChatlogBase(BaseModel):
    """tm60_chatlog 기본 스키마"""
    fdnis: str
    m_code: str
    m_name: str
    m_nickname: str
    u_tel: str
    t_tel: str
    u_id: str
    u_name: str


class Tm60ChatlogResponse(Tm60ChatlogBase):
    """tm60_chatlog 응답 스키마"""
    idx: int

    # 시간 정보
    starttm: Optional[str] = ""
    endtm: Optional[str] = ""
    chatstart: Optional[str] = ""
    chatend: Optional[str] = ""

    # 날짜/시간 분리 필드
    yyyy: str
    mm: str
    dd: str
    hh: str

    # 파일 및 상태
    fname: str
    scode: str
    platform: str

    # 채팅 시간
    chattm: int
    realchattm: int

    # 요금 정보
    usepoint: int
    fee: int
    t_money: int
    t2_money: float

    # 상태 플래그
    success: int
    call_chk: int
    menu: int

    # 통화 정보
    call_span: int
    calltm: int

    # 단위 요금
    unit_use: int
    unit_sec: int
    unit_fee: float
    prate: int

    model_config = ConfigDict(from_attributes=True)


class Tm60ChatlogListResponse(BaseModel):
    """tm60_chatlog 목록 응답 스키마"""
    items: list[Tm60ChatlogResponse]
    total: int


class Tm60ChatlogSearchParams(BaseModel):
    """tm60_chatlog 검색 파라미터"""
    yyyy: Optional[str] = None
    mm: Optional[str] = None
    dd: Optional[str] = None
    m_code: Optional[str] = None
    m_nickname: Optional[str] = None
    u_id: Optional[str] = None
    platform: Optional[str] = None
    success: Optional[int] = None
    page: int = 1
    page_size: int = 20
