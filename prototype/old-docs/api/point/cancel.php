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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';

// DB연결
$database = new Database(); $db = $database->getConnection();
$order    = new Order($db);
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);

$data = json_decode($_POST["orderObj"]);
$orderInfo = $order->read_trade_idx($data->IDX);

$tid      = $orderInfo['TID'];
$user_idx = $orderInfo['USER_IDX'];
$user_id  = $orderInfo['USER_ID'];
$amount   = $orderInfo['AMOUNT'];
$pgcode   = $orderInfo['PGCODE'];
$product_name = $orderInfo['PRODUCT_NAME'];

$arsInfo = $ars->getUserInfoById($user_id);
$ars_point =  $arsInfo['u_point'];

$chk_point = $ars_point - $product_name;

if( $chk_point < 0 ){
    http_response_code(200);
    echo json_encode(array("message" => "취소할 포인트가 부족합니다.\n 현재 포인트 : ".$ars_point,"isSuc"=>FALSE));
    exit;
}

$data = array(
    'pgcode' => $pgcode,
    'client_id' => 'sajurot',
    'user_id' => $user_id,
    'tid'    => $tid,
    'amount' => $amount,
    'ip_addr' => '183.111.182.230'
);

// JSON 형식으로 인코딩합니다.
$jsonData = json_encode($data);

// cURL 초기화합니다.
$ch = curl_init();

// cURL 옵션을 설정합니다.
curl_setopt($ch, CURLOPT_URL, 'https://pgapi.payletter.com/v1.0/payments/cancel');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Authorization: PLKEY RTkyQzg3MEU2QzEzMzUwOTBCNTAzRTUxOENCMjM4RDY=',
    'Content-Type: application/json'
));
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);

// cURL 실행합니다.
$response = curl_exec($ch);

// cURL 종료합니다.
curl_close($ch);

// 결과를 출력합니다.
$cancel_info = json_decode($response);
if (isset($cancel_info->tid)) {
    $cancel_tid     = $cancel_info->tid;
    $cancel_cid     = $cancel_info->cid;
    $cancel_amount  = $cancel_info->amount;
    $cancel_date    = $cancel_info->cancel_date;

    $order->update_cancel_info($cancel_tid,$cancel_amount,$cancel_date);
    $ars -> update_point_by_cancel($user_id,$chk_point);

    http_response_code(200);
    echo json_encode(array("message" => "취소 되었습니다.","isSuc"=>TRUE));
    exit;
} else {
    http_response_code(200);
    echo json_encode(array("message" => "관리자에게 문의 부탁드립니다.","isSuc"=>FALSE));
    exit;
}

?>
