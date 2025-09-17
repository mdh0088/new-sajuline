<?php 
header("Content-type: text/html; charset=utf-8");

    //-----------------------------------------------------------------------------------------
    // Description    : Callback URL로 반환된 결제 결과 받아오기(json)
    //                - 결제가 성공한 경우 callback_url로 결제 결과가 반환됩니다. (json)
    //                - 전달받은 Callback URL 을 통해서 결과값을 받아서 가맹점에 맞는 충전, 구매 등의 로직을 수행하도록 합니다.
    //-----------------------------------------------------------------------------------------

    //-- Callback URL로 반환된 결제 결과 (JSON 파싱)
    $objJsonData = json_decode(file_get_contents('php://input'));

    if(empty($objJsonData))
    {
        echo "{\"code\":9999, \"message\":\"Response data is empty\"}";
        return;
    }

    //-----------------------------------------------------------------------------------------
    // Description    : 결제 결과 정보 세팅
    //                - 고객사에서 아래 결제 정보를 DB에 저장해 놓으시면 됩니다. 
    //                - 아래 정보들을 디버깅성으로 파일로그를 남겨놓으시기를 권고 드립니다.
    //                - Return Url / CallBack Url로 전달된 파라메터는 위/변조 방지를 위하여 SHA256 hash 값을 생성한 후 전달된 payhash 와 비교 검증을 수행하시기 바랍니다.
    //                - CallBack URL에서 처리 완료 후 성공시 {"code":0, "message":"실패시 실패 사유"} 형태의 json 문자열을 출력해 주시기 바랍니다.
    //                - code 가 0이 아닌 경우에는 통보가 실패한 것으로 간주되어 5분마다 최대 20번까지 재 전송됩니다.
    //-----------------------------------------------------------------------------------------    

    $strUserID              = $objJsonData->user_id;                    //--가맹점 결제자(회원) 아이디(email, 영문 및 숫자 가능)
    $strUserName            = $objJsonData->user_name;                  //--가맹점 결제자(회원) 이름
    $strOrderNo             = $objJsonData->order_no;                   //--가맹점의 주문 번호
    $strServiceName         = $objJsonData->service_name;               //--결제 서비스명
    $strProductName         = $objJsonData->product_name;               //--결제상품명

    $strCustomParameter     = $objJsonData->custom_parameter;           //--주문요청시 가맹점이 전송한 값
    $strTID                 = $objJsonData->tid;                        //--결제고유번호
    $strCID                 = $objJsonData->cid;                        //--승인번호
    $strAmt                 = $objJsonData->amount;                     //--결제요청 금액
    $strPayInfo             = $objJsonData->pay_info;                   //--결제 부가정보

    $strPGCode              = $objJsonData->pgcode;                     //--결제요청한 pg명
    $strDomesticFlag        = $objJsonData->domestic_flag;              //--국내 / 해외 신용카드 구분 (Y : 국내, N : 해외)
    $strBillKey             = $objJsonData->billkey;                    //--자동결제 재결제용 빌키
    $strTransactionDate     = $objJsonData->transaction_date;           //--거래일시(YYYY-MM-DD HH:MM:SS)
    $strCardInfo            = $objJsonData->card_info;                  //--카드 번호 (중간 4자리 masking 처리)

    $strPayHash             = $objJsonData->payhash;                    //--파라메터 검증을 위한 SHA256 hash 값 SHA256(user_id +amount + tid +결제용 API Key) * 일부 결제 수단은 전달되지 않습니다.(가상계좌 등)
    $strInstallMonth        = $objJsonData->install_month;               //--할부개월수

    //-- 현금영수증은 일부 결제 수단에 한해서 전달됩니다. callback_url에서 전달받은 결제 결과 확인 후 세팅 바랍니다.
    //$strReceiptCID          = $objJsonData->cash_receipt->cid;          //--승인번호
    //$strReceiptCode         = $objJsonData->cash_receipt->code;         //--결과코드
    //$strReceiptDealNo       = $objJsonData->cash_receipt->deal_no;      //--발급시 전달받은 주문번호
    //$strReceiptIssueType    = $objJsonData->cash_receipt->issue_type;   //--현금영수증 발행 구분(1:구매자발급, 2:자체발급)
    //$strReceiptMsg          = $objJsonData->cash_receipt->message;      //--결과메시지

    //$strReceiptPayerSID     = $objJsonData->cash_receipt->payer_sid;    //--신분확인 번호(휴대폰번호, 사업자번호)
    //$strReceiptType         = $objJsonData->cash_receipt->type;         //--거래자구분(01:소득공제용, 02:사업자지출증빙용)

    //-- 처리 완료 후 성공시 {"code":0, "message":"success"} 외의 html 및 다른 코드가 해당페이지에 노출 되지 않도록 합니다.
    //-- code 값은 성공시 0, 실패시 0이 아닌 값
    echo "{\"code\":0, \"message\":\"success\"}";
    

?>