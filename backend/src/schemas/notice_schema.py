"""
공지사항 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from src.models.notice_model import NoticeType, TargetAudience


class NoticeBase(BaseModel):
    """공지사항 기본 스키마"""
    notice_type: NoticeType = Field(default=NoticeType.GENERAL, description="공지 타입")
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    target_audience: TargetAudience = Field(default=TargetAudience.ALL, description="대상")
    is_important: bool = Field(default=False, description="중요 공지")
    is_popup: bool = Field(default=False, description="팝업 표시")
    is_active: bool = Field(default=True, description="활성화 여부")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="첨부파일")


class NoticeResponse(NoticeBase):
    """공지사항 응답 스키마"""
    notice_id: int = Field(..., description="공지사항 ID")
    view_count: int = Field(..., ge=0, description="조회수")
    created_by: int = Field(..., description="작성자 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
    # 작성자 정보 (필요시 Join으로 가져올 수 있음)
    admin_name: Optional[str] = Field(None, description="작성자명")
    
    model_config = ConfigDict(from_attributes=True)


class NoticeListParams(BaseModel):
    """공지사항 목록 조회 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    notice_type: Optional[NoticeType] = Field(None, description="공지 타입 필터")
    target_audience: Optional[TargetAudience] = Field(None, description="대상 필터")
    is_active: Optional[bool] = Field(None, description="활성화 상태 필터")
    is_important: Optional[bool] = Field(None, description="중요 공지 필터")
    search: Optional[str] = Field(None, description="제목/내용 검색어")


# 상세 응답 (이전/다음 ID 포함)
class NoticeDetailResponse(NoticeResponse):
    """공지사항 상세 응답 스키마 (이전/다음 이동용 ID 포함)"""
    before_notice_id: Optional[int] = Field(None, description="이전 공지 notice_id (없으면 null)")
    after_notice_id: Optional[int] = Field(None, description="다음 공지 notice_id (없으면 null)")

