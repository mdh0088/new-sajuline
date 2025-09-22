<?php
//header("Content-type: text/html; charset=utf-8");
header("Access-Control-Allow-Origin: https://www.sajuline.com/api/");
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
$database = new Database();
$db = $database->getConnection();
$order    = new Order($db);
$order_no =  $order -> generateOrderNumber();



session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인후 이용해주세요.","callback"=>"/","isSuc"=>FALSE));
    exit;
}


$is_cs = $_SESSION['IS_CS'];
if ($_SESSION['IS_CS'] == 'Y'){
    echo json_encode(array("message" => "일반 이용자만 이용가능합니다.","callback"=>"/","isSuc"=>FALSE));
    exit;
}

$user_idx  = $_SESSION['IDX'];
$user_id   = $_SESSION['USER_ID'];
$nick_name = $_SESSION['NICK_NAME'];
$email     = $_SESSION['EMAIL'];

$data = json_decode($_POST["pointObj"]);
$strUrl = 'https://pgapi.payletter.com/v1.0/payments/request';
//$strUrl = 'https://testpgapi.payletter.com/v1.0/payments/request'; //test용

// 결제 요청 파라미터 설정 (JSON)
// callback_url : 결제 완료 후 callback을 받을 가맹점 페이지 주소

//$key = "mysajuro##";
//$encrypted = base64_encode($data->product_name ^ $key);
//$return_url     = "https://sajurot.com/app/charge/point_success";
//$return_url     = "https://sajurot.com/app/charge/return?amount='.$encrypted";

$return_url     = "https://www.sajuline.com/api/point/return";
$cancel_url     = "https://www.sajuline.com/app/charge/point_cancel";
$callback_url   = "https://www.sajuline.com/api/point/CallBack";

if ($data -> charge_type == 'virtualaccount'){
    $callback_url   = "https://www.sajuline.com/api/point/virtual_callback";
}

// 현재 시간에서 24시간 후의 Unix 타임스탬프 계산
$future_timestamp = time() + (24 * 60 * 60);
// yyymmdd 형식으로 날짜 포맷 지정
$date_format = 'Ymd';
// hhss 형식으로 시간 포맷 지정
$time_format = 'Hi';


$user_info_query = "
SELECT
    TU.USER_ID
    , TU.GRADE
    , TG.DISCOUNT_VALUE
    , TG.GRADE_IMG
FROM TBL_USER TU LEFT JOIN TBL_GRADE TG ON TU.GRADE = TG.GRADE
WHERE
    TU.IDX = '".$user_idx."';
";
$user_info_stmt = $db->prepare( $user_info_query );
$user_info_stmt->execute();
$user_info = $user_info_stmt->fetch(PDO::FETCH_ASSOC);


// 쿼리 작성
$product_query = "
SELECT
    IDX,
    PRODUCT_NAME,
    PRODUCT_VALUE,

    -- 유저 할인율 포함 최종 할인율 (최소 0 보장)
    GREATEST(DISCOUNT_VALUE + {$user_info['DISCOUNT_VALUE']}, 0) AS TOTAL_DISCOUNT_RATE,

    -- 충전 포인트 적용 금액
    FLOOR(PRODUCT_VALUE * (1 + SAVE_VALUE / 100.0)) AS SAVE_VALUE,

    -- 할인 적용 금액
    FLOOR(PRODUCT_VALUE * (1 - GREATEST(DISCOUNT_VALUE + {$user_info['DISCOUNT_VALUE']}, 0) / 100.0)) AS DISCOUNT_VALUE,

    -- 세금 계산 (할인된 금액의 10%)

    -- 총액 (할인 적용 금액 + 세금)
    FLOOR(PRODUCT_VALUE * (1 - GREATEST(DISCOUNT_VALUE + {$user_info['DISCOUNT_VALUE']}, 0) / 100.0) * 1.1) AS TOTAL_PRICE

FROM TBL_PRODUCT
WHERE IDX = ".$data->product_no.";
";
$product_stmt = $db->prepare( $product_query );
$product_stmt->execute();
$product_info = $product_stmt->fetch(PDO::FETCH_ASSOC);

if (!$product_info){
    echo json_encode(array("message" => "데이터 변조는 중대범죄입니다.\n","callback"=>"/","isSuc"=>FALSE));
    exit;
}


$pay_key = "";
$client_id = "";
if ($data -> charge_type!="naverpay"){
    $pay_key = "RTkyQzg3MEU2QzEzMzUwOTBCNTAzRTUxOENCMjM4RDY=";
    $client_id = "sajurot";
    //$pay_key = "MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=";
    //$client_id = "pay_test";
} else {
    $pay_key = "OTRFQjlDREJCRUNFNDQ4MDRFM0NCNTQxN0NGREU2RDA=";
    //조회키 NzZBQzBFRjAxREVGQ0ZDODFFOTBGNUI0NkRFMzVCQkU=
    $client_id = "sajurot1";
    //$pay_key = "MTFBNTAzNTEwNDAxQUIyMjlCQzgwNTg1MkU4MkZENDA=";
    //$client_id = "pay_test";
}


// 날짜와 시간 출력
$strPostData = array(
                "pgcode"            => $data -> charge_type,                    //결제요청한 pg명
                "user_id"           => $user_id,                                //결제자 아이디
                "user_name"         => $nick_name,                              //결제자 닉네임
                "service_name"      => "사주라인",                                 //결제 서비스명
                "client_id"         => $client_id,                               //결제 상점명
                "order_no"          => $order_no,                               //주문번호
                //"amount"            => $data -> point + ($data -> point/10),    //결제 요청금액
                "amount"            => $product_info['TOTAL_PRICE'],
                "custom_parameter"        => $product_info['SAVE_VALUE'],
                "taxfree_amount"    => 0,                                       //비과세 금액
                //"tax_amount"        => $data -> tax_amount,                     //부가세 금액(세팅하지 않는 경우 (결제금액 - 비과세 금액)/11 : 소수점이하 반올림>으로 자동 계산)
                "tax_amount"        => $product_info['TAX_VALUE'],
                //"product_name"      => $product_name,
                "product_name"      => $product_info['PRODUCT_NAME'],
                "email_flag"        => "Y",
                "email_addr"        => $email,
                "autopay_flag"      => "N",
                "receipt_flag"      => "Y",
                //"custom_parameter"  => $user_idx,
                "return_url"        => $return_url,
                "callback_url"      => $callback_url,
                "cancel_url"        => $cancel_url,
                "expire_date"       => date($date_format, $future_timestamp),
                "expire_time"       => date($time_format, $future_timestamp)
            );


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
    curl_close($objCurl);
    exit;
}

curl_close($objCurl);
?>
