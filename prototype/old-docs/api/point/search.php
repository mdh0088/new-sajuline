<?php
/*
header("Access-Control-Allow-Origin: https://sajurot.com/api/");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");
*/

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/commonInfo.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/order.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';

// DB연결
$database       = new Database(); $db = $database->getConnection();
$order          = new Order($db); $order_no =  $order -> generateOrderNumber();
$utilities      = new Utilities($db);
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);


session_start();
if (!isset($_SESSION['IDX'])){
    exit;
}

if ($_SESSION['IS_CS']=='Y'){
    exit;
}

//hold인 상태의 결제 리스트 찾음
$hold_order_list  = $order->read_order_hold($_SESSION['IDX']);
$order_count = count($hold_order_list);

//hold상태의 결제 수가 0개 이상라면 아래의 로직 수행
if ($order_count > 0) {

    //hold상태의 결제 수만큼 반복
    foreach ($hold_order_list as $order_item) {
        //결제 요청한 날 기준으로 api 호출
        $url = "https://pgapi.payletter.com/v1.0/payments/transaction/list?" . http_build_query([
                "client_id" => "sajurot",
                "date"      => $order_item['REGIST_DATE'],
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


        $obj = json_decode($strResponse,true);

        //반환된 결제 조회 값을 반복문 돌림, 2중 배열로 되어 있기에 for문 2번 돌린다.
        foreach ($obj as $innerArray) {
            foreach ($innerArray as $item) {
                //해당 일자에 결제혼 모든 결제가 조회되기 때문에 일일히 DB에서 조회해서 HOLD 상태의
                //결제 데이터를 찾는다.
                $chk_data = array("ORDER_NO" => $item['order_no'],"PAY_TYPE" => 'HOLD',"USER_IDX"=>$_SESSION['IDX']);

                //만약 해당 데이터가 잇다면 아래의 로직을 수행한다.
                if($utilities -> chkTableInfoByObj('TBL_USER_TRADE',$chk_data)){
                    //SUCCESS로 상태를 변경한다.
                    if ($order->update_order_paytype($item['order_no'],'SUCCESS')){
                        //변경이 됐다면 ARS DB와 통신하여 포인트를 증가 시켜준다.
                        $chk_data = array("u_id" => $item['user_id'],"u_point"=>$item['amount']);
                        $ars -> charge_point($chk_data);
                    }
                }
            }
        }
    }


}




?>
