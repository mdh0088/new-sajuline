"""
Phone Verification (minimal) Router

DB 비의존 준비 엔드포인트만 복구: /api/v1/sms/prepare-kcp-auth
"""

from typing import Dict, Any
from fastapi import APIRouter

from ..infrastructure.redis_service import phone_verification_redis
from ..infrastructure.kcp_config import get_kcp_configuration
from ..infrastructure.kcp_service import KCPService


sms_router = APIRouter(
	prefix="/api/v1/sms",
	tags=["SMS Verification (minimal)"],
)


@sms_router.post("/prepare-kcp-auth")
async def prepare_kcp_auth_minimal(payload: Dict[str, Any]) -> Dict[str, Any]:
	"""KCP 인증 iframe 호출을 위한 최소 데이터 생성 (DB 비의존)

	- Redis에 세션 생성
	- KCP up_hash 생성(ct_cli)
	- 프론트 호출 파라미터 반환
	"""
	service = phone_verification_redis
	kcp_config = get_kcp_configuration()
	kcp_service = KCPService(kcp_config)

	# 입력 값 (프론트가 기존대로 name, phone, birth_date 전달)
	phone = str(payload.get("phone", ""))
	name = str(payload.get("name", ""))
	birth_date = str(payload.get("birth_date", ""))

	# 세션 생성
	session_id, _, _ = await service.create_verification_session(
		phone=phone,
		name=name,
		birth_date=birth_date,
	)

	# KCP hash data (cert_able_yn=Y 시나리오와 동일: 입력값 없이 해시)
	hash_data = (
		kcp_config.site_cd
		+ session_id
		+ kcp_config.web_siteid
		+ ""
		+ "00"
		+ "00"
		+ "00"
		+ ""
		+ ""
	)
	up_hash = kcp_service.make_hash_data(hash_data)

	return {
		"session_id": session_id,
		"up_hash": up_hash,
		"site_cd": kcp_config.site_cd,
		"web_siteid": kcp_config.web_siteid,
		"return_url": f"{kcp_config.ret_url}/api/phone-verification/kcp/callback",
	}

