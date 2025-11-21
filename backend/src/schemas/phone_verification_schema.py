"""
휴대폰 본인인증 스키마

KCP 본인인증 요청/응답 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional


class PhoneVerificationInitiateRequest(BaseModel):
    """본인인증 시작 요청 - KCP 모달에서 사용자 정보 입력"""

    phone_number: str = Field(..., description="휴대폰 번호 (하이픈 없이)", pattern=r'^010\d{8}$')
    return_url: str = Field(default="/signup", description="인증 완료 후 리다이렉트할 URL (Fallback용)")


class PhoneVerificationForFindIdRequest(BaseModel):
    """ID 찾기용 본인인증 시작 요청"""

    return_url: str = Field(..., description="인증 완료 후 리다이렉트할 URL")


class PhoneVerificationForFindPasswordRequest(BaseModel):
    """비밀번호 찾기용 본인인증 시작 요청"""

    user_id: str = Field(..., description="사용자 ID")
    return_url: str = Field(..., description="인증 완료 후 리다이렉트할 URL")


class PhoneVerificationInitiateResponse(BaseModel):
    """본인인증 시작 응답"""

    gateway_url: str = Field(..., description="KCP 인증 게이트웨이 URL")
    form_data: dict = Field(..., description="KCP Form 데이터 (POST 전송용)")
    session_id: str = Field(..., description="세션 ID")
    site_cd: str = Field(..., description="KCP 사이트 코드")


class PhoneVerificationCallbackResponse(BaseModel):
    """본인인증 콜백 응답"""

    success: bool = Field(..., description="성공 여부")
    phone: str = Field(..., description="인증된 휴대폰 번호")
    phone_chk: str = Field(..., description="휴대폰 인증 토큰")
    ci: str = Field(..., description="연계정보 (CI)")
    di: str = Field(..., description="중복가입확인정보 (DI)")
    name: str = Field(..., description="인증된 이름")
    birth_date: str = Field(..., description="인증된 생년월일")
    gender: str = Field(..., description="인증된 성별")


class PhoneVerificationStatusResponse(BaseModel):
    """본인인증 상태 조회 응답"""

    status: str = Field(..., description="인증 상태 (initiated, verified)")
    name: Optional[str] = Field(None, description="사용자 이름")
    phone_number: Optional[str] = Field(None, description="휴대폰 번호")
    carrier: Optional[str] = Field(None, description="통신사")
    verified_at: Optional[str] = Field(None, description="인증 완료 시간")
