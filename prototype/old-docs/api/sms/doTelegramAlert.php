<?php
header('Content-Type: text/html; charset=UTF-8');


include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_telegram.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

// get database connection
$database = new Database();
$db = $database->getConnection();
// utilities
$utilities = new Utilities($db);
$telegramAlert = new TelegramAlert();

$telegramAlert->sendSMS();



//$kakaoAlert-> cs_login_alert("01047753790","무무문동","123");
//$kakaoAlert-> cs_faq_alert("01047753790");
//$kakaoAlert-> user_faq_alert("01047753790","무무문동");
//$kakaoAlert-> user_virtual_alert("01047753790","무무문동","2023-05-04","20000","ord-223344","22000");
//$kakaoAlert-> user_money_request_alert("01047753790","무무문동","20000","신한은행","110-366-053669","문동현","2023-05-04","22000");
//$kakaoAlert-> user_charge_confirm_alert("01047753790","무무문동","ord-223344","22000","20000","456789");
//$kakaoAlert-> user_join_alert("01047753790","무무문동");

//$kakaoAlert->sendSMS($no, $tel_num, $reserve_time, $custom_key, $msg_content, $sms_content, $use_sms, $app_user_id, $url_pc, $url_mobile, $scheme_android, $scheme_ios);



