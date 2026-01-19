"""
KCP Callback Router

KCP 본인인증 서비스의 콜백을 처리하는 라우터
"""
from fastapi import APIRouter, Form, HTTPException
from typing import Optional
import logging

from ..application.simplified_service import simplified_phone_verification_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/phone-verification/kcp",
    tags=["KCP Callback"]
)


@router.post("/callback")
async def kcp_callback(
    site_cd: str = Form(..., description="사이트 코드"),
    ordr_idxx: str = Form(..., description="주문번호 (세션ID)"),
    req_tx: str = Form(..., description="요청 구분"),
    cert_no: str = Form(..., description="인증번호"),
    enc_cert_data2: str = Form(..., description="암호화된 인증 데이터"),
    dn_hash: str = Form(..., description="다운 해시"),
    res_cd: str = Form(..., description="결과 코드"),
    res_msg: str = Form(None, description="결과 메시지")
):
    """
    KCP 본인인증 콜백 처리
    
    KCP 인증창에서 인증 완료 후 호출되는 엔드포인트.
    smartcert_proc_res.php 로직을 Python으로 구현.
    """
    try:
        logger.info(f"KCP callback received for session: {ordr_idxx}, res_cd: {res_cd}")
        
        # Process KCP callback
        result = await simplified_phone_verification_service.process_kcp_callback(
            site_cd=site_cd,
            ordr_idxx=ordr_idxx,
            cert_no=cert_no,
            enc_cert_data2=enc_cert_data2,
            dn_hash=dn_hash,
            res_cd=res_cd
        )
        
        if result["success"]:
            # 성공 시 HTML 응답 (기존 PHP와 동일한 방식)
            # 프론트엔드에 결과 전달
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script>
                    // 즉시 실행으로 변경하여 모달 표시 시간 최소화
                    (function() {{
                        try {{
                            // 모바일과 PC 구분
                            if (navigator.maxTouchPoints) {{
                                // 모바일
                                window.parent.postMessage({{
                                    type: 'kcp_verification_complete',
                                    success: true,
                                    phone: '{result.get("phone", "")}',
                                    phone_chk: '{result.get("phone_chk", "")}',
                                    ci: '{result.get("ci", "")}',
                                    di: '{result.get("di", "")}'
                                }}, '*');
                            }} else {{
                                // PC
                                if (window.opener) {{
                                    window.opener.postMessage({{
                                        type: 'kcp_verification_complete',
                                        success: true,
                                        phone: '{result.get("phone", "")}',
                                        phone_chk: '{result.get("phone_chk", "")}',
                                        ci: '{result.get("ci", "")}',
                                        di: '{result.get("di", "")}'
                                    }}, '*');
                                }}
                            }}
                            // 즉시 창 닫기
                            setTimeout(function() {{
                                window.close();
                            }}, 100); // 100ms 후 창 닫기로 메시지 전달 시간 확보
                        }} catch(e) {{
                            console.error('KCP callback error:', e);
                            window.close();
                        }}
                    }})();
                </script>
            </head>
            <body>
                <!-- 메시지 숨김 처리 -->
            </body>
            </html>
            """
            
            from fastapi.responses import HTMLResponse
            # KCP 콜백 페이지는 인라인 스크립트/스타일을 사용하므로 CSP를 완화합니다 (이 응답에 한함)
            csp = (
                "default-src 'self' https: data: blob:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
                "style-src 'self' 'unsafe-inline' https:; "
                "img-src 'self' https: data:; "
                "connect-src 'self' https:; "
                "frame-ancestors *;"
            )
            return HTMLResponse(content=html_response, headers={"Content-Security-Policy": csp})
        else:
            # 실패 시 HTML 응답
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script>
                    window.onload = function() {{
                        try {{
                            if (navigator.maxTouchPoints) {{
                                window.parent.postMessage({{
                                    type: 'kcp_verification_complete',
                                    success: false,
                                    message: '{result.get("message", "인증에 실패했습니다.")}'
                                }}, '*');
                            }} else {{
                                if (window.opener) {{
                                    window.opener.postMessage({{
                                        type: 'kcp_verification_complete',
                                        success: false,
                                        message: '{result.get("message", "인증에 실패했습니다.")}'
                                    }}, '*');
                                }}
                            }}
                            alert('{result.get("message", "인증에 실패했습니다.")}');
                            window.close();
                        }} catch(e) {{
                            console.error('KCP callback error:', e);
                            alert('{result.get("message", "인증에 실패했습니다.")}');
                        }}
                    }}
                </script>
            </head>
            <body>
                <p>{result.get("message", "인증에 실패했습니다.")}</p>
            </body>
            </html>
            """
            
            from fastapi.responses import HTMLResponse
            csp = (
                "default-src 'self' https: data: blob:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
                "style-src 'self' 'unsafe-inline' https:; "
                "img-src 'self' https: data:; "
                "connect-src 'self' https:; "
                "frame-ancestors *;"
            )
            return HTMLResponse(content=html_response, status_code=400, headers={"Content-Security-Policy": csp})
            
    except Exception as e:
        logger.error(f"KCP callback processing error: {e}")
        raise HTTPException(status_code=500, detail="인증 처리 중 오류가 발생했습니다.")


