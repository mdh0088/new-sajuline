"""
Phone Verification Domain Services

핸드폰 인증 도메인 서비스 (비즈니스 로직)
"""
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .entities import (
    PhoneVerificationSession,
    PhoneVerificationRequest,
    PhoneVerificationResult,
    VerificationStatus,
    KCPConfiguration
)


class PhoneVerificationDomainService:
    """핸드폰 인증 도메인 서비스"""
    
    @staticmethod
    def generate_session_id() -> str:
        """세션 ID 생성 (요청번호)"""
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S") + str(now.microsecond)[:6]
    
    @staticmethod
    def generate_hash(kcp_config: KCPConfiguration, data: str) -> str:
        """
        KCP 해시 생성
        PHP의 make_hash_data 함수 포팅
        """
        # KCP 라이브러리의 해시 생성 로직
        # 실제 구현은 KCP 바이너리를 호출하거나 동일한 알고리즘 구현 필요
        # 여기서는 간단한 예시로 SHA256 사용
        hash_str = f"{kcp_config.site_key}{data}"
        return hashlib.sha256(hash_str.encode()).hexdigest()
    
    @staticmethod
    def verify_hash(kcp_config: KCPConfiguration, hash_value: str, data: str) -> bool:
        """
        KCP 해시 검증
        PHP의 check_valid_hash 함수 포팅
        """
        expected_hash = PhoneVerificationDomainService.generate_hash(kcp_config, data)
        return hash_value == expected_hash
    
    @staticmethod
    def create_up_hash_data(
        session: PhoneVerificationSession,
        kcp_config: KCPConfiguration
    ) -> str:
        """up_hash 생성을 위한 데이터 조합"""
        request = session.request_data
        
        # 날짜 데이터 파싱
        year = month = day = "00"
        if request.birth_date:
            year = request.birth_date[:4]
            month = request.birth_date[4:6]
            day = request.birth_date[6:8]
        
        # cert_able_yn="Y"일 때 (인증창 입력 활성화 시) - 사용자 정보 없이 해시 생성
        # PHP: if ( $cert_able_yn == "Y" ) { $hash_data = $site_cd . $ordr_idxx . $web_siteid . "" . "00" . "00" . "00" . "" . ""; }
        hash_data = (
            f"{kcp_config.site_cd}"
            f"{session.session_id}"
            f"{kcp_config.web_siteid}"
            f""  # user_name (빈 값)
            f"00"  # year (00)
            f"00"  # month (00) 
            f"00"  # day (00)
            f""  # sex_code (빈 값)
            f""  # local_code (빈 값)
        )
        
        return hash_data
    
    @staticmethod
    def create_dn_hash_verification_data(
        site_cd: str,
        session_id: str,
        cert_no: str
    ) -> str:
        """dn_hash 검증을 위한 데이터 조합"""
        return f"{site_cd}{session_id}{cert_no}"
    
    @staticmethod
    def validate_session_expiry(session: PhoneVerificationSession) -> bool:
        """세션 만료 여부 확인"""
        return datetime.utcnow() < session.expires_at
    
    @staticmethod
    def can_start_verification(session: PhoneVerificationSession) -> bool:
        """인증 시작 가능 여부 확인"""
        return (
            session.status == VerificationStatus.PENDING
            and PhoneVerificationDomainService.validate_session_expiry(session)
        )
    
    @staticmethod
    def can_complete_verification(session: PhoneVerificationSession) -> bool:
        """인증 완료 가능 여부 확인"""
        return (
            session.status == VerificationStatus.IN_PROGRESS
            and PhoneVerificationDomainService.validate_session_expiry(session)
        )
    
    @staticmethod
    def create_form_data(
        session: PhoneVerificationSession,
        kcp_config: KCPConfiguration,
        up_hash: str
    ) -> Dict[str, Any]:
        """KCP 인증창에 전달할 폼 데이터 생성"""
        request = session.request_data
        
        # KCP 인증 방법 코드 매핑
        method_mapping = {
            "SMS": "01",
            "PASS": "02", 
            "CARD": "03"
        }
        cert_method = method_mapping.get(request.method.value, "01")
        
        form_data = {
            "ordr_idxx": session.session_id,
            "req_tx": "cert",
            "cert_method": cert_method,
            "web_siteid": kcp_config.web_siteid,
            "site_cd": kcp_config.site_cd,
            "Ret_URL": kcp_config.return_url,
            "cert_otp_use": kcp_config.cert_otp_use,
            "cert_enc_use_ext": kcp_config.cert_enc_use_ext,
            "up_hash": up_hash,
            "cert_able_yn": "Y" if request.name else "",
            "web_siteid_hashYN": "Y",
            "param_opt_1": session.user_id or "",
            "param_opt_2": "",
            "param_opt_3": ""
        }
        
        # 사용자 정보가 있는 경우 추가
        if request.name:
            form_data.update({
                "user_name": request.name,
                "year": request.birth_date[:4] if request.birth_date else "",
                "month": request.birth_date[4:6] if request.birth_date else "",
                "day": request.birth_date[6:8] if request.birth_date else "",
                "sex_code": request.gender or "",
                "local_code": request.local_code or "01"
            })
        
        # 통신사 고정 설정
        if request.carrier:
            form_data["fix_commid"] = request.carrier.value
        
        return form_data
    
    @staticmethod
    def mask_phone_number(phone_no: str) -> str:
        """전화번호 마스킹"""
        if len(phone_no) < 7:
            return phone_no
        return f"{phone_no[:3]}****{phone_no[-4:]}"
    
    @staticmethod
    def format_phone_number(phone_no: str) -> str:
        """전화번호 포맷팅 (하이픈 추가)"""
        phone_no = phone_no.replace("-", "")
        
        if len(phone_no) == 11:
            return f"{phone_no[:3]}-{phone_no[3:7]}-{phone_no[7:]}"
        elif len(phone_no) == 10:
            if phone_no[:2] == "02":
                return f"{phone_no[:2]}-{phone_no[2:6]}-{phone_no[6:]}"
            else:
                return f"{phone_no[:3]}-{phone_no[3:6]}-{phone_no[6:]}"
        elif len(phone_no) == 8:
            # 특수번호
            return f"{phone_no[:4]}-{phone_no[4:]}"
        
        return phone_no