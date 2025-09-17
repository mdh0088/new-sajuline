<?php 
header("Content-type: text/html; charset=utf-8");

    //-----------------------------------------------------------------------------------------
    // Description    : 결제 요청 API URL 및 파라미터 설정
    //                - 테스트 URL : https://testpgapi.payletter.com/v1.0/payments/request
    //                - 라이브 URL : https://pgapi.payletter.com/v1.0/payments/request
    //                - 휴대폰 이외의 PG로 결제 요청시 설정할 파라미터는 가이드 문서를 참고하시기 바랍니다.
    //                - 가이드 문서 URL: https://pg.payletter.com/APIDocument/index.html
    //-----------------------------------------------------------------------------------------
    $strUrl = 'https://testpgapi.payletter.com/v1.0/payments/request'; 

    // 결제 요청 파라미터 설정 (JSON)
    // callback_url : 결제 완료 후 callback을 받을 가맹점 페이지 주소
    $strPostData = '{
            "pgcode"            : "mobile",
            "user_id"           : "tests",
            "user_name"         : "테스터",
            "service_name"      : "페이레터",
            "client_id"         : "pay_test",
            "order_no"          : "1234567890",
            "amount"            : 1000,
            "product_name"      : "테스트상품",
            "email_flag"        : "Y",
            "email_addr"        : "payletter@payletter.com",
            "autopay_flag"      : "N",
            "receipt_flag"      : "Y",
            "custom_parameter"  : "this is custom parameter",
            "return_url"        : "https://testpg.payletter.com/return.asp",
            "callback_url"      : "https://pg.payletter.com",    
            "cancel_url"        : "https://testpg.payletter.com/cancel.asp"
            }';

    //-----------------------------------------------------------------------------------------
    // Description    : 결제 요청 (POST)
    //                - HttpRequestHeader Authorization : PLKEY + {가맹점_apikey}
    //                - 가맹점 계약이 완료되면 API Key가 발급되며 가맹점 관리자 페이지에서 확인하실 수 있습니다.
    //                - 가입 전에 테스트 환경에서 미리 구성된 API Key로 연동 테스트가 가능합니다. 
    //                - 가맹점 아이디 : pay_test
    //                - API Key (PAYMENT) : MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=
    //                - API Key (SEARCH)  : MUI3MjM0RUExQTgyRDA1ODZGRDUyOEM4OTY2QTVCN0Y=
    //-----------------------------------------------------------------------------------------
    $arrHeaderData   = [];
    $arrHeaderData[] = 'Content-Type: application/json';
    $arrHeaderData[] = 'Authorization: PLKEY MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=';

    $objCurl = curl_init(); 
    curl_setopt($objCurl, CURLOPT_URL, $strUrl); 
    curl_setopt($objCurl, CURLOPT_HTTPHEADER, $arrHeaderData); 
    curl_setopt($objCurl, CURLOPT_POST, 1); 
    curl_setopt($objCurl, CURLOPT_POSTFIELDS, iconv("euc-kr", "utf-8", $strPostData)); 
    curl_setopt($objCurl, CURLOPT_RETURNTRANSFER, true);

    //-----------------------------------------------------------------------------------------
    // Description : API 요청에 대한 성공/실패 여부 (오류코드) 
    //               HTTP StatusCode 200 OK 인 경우에만 요청 처리 성공이며, 성공이 아닌 경우에는 아래 StatusCode를 참고하시기 바랍니다.          
    //               - 401 : [998] Authentication token is missing or incorrect. (인증 오류)
    //               - 403 : [993] Yon do not have authorization. (인증 오류)
    //               - 405 : [995] 요청된 메소드는 권한이 없습니다. (POST / GET 등 메소드 오류)
    //               - 406 : [2000]~[5000] 오류 상세 메시지 (비즈니스 로직 처리중 오류 발생)
    //               - 500 : [999] Internal server error (System 오류)
    //-----------------------------------------------------------------------------------------
        
    $strResponse   = curl_exec($objCurl); 

    // 요청 처리 성공인 경우                                       
    // Response Parameters (성공시) : token, online_url, mobile_url
    if(curl_getinfo($objCurl, CURLINFO_HTTP_CODE) == 200) 
    {
        echo $strResponse;
    }
    // 성공이 아닌 경우
    // Response Parameters (실패시) : code, message
    else
    {
        echo $strResponse;
    }

    curl_close($objCurl); 
?>
 