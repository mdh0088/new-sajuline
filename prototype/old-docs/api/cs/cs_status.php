<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";

$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$sms = new SMS($db);
$kakaoAlert = new kakaoAlert();

$cs_list = $cs -> getCsList();
foreach ($cs_list as $key => $value) {
    $ars_status = $ars->getCsStatus($cs_list[$key]['CODE']);
    $cs->update_cs_status($cs_list[$key]['IDX'],$ars_status);

    //대기자 알림톡 전송 로직 시작
    //현재 상태가 사주로 DB에서으 상태가 상담중 OR 부재중이고 ARS DB에서의 상태가 대기중이라면
    // -> 상태값이 대기중으로 변했다는 것을 의미, ARS가 항상 최신이므로.
    if (($cs_list[$key]['STATUS'] == 2 ||$cs_list[$key]['STATUS'] == 3) && $ars_status == 1){
        // 대기자 리스트를 뽑는다.
        $wait_list = $sms->read_wait_list($cs_list[$key]['IDX']);
        // 대기자가 1명이라도 있다면 전송 로직 시작
        if (count($wait_list) > 0){
            foreach ($wait_list as $smsKey => $smsValue) {
                // cs_login_alert으로 카카오 알림톡 전송
                $result = $kakaoAlert->cs_login_alert($wait_list[$smsKey]['PHONE'], $wait_list[$smsKey]['CS_NICK_NAME'], $cs_list[$key]['IDX']);
                //전송 결과가 성공이라면 해당 대기자 데이터 삭제
                if ($result['isSuc']){
                    $sms->delete_wait_list($wait_list[$smsKey]['USER_IDX'],$cs_list[$key]['IDX']);
                    $obj = array(
                        "USER_TYPE" => "USER",
                        "USER_IDX"=>$wait_list[$smsKey]['USER_IDX'],
                        "NO"=>$result['no'],
                        "CODE"=>$result['template'],
                        "CONT"=>$result['cont'],
                        "RESULT_CODE"=>$result['code']
                    );
                    $sms->add_history($obj);
                } else {
                    $obj = array(
                        "USER_TYPE" => "USER",
                        "USER_IDX"=>$wait_list[$smsKey]['USER_IDX'],
                        "NO"=>$result['no'],
                        "CODE"=>$result['template'],
                        "CONT"=>"",
                        "RESULT_CODE"=>$result['code']
                    );
                    $sms->add_history($obj);
                }
            }
        }
    }
}




//print_r($chatlist);

// query products
http_response_code(200);

