"""
Simplified Phone Verification Router

Standard SMS verification API endpoints using Redis.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from typing import Optional

from ..domain.simplified_entities import (
    SendCodeRequest,
    SendCodeResponse,
    VerifyCodeRequest,
    VerifyCodeResponse,
    CheckVerifiedRequest,
    CheckVerifiedResponse,
    ResendCodeRequest
)
from typing import Dict, Any
from ..application.simplified_service import simplified_phone_verification_service
from src.common.response.wrapper import ResponseWrapper
from src.common.exceptions.custom import ValidationError, BusinessLogicError, ExternalServiceError
from src.common.decorators.error_handler import handle_errors
from src.common.logging.events import log_event
from src.common.infrastructure.rate_limiter import rate_limiter


router = APIRouter(
    prefix="/api/v1/sms",
    tags=["SMS Verification"],
    responses={
        404: {"description": "Not found"},
        429: {"description": "Too many requests"}
    }
)


@router.post(
    "/send-code",
    response_model=ResponseWrapper[SendCodeResponse],
    summary="SMS 인증 코드 발송",
    description="휴대폰으로 6자리 인증 코드를 발송합니다.",
    status_code=status.HTTP_200_OK
)
@handle_errors
async def send_verification_code(
    request: SendCodeRequest
) -> ResponseWrapper[SendCodeResponse]:
    """
    SMS 인증 코드 발송
    
    - 휴대폰 번호로 6자리 인증 코드 발송
    - 5분간 유효
    - 시간당 3회 제한
    """
    try:
        # Additional rate limiting check at API level
        allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
            key=f"sms:{request.phone}",
            max_requests=3,
            window_seconds=3600,
            cost=1
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"SMS 발송 한도를 초과했습니다. {int(reset_time)}초 후 다시 시도해주세요."
            )
        
        # Send verification code
        response = await simplified_phone_verification_service.send_verification_code(request)
        # 성공 이벤트
        log_event(
            "phone.verify.send.success",
            domain="app.auth",
            level="INFO",
            user_id=None,
            channel="sms",
            referer="api",
        )
        
        return ResponseWrapper(
            success=True,
            data=response,
            message="인증 코드가 발송되었습니다."
        )
        
    except (ValidationError, BusinessLogicError, ExternalServiceError) as e:
        log_event(
            "phone.verify.send.fail",
            domain="app.auth",
            level="ERROR",
            error_code=type(e).__name__,
            reason="validation_or_external_error",
        )
        return ResponseWrapper(
            success=False,
            data=None,
            message=str(e),
            error={
                "type": type(e).__name__,
                "detail": str(e)
            }
        )
    except Exception as e:
        log_event(
            "phone.verify.send.fail",
            domain="app.auth",
            level="ERROR",
            error_code="UNEXPECTED",
            reason="unexpected_error",
        )
        return ResponseWrapper(
            success=False,
            data=None,
            message="인증 코드 발송 중 오류가 발생했습니다.",
            error={
                "type": "UnexpectedError",
                "detail": str(e)
            }
        )


@router.post(
    "/kcp-redirect",
    summary="KCP 인증 중간 리다이렉트 (PHP 패턴)",
    description="KCP 인증 중간 리다이렉트 HTML 페이지 반환",
    status_code=status.HTTP_200_OK
)
async def kcp_redirect(
    site_cd: str = Form(...),
    ordr_idxx: str = Form(...),
    req_tx: str = Form(...),
    cert_method: str = Form(None),
    web_siteid: str = Form(None),
    Ret_URL: str = Form(None),
    cert_otp_use: str = Form(None),
    cert_enc_use_ext: str = Form(None),
    cert_able_yn: str = Form(None),
    web_siteid_hashYN: str = Form(None),
    user_name: str = Form(""),
    year: str = Form("00"),
    month: str = Form("00"),
    day: str = Form("00"),
    sex_code: str = Form(""),
    local_code: str = Form(""),
    fix_commid: str = Form(""),
    param_opt_1: str = Form(""),
    param_opt_2: str = Form(""),
    param_opt_3: str = Form("")
):
    try:
        service = simplified_phone_verification_service
        kcp_config = service.kcp_config
        kcp_service = service.kcp_service

        up_hash = ""
        if req_tx == "cert":
            if cert_able_yn == "Y":
                hash_data = (
                    site_cd +
                    ordr_idxx +
                    web_siteid +
                    "" +
                    "00" +
                    "00" +
                    "00" +
                    "" +
                    ""
                )
            else:
                hash_data = (
                    site_cd +
                    ordr_idxx +
                    web_siteid +
                    user_name +
                    year.zfill(2) +
                    month.zfill(2) +
                    day.zfill(2) +
                    sex_code +
                    local_code
                )
            up_hash = kcp_service.make_hash_data(hash_data)

        all_params = {
            "site_cd": site_cd,
            "ordr_idxx": ordr_idxx,
            "req_tx": req_tx,
            "cert_method": cert_method or "",
            "web_siteid": web_siteid or "",
            "Ret_URL": Ret_URL or "",
            "cert_otp_use": cert_otp_use or "",
            "cert_enc_use_ext": cert_enc_use_ext or "",
            "cert_able_yn": cert_able_yn or "",
            "web_siteid_hashYN": web_siteid_hashYN or "",
            "user_name": user_name,
            "year": year,
            "month": month,
            "day": day,
            "sex_code": sex_code,
            "local_code": local_code,
            "fix_commid": fix_commid,
            "param_opt_1": param_opt_1,
            "param_opt_2": param_opt_2,
            "param_opt_3": param_opt_3,
            "up_hash": up_hash,
            "kcp_cert_lib_ver": kcp_service.get_kcp_lib_ver()
        }

        form_fields = ""
        for name, value in all_params.items():
            if value:
                form_fields += f'<input type="hidden" name="{name}" value="{value}"/>\n            '

        html_response = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>*** KCP Online Payment System [Python Version] ***</title>
        <script type="text/javascript">
            function submitForm() {{
                var frm = document.form_auth;
                if ( frm.req_tx && frm.req_tx.value == "cert" ) {{
                    try {{
                        if (window.opener && window.opener.document && window.opener.document.form_auth && window.opener.document.form_auth.veri_up_hash) {{
                            window.opener.document.form_auth.veri_up_hash.value = frm.up_hash.value;
                        }}
                    }} catch(e) {{}}
                    frm.action="{kcp_config.gateway_url}";
                    frm.submit();
                }} else if ( frm.req_tx && ( frm.req_tx.value == "auth" || frm.req_tx.value == "otp_auth" ) ) {{
                    frm.action="./kcp-callback";
                    frm.submit();
                }}
            }}
            window.onload = submitForm;
            setTimeout(submitForm, 100);
        </script>
    </head>
    <body oncontextmenu="return false;" ondragstart="return false;" onselectstart="return false;">
        <form name="form_auth" method="post">
            {form_fields}
        </form>
        <div style="text-align:center; margin-top:20px;">
            <p>KCP 인증창으로 이동 중입니다...</p>
        </div>
    </body>
    </html>"""

        response = HTMLResponse(content=html_response)
        response.headers["Content-Security-Policy"] = "default-src 'self' *; script-src 'self' 'unsafe-inline' *; connect-src *;"
        return response
    except Exception as e:
        return HTMLResponse(content=f"<html><body><p>Error: {str(e)}</p></body></html>", status_code=500)