"""
Phone Verification Router

핸드폰 인증 API 라우터
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import (
    PhoneVerificationRequest,
    PhoneVerificationInitResponse,
    PhoneVerificationCallbackRequest,
    PhoneVerificationStatusResponse,
    VerificationStatus
)
from ..application.services import PhoneVerificationApplicationService
from src.common.database.session import get_async_session
from src.common.response.wrapper import ResponseWrapper
from src.common.exceptions.custom import ValidationError, BusinessLogicError, ExternalServiceError
from src.common.decorators.error_handler import handle_errors


router = APIRouter(
    prefix="/phone-verification",
    tags=["Phone Verification"],
    responses={404: {"description": "Not found"}}
)


# Dependency Injection
async def get_phone_verification_service(
    session: AsyncSession = Depends(get_async_session)
) -> PhoneVerificationApplicationService:
    """핸드폰 인증 서비스 의존성 주입"""
    return PhoneVerificationApplicationService(session)


@router.post(
    "/initiate",
    response_model=ResponseWrapper[PhoneVerificationInitResponse],
    summary="핸드폰 인증 시작",
    description="핸드폰 본인인증을 시작합니다. KCP 인증창에 필요한 정보를 반환합니다."
)
@handle_errors
async def initiate_verification(
    request: PhoneVerificationRequest,
    user_id: Optional[str] = None,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[PhoneVerificationInitResponse]:
    """
    핸드폰 인증 시작
    
    Args:
        request: 인증 요청 데이터
        user_id: 사용자 ID (선택)
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[PhoneVerificationInitResponse]: 인증 시작 정보
    
    Raises:
        HTTPException: 400 - 유효하지 않은 요청
        HTTPException: 409 - 중복 인증 시도
    """
    try:
        result = await service.initiate_verification(request, user_id)
        return ResponseWrapper(
            success=True,
            data=result,
            message="인증이 시작되었습니다."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/callback",
    response_model=ResponseWrapper[PhoneVerificationStatusResponse],
    summary="KCP 인증 콜백",
    description="KCP에서 인증 결과를 받아 처리합니다. (내부 API)"
)
@handle_errors
async def handle_verification_callback(
    # Form 데이터로 받기 (KCP 콜백 형식)
    site_cd: str = Form(..., description="사이트 코드"),
    ordr_idxx: str = Form(..., description="요청 번호 (세션 ID)"),
    cert_no: str = Form(..., description="인증 번호"),
    enc_cert_data2: str = Form(..., description="암호화된 인증 데이터"),
    dn_hash: str = Form(..., description="응답 해시"),
    res_cd: str = Form(..., description="결과 코드"),
    res_msg: Optional[str] = Form(None, description="결과 메시지"),
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[PhoneVerificationStatusResponse]:
    """
    KCP 인증 콜백 처리
    
    Args:
        site_cd: 사이트 코드
        ordr_idxx: 요청 번호 (세션 ID)
        cert_no: 인증 번호
        enc_cert_data2: 암호화된 인증 데이터
        dn_hash: 응답 해시
        res_cd: 결과 코드
        res_msg: 결과 메시지
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[PhoneVerificationStatusResponse]: 처리 결과
    
    Raises:
        HTTPException: 400 - 유효하지 않은 데이터
        HTTPException: 410 - 만료된 세션
        HTTPException: 502 - 외부 서비스 오류
    """
    try:
        callback_request = PhoneVerificationCallbackRequest(
            site_cd=site_cd,
            ordr_idxx=ordr_idxx,
            cert_no=cert_no,
            enc_cert_data2=enc_cert_data2,
            dn_hash=dn_hash,
            res_cd=res_cd,
            res_msg=res_msg
        )
        
        result = await service.handle_callback(callback_request)
        
        message = "인증이 완료되었습니다." if result.status == VerificationStatus.COMPLETED else "인증에 실패했습니다."
        
        return ResponseWrapper(
            success=result.status == VerificationStatus.COMPLETED,
            data=result,
            message=message
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e)
        )
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


@router.get(
    "/status/{session_id}",
    response_model=ResponseWrapper[PhoneVerificationStatusResponse],
    summary="인증 상태 조회",
    description="세션 ID로 인증 상태를 조회합니다."
)
@handle_errors
async def get_verification_status(
    session_id: str,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[PhoneVerificationStatusResponse]:
    """
    인증 상태 조회
    
    Args:
        session_id: 세션 ID
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[PhoneVerificationStatusResponse]: 인증 상태
    
    Raises:
        HTTPException: 404 - 세션을 찾을 수 없음
    """
    try:
        result = await service.get_verification_status(session_id)
        return ResponseWrapper(
            success=True,
            data=result,
            message="인증 상태를 조회했습니다."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/user/{user_id}",
    response_model=ResponseWrapper[List[PhoneVerificationStatusResponse]],
    summary="사용자 인증 이력",
    description="사용자의 인증 이력을 조회합니다."
)
@handle_errors
async def get_user_verifications(
    user_id: str,
    status: Optional[VerificationStatus] = None,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[List[PhoneVerificationStatusResponse]]:
    """
    사용자 인증 이력 조회
    
    Args:
        user_id: 사용자 ID
        status: 상태 필터 (선택)
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[List[PhoneVerificationStatusResponse]]: 인증 이력
    """
    result = await service.get_user_verifications(user_id, status)
    return ResponseWrapper(
        success=True,
        data=result,
        message=f"인증 이력 {len(result)}건을 조회했습니다."
    )


@router.post(
    "/verify-token",
    response_model=ResponseWrapper[bool],
    summary="인증 토큰 검증",
    description="인증 완료 토큰의 유효성을 검증합니다. (기존 PHP 호환)"
)
@handle_errors
async def verify_phone_token(
    token: str,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[bool]:
    """
    인증 토큰 검증 (기존 PHP 호환)
    
    Args:
        token: 암호화된 인증 토큰
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[bool]: 토큰 유효성
    """
    is_valid = await service.validate_verification_token(token)
    return ResponseWrapper(
        success=is_valid,
        data=is_valid,
        message="토큰이 유효합니다." if is_valid else "토큰이 유효하지 않습니다."
    )


@router.post(
    "/generate-token/{session_id}",
    response_model=ResponseWrapper[str],
    summary="인증 토큰 생성",
    description="인증 완료 후 토큰을 생성합니다. (기존 PHP 호환)"
)
@handle_errors
async def generate_verification_token(
    session_id: str,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[str]:
    """
    인증 토큰 생성 (기존 PHP 호환)
    
    Args:
        session_id: 세션 ID
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[str]: 암호화된 인증 토큰
    
    Raises:
        HTTPException: 400 - 인증이 완료되지 않음
    """
    try:
        token = await service.generate_verification_token(session_id)
        return ResponseWrapper(
            success=True,
            data=token,
            message="인증 토큰을 생성했습니다."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/check-duplicate",
    response_model=ResponseWrapper[bool],
    summary="중복 가입 확인",
    description="CI/DI를 이용해 중복 가입을 확인합니다."
)
@handle_errors
async def check_duplicate_registration(
    ci: Optional[str] = None,
    di: Optional[str] = None,
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[bool]:
    """
    중복 가입 확인
    
    Args:
        ci: CI 값
        di: DI 값
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[bool]: 중복 여부
    
    Raises:
        HTTPException: 400 - CI/DI 없음
    """
    if not ci and not di:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CI 또는 DI 값이 필요합니다."
        )
    
    is_duplicate = await service.check_duplicate_by_ci_di(ci, di)
    return ResponseWrapper(
        success=True,
        data=is_duplicate,
        message="중복 가입이 확인되었습니다." if is_duplicate else "가입 가능합니다."
    )


@router.post(
    "/cleanup",
    response_model=ResponseWrapper[int],
    summary="만료 세션 정리",
    description="만료된 인증 세션을 정리합니다. (관리자 전용)"
)
@handle_errors
async def cleanup_expired_sessions(
    service: PhoneVerificationApplicationService = Depends(get_phone_verification_service)
) -> ResponseWrapper[int]:
    """
    만료된 세션 정리
    
    Args:
        service: 인증 서비스
    
    Returns:
        ResponseWrapper[int]: 정리된 세션 수
    """
    count = await service.cleanup_expired_sessions()
    return ResponseWrapper(
        success=True,
        data=count,
        message=f"{count}개의 만료된 세션을 정리했습니다."
    )


@router.get(
    "/config-test",
    response_model=ResponseWrapper[dict],
    summary="KCP 설정 테스트",
    description="KCP 설정 및 바이너리 상태를 테스트합니다."
)
@handle_errors
async def test_kcp_configuration() -> ResponseWrapper[dict]:
    """
    KCP 설정 테스트
    
    Returns:
        ResponseWrapper[dict]: KCP 설정 정보 및 바이너리 상태
    """
    import os
    import platform
    from ..infrastructure.kcp_config import get_kcp_configuration
    from ..infrastructure.kcp_service import KCPService
    
    try:
        # KCP 설정 로드
        config = get_kcp_configuration()
        
        # 바이너리 존재 확인
        ct_cli_path = os.path.join(config.home_dir, "ct_cli")
        binary_exists = os.path.exists(ct_cli_path)
        
        # 시스템 아키텍처 정보
        system_info = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "architecture": platform.architecture()[0]
        }
        
        # KCP 서비스 테스트
        kcp_service = KCPService(config)
        kcp_available = False
        kcp_version = "Unknown"
        
        if binary_exists:
            try:
                kcp_version = kcp_service.get_kcp_lib_ver()
                # 간단한 해시 테스트
                test_hash = kcp_service.make_hash_data("test_data")
                kcp_available = test_hash != "HS01"  # 에러 코드가 아니면 성공
            except Exception as e:
                kcp_version = f"Error: {str(e)}"
        
        test_result = {
            "kcp_config": {
                "site_cd": config.site_cd,
                "web_siteid": config.web_siteid,
                "gateway_url": config.gateway_url,
                "home_dir": config.home_dir,
                "is_test_mode": config.is_test_mode,
                "return_url": config.return_url
            },
            "binary_status": {
                "ct_cli_path": ct_cli_path,
                "binary_exists": binary_exists,
                "kcp_available": kcp_available,
                "kcp_version": kcp_version
            },
            "system_info": system_info,
            "docker_env": settings.DOCKER_ENV
        }
        
        return ResponseWrapper(
            success=True,
            data=test_result,
            message="KCP 설정 테스트가 완료되었습니다."
        )
        
    except Exception as e:
        return ResponseWrapper(
            success=False,
            data={"error": str(e)},
            message=f"KCP 설정 테스트 중 오류가 발생했습니다: {str(e)}"
        )