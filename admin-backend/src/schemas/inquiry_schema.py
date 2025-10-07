"""
상담사 문의(Inquiry) 스키마 (관리자 백엔드)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class InquiryListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search_type: str = Field(default="all", description="all|user_title|user_content|reply_content")
    search_name: Optional[str] = Field(default=None)
    counselor_id: Optional[str] = Field(default=None, description="inquirer_id와 매칭")
    start_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")


class InquiryWithCounselorItem(BaseModel):
    inquiry: Dict[str, Any]
    counselor: Dict[str, Any]


class InquiryListResponse(BaseModel):
    items: List[InquiryWithCounselorItem]
    page: int
    limit: int
    total: int


class InquiryDetailResponse(BaseModel):
    inquiry: Dict[str, Any]
    counselor: Dict[str, Any]


class InquiryReplyUpdateRequest(BaseModel):
    inquiry_id: int
    reply_content: str = Field(..., min_length=1)


class InquiryUpdateRequest(BaseModel):
    inquiry_id: int
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    reply_content: Optional[str] = Field(None)


class InquiryDeleteResponse(BaseModel):
    inquiry_id: int
    deleted: bool


class UserInquiryListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search_type: str = Field(default="all", description="all|title|content")
    search_name: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None, description="inquirer_id와 매칭")
    start_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")


class InquiryWithUserItem(BaseModel):
    inquiry: Dict[str, Any]
    user: Dict[str, Any]


class UserInquiryListResponse(BaseModel):
    items: List[InquiryWithUserItem]
    page: int
    limit: int
    total: int


class InquiryUserDetailResponse(BaseModel):
    inquiry: Dict[str, Any]
    user: Dict[str, Any]


class UserToCsListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search_type: str = Field(default="all", description="all|user_title|user_content|reply_content")
    search_name: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)
    counselor_id: Optional[str] = Field(default=None)
    start_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")
    end_dt: Optional[str] = Field(default=None, description="yyyy-mm-dd")


class InquiryWithUserAndCounselorItem(BaseModel):
    inquiry: Dict[str, Any]
    user: Dict[str, Any]
    counselor: Dict[str, Any]


class UserToCsListResponse(BaseModel):
    items: List[InquiryWithUserAndCounselorItem]
    page: int
    limit: int
    total: int


class UserToCsDetailResponse(BaseModel):
    inquiry: Dict[str, Any]
    user: Dict[str, Any]
    counselor: Dict[str, Any]


