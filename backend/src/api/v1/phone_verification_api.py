"""
휴대폰 본인인증 API

KCP 본인인증을 사용한 휴대폰 인증 엔드포인트
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from src.services.phone_verification_service import (
    PhoneVerificationService,
    get_phone_verification_service
)
from src.schemas.phone_verification_schema import (
    PhoneVerificationInitiateRequest,
    PhoneVerificationInitiateResponse,
    PhoneVerificationStatusResponse
)
from src.common.response.wrapper import ok, APIResponse
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError

router = APIRouter(prefix="/phone-verification", tags=["phone-verification"])


@router.post(
    "/initiate",
    response_model=APIResponse[PhoneVerificationInitiateResponse],
    summary="본인인증 시작",
    description="KCP 본인인증 프로세스를 시작하고 게이트웨이 URL을 반환합니다"
)
async def initiate_verification(
    request: PhoneVerificationInitiateRequest,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """본인인증 시작

    Args:
        request: 본인인증 요청 데이터
        phone_service: 휴대폰 인증 서비스

    Returns:
        PhoneVerificationInitiateResponse: 게이트웨이 URL 및 세션 정보
    """
    log = get_logger_with_request_id()
    log.info("Phone verification initiate request",
            phone=request.phone_number[:3] + "****" + request.phone_number[-4:])

    result = await phone_service.initiate_verification(
        phone_number=request.phone_number
    )

    return ok(
        data=PhoneVerificationInitiateResponse(**result),
        message="본인인증이 시작되었습니다"
    )


async def _kcp_callback_handler(
    site_cd: str,
    ordr_idxx: str,
    cert_no: str,
    enc_cert_data2: str,
    dn_hash: str,
    res_cd: str,
    res_msg: str,
    phone_service: PhoneVerificationService
) -> HTMLResponse:
    """KCP 콜백 처리 핸들러 (GET/POST 공통)"""
    log = get_logger_with_request_id()
    log.info("KCP callback received",
            session_id=ordr_idxx,
            res_cd=res_cd)

    try:
        # KCP 콜백 처리
        result = await phone_service.process_callback(
            site_cd=site_cd,
            ordr_idxx=ordr_idxx,
            cert_no=cert_no,
            enc_cert_data2=enc_cert_data2,
            dn_hash=dn_hash,
            res_cd=res_cd,
            res_msg=res_msg
        )

        # 성공 응답 HTML (Prototype 패턴)
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script>
                window.onload = function() {{
                    const messageData = {{
                        type: 'kcp_verification_complete',
                        success: true,
                        phone: '{result.get("phone", "")}',
                        phone_chk: '{result.get("phone_chk", "")}',
                        ci: '{result.get("ci", "")}',
                        di: '{result.get("di", "")}',
                        name: '{result.get("name", "")}',
                        birth_date: '{result.get("birth_date", "")}',
                        gender: '{result.get("gender", "")}'
                    }};
                    try {{
                        if (window.parent && window.parent !== window) {{
                            window.parent.postMessage(messageData, '*');
                        }}
                        if (window.opener) {{
                            window.opener.postMessage(messageData, '*');
                        }}
                    }} catch(e) {{}}
                    setTimeout(function() {{ window.close(); }}, 200);
                }}
            </script>
        </head>
        <body style="display:none;"></body>
        </html>
        """

        response = HTMLResponse(content=html_response)
        # CSP 완화
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' https:; "
            "script-src 'self' 'unsafe-inline' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors *;"
        )
        return response

    except (ValidationError, Exception) as e:
        log.error("KCP callback failed",
                 session_id=ordr_idxx,
                 error=str(e),
                 exc_info=True)

        # 실패 응답 HTML (Prototype 패턴)
        error_message = str(e).replace("'", "\\'")
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script>
                window.onload = function() {{
                    const messageData = {{
                        type: 'kcp_verification_complete',
                        success: false,
                        message: '{error_message}'
                    }};
                    try {{
                        if (window.parent && window.parent !== window) {{
                            window.parent.postMessage(messageData, '*');
                        }}
                        if (window.opener) {{
                            window.opener.postMessage(messageData, '*');
                        }}
                    }} catch(e) {{}}
                    setTimeout(function() {{ window.close(); }}, 200);
                }}
            </script>
        </head>
        <body style="display:none;"></body>
        </html>
        """

        response = HTMLResponse(content=html_response, status_code=400)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' https:; "
            "script-src 'self' 'unsafe-inline' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors *;"
        )
        return response


@router.post(
    "/callback",
    response_class=HTMLResponse,
    summary="KCP 콜백 처리",
    description="KCP 인증 완료 후 콜백을 처리합니다 (POST Form)"
)
async def kcp_callback(
    request: Request,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """KCP 콜백 처리 - POST Form 데이터 파싱"""
    log = get_logger_with_request_id()

    try:
        # 미들웨어에서 이미 파싱한 request body 가져오기 (스트림 소진 방지)
        form_dict = getattr(request.state, "request_body", {})

        # 필수 파라미터 추출
        site_cd = form_dict.get("site_cd", "")
        ordr_idxx = form_dict.get("ordr_idxx", "")
        cert_no = form_dict.get("cert_no", "")
        enc_cert_data2 = form_dict.get("enc_cert_data2", "")
        dn_hash = form_dict.get("dn_hash", "")
        res_cd = form_dict.get("res_cd", "")
        res_msg = form_dict.get("res_msg", "")

        log.info("KCP callback received",
                session_id=ordr_idxx,
                res_cd=res_cd)

        # 필수 파라미터 검증
        if not all([site_cd, ordr_idxx, cert_no, enc_cert_data2, dn_hash, res_cd]):
            missing = []
            if not site_cd: missing.append("site_cd")
            if not ordr_idxx: missing.append("ordr_idxx")
            if not cert_no: missing.append("cert_no")
            if not enc_cert_data2: missing.append("enc_cert_data2")
            if not dn_hash: missing.append("dn_hash")
            if not res_cd: missing.append("res_cd")

            log.error("KCP callback - Missing required parameters",
                     missing_params=missing)
            raise ValidationError(f"필수 파라미터 누락: {', '.join(missing)}")

        return await _kcp_callback_handler(
            site_cd, ordr_idxx, cert_no,
            enc_cert_data2, dn_hash, res_cd, res_msg,
            phone_service
        )
    except ValidationError:
        raise
    except Exception as e:
        log.error("KCP callback processing failed",
                 error=str(e),
                 exc_info=True)
        raise


@router.get(
    "/status/{session_id}",
    response_model=APIResponse[PhoneVerificationStatusResponse],
    summary="인증 상태 조회",
    description="세션 ID로 본인인증 상태를 조회합니다"
)
async def get_verification_status(
    session_id: str,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """인증 상태 조회

    Args:
        session_id: 세션 ID
        phone_service: 휴대폰 인증 서비스

    Returns:
        PhoneVerificationStatusResponse: 인증 상태 정보
    """
    log = get_logger_with_request_id()
    log.info("Get verification status", session_id=session_id)

    session_data = await phone_service.get_verification_status(session_id)

    if not session_data:
        raise ValidationError("세션을 찾을 수 없습니다")

    return ok(
        data=PhoneVerificationStatusResponse(**session_data),
        message="인증 상태를 조회했습니다"
    )
