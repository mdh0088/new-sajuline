"""
Simplified Phone Verification Application Service

Integrates Redis session management with proper KCP binary authentication.
IMPORTANT: Must use KCP ct_cli binary for all hash operations and encryption.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import secrets

from ..domain.simplified_entities import (
    SendCodeRequest,
    SendCodeResponse,
    VerifyCodeRequest,
    VerifyCodeResponse,
    CheckVerifiedRequest,
    CheckVerifiedResponse
)
from ..infrastructure.redis_service import phone_verification_redis
from ..infrastructure.kcp_service import KCPService, KCPEncryptor
from ..infrastructure.kcp_config import get_kcp_configuration
from ..infrastructure.simplified_repository import SimplifiedPhoneVerificationRepository
from ..domain.services import PhoneVerificationDomainService
from src.common.exceptions.custom import ValidationError, BusinessLogicError, ExternalServiceError
from src.common.database.session import get_db

logger = logging.getLogger(__name__)


class SimplifiedPhoneVerificationService:
    """
    간소화된 핸드폰 인증 서비스
    
    KCP 바이너리 프로토콜을 완전히 준수하면서 Redis로 세션 관리
    """
    
    def __init__(self):
        self.redis_service = phone_verification_redis
        self.kcp_config = get_kcp_configuration()
        self.kcp_service = KCPService(self.kcp_config)
        self.domain_service = PhoneVerificationDomainService()
    
    async def send_verification_code(
        self,
        request: SendCodeRequest
    ) -> SendCodeResponse:
        """
        인증 코드 발송 (KCP 프로토콜 준수)
        
        1. Redis에 세션 생성 및 코드 저장
        2. KCP up_hash 생성 (ct_cli 바이너리 사용)
        3. SMS 발송 
        4. 세션 ID와 up_hash 반환
        """
        try:
            # Create verification session in Redis
            session_id, verification_code, expires_at = await self.redis_service.create_verification_session(
                phone=request.phone,
                name=request.name,
                birth_date=request.birth_date
            )
            
            # KCP up_hash 생성을 위한 데이터 준비
            # PHP 코드 참조: smartcert_proc_req.php line 167-176
            birth_str = request.birth_date.replace("-", "")  # YYYY-MM-DD -> YYYYMMDD
            year = birth_str[0:4] if birth_str else "0000"
            month = birth_str[4:6] if birth_str else "00" 
            day = birth_str[6:8] if birth_str else "00"
            
            # sex_code와 local_code는 기본값 사용 (실제 구현 시 사용자 입력 받아야 함)
            sex_code = ""  # 성별 코드 (비어있을 수 있음)
            local_code = "01"  # 내국인
            
            # up_hash 데이터 생성 (PHP smartcert_proc_req.php 참조)
            hash_data = (
                self.kcp_config.site_cd +  # site_cd
                session_id +                # ordr_idxx (세션 ID를 주문번호로 사용)
                self.kcp_config.web_siteid + # web_siteid  
                request.name +               # user_name
                year +                       # year
                month +                      # month
                day +                        # day
                sex_code +                   # sex_code
                local_code                   # local_code
            )
            
            # KCP ct_cli 바이너리를 사용하여 up_hash 생성
            up_hash = self.kcp_service.make_hash_data(hash_data)
            
            # Redis에 up_hash 저장 (나중에 dn_hash 검증을 위해)
            await self.redis_service.update_session_data(
                session_id=session_id,
                data={"up_hash": up_hash}
            )
            
            # Send SMS via KCP (if in production mode)
            if not self.kcp_config.is_test_mode:
                try:
                    # KCP SMS 발송을 위한 데이터 준비
                    sms_result = await self._send_sms_via_kcp(
                        phone=request.phone,
                        code=verification_code,
                        name=request.name
                    )
                    
                    if not sms_result:
                        # SMS 발송 실패 시 세션 삭제
                        await self.redis_service.delete_session(session_id)
                        raise ExternalServiceError("SMS 발송에 실패했습니다. 잠시 후 다시 시도해주세요.")
                        
                except Exception as e:
                    logger.error(f"KCP SMS sending failed: {e}")
                    # SMS 발송 실패 시 세션 삭제
                    await self.redis_service.delete_session(session_id)
                    raise ExternalServiceError("SMS 발송 중 오류가 발생했습니다.")
            else:
                # Test mode - log the code and up_hash
                logger.info(f"[TEST MODE] Verification code for {request.phone}: {verification_code}")
                logger.info(f"[TEST MODE] up_hash: {up_hash[:20]}...")
            
            # Calculate remaining time
            remaining_time = int((expires_at - datetime.utcnow()).total_seconds())
            
            return SendCodeResponse(
                session_id=session_id,
                expires_at=expires_at,
                remaining_time=remaining_time,
                message=f"인증번호가 {request.phone}로 발송되었습니다.",
                up_hash=up_hash  # KCP 인증창 호출을 위해 필요
            )
            
        except (ValidationError, BusinessLogicError, ExternalServiceError):
            raise
        except Exception as e:
            logger.error(f"Failed to send verification code: {e}")
            raise BusinessLogicError("인증 코드 발송 중 오류가 발생했습니다.")
    
    async def verify_code(
        self,
        request: VerifyCodeRequest
    ) -> VerifyCodeResponse:
        """
        인증 코드 확인
        
        1. Redis에서 세션 조회
        2. 코드 검증
        3. 성공 시 토큰 발급
        """
        try:
            # Verify code
            success, token, verified_data = await self.redis_service.verify_code(
                session_id=request.session_id,
                code=request.code
            )
            
            if success and token and verified_data:
                # KCP 암호화 플래그 생성 (기존 PHP 방식 호환)
                phone_chk = KCPEncryptor.encrypt_phone_verification_flag()
                
                return VerifyCodeResponse(
                    verified=True,
                    token=token,
                    phone=verified_data.get("phone"),
                    message="핸드폰 인증이 완료되었습니다.",
                    phone_chk=phone_chk  # 프론트엔드 호환을 위한 암호화 플래그
                )
            else:
                return VerifyCodeResponse(
                    verified=False,
                    token=None,
                    phone=None,
                    message="인증에 실패했습니다."
                )
                
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Failed to verify code: {e}")
            raise BusinessLogicError("인증 코드 확인 중 오류가 발생했습니다.")
    
    async def check_verified(
        self,
        request: CheckVerifiedRequest
    ) -> CheckVerifiedResponse:
        """
        인증 상태 확인
        
        토큰으로 인증 여부 확인
        """
        try:
            # Check verification token
            verified_data = await self.redis_service.check_verification_token(request.token)
            
            if verified_data:
                return CheckVerifiedResponse(
                    verified=True,
                    phone=verified_data.get("phone"),
                    verified_at=datetime.fromisoformat(verified_data.get("verified_at")),
                    user_info=verified_data.get("user_info")
                )
            else:
                return CheckVerifiedResponse(
                    verified=False,
                    phone=None,
                    verified_at=None,
                    user_info=None
                )
                
        except Exception as e:
            logger.error(f"Failed to check verification: {e}")
            raise BusinessLogicError("인증 확인 중 오류가 발생했습니다.")
    
    async def resend_code(
        self,
        session_id: str
    ) -> SendCodeResponse:
        """
        인증 코드 재발송
        
        기존 세션의 정보로 새 세션 생성
        """
        try:
            # Get existing session
            session_data = await self.redis_service.get_verification_session(session_id)
            if not session_data:
                raise ValidationError("인증 세션이 만료되었거나 존재하지 않습니다.")
            
            # Delete old session
            await self.redis_service.delete_session(session_id)
            
            # Create new session with same data
            request = SendCodeRequest(
                phone=session_data["phone"],
                name=session_data["user_info"]["name"],
                birth_date=session_data["user_info"]["birth_date"]
            )
            
            return await self.send_verification_code(request)
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Failed to resend code: {e}")
            raise BusinessLogicError("인증 코드 재발송 중 오류가 발생했습니다.")
    
    async def process_kcp_callback(
        self,
        site_cd: str,
        ordr_idxx: str,  # session_id
        cert_no: str,
        enc_cert_data2: str,
        dn_hash: str,
        res_cd: str
    ) -> Dict[str, Any]:
        """
        KCP 인증 콜백 처리 (smartcert_proc_res.php 로직 구현)
        
        1. dn_hash 검증 (ct_cli 바이너리 사용)
        2. enc_cert_data2 복호화 (ct_cli 바이너리 사용)  
        3. CI/DI 추출 및 저장
        """
        try:
            # 결과 코드 확인
            if res_cd != "0000":
                logger.error(f"KCP authentication failed with code: {res_cd}")
                return {
                    "success": False,
                    "message": "본인인증에 실패했습니다."
                }
            
            # dn_hash 검증 (PHP smartcert_proc_res.php line 116-122 참조)
            veri_str = site_cd + ordr_idxx + cert_no  # 검증 문자열 생성
            
            # KCP ct_cli 바이너리를 사용하여 dn_hash 검증
            is_valid = self.kcp_service.check_valid_hash(dn_hash, veri_str)
            
            if not is_valid:
                logger.error("dn_hash validation failed - possible data tampering")
                return {
                    "success": False,
                    "message": "데이터 무결성 검증에 실패했습니다."
                }
            
            # enc_cert_data2 복호화 (PHP smartcert_proc_res.php line 135 참조)
            decrypted_data = self.kcp_service.decrypt_enc_cert(
                cert_no=cert_no,
                enc_cert_data=enc_cert_data2,
                opt="1"  # UTF-8 인코딩 옵션
            )
            
            if not decrypted_data:
                logger.error("Failed to decrypt enc_cert_data2")
                return {
                    "success": False,
                    "message": "인증 데이터 복호화에 실패했습니다."
                }
            
            # 복호화된 데이터에서 필요한 정보 추출
            phone_no = decrypted_data.get("phone_no", "")
            user_name = decrypted_data.get("user_name", "")
            birth_day = decrypted_data.get("birth_day", "")
            ci_url = decrypted_data.get("ci_url", "")  # CI 값
            di_url = decrypted_data.get("di_url", "")  # DI 값 (중복가입 확인용)
            
            # Redis 세션 업데이트 (CI/DI 포함)
            session_data = await self.redis_service.get_verification_session(ordr_idxx)
            if session_data:
                await self.redis_service.update_session_data(
                    session_id=ordr_idxx,
                    data={
                        "kcp_verified": True,
                        "ci": ci_url,
                        "di": di_url,
                        "verified_phone": phone_no,
                        "verified_name": user_name,
                        "verified_birth": birth_day
                    }
                )
            
            # DB에 인증 결과 저장 (CI/DI 영구 보관)
            try:
                async for db in get_db():
                    repo = SimplifiedPhoneVerificationRepository(db)
                    await repo.save_verification(
                        phone_no=phone_no,
                        user_name=user_name,
                        birth_date=birth_day,
                        ci=ci_url,
                        di=di_url,
                        cert_no=cert_no,
                        res_cd=res_cd
                    )
                    break
            except Exception as e:
                logger.error(f"Failed to save verification to DB: {e}")
                # DB 저장 실패해도 인증은 성공으로 처리
            
            # PHP 호환 암호화 플래그 생성
            phone_chk = KCPEncryptor.encrypt_phone_verification_flag()
            
            return {
                "success": True,
                "phone": phone_no,
                "name": user_name,
                "birth_day": birth_day,
                "ci": ci_url,
                "di": di_url,
                "phone_chk": phone_chk,
                "message": "본인인증이 완료되었습니다."
            }
            
        except Exception as e:
            logger.error(f"KCP callback processing failed: {e}")
            return {
                "success": False,
                "message": "인증 처리 중 오류가 발생했습니다."
            }
    
    async def _send_sms_via_kcp(
        self,
        phone: str,
        code: str,
        name: str
    ) -> bool:
        """
        SMS 발송 (KCP 본인인증과 별개)
        
        Note: KCP는 본인인증 서비스이므로 
        실제 SMS는 별도 서비스 사용 권장
        """
        try:
            # 실제 SMS 서비스 API 호출
            # 예: AWS SNS, Twilio, 알리고 등
            
            # 임시로 로그만 남김
            logger.info(f"[SMS] Sending code {code} to {phone} for {name}")
            
            # 실제 구현 시:
            # - SMS 전송 서비스 API 호출
            # - 발송 결과 확인
            
            return True
            
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False


# Singleton instance
simplified_phone_verification_service = SimplifiedPhoneVerificationService()

