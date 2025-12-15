<?php
header("Content-type: text/html; charset=utf-8");

include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/commonInfo.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/order.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

$objJsonData = json_decode(file_get_contents('php://input'));


// DB연결
$database       = new Database(); $db = $database->getConnection();
$order          = new Order($db); $order_no =  $order -> generateOrderNumber();
$utilities      = new Utilities($db);
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$user           = new User($db);
$sms            = new SMS($db);
$kakaoAlert     = new kakaoAlert();

$order -> create_trade_log($objJsonData);
$user_idx = $objJsonData->custom_parameter;

$hold_order_list  = $order->read_order_hold_by_orderno($objJsonData->order_no);
$order_count = count($hold_order_list);

//hold상태의 결제 수가 0개 이상라면 아래의 로직 수행
//if ($order_count > 0) {

$date_string = $objJsonData -> transaction_date;
$trsction_date= date("Ymd", strtotime($date_string));

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


//hold상태의 결제 수만큼 반복
foreach ($hold_order_list as $order_item) {
    //결제 요청한 날 기준으로 api 호출
    $url = "https://pgapi.payletter.com/v1.0/payments/transaction/list?" . http_build_query([
            "client_id" => "sajurot",
            "date" => $trsction_date,
            "date_type" => "transaction"
        ]);

    $headers = array(
        "Authorization: PLKEY ODE2NDFDNTg3RTU5NkI2QkY5QjhFRTVFMEVDNDYyOTE="
    );

    $objCurl = curl_init();
    curl_setopt($objCurl, CURLOPT_URL, $url);
    curl_setopt($objCurl, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($objCurl, CURLOPT_RETURNTRANSFER, true);
    $strResponse = curl_exec($objCurl);


    $obj = json_decode($strResponse, true);

    //반환된 결제 조회 값을 반복문 돌림, 2중 배열로 되어 있기에 for문 2번 돌린다.
    foreach ($obj as $innerArray) {
        foreach ($innerArray as $item) {
            if ($objJsonData->order_no == $item['order_no']) {
                //해당 일자에 결제혼 모든 결제가 조회되기 때문에 일일히 DB에서 조회해서 HOLD 상태의
                //결제 데이터를 찾는다.
                $chk_data = array("ORDER_NO" => $item['order_no'], "PAY_TYPE" => 'HOLD');
                //만약 해당 데이터가 잇다면 아래의 로직을 수행한다.
                if ($utilities->chkTableInfoByObj('TBL_USER_TRADE', $chk_data)) {
                    //SUCCESS로 상태를 변경한다.
                    if ($order->update_order_paytype($item['order_no'], 'SUCCESS',$objJsonData->amount)) {

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
                            } else if($product_name == '500000'){
                                $event_point = $u_point * (15 / 100);
                            }
                            $u_point = $u_point+$event_point;
                            $user->add_event_log('1',$objJsonData->custom_parameter,'충전 추가 포인트이벤트',$event_point);
                        }

                        //변경이 됐다면 ARS DB와 통신하여 포인트를 증가 시켜준다.
                        $chk_data = array("u_id" => $item['user_id'], "u_point" => $u_point);
                        $ars->charge_point($chk_data);
/*

                        $chk_data = array("IDX" => $objJsonData->custom_parameter);
                        $user_info= $utilities->readOne('TBL_USER',$chk_data);

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
                }
            }

        }
    }
}


//}



/*
if ($order->update_order_paytype($objJsonData->order_no,'SUCCESS')){
    //변경이 됐다면 ARS DB와 통신하여 포인트를 증가 시켜준다.
    $chk_data = array("u_id" => $objJsonData->user_id,"u_point"=>$objJsonData->product_name);
    $ars -> charge_point($chk_data);
}

*/



$current_timestamp = time();
$current_time = date('Y-m-d H:i:s', $current_timestamp);

$startToken = '--- START ('.$current_time.') ---';
$endToken = '--- END ('.$current_time.') --'. "\n";
$logData = $startToken . "\n";
foreach ($objJsonData as $key => $value) {
    $logData .= $key . ': ' . var_export($value, true) . "\n";
}
$logData .= $endToken . "\n";

$logFilePath = $_SERVER['DOCUMENT_ROOT'].'/log/charge/' . date('Ymd') . '.txt';
file_put_contents($logFilePath, $logData, FILE_APPEND);


echo "{\"code\":0, \"message\":\"success\"}";


?>
