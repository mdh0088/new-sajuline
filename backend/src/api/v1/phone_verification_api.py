"""
휴대폰 본인인증 API

KCP 본인인증을 사용한 휴대폰 인증 엔드포인트
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.phone_verification_service import (
    PhoneVerificationService,
    get_phone_verification_service
)
from typing import Optional, Dict
from src.schemas.phone_verification_schema import (
    PhoneVerificationInitiateRequest,
    PhoneVerificationInitiateResponse,
    PhoneVerificationStatusResponse,
    PhoneVerificationForFindIdRequest,
    PhoneVerificationForFindPasswordRequest
)
from src.schemas.user_schema import FindPasswordRequest
from src.common.response.wrapper import ok, APIResponse
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError
from src.config.settings import settings

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
            phone=request.phone_number[:3] + "****" + request.phone_number[-4:],
            return_url=request.return_url)

    result = await phone_service.initiate_verification(
        phone_number=request.phone_number,
        return_url=request.return_url
    )

    return ok(
        data=PhoneVerificationInitiateResponse(**result),
        message="본인인증이 시작되었습니다"
    )


@router.post(
    "/initiate-for-find-id",
    response_model=APIResponse[PhoneVerificationInitiateResponse],
    summary="ID 찾기용 본인인증 시작",
    description="ID 찾기를 위한 본인인증 프로세스를 시작합니다 (전화번호 미입력)"
)
async def initiate_verification_for_find_id(
    request: PhoneVerificationForFindIdRequest,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """ID 찾기용 본인인증 시작"""
    log = get_logger_with_request_id()
    log.info("Phone verification for find-id request", return_url=request.return_url)

    result = await phone_service.initiate_verification_for_find_id(
        return_url=request.return_url
    )

    return ok(
        data=PhoneVerificationInitiateResponse(**result),
        message="본인인증이 시작되었습니다"
    )


@router.post(
    "/initiate-for-find-password",
    response_model=APIResponse[PhoneVerificationInitiateResponse],
    summary="비밀번호 찾기용 본인인증 시작",
    description="비밀번호 찾기를 위한 본인인증 프로세스를 시작합니다 (user_id 포함)"
)
async def initiate_verification_for_find_password(
    request: PhoneVerificationForFindPasswordRequest,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """비밀번호 찾기용 본인인증 시작"""
    log = get_logger_with_request_id()
    log.info("Phone verification for find-password request",
             user_id=request.user_id,
             return_url=request.return_url)

    result = await phone_service.initiate_verification_for_find_password(
        user_id=request.user_id,
        return_url=request.return_url
    )

    return ok(
        data=PhoneVerificationInitiateResponse(**result),
        message="본인인증이 시작되었습니다"
    )


async def _kcp_callback_handler(
    result:Dict
) -> HTMLResponse:
    """KCP 콜백 처리 핸들러 (GET/POST 공통)"""
    log = get_logger_with_request_id()
    log.info("KCP callback received",
            result=result)
    try:
        # 성공 응답 HTML (Popup + Fallback 패턴)
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>본인인증 완료</title>
            <script>
                window.onload = function() {{
                    const messageData = {{
                        type: 'kcp_verification_complete',
                        success: true,
                        phone: '{result.get("phone", "")}',
                        phone_chk: '{result.get("phone_chk", "")}',
                        is_phone_matched: {str(result.get("is_phone_matched", False)).lower()},
                        ci: '{result.get("ci", "")}',
                        di: '{result.get("di", "")}',
                        name: '{result.get("name", "")}',
                        birth_date: '{result.get("birth_date", "")}',
                        gender: '{result.get("gender", "")}'
                    }};

                    let sent = false;

                    // 1. Try posting to opener window (popup case - Desktop 우선)
                    try {{
                        if (window.opener && !window.opener.closed) {{
                            console.log('[KCP] Sending postMessage to opener');
                            window.opener.postMessage(messageData, '*');
                            sent = true;
                        }}
                    }} catch(e) {{
                        console.error('[KCP] Failed to send to opener:', e);
                    }}

                    // 2. opener가 없으면 parent 시도 (iframe case - 현재 미사용)
                    if (!sent) {{
                        try {{
                            if (window.parent && window.parent !== window) {{
                                console.log('[KCP] Sending postMessage to parent');
                                window.parent.postMessage(messageData, '*');
                                sent = true;
                            }}
                        }} catch(e) {{
                            console.error('[KCP] Failed to send to parent:', e);
                        }}
                    }}

                    // 3. Fallback: 둘 다 실패한 경우 리다이렉트 (Mobile)
                    if (!sent) {{
                        console.log('[KCP] Fallback: Redirecting to page');

                        // KCP 결과를 URL query parameter로 전달
                        const params = new URLSearchParams({{
                            from_kcp: 'true',
                            phone: '{result.get("phone", "")}',
                            phone_chk: '{str(result.get("is_phone_matched", False)).lower()}',
                            verified_phone: '{result.get("phone", "")}'
                        }});

                        // 비밀번호 찾기용 user_id 추가 (있는 경우에만)
                        const userId = '{result.get("user_id", "")}';
                        if (userId) {{
                            params.append('user_id', userId);
                        }}

                        // Redirect to page with KCP result (환경변수 기반 URL)
                        window.location.href = `{settings.frontend_url}{result.get("return_url", "/signup")}?${{params.toString()}}`;
                    }} else {{
                        // Success - close popup after delay
                        setTimeout(function() {{
                            try {{ window.close(); }} catch(e) {{}}
                        }}, 200);
                    }}
                }}
            </script>
        </head>
        <body style="display:none;">
            <p style="text-align:center; margin-top:20px;">인증이 완료되었습니다. 잠시만 기다려주세요...</p>
        </body>
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


@router.api_route(
    "/callback",
    methods=["GET", "POST"],
    response_class=HTMLResponse,
    summary="KCP 콜백 처리",
    description="KCP 인증 완료 후 콜백을 처리합니다 (GET/POST)"
)
async def kcp_callback(
    request: Request,
    session_id: Optional[str] = None,
    phone_service: PhoneVerificationService = Depends(get_phone_verification_service)
):
    """KCP 콜백 처리 - GET/POST 모두 지원

    KCP 인증 완료 후:
    1. POST: KCP에서 인증 결과와 함께 호출 → 처리 후 프론트엔드로 리다이렉트
    2. GET: 세션 상태 확인 후 프론트엔드로 리다이렉트 (모바일 fallback)
    """
    log = get_logger_with_request_id()

    # session_id 추출 (쿼리 파라미터에서)
    if not session_id:
        session_id = request.query_params.get("session_id", "")

    log.info("KCP callback received",
            method=request.method,
            session_id=session_id,
            query_params=dict(request.query_params))

    try:
        # POST 요청: KCP에서 인증 결과와 함께 호출
        if request.method == "POST":
            # Form 데이터 파싱
            form_dict = getattr(request.state, "request_body", {})

            # request_body가 비어있거나 메타데이터만 있는 경우 직접 파싱
            if not form_dict or "content_type" in form_dict:
                try:
                    form_data = await request.form()
                    form_dict = dict(form_data)
                    log.info("KCP callback - Form data parsed",
                            form_keys=list(form_dict.keys()))
                except Exception as e:
                    log.warning("KCP callback - Failed to parse form data", error=str(e))
                    form_dict = {}

            # KCP 필수 파라미터 추출
            site_cd = form_dict.get("site_cd", "")
            ordr_idxx = form_dict.get("ordr_idxx", "") or session_id
            cert_no = form_dict.get("cert_no", "")
            enc_cert_data2 = form_dict.get("enc_cert_data2", "")
            dn_hash = form_dict.get("dn_hash", "")
            res_cd = form_dict.get("res_cd", "")
            res_msg = form_dict.get("res_msg", "")

            # 필수 파라미터 검증
            if all([site_cd, ordr_idxx, cert_no, enc_cert_data2, dn_hash, res_cd]):
                # KCP 결과 처리
                result = await phone_service.process_callback(
                    site_cd=site_cd,
                    ordr_idxx=ordr_idxx,
                    cert_no=cert_no,
                    enc_cert_data2=enc_cert_data2,
                    dn_hash=dn_hash,
                    res_cd=res_cd,
                    res_msg=res_msg
                )

                log.info("KCP callback processed successfully",
                        session_id=ordr_idxx,
                        phone=result.get("phone", "")[:3] + "****")

                # 성공 시 프론트엔드로 리다이렉트 또는 postMessage
                return await _kcp_callback_handler(result)
            else:
                # POST인데 필수 파라미터 없음 → 세션에서 결과 확인
                log.warning("KCP callback POST - Missing required parameters, checking session",
                           session_id=session_id)

        # GET 요청 또는 POST에서 파라미터 없는 경우: 세션 상태 확인
        if not session_id:
            log.info("KCP callback - No session_id provided")
            return _render_info_page("본인인증 페이지",
                                    "이 페이지는 직접 접근할 수 없습니다.<br>회원가입 페이지에서 본인인증을 진행해주세요.")

        # 세션 상태 확인
        session_data = await phone_service.get_verification_status(session_id)

        if not session_data:
            log.warning("KCP callback - Session not found", session_id=session_id)
            return _render_info_page("세션 만료",
                                    "인증 세션이 만료되었습니다.<br>다시 인증을 진행해주세요.")

        session_status = session_data.get("status", "")
        return_url = session_data.get("return_url", "/signup")

        log.info("KCP callback - Session status check",
                session_id=session_id,
                status=session_status,
                return_url=return_url)

        if session_status == "verified":
            # 이미 인증 완료된 경우 → 프론트엔드로 리다이렉트
            result = {
                "success": True,
                "phone": session_data.get("phone", ""),
                "phone_chk": session_data.get("phone_chk", ""),
                "is_phone_matched": session_data.get("phone") == session_data.get("phone_number"),
                "ci": session_data.get("ci", ""),
                "di": session_data.get("di", ""),
                "name": session_data.get("verified_name", ""),
                "birth_date": session_data.get("verified_birth_date", ""),
                "gender": session_data.get("verified_gender", ""),
                "return_url": return_url,
                "user_id": session_data.get("user_id", "")
            }
            return await _kcp_callback_handler(result)
        elif session_status == "initiated":
            # 인증 대기 중 → 대기 페이지 표시
            return _render_info_page("인증 처리 중",
                                    "본인인증을 처리하고 있습니다.<br>잠시만 기다려주세요...",
                                    auto_refresh=True)
        else:
            # 알 수 없는 상태
            return _render_info_page("인증 오류",
                                    "인증 처리 중 오류가 발생했습니다.<br>다시 시도해주세요.")

    except ValidationError as e:
        log.error("KCP callback validation error", error=str(e))
        return _render_error_page(str(e))
    except Exception as e:
        log.error("KCP callback processing failed", error=str(e), exc_info=True)
        return _render_error_page("인증 처리 중 오류가 발생했습니다.")


def _render_info_page(title: str, message: str, auto_refresh: bool = False) -> HTMLResponse:
    """안내 페이지 렌더링"""
    refresh_script = """
        <script>
            // 3초 후 새로고침
            setTimeout(function() {
                window.location.reload();
            }, 3000);
        </script>
    """ if auto_refresh else ""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {refresh_script}
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 20px;
            }}
            .container {{ max-width: 400px; }}
            h2 {{ margin-bottom: 16px; }}
            p {{ margin-bottom: 24px; opacity: 0.9; line-height: 1.6; }}
            a {{
                display: inline-block;
                padding: 12px 24px;
                background: white;
                color: #764ba2;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{title}</h2>
            <p>{message}</p>
            <a href="{settings.frontend_url}">홈으로 돌아가기</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


def _render_error_page(error_message: str) -> HTMLResponse:
    """에러 페이지 렌더링 (postMessage + 리다이렉트)"""
    safe_error = error_message.replace("'", "\\'").replace('"', '\\"')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script>
            window.onload = function() {{
                const messageData = {{
                    type: 'kcp_verification_complete',
                    success: false,
                    message: '{safe_error}'
                }};
                try {{
                    if (window.opener && !window.opener.closed) {{
                        window.opener.postMessage(messageData, '*');
                    }}
                    if (window.parent && window.parent !== window) {{
                        window.parent.postMessage(messageData, '*');
                    }}
                }} catch(e) {{}}
                setTimeout(function() {{
                    try {{ window.close(); }} catch(e) {{
                        window.location.href = '{settings.frontend_url}';
                    }}
                }}, 500);
            }}
        </script>
    </head>
    <body style="display:none;"></body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


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
