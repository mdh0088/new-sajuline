"""
Phone Verification Application Service

핸드폰 인증 애플리케이션 서비스 (비즈니스 로직)
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import (
    PhoneVerificationRequest,
    PhoneVerificationSession,
    PhoneVerificationInitResponse,
    PhoneVerificationCallbackRequest,
    PhoneVerificationResult,
    PhoneVerificationStatusResponse,
    VerificationStatus,
    KCPConfiguration
)
from ..domain.models import PhoneVerification
from ..domain.services import PhoneVerificationDomainService
from ..infrastructure.repositories import PhoneVerificationRepository
from ..infrastructure.kcp_service import KCPService, KCPEncryptor
from ..infrastructure.kcp_config import get_kcp_configuration

from src.common.exceptions.custom import ValidationError, BusinessLogicError, ExternalServiceError


class PhoneVerificationApplicationService:
    """핸드폰 인증 애플리케이션 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PhoneVerificationRepository(session)
        self.kcp_config = get_kcp_configuration()
        self.kcp_service = KCPService(self.kcp_config)
        self.domain_service = PhoneVerificationDomainService()
    
    async def initiate_verification(
        self,
        request: PhoneVerificationRequest,
        user_id: Optional[str] = None
    ) -> PhoneVerificationInitResponse:
        """
        핸드폰 인증 시작
        
        Args:
            request: 인증 요청 데이터
            user_id: 사용자 ID (선택)
            
        Returns:
            PhoneVerificationInitResponse: 인증 시작 응답
            
        Raises:
            ValidationError: 입력 검증 실패
            BusinessLogicError: 비즈니스 로직 실패
        """
        # 1. 중복 인증 확인 (전화번호가 있는 경우)
        if request.phone_number:
            await self._check_duplicate_verification(request.phone_number)
        
        # 2. 세션 생성
        session_id = self.domain_service.generate_session_id()
        expires_at = datetime.utcnow() + timedelta(minutes=60)
        
        session = PhoneVerificationSession(
            session_id=session_id,
            user_id=user_id,
            status=VerificationStatus.PENDING,
            request_data=request,
            expires_at=expires_at
        )
        
        # 3. up_hash 생성
        hash_data = self.domain_service.create_up_hash_data(session, self.kcp_config)
        up_hash = self.kcp_service.make_hash_data(hash_data)
        
        # 4. 폼 데이터 생성
        form_data = self.domain_service.create_form_data(session, self.kcp_config, up_hash)
        
        # 5. 데이터베이스 저장
        verification = PhoneVerification(
            session_id=session_id,
            user_id=user_id,
            status=VerificationStatus.PENDING,
            user_name=request.name,
            birth_date=request.birth_date,
            phone_number=request.phone_number,
            carrier=request.carrier,
            gender=request.gender,
            local_code=request.local_code,
            verification_method=request.method,
            up_hash=up_hash,
            expires_at=expires_at
        )
        
        await self.repository.create(verification)
        await self.session.commit()
        
        return PhoneVerificationInitResponse(
            session_id=session_id,
            gateway_url=self.kcp_config.gateway_url,
            up_hash=up_hash,
            form_data=form_data,
            expires_at=expires_at
        )
    
    async def handle_callback(
        self,
        callback: PhoneVerificationCallbackRequest
    ) -> PhoneVerificationStatusResponse:
        """
        KCP 콜백 처리
        
        Args:
            callback: KCP 콜백 데이터
            
        Returns:
            PhoneVerificationStatusResponse: 처리 결과
            
        Raises:
            ValidationError: 검증 실패
            ExternalServiceError: 외부 서비스 오류
        """
        # 1. 세션 조회
        verification = await self.repository.get_by_session_id(callback.ordr_idxx)
        if not verification:
            raise ValidationError("유효하지 않은 세션입니다.")
        
        # 2. 만료 확인
        if verification.is_expired():
            await self.repository.update_status(
                verification.session_id,
                VerificationStatus.EXPIRED
            )
            await self.session.commit()
            raise BusinessLogicError("인증 세션이 만료되었습니다.")
        
        # 3. 결과 코드 확인
        if callback.res_cd != "0000":
            await self.repository.update_status(
                verification.session_id,
                VerificationStatus.FAILED,
                res_cd=callback.res_cd,
                res_msg=callback.res_msg
            )
            await self.session.commit()
            
            return PhoneVerificationStatusResponse(
                session_id=verification.session_id,
                status=VerificationStatus.FAILED,
                error_message=callback.res_msg or "인증에 실패했습니다.",
                expires_at=verification.expires_at
            )
        
        # 4. dn_hash 검증
        dn_verification_data = self.domain_service.create_dn_hash_verification_data(
            callback.site_cd,
            callback.ordr_idxx,
            callback.cert_no
        )
        
        if not self.kcp_service.check_valid_hash(callback.dn_hash, dn_verification_data):
            await self.repository.update_status(
                verification.session_id,
                VerificationStatus.FAILED,
                res_cd="9999",
                res_msg="dn_hash 변조 위험"
            )
            await self.session.commit()
            raise ValidationError("인증 데이터가 변조되었습니다.")
        
        # 5. 암호화 데이터 복호화
        decrypted_data = self.kcp_service.decrypt_enc_cert(
            callback.cert_no,
            callback.enc_cert_data2
        )
        
        if not decrypted_data:
            await self.repository.update_status(
                verification.session_id,
                VerificationStatus.FAILED,
                res_cd="9998",
                res_msg="복호화 실패"
            )
            await self.session.commit()
            raise ExternalServiceError("인증 데이터 복호화에 실패했습니다.")
        
        # 6. 인증 결과 저장
        verification = await self.repository.update_verification_result(
            verification.session_id,
            callback.cert_no,
            decrypted_data
        )
        
        # 7. 해시 정보 업데이트
        verification.dn_hash = callback.dn_hash
        verification.enc_cert_data = callback.enc_cert_data2
        
        await self.session.commit()
        
        # 8. 결과 반환
        result = PhoneVerificationResult(
            session_id=verification.session_id,
            cert_no=verification.cert_no,
            comm_id=verification.comm_id,
            phone_no=verification.phone_no,
            user_name=verification.verified_name,
            birth_day=verification.verified_birth,
            sex_code=verification.sex_code,
            local_code=verification.local_code,
            ci=verification.ci,
            di=verification.di,
            res_cd=verification.res_cd,
            res_msg=verification.res_msg,
            verified_at=verification.verified_at
        )
        
        return PhoneVerificationStatusResponse(
            session_id=verification.session_id,
            status=VerificationStatus.COMPLETED,
            result=result,
            expires_at=verification.expires_at
        )
    
    async def get_verification_status(
        self,
        session_id: str
    ) -> PhoneVerificationStatusResponse:
        """
        인증 상태 조회
        
        Args:
            session_id: 세션 ID
            
        Returns:
            PhoneVerificationStatusResponse: 인증 상태
            
        Raises:
            ValidationError: 세션을 찾을 수 없음
        """
        verification = await self.repository.get_by_session_id(session_id)
        if not verification:
            raise ValidationError("유효하지 않은 세션입니다.")
        
        # 만료 확인 및 상태 업데이트
        if verification.is_expired() and verification.status in [
            VerificationStatus.PENDING,
            VerificationStatus.IN_PROGRESS
        ]:
            verification = await self.repository.update_status(
                session_id,
                VerificationStatus.EXPIRED
            )
            await self.session.commit()
        
        result = None
        if verification.status == VerificationStatus.COMPLETED:
            result = PhoneVerificationResult(
                session_id=verification.session_id,
                cert_no=verification.cert_no,
                comm_id=verification.comm_id,
                phone_no=verification.phone_no,
                user_name=verification.verified_name,
                birth_day=verification.verified_birth,
                sex_code=verification.sex_code,
                local_code=verification.local_code,
                ci=verification.ci,
                di=verification.di,
                res_cd=verification.res_cd,
                res_msg=verification.res_msg,
                verified_at=verification.verified_at
            )
        
        return PhoneVerificationStatusResponse(
            session_id=verification.session_id,
            status=verification.status,
            result=result,
            error_message=verification.res_msg if verification.status == VerificationStatus.FAILED else None,
            expires_at=verification.expires_at
        )
    
    async def get_user_verifications(
        self,
        user_id: str,
        status: Optional[VerificationStatus] = None
    ) -> list[PhoneVerificationStatusResponse]:
        """
        사용자의 인증 이력 조회
        
        Args:
            user_id: 사용자 ID
            status: 상태 필터 (선택)
            
        Returns:
            list[PhoneVerificationStatusResponse]: 인증 이력
        """
        verifications = await self.repository.get_by_user_id(user_id, status)
        
        results = []
        for verification in verifications:
            result = None
            if verification.status == VerificationStatus.COMPLETED:
                result = PhoneVerificationResult(
                    session_id=verification.session_id,
                    cert_no=verification.cert_no,
                    comm_id=verification.comm_id,
                    phone_no=verification.phone_no,
                    user_name=verification.verified_name,
                    birth_day=verification.verified_birth,
                    sex_code=verification.sex_code,
                    local_code=verification.local_code,
                    ci=verification.ci,
                    di=verification.di,
                    res_cd=verification.res_cd,
                    res_msg=verification.res_msg,
                    verified_at=verification.verified_at
                )
            
            results.append(PhoneVerificationStatusResponse(
                session_id=verification.session_id,
                status=verification.status,
                result=result,
                error_message=verification.res_msg if verification.status == VerificationStatus.FAILED else None,
                expires_at=verification.expires_at
            ))
        
        return results
    
    async def check_duplicate_by_ci_di(
        self,
        ci: Optional[str] = None,
        di: Optional[str] = None
    ) -> bool:
        """
        CI/DI 중복 확인
        
        Args:
            ci: CI 값
            di: DI 값
            
        Returns:
            bool: 중복 여부
        """
        if ci:
            existing = await self.repository.get_by_ci(ci)
            if existing:
                return True
        
        if di:
            existing = await self.repository.get_by_di(di)
            if existing:
                return True
        
        return False
    
    async def generate_verification_token(self, session_id: str) -> str:
        """
        인증 완료 토큰 생성 (기존 PHP 호환)
        
        Args:
            session_id: 세션 ID
            
        Returns:
            str: 암호화된 인증 토큰
        """
        verification = await self.repository.get_by_session_id(session_id)
        if not verification or not verification.is_verified():
            raise ValidationError("인증이 완료되지 않았습니다.")
        
        return KCPEncryptor.encrypt_phone_verification_flag()
    
    async def validate_verification_token(self, token: str) -> bool:
        """
        인증 완료 토큰 검증 (기존 PHP 호환)
        
        Args:
            token: 암호화된 인증 토큰
            
        Returns:
            bool: 토큰 유효성
        """
        return KCPEncryptor.validate_phone_verification_flag(token)
    
    async def cleanup_expired_sessions(self) -> int:
        """
        만료된 세션 정리
        
        Returns:
            int: 정리된 세션 수
        """
        count = await self.repository.cleanup_expired()
        await self.session.commit()
        return count
    
    async def _check_duplicate_verification(self, phone_no: str) -> None:
        """
        중복 인증 확인 (30분 이내)
        
        Args:
            phone_no: 전화번호
            
        Raises:
            BusinessLogicError: 중복 인증 시도
        """
        recent = await self.repository.get_recent_by_phone(phone_no, minutes=30)
        if recent:
            raise BusinessLogicError(
                f"최근 30분 이내에 이미 인증을 완료하셨습니다. "
                f"({self.domain_service.mask_phone_number(phone_no)})"
            )