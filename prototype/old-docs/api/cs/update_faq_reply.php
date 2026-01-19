<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$sms = new SMS($db);
$kakaoAlert = new kakaoAlert();

$data = json_decode($_POST["csObj"]);

session_start();
$data ->CS_IDX = $_SESSION['IDX'];

if ($cs->update_faq_reply($data)){

    $chk_data = array("IDX" => $data->IDX);
    $faq_info= $utilities->readOne('TBL_CS_FAQ',$chk_data);

    $chk_data = array("IDX" => $faq_info['USER_IDX']);
    $user_info= $utilities->readOne('TBL_USER',$chk_data);

    $result = $kakaoAlert->user_faq_alert($user_info['PHONE'], $user_info['NICK_NAME']);
    if ($result['isSuc']){
        $obj = array(
            "USER_TYPE" => "USER",
            "USER_IDX"=>$user_info['IDX'],
            "NO"=>$result['no'],
            "CODE"=>$result['template'],
            "CONT"=>$result['cont'],
            "RESULT_CODE"=>$result['code']
        );
        $sms->add_history($obj);
    } else {
        $obj = array(
            "USER_TYPE" => "USER",
            "USER_IDX"=>$user_info['IDX'],
            "NO"=>$result['no'],
            "CODE"=>$result['template'],
            "CONT"=>"",
            "RESULT_CODE"=>$result['code']
        );
        $sms->add_history($obj);
    }

    echo json_encode(array("message" => "저장 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);

}
?>
