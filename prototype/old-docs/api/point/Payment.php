<?php
//header("Content-type: text/html; charset=utf-8");
header("Access-Control-Allow-Origin: https://sajutarot.com/api/");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/commonInfo.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/order.php';

// DB연결
$database = new Database(); $db = $database->getConnection();
$order    = new Order($db); $order_no =  $order -> generateOrderNumber();



session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인후 이용해주세요.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


$is_cs = $_SESSION['IS_CS'];
if ($_SESSION['IS_CS'] == 'Y'){
    echo json_encode(array("message" => "일반 이용자만 이용가능합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

$user_idx  = $_SESSION['IDX'];
$user_id   = $_SESSION['USER_ID'];
$nick_name = $_SESSION['NICK_NAME'];
$email     = $_SESSION['EMAIL'];

$data = json_decode($_POST["pointObj"]);
$strUrl = 'https://pgapi.payletter.com/v1.0/payments/request';


// 결제 요청 파라미터 설정 (JSON)
// callback_url : 결제 완료 후 callback을 받을 가맹점 페이지 주소

//$key = "mysajuro##";
//$encrypted = base64_encode($data->product_name ^ $key);
//$return_url     = "https://sajurot.com/app/charge/point_success";
//$return_url     = "https://sajurot.com/app/charge/return?amount='.$encrypted";

$return_url     = "https://sajutarot.com/api/point/return";
$cancel_url     = "https://sajutarot.com/app/charge/point_cancel";
$callback_url   = "https://sajutarot.com/api/point/CallBack";

if ($data -> charge_type == 'virtualaccount'){
    $callback_url   = "https://sajutarot.com/api/point/virtual_callback";
}

// 현재 시간에서 24시간 후의 Unix 타임스탬프 계산
$future_timestamp = time() + (24 * 60 * 60);
// yyymmdd 형식으로 날짜 포맷 지정
$date_format = 'Ymd';
// hhss 형식으로 시간 포맷 지정
$time_format = 'Hi';


$product_name="";
if ($data->point == '30000'){
    $product_name = "30000";
} else if($data->point == '50000'){
    $product_name = "50000";
} else if($data->point == '100000'){
    $product_name = "100000";
} else if($data->point == '200000'){
    $product_name = "200000";
} else if($data->point == '300000'){
    $product_name = "300000";
} else if($data->point == '500000'){
    $product_name = "500000";
} else {
    echo json_encode(array("message" => $data->product_name."데이터 변조는 중대범죄입니다.\n","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

$pay_key = "";
$client_id = "";
if ($data -> charge_type!="naverpay"){
    $pay_key = "RTkyQzg3MEU2QzEzMzUwOTBCNTAzRTUxOENCMjM4RDY=";
    $client_id = "sajurot";
} else {
    $pay_key = "OTRFQjlDREJCRUNFNDQ4MDRFM0NCNTQxN0NGREU2RDA=";
    //조회키 NzZBQzBFRjAxREVGQ0ZDODFFOTBGNUI0NkRFMzVCQkU=
    $client_id = "sajurot1";
}


// 날짜와 시간 출력
$strPostData = array(
                "pgcode"            => $data -> charge_type,                    //결제요청한 pg명
                "user_id"           => $user_id,                                //결제자 아이디
                "user_name"         => $nick_name,                              //결제자 닉네임
                "service_name"      => "사주로",                                 //결제 서비스명
                "client_id"         => $client_id,                               //결제 상점명
                "order_no"          => $order_no,                               //주문번호
                "amount"            => $data -> point + ($data -> point/10),    //결제 요청금액
                "taxfree_amount"    => 0,                                       //비과세 금액
                "tax_amount"        => $data -> tax_amount,                     //부가세 금액(세팅하지 않는 경우 (결제금액 - 비과세 금액)/11 : 소수점이하 반올림으로 자동 계산)
                "product_name"      => $product_name,
                "email_flag"        => "Y",
                "email_addr"        => $email,
                "autopay_flag"      => "N",
                "receipt_flag"      => "Y",
                "custom_parameter"  => $user_idx,
                "return_url"        => $return_url,
                "callback_url"      => $callback_url,
                "cancel_url"        => $cancel_url,
                "expire_date"       => date($date_format, $future_timestamp),
                "expire_time"       => date($time_format, $future_timestamp)
            );

//-----------------------------------------------------------------------------------------
// Description    : 결제 요청 (POST)
//                - HttpRequestHeader Authorization : PLKEY + {가맹점_apikey}
//                - 가맹점 계약이 완료되면 API Key가 발급되며 가맹점 관리자 페이지에서 확인하실 수 있습니다.
//                - 가입 전에 테스트 환경에서 미리 구성된 API Key로 연동 테스트가 가능합니다.
//                - 가맹점 아이디 : pay_test
//                - API Key (PAYMENT) : MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=
//                - API Key (SEARCH)  : MUI3MjM0RUExQTgyRDA1ODZGRDUyOEM4OTY2QTVCN0Y=
//-----------------------------------------------------------------------------------------




$headers = array(
    "Authorization: PLKEY $pay_key",
    "Content-Type: application/json"
);

$strPostData = json_encode($strPostData);
$objCurl = curl_init();
curl_setopt($objCurl, CURLOPT_URL, $strUrl);
curl_setopt($objCurl, CURLOPT_HTTPHEADER, $headers);
curl_setopt($objCurl, CURLOPT_POST, true);
curl_setopt($objCurl, CURLOPT_POSTFIELDS, iconv("euc-kr", "utf-8", $strPostData));
curl_setopt($objCurl, CURLOPT_RETURNTRANSFER, true);
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
    echo json_encode(array("message" => "알 수 없는 오류가 발생했습니다.\n관리자에게 문의 부탁드립니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    curl_close($objCurl);
    exit;
}

curl_close($objCurl);
?>
