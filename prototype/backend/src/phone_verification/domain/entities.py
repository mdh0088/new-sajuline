"""
Phone Verification Domain Entities

핸드폰 인증 도메인 엔티티 정의
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    """인증 상태"""
    PENDING = "pending"          # 인증 대기
    IN_PROGRESS = "in_progress"  # 인증 진행 중
    COMPLETED = "completed"       # 인증 완료
    FAILED = "failed"            # 인증 실패
    EXPIRED = "expired"          # 인증 만료


class MobileCarrier(str, Enum):
    """이동통신사"""
    SKT = "SKT"
    KT = "KTF"
    LGT = "LGT"
    MVNO = "MVNO"  # 알뜰폰


class VerificationMethod(str, Enum):
    """인증 방법"""
    SMS = "SMS"      # SMS 인증
    PASS = "PASS"    # PASS 인증
    CARD = "CARD"    # 신용카드 인증


class PhoneVerificationRequest(BaseModel):
    """핸드폰 인증 요청"""
    name: str = Field(..., description="사용자 이름")
    birth_date: str = Field(..., pattern=r'^\d{8}$', description="생년월일 (YYYYMMDD)")
    phone_number: str = Field(..., pattern=r'^01[0-9]{8,9}$', description="휴대폰번호")
    carrier: MobileCarrier = Field(..., description="통신사")
    gender: str = Field(..., pattern=r'^[MF]$', description="성별 (M/F)")
    local_code: str = Field("01", description="내/외국인 (01:내국인, 02:외국인)")
    method: VerificationMethod = Field(VerificationMethod.SMS, description="인증방법", alias="verification_method")
    return_url: Optional[str] = Field(None, description="인증 완료 후 리턴 URL")
    

class PhoneVerificationSession(BaseModel):
    """핸드폰 인증 세션"""
    session_id: str = Field(..., description="세션 ID (ordr_idxx)")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    status: VerificationStatus = Field(VerificationStatus.PENDING, description="인증 상태")
    request_data: PhoneVerificationRequest = Field(..., description="인증 요청 데이터")
    cert_no: Optional[str] = Field(None, description="인증 번호")
    enc_cert_data: Optional[str] = Field(None, description="암호화된 인증 데이터")
    up_hash: Optional[str] = Field(None, description="요청 해시")
    dn_hash: Optional[str] = Field(None, description="응답 해시")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정 시간")
    expires_at: datetime = Field(..., description="만료 시간")


class PhoneVerificationResult(BaseModel):
    """핸드폰 인증 결과"""
    session_id: str = Field(..., description="세션 ID")
    cert_no: str = Field(..., description="인증 번호")
    comm_id: str = Field(..., description="통신사 코드")
    phone_no: str = Field(..., description="전화번호")
    user_name: str = Field(..., description="이름")
    birth_day: str = Field(..., description="생년월일")
    sex_code: str = Field(..., description="성별 코드")
    local_code: str = Field(..., description="내/외국인 코드")
    ci: str = Field(..., description="CI (연계정보)")
    di: str = Field(..., description="DI (중복가입확인정보)")
    res_cd: str = Field(..., description="결과 코드")
    res_msg: str = Field(..., description="결과 메시지")
    verified_at: datetime = Field(default_factory=datetime.utcnow, description="인증 완료 시간")


class KCPConfiguration(BaseModel):
    """KCP 설정"""
    site_cd: str = Field(..., description="사이트 코드")
    site_key: str = Field(..., description="사이트 키 (암호화 키)")
    web_siteid: str = Field(..., description="웹사이트 ID")
    gateway_url: str = Field(..., description="KCP 게이트웨이 URL")
    return_url: str = Field(..., description="인증 결과 리턴 URL")
    home_dir: str = Field(..., description="KCP 바이너리 파일 홈 디렉토리 (pp_cli, pp_cli_exe 경로)")
    enc_key: str = Field(..., description="KCP 암호화 키 (g_conf_ENC_KEY)")
    cert_otp_use: str = Field("Y", description="OTP 사용 여부")
    cert_enc_use_ext: str = Field("Y", description="암호화 고도화 사용")
    is_test_mode: bool = Field(False, description="테스트 모드 여부")
    
    @property
    def cert_url(self) -> str:
        """KCP 인증창 URL (gateway_url과 동일)"""
        return self.gateway_url
    
    @property
    def ret_url(self) -> str:
        """인증 결과 리턴 URL (return_url과 동일)"""
        return self.return_url


class PhoneVerificationInitResponse(BaseModel):
    """인증 시작 응답"""
    session_id: str = Field(..., description="세션 ID")
    gateway_url: str = Field(..., description="KCP 인증창 URL")
    up_hash: str = Field(..., description="요청 해시값")
    form_data: dict = Field(..., description="폼 데이터")
    expires_at: datetime = Field(..., description="만료 시간")


class PhoneVerificationCallbackRequest(BaseModel):
    """KCP 콜백 요청"""
    site_cd: str = Field(..., description="사이트 코드")
    ordr_idxx: str = Field(..., description="요청 번호 (세션 ID)")
    cert_no: str = Field(..., description="인증 번호")
    enc_cert_data2: str = Field(..., description="암호화된 인증 데이터")
    dn_hash: str = Field(..., description="응답 해시")
    res_cd: str = Field(..., description="결과 코드")
    res_msg: Optional[str] = Field(None, description="결과 메시지")


class PhoneVerificationStatusResponse(BaseModel):
    """인증 상태 응답"""
    session_id: str = Field(..., description="세션 ID")
    status: VerificationStatus = Field(..., description="인증 상태")
    result: Optional[PhoneVerificationResult] = Field(None, description="인증 결과")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    expires_at: datetime = Field(..., description="만료 시간")