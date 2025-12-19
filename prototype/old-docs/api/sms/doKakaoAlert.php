<?php
header('Content-Type: text/html; charset=UTF-8');


include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

// get database connection
$database = new Database();
$db = $database->getConnection();
// utilities
$utilities = new Utilities($db);
$kakaoAlert = new kakaoAlert();
$template = $_GET['template'];
$phone = $_GET['phone'];

$SMS = new SMS($db);

if ($phone!='') {
    $result="";

    if ($template == "50047") {
        $result = $kakaoAlert->cs_login_alert($phone, "무무문동", "123");
    } else if ($template == "50046") {
        $result = $kakaoAlert->cs_faq_alert($phone);
    } else if ($template == "50045") {
        $result = $kakaoAlert->user_faq_alert($phone, "무무문동");
    } else if ($template == "50044") {
        $result = $kakaoAlert->user_virtual_alert($phone, "무무문동", "2023-05-04", "20000", "ord-223344", "22000");
    } else if ($template == "50043") {
        $result = $kakaoAlert->user_money_request_alert($phone, "무무문동", "20000", "신한은행", "110-366-053669", "문동현", "2023-05-04", "22000");
    } else if ($template == "50042") {
        $result = $kakaoAlert->user_charge_confirm_alert($phone, "무무문동", "ord-223344", "22000", "20000", "456789");
    } else if ($template == "50041") {
        $result = $kakaoAlert->user_join_alert($phone, "무무문동");
    }

    if ($result['isSuc']){

        echo
        "
        결과 : 성공 <BR>
        탬플릿 : {$result['template']} <br>
        전송번호 : {$result['no']} <BR>
        결과코드 : {$result['code']} <BR>
        전송메시지 : {$result['cont']}
        ";


        $obj = array(
                    "USER_TYPE" => "USER",
                    "USER_IDX"=>"60",
                    "NO"=>$result['no'],
                    "CODE"=>$result['template'],
                    "CONT"=>$result['cont'],
                    "RESULT_CODE"=>$result['code']
                    );

        $SMS->add_history($obj);
    }


}


    //$kakaoAlert-> cs_login_alert("01047753790","무무문동","123");
    //$kakaoAlert-> cs_faq_alert("01047753790");
    //$kakaoAlert-> user_faq_alert("01047753790","무무문동");
    //$kakaoAlert-> user_virtual_alert("01047753790","무무문동","2023-05-04","20000","ord-223344","22000");
    //$kakaoAlert-> user_money_request_alert("01047753790","무무문동","20000","신한은행","110-366-053669","문동현","2023-05-04","22000");
    //$kakaoAlert-> user_charge_confirm_alert("01047753790","무무문동","ord-223344","22000","20000","456789");
    //$kakaoAlert-> user_join_alert("01047753790","무무문동");

    //$kakaoAlert->sendSMS($no, $tel_num, $reserve_time, $custom_key, $msg_content, $sms_content, $use_sms, $app_user_id, $url_pc, $url_mobile, $scheme_android, $scheme_ios);