@router.post(
    "/kcp-callback",
    summary="KCP 인증 콜백",
    description="KCP 인증 완료 후 호출되는 콜백 엔드포인트",
    status_code=status.HTTP_200_OK
)
async def kcp_callback_sms(
    site_cd: str = Form(..., description="사이트 코드"),
    ordr_idxx: str = Form(..., description="주문번호 (세션ID)"),
    req_tx: str = Form(..., description="요청 구분"),
    cert_no: str = Form(..., description="인증번호"),
    enc_cert_data2: str = Form(..., description="암호화된 인증 데이터"),
    dn_hash: str = Form(..., description="다운 해시"),
    res_cd: str = Form(..., description="결과 코드"),
    res_msg: str = Form(None, description="결과 메시지")
):
    try:
        result = await simplified_phone_verification_service.process_kcp_callback(
            site_cd=site_cd,
            ordr_idxx=ordr_idxx,
            cert_no=cert_no,
            enc_cert_data2=enc_cert_data2,
            dn_hash=dn_hash,
            res_cd=res_cd
        )
        # 성공/실패 HTML 동일 패턴 (f-string 미사용)
        success = result.get("success", False)
        success_str = "true" if success else "false"
        phone = (result.get("phone", "") or "")
        phone_chk = (result.get("phone_chk", "") or "")
        ci = (result.get("ci", "") or "")
        di = (result.get("di", "") or "")
        message = (result.get("message", "") or "").replace("'", "\\'")
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset=\"utf-8\">
            <script>
                window.onload = function() {
                    const messageData = {
                        type: 'kcp_verification_complete',
                        success: %s,
                        phone: '%s',
                        phone_chk: '%s',
                        ci: '%s',
                        di: '%s',
                        message: '%s'
                    };
                    try {
                        if (window.parent && window.parent !== window) { window.parent.postMessage(messageData, '*'); }
                        if (window.opener) { window.opener.postMessage(messageData, '*'); }
                    } catch(e) {}
                    setTimeout(() => { window.close(); }, 200);
                }
            </script>
        </head>
        <body style=\"display:none;\"></body>
        </html>
        """ % (success_str, phone, phone_chk, ci, di, message)
        response = HTMLResponse(content=html, status_code=200 if success else 400)
        response.headers["Content-Security-Policy"] = "default-src 'self' *; script-src 'self' 'unsafe-inline' *; style-src 'self' 'unsafe-inline' *; connect-src *;"
        return response
    except Exception as e:
        return HTMLResponse(content=f"<html><body><p>Error: {str(e)}</p></body></html>", status_code=500)

@router.post(
    "/prepare-kcp-auth",
    response_model=ResponseWrapper[Dict[str, Any]],
    summary="KCP 인증 준비",
    description="KCP iframe 인증을 위한 up_hash 생성 및 세션 준비",
    status_code=status.HTTP_200_OK
)
@handle_errors
async def prepare_kcp_auth(
    request: SendCodeRequest
) -> ResponseWrapper[Dict[str, Any]]:
    """
    KCP 인증을 위한 up_hash 생성 및 세션 준비
    프론트엔드에서 직접 KCP iframe 호출을 위한 데이터 제공
    """
    try:
        service = simplified_phone_verification_service
        
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4()).replace("-", "")[:20]
        
        # Generate up_hash using KCP service
        kcp_config = service.kcp_config
        kcp_service = service.kcp_service
        
        # For KCP test environment with cert_able_yn = "Y"
        hash_data = (
            kcp_config.site_cd +     # "S6186"
            session_id +              # Session ID (20 chars)
            kcp_config.web_siteid +   # "J23022409076"
            "" +                      # user_name: empty
            "00" +                    # year: "00"
            "00" +                    # month: "00"
            "00" +                    # day: "00"
            "" +                      # sex_code: empty
            ""                        # local_code: empty
        )
        
        # Log the hash data for debugging
        print(f"Hash data for KCP (cert_able_yn=Y): site_cd={kcp_config.site_cd}, session_id={session_id}, web_siteid={kcp_config.web_siteid}")
        print(f"Hash data string: {hash_data}")
        
        # Generate up_hash using KCP binary
        up_hash = kcp_service.make_hash_data(hash_data)
        print(f"Generated up_hash: {up_hash}")
        
        # Store session in Redis for later verification
        await service.redis_service.create_verification_session(
            phone=request.phone,
            name=request.name,
            birth_date=request.birth_date
        )
        
        return ResponseWrapper(
            success=True,
            data={
                "session_id": session_id,
                "up_hash": up_hash,
                "site_cd": kcp_config.site_cd,
                "web_siteid": kcp_config.web_siteid,
                "return_url": "http://localhost:8000/api/v1/sms/kcp-callback"
            },
            message="KCP 인증 준비가 완료되었습니다."
        )
        
    except Exception as e:
        print(f"KCP prepare-kcp-auth error: {e}")
        import traceback
        traceback.print_exc()
        return ResponseWrapper(
            success=False,
            data=None,
            message="KCP 인증 준비 중 오류가 발생했습니다.",
            error={
                "type": "UnexpectedError",
                "detail": str(e)
            }
        )


@router.post(
    "/verify-code",
    response_model=ResponseWrapper[VerifyCodeResponse],
    summary="SMS 인증 코드 확인",
    description="발송된 인증 코드를 확인합니다.",
    status_code=status.HTTP_200_OK
)
@handle_errors
async def verify_code(
    request: VerifyCodeRequest
) -> ResponseWrapper[VerifyCodeResponse]:
    try:
        response = await simplified_phone_verification_service.verify_code(request)
        return ResponseWrapper(
            success=response.verified,
            data=response,
            message=response.message
        )
    except (ValidationError, BusinessLogicError) as e:
        return ResponseWrapper(
            success=False,
            data=None,
            message=str(e),
            error={
                "type": type(e).__name__,
                "detail": str(e)
            }
        )
    except Exception as e:
        return ResponseWrapper(
            success=False,
            data=None,
            message="인증 코드 확인 중 오류가 발생했습니다.",
            error={
                "type": "UnexpectedError",
                "detail": str(e)
            }
        )


@router.post(
    "/check-verified",
    response_model=ResponseWrapper[CheckVerifiedResponse],
    summary="인증 상태 확인",
    description="인증 토큰으로 인증 상태를 확인합니다.",
    status_code=status.HTTP_200_OK
)
@handle_errors
async def check_verified(
    request: CheckVerifiedRequest
) -> ResponseWrapper[CheckVerifiedResponse]:
    try:
        response = await simplified_phone_verification_service.check_verified(request)
        return ResponseWrapper(
            success=response.verified,
            data=response,
            message="인증 상태를 확인했습니다." if response.verified else "유효하지 않은 인증 토큰입니다."
        )
    except Exception as e:
        return ResponseWrapper(
            success=False,
            data=None,
            message="인증 확인 중 오류가 발생했습니다.",
            error={
                "type": "UnexpectedError",
                "detail": str(e)
            }
        )


@router.post(
    "/resend-code",
    response_model=ResponseWrapper[SendCodeResponse],
    summary="인증 코드 재발송",
    description="인증 코드를 다시 발송합니다.",
    status_code=status.HTTP_200_OK
)
@handle_errors
async def resend_verification_code(
    request: ResendCodeRequest
) -> ResponseWrapper[SendCodeResponse]:
    try:
        response = await simplified_phone_verification_service.resend_code(request.session_id)
        return ResponseWrapper(
            success=True,
            data=response,
            message="인증 코드가 재발송되었습니다."
        )
    except (ValidationError, BusinessLogicError, ExternalServiceError) as e:
        return ResponseWrapper(
            success=False,
            data=None,
            message=str(e),
            error={
                "type": type(e).__name__,
                "detail": str(e)
            }
        )
    except Exception as e:
        return ResponseWrapper(
            success=False,
            data=None,
            message="인증 코드 재발송 중 오류가 발생했습니다.",
            error={
                "type": "UnexpectedError",
                "detail": str(e)
            }
        )


