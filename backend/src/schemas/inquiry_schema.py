"""
1:1 문의 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.models.inquiry_model import InquirerType


class InquiryBase(BaseModel):
    """1:1 문의 기본 스키마"""
    inquirer_type: InquirerType = Field(..., description="문의자 타입: USER, COUNSELOR, GUEST")
    inquirer_id: Optional[str] = Field(None, description="문의자 ID")
    counselor_id: Optional[str] = Field(None, description="문의 상담사 ID")
    category: Optional[str] = Field(None, description="문의 카테고리")
    title: Optional[str] = Field(None, description="제목")
    content: str = Field(..., min_length=1, description="내용")


class InquiryCreate(InquiryBase):
    """1:1 문의 생성 요청 스키마"""
    pass


class UserInquiryCreateRequest(BaseModel):
    """사용자 → 상담사 문의 생성 요청 스키마 (클라이언트 입력)
    서버가 inquirer_type/inquirer_id를 세션으로 보강하므로 노출하지 않음
    """
    counselor_id: str = Field(..., description="문의 대상 상담사 ID")
    category: Optional[str] = Field(None, description="문의 카테고리")
    title: Optional[str] = Field(None, description="제목")
    content: str = Field(..., min_length=1, description="내용")


class InquiryUpdate(BaseModel):
    """1:1 문의 수정 요청 스키마"""
    category: Optional[str] = Field(None, description="문의 카테고리")
    title: Optional[str] = Field(None, description="제목")
    content: Optional[str] = Field(None, min_length=1, description="내용")


class AdminReplyCreate(BaseModel):
    """관리자 답변 생성 요청 스키마"""
    reply_content: str = Field(..., min_length=1, description="관리자 답변")


class InquiryResponse(InquiryBase):
    """1:1 문의 응답 스키마"""
    inquiry_id: int = Field(..., description="문의 ID")
    inquiry_type: Optional[str] = Field(None, description="문의 유형: PAY, ACCOUNT, CS, EVENT, ETC")
    is_read: bool = Field(..., description="읽음 상태")
    reply_content: Optional[str] = Field(None, description="관리자 답변")
    answered_at: Optional[datetime] = Field(None, description="답변 시간")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    model_config = ConfigDict(from_attributes=True)


class InquirySummary(BaseModel):
    """1:1 문의 요약 정보 (목록 조회용)"""
    inquiry_id: int = Field(..., description="문의 ID")
    inquirer_type: InquirerType = Field(..., description="문의자 타입")
    inquirer_id: Optional[str] = Field(None, description="문의자 ID")
    counselor_id: Optional[str] = Field(None, description="문의 상담사 ID")
    category: Optional[str] = Field(None, description="문의 카테고리")
    inquiry_type: Optional[str] = Field(None, description="문의 유형: PAY, ACCOUNT, CS, EVENT, ETC")
    title: Optional[str] = Field(None, description="제목")
    content: Optional[str] = Field(None, description="내용")
    reply_content: Optional[str] = Field(None, description="관리자 답변")
    answered_at: Optional[datetime] = Field(None, description="답변 시간")
    is_read: bool = Field(..., description="읽음 상태")
    has_reply: bool = Field(False, description="답변 여부")
    created_at: datetime = Field(..., description="생성일시")

    model_config = ConfigDict(from_attributes=True)


class InquiryListParams(BaseModel):
    """1:1 문의 목록 조회 파라미터"""
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지당 항목 수")
    inquirer_type: Optional[InquirerType] = Field(None, description="문의자 타입 필터")
    inquirer_id: Optional[str] = Field(None, description="문의자 ID 필터")
    counselor_id: Optional[str] = Field(None, description="상담사 ID 필터")
    category: Optional[str] = Field(None, description="카테고리 필터")
    is_read: Optional[bool] = Field(None, description="읽음 상태 필터")
    has_reply: Optional[bool] = Field(None, description="답변 여부 필터")
    search: Optional[str] = Field(None, description="제목/내용 검색어")


class InquiryListResponse(BaseModel):
    """1:1 문의 목록 응답 스키마"""
    inquiries: list[InquirySummary] = Field(..., description="문의 목록")
    total: int = Field(..., description="전체 문의 수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 항목 수")


class InquiryStatistics(BaseModel):
    """1:1 문의 통계 정보"""
    total_count: int = Field(..., description="전체 문의 수")
    unread_count: int = Field(..., description="미읽음 문의 수")
    unanswered_count: int = Field(..., description="미답변 문의 수")
    user_inquiries: int = Field(..., description="사용자 문의 수")
    counselor_inquiries: int = Field(..., description="상담사 문의 수")
    guest_inquiries: int = Field(..., description="비회원 문의 수")


class UserAdminInquiryCreateRequest(BaseModel):
    """사용자 → 관리자 문의 생성 요청 스키마

    category는 'USER_TO_ADMIN'으로 자동 설정
    inquirer_type은 'USER'로 자동 설정
    inquirer_id는 로그인한 user_id로 자동 설정
    """
    inquiry_type: str = Field(..., description="문의 유형: PAY(결제문의), ACCOUNT(계정문의), CS(상담문의), EVENT(이벤트문의), ETC(기타문의)")
    title: Optional[str] = Field(None, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="문의 내용")

    model_config = ConfigDict(from_attributes=True)


class CounselorReplyRequest(BaseModel):
    """상담사가 사용자 문의에 답변하는 요청 스키마"""
    reply_content: str = Field(..., min_length=1, description="답변 내용")

    model_config = ConfigDict(from_attributes=True)


class CounselorAdminInquiryCreateRequest(BaseModel):
    """상담사 → 관리자 문의 생성 요청 스키마

    category는 'CS_TO_ADMIN'으로 자동 설정
    inquirer_type은 'COUNSELOR'로 자동 설정
    inquirer_id는 로그인한 counselor_id로 자동 설정
    """
    inquiry_type: str = Field(..., description="문의 유형: PAY(결제문의), ACCOUNT(계정문의), CS(상담문의), EVENT(이벤트문의), ETC(기타문의)")
    title: Optional[str] = Field(None, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="문의 내용")

    model_config = ConfigDict(from_attributes=True)