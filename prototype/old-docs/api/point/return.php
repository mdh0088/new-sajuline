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
    exit;
    header('Location: /app/charge/point');
}

//결제 데이터 DB적제 로직
//결제 타입이 신용카드, 카카오라면

$u_point = 0;
$product_name = $objJsonData->product_name;
if ($product_name == '30000'){
    $u_point = 30000;
} else if($product_name == '50000'){
    $u_point = 50000 ;
} else if($product_name == '100000'){
    $u_point = 100000;
} else if($product_name == '200000'){
    $u_point = 200000;
} else if($product_name == '300000'){
    $u_point = 300000;
} else if($product_name == '500000'){
    $u_point = 500000;
}
$order_info = $order->read_charge_event();
$current_date = date("Y-m-d H:i:s");
$start_date = $order_info['START_DATE'];
$end_date = $order_info['END_DATE'];

//이벤트 중이라면 추가 포인트 지급
if ($current_date >= $start_date  &&  $current_date < $end_date && $order_info['USE_YN']=='Y'){
    $event_point=0;
    if ($product_name == '30000'){
        $event_point = $u_point * (5 / 100);
    } else if($product_name == '50000'){
        $event_point = $u_point * (5 / 100);
    } else if($product_name == '100000'){
        $event_point = $u_point * (10 / 100);
    } else if($product_name == '200000'){
        $event_point = $u_point * (10 / 100);
    } else if($product_name == '300000'){
        $event_point = $u_point * (15 / 100);
    } else if($product_name == '500000'
    ){
        $event_point = $u_point * (15 / 100);
    }
    $u_point = $u_point+$event_point;
    $user->add_event_log('1',$objJsonData->custom_parameter,'충전 추가 포인트이벤트',$event_point);
}
$objJsonData->product_name = $u_point;

if($objJsonData->pgcode != 'virtualaccount'){

    $order -> create_trade_card($objJsonData);
    $chk_data = array("u_id" => $objJsonData->user_id,"u_point"=>$u_point);
    if ($objJsonData->pay_type == "SUCCESS"){
        $ars -> charge_point($chk_data);

        /*
        $chk_data = array("IDX" => $objJsonData->custom_parameter);
        $user_info= $utilities->readOne('TBL_USER',$chk_data);

        //$chk_data = array("USER_ID" => $user_info['USER_ID'],"PHONE" => $user_info['PHONE']);
        //$ars_userObj = $ars->getUserInfo($chk_data);

        $phone = $user_info['PHONE'];
        $user_nick_name = $user_info['NICK_NAME'];
        $order_no = $objJsonData->order_no;
        $product_name = $objJsonData->product_name;
        $amount = $objJsonData->amount;
        //$point = $ars_userObj['u_point'];
        $point = $objJsonData->product_name;

        $result = $kakaoAlert->user_charge_confirm_alert($phone, $user_nick_name,$order_no,$product_name,$amount,$point);

        if ($result['isSuc']){
            $obj = array(
                "USER_TYPE" => "USER",
                "USER_IDX"=>$objJsonData->custom_parameter,
                "NO"=>$result['no'],
                "CODE"=>$result['template'],
                "CONT"=>$result['cont'],
                "RESULT_CODE"=>$result['code']
            );
            $sms->add_history($obj);
        } else {
            $obj = array(
                "USER_TYPE" => "USER",
                "USER_IDX"=>$objJsonData->custom_parameter,
                "NO"=>$result['no'],
                "CODE"=>$result['template'],
                "CONT"=>"",
                "RESULT_CODE"=>$result['code']
            );
            $sms->add_history($obj);
        }*/
    }

    header('Location: /app/charge/return?charge_type=card&amount='.$u_point);
    exit;

//결제 타입이 무통장 입금이라면
} else if($objJsonData->pgcode == 'virtualaccount'){
    $order -> create_trade_virtual($objJsonData);
    header('Location: /app/charge/return?charge_type=virtual&amount='.$objJsonData->amount);
    exit;
}

?>



