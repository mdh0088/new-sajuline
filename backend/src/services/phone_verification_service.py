"""
휴대폰 본인인증 서비스

KCP 본인인증 API를 사용한 휴대폰 인증 처리
"""
import uuid
import redis.asyncio as redis
from typing import Optional, Dict
from datetime import datetime, timedelta

from src.common.utils.kcp_utils import (
    make_hash_data,
    check_valid_hash,
    decrypt_enc_cert,
    get_kcp_gateway_url,
    get_kcp_callback_url,
    get_kcp_site_cd,
    get_kcp_web_siteid,
    xor_encrypt,
    xor_decrypt,
    normalize_phone_number
)
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError


class PhoneVerificationService:
    """휴대폰 본인인증 서비스"""

    def __init__(self, redis_client: redis.Redis):
        """
        Args:
            redis_client: Redis 클라이언트 (세션 저장용)
        """
        self.redis = redis_client

    async def initiate_verification(
        self,
        phone_number: str
    ) -> Dict[str, str]:
        """본인인증 프로세스 시작

        Args:
            phone_number: 휴대폰 번호 (하이픈 없이)

        Returns:
            Dict[str, str]: gateway_url, session_id 포함

        Raises:
            ValidationError: 입력값 검증 실패
        """
        log = get_logger_with_request_id()

        # 입력값 검증
        self._validate_input(phone_number)

        # 세션 ID 생성 (KCP ordr_idxx)
        session_id = f"PHONE_{uuid.uuid4().hex[:20]}"

        # Redis에 세션 정보 저장 (15분 TTL)
        session_data = {
            "phone_number": phone_number,
            "status": "initiated",
            "created_at": datetime.utcnow().isoformat()
        }

        await self._save_session(session_id, session_data, ttl=900)

        # KCP 게이트웨이 파라미터 생성
        site_cd = get_kcp_site_cd()
        web_siteid = get_kcp_web_siteid()
        callback_url = get_kcp_callback_url()

        # 인증 데이터 해시 생성 (cert_able_yn="Y" 모드 - 사용자가 KCP 모달에서 직접 입력)
        # 프로토타입 참조: site_cd + ordr_idxx + web_siteid + "" + "00" + "00" + "00" + "" + ""
        # = site_cd + session_id + web_siteid + "000000"
        cert_data = f"{site_cd}{session_id}{web_siteid}000000"
        hash_data = make_hash_data(cert_data)

        # KCP 게이트웨이 URL (Form POST 방식)
        gateway_url = get_kcp_gateway_url()

        # KCP Form 데이터 (cert_able_yn="Y" 모드 - 사용자가 KCP 모달에서 직접 입력)
        form_data = {
            "site_cd": site_cd,
            "ordr_idxx": session_id,
            "Ret_URL": callback_url,
            "req_tx": "cert",
            "cert_method": "01",
            "web_siteid": web_siteid,
            "web_siteid_hashYN": "Y",
            "cert_able_yn": "Y",
            "up_hash": hash_data,
            "cert_otp_use": "Y",
            "cert_enc_use_ext": "Y",
            "param_opt_1": "",
            "param_opt_2": "",
            "param_opt_3": ""
        }

        log.info("Phone verification initiated",
                session_id=session_id,
                phone=phone_number[:3] + "****" + phone_number[-4:])

        return {
            "gateway_url": gateway_url,
            "form_data": form_data,
            "session_id": session_id,
            "site_cd": site_cd
        }

    async def initiate_verification_for_find_id(
        self,
        return_url: str
    ) -> Dict[str, str]:
        """ID 찾기용 본인인증 프로세스 시작 (전화번호 미입력)

        Args:
            return_url: 인증 완료 후 리다이렉트할 URL (모바일 fallback용)

        Returns:
            Dict[str, str]: gateway_url, session_id 포함
        """
        log = get_logger_with_request_id()

        # 세션 ID 생성 (KCP ordr_idxx)
        session_id = f"FINDID_{uuid.uuid4().hex[:18]}"

        # Redis에 세션 정보 저장 (15분 TTL)
        session_data = {
            "phone_number": "01000000000",  # 더미 값
            "status": "initiated",
            "purpose": "find_id",  # ID 찾기 용도 표시
            "return_url": return_url,
            "created_at": datetime.utcnow().isoformat()
        }

        await self._save_session(session_id, session_data, ttl=900)

        # KCP 게이트웨이 파라미터 생성
        site_cd = get_kcp_site_cd()
        web_siteid = get_kcp_web_siteid()
        callback_url = get_kcp_callback_url()

        # 인증 데이터 해시 생성
        cert_data = f"{site_cd}{session_id}{web_siteid}000000"
        hash_data = make_hash_data(cert_data)

        # KCP 게이트웨이 URL
        gateway_url = get_kcp_gateway_url()

        # KCP Form 데이터
        form_data = {
            "site_cd": site_cd,
            "ordr_idxx": session_id,
            "Ret_URL": callback_url,
            "req_tx": "cert",
            "cert_method": "01",
            "web_siteid": web_siteid,
            "web_siteid_hashYN": "Y",
            "cert_able_yn": "Y",
            "up_hash": hash_data,
            "cert_otp_use": "Y",
            "cert_enc_use_ext": "Y",
            "param_opt_1": "",
            "param_opt_2": "",
            "param_opt_3": ""
        }

        log.info("Phone verification for find-id initiated",
                session_id=session_id,
                return_url=return_url)

        return {
            "gateway_url": gateway_url,
            "form_data": form_data,
            "session_id": session_id,
            "site_cd": site_cd
        }

    async def initiate_verification_for_find_password(
        self,
        user_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """비밀번호 찾기용 본인인증 프로세스 시작 (user_id 포함)

        Args:
            user_id: 사용자 ID
            return_url: 인증 완료 후 리다이렉트할 URL (모바일 fallback용)

        Returns:
            Dict[str, str]: gateway_url, session_id 포함
        """
        log = get_logger_with_request_id()

        # 세션 ID 생성 (KCP ordr_idxx)
        session_id = f"FINDPW_{uuid.uuid4().hex[:18]}"

        # Redis에 세션 정보 저장 (15분 TTL)
        session_data = {
            "phone_number": "01000000000",  # 더미 값
            "status": "initiated",
            "purpose": "find_password",  # 비밀번호 찾기 용도 표시
            "user_id": user_id,  # 사용자 ID 저장
            "return_url": return_url,
            "created_at": datetime.utcnow().isoformat()
        }

        await self._save_session(session_id, session_data, ttl=900)

        # KCP 게이트웨이 파라미터 생성
        site_cd = get_kcp_site_cd()
        web_siteid = get_kcp_web_siteid()
        callback_url = get_kcp_callback_url()

        # 인증 데이터 해시 생성
        cert_data = f"{site_cd}{session_id}{web_siteid}000000"
        hash_data = make_hash_data(cert_data)

        # KCP 게이트웨이 URL
        gateway_url = get_kcp_gateway_url()

        # KCP Form 데이터
        form_data = {
            "site_cd": site_cd,
            "ordr_idxx": session_id,
            "Ret_URL": callback_url,
            "req_tx": "cert",
            "cert_method": "01",
            "web_siteid": web_siteid,
            "web_siteid_hashYN": "Y",
            "cert_able_yn": "Y",
            "up_hash": hash_data,
            "cert_otp_use": "Y",
            "cert_enc_use_ext": "Y",
            "param_opt_1": "",
            "param_opt_2": "",
            "param_opt_3": ""
        }

        log.info("Phone verification for find-password initiated",
                session_id=session_id,
                user_id=user_id,
                return_url=return_url)

        return {
            "gateway_url": gateway_url,
            "form_data": form_data,
            "session_id": session_id,
            "site_cd": site_cd
        }

    async def process_callback(
        self,
        site_cd: str,
        ordr_idxx: str,
        cert_no: str,
        enc_cert_data2: str,
        dn_hash: str,
        res_cd: str,
        res_msg: Optional[str] = None
    ) -> Dict:
        """KCP 콜백 처리

        Args:
            site_cd: KCP 사이트 코드
            ordr_idxx: 세션 ID
            cert_no: 인증 번호
            enc_cert_data2: 암호화된 인증 데이터
            dn_hash: 해시 데이터
            res_cd: 응답 코드 (0000: 성공)
            res_msg: 응답 메시지

        Returns:
            Dict: success, phone, phone_chk, ci, di 등 포함

        Raises:
            ValidationError: 검증 실패
        """
        log = get_logger_with_request_id()

        # 1. 응답 코드 확인
        if res_cd != "0000":
            log.warning("KCP verification failed",
                       session_id=ordr_idxx,
                       res_cd=res_cd,
                       res_msg=res_msg)
            raise ValidationError(f"본인인증 실패: {res_msg or res_cd}")

        # 2. 세션 확인
        session_data = await self._get_session(ordr_idxx)
        if not session_data:
            log.error("Session not found", session_id=ordr_idxx)
            raise ValidationError("세션이 만료되었거나 유효하지 않습니다")

        # 3. 해시 검증
        cert_data = f"{site_cd}{ordr_idxx}{cert_no}"
        is_valid_hash = check_valid_hash(cert_data, dn_hash)

        if not is_valid_hash:
            log.error("Hash validation failed",
                     session_id=ordr_idxx,
                     cert_no=cert_no)
            raise ValidationError("해시 검증 실패")

        # 4. 암호화 데이터 복호화
        decrypted_data = decrypt_enc_cert(cert_no, enc_cert_data2, "0")

        if not decrypted_data:
            log.error("Failed to decrypt cert data",
                     session_id=ordr_idxx,
                     cert_no=cert_no)
            raise ValidationError("인증 데이터 복호화 실패")

        # 5. 복호화된 데이터 파싱
        phone_raw = decrypted_data.get('phone_no', '')
        phone = normalize_phone_number(phone_raw)  # 하이픈 제거하여 정규화
        name = decrypted_data.get('name', '')
        birth_date = decrypted_data.get('birthday', '')
        gender = decrypted_data.get('sex_code', '')
        ci = decrypted_data.get('ci_no', '')
        di = decrypted_data.get('di_no', '')

        # 6. 인증 플래그 생성 (XOR 암호화)
        phone_chk = xor_encrypt(f"{phone}_{ci}_{datetime.utcnow().timestamp()}")

        # 7. 세션 업데이트 (검증 완료 상태로)
        session_data.update({
            "status": "verified",
            "phone": phone,
            "phone_chk": phone_chk,
            "ci": ci,
            "di": di,
            "verified_name": name,
            "verified_birth_date": birth_date,
            "verified_gender": gender,
            "verified_at": datetime.utcnow().isoformat()
        })

        await self._save_session(ordr_idxx, session_data, ttl=1800)  # 30분 연장

        # 8. step2 입력 번호와 KCP 인증 번호 비교
        original_phone_raw = session_data.get('phone_number', '')
        original_phone = normalize_phone_number(original_phone_raw)  # 하이픈 제거하여 정규화
        is_phone_matched = phone == original_phone

        log.info("Phone verification completed",
                session_id=ordr_idxx,
                phone=phone[:3] + "****" + phone[-4:],
                original_phone=original_phone[:3] + "****" + original_phone[-4:],
                phone_raw=phone_raw,
                original_phone_raw=original_phone_raw,
                ci=ci[:8] + "...",
                is_phone_matched=is_phone_matched)

        return {
            "success": True,
            "phone": phone,
            "phone_chk": phone_chk,
            "is_phone_matched": is_phone_matched,
            "ci": ci,
            "di": di,
            "name": name,
            "birth_date": birth_date,
            "gender": gender,
            "return_url": session_data.get("return_url", "/signup"),  # 세션의 return_url 반환
            "user_id": session_data.get("user_id", "")  # 비밀번호 찾기용 user_id (있는 경우에만)
        }

    async def verify_phone_chk(self, phone: str, phone_chk: str) -> bool:
        """phone_chk 토큰 검증

        Args:
            phone: 휴대폰 번호
            phone_chk: 검증 토큰

        Returns:
            bool: 유효하면 True
        """
        log = get_logger_with_request_id()

        try:
            # XOR 복호화
            decrypted = xor_decrypt(phone_chk)
            parts = decrypted.split('_')

            if len(parts) < 3:
                log.warning("Invalid phone_chk format")
                return False

            verified_phone = parts[0]
            # ci = parts[1]
            timestamp = float(parts[2])

            # 전화번호 일치 확인
            if verified_phone != phone:
                log.warning("Phone number mismatch")
                return False

            # 유효기간 확인 (30분)
            token_time = datetime.fromtimestamp(timestamp)
            if datetime.utcnow() - token_time > timedelta(minutes=30):
                log.warning("phone_chk expired")
                return False

            return True

        except Exception as e:
            log.error("Failed to verify phone_chk", error=str(e))
            return False

    async def get_verification_status(self, session_id: str) -> Optional[Dict]:
        """인증 상태 조회

        Args:
            session_id: 세션 ID

        Returns:
            Optional[Dict]: 세션 데이터 또는 None
        """
        return await self._get_session(session_id)

    def _validate_input(
        self,
        phone_number: str
    ) -> None:
        """입력값 검증

        Raises:
            ValidationError: 검증 실패
        """
        # 휴대폰 번호 검증
        if not phone_number or len(phone_number) != 11 or not phone_number.startswith('010'):
            raise ValidationError("올바른 휴대폰 번호를 입력해주세요 (010으로 시작하는 11자리)")

    async def _save_session(self, session_id: str, data: Dict, ttl: int) -> None:
        """Redis에 세션 저장

        Args:
            session_id: 세션 ID
            data: 저장할 데이터
            ttl: TTL (초)
        """
        import json
        key = f"phone_verification:{session_id}"
        await self.redis.setex(key, ttl, json.dumps(data))

    async def _get_session(self, session_id: str) -> Optional[Dict]:
        """Redis에서 세션 조회

        Args:
            session_id: 세션 ID

        Returns:
            Optional[Dict]: 세션 데이터 또는 None
        """
        import json
        key = f"phone_verification:{session_id}"
        data = await self.redis.get(key)

        if not data:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None


# 의존성 함수 (프로젝트 규격 준수)
from fastapi import Depends
from src.core.redis import get_redis

def get_phone_verification_service(
    redis_client: redis.Redis = Depends(get_redis)
) -> PhoneVerificationService:
    """PhoneVerificationService 팩토리 함수"""
    return PhoneVerificationService(redis_client)
