<?php
header("Content-type: text/html; charset=utf-8");

include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/order.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

$database       = new Database(); $db = $database->getConnection();
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$order          = new Order($db);
$ars            = new ARS($ars_db);
$utilities      = new Utilities($db);
$user           = new User($db);
$sms            = new SMS($db);
$kakaoAlert     = new kakaoAlert();

/*$objJsonData = json_decode(file_get_contents('php://input'));*/
$objJsonData = new stdClass();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $objJsonData = (object) $_POST;
}

if ($objJsonData->code == 0){
    $objJsonData->pay_type = "SUCCESS";
} ELSE {
    $objJsonData->pay_type = "FAIL";
}

//결제 정보가 있다면 다시 결제 페이지로 (뒤로가기 예방)
if ($utilities -> chkTableInfoByValue('TBL_USER_TRADE','ORDER_NO',$objJsonData->order_no)){
    header('Location: /app/charge/point');
    exit;
}

//결제 데이터 DB적제 로직
//결제 타입이 신용카드, 카카오라면
if($objJsonData->pgcode != 'virtualaccount'){

    $order -> create_trade_card($objJsonData);
    $chk_data = array("u_id" => $objJsonData->user_id,"u_point"=>$objJsonData->custom_parameter);
    if ($objJsonData->pay_type == "SUCCESS"){
        $ars -> charge_point($chk_data);
        $order -> save_user_trade_mileage($objJsonData->user_id, $objJsonData->amount, $objJsonData->order_no);
    }

    header('Location: /app/charge/return?charge_type=card&amount='.$objJsonData->amount.'&user_point='.$objJsonData->custom_parameter);
    exit;

//결제 타입이 무통장 입금이라면
} else if($objJsonData->pgcode == 'virtualaccount'){
    $order -> create_trade_virtual($objJsonData);
    header('Location: /app/charge/return?charge_type=virtual&amount='.$objJsonData->amount.'&user_point='.$objJsonData->custom_parameter);
    exit;
}

?>



