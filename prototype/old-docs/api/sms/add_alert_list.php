<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';

$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$user = new User($db);
$sms = new SMS($db);

$data = json_decode($_POST["csObj"]);
session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인후 이용 부탁드립니다.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

$data->USER_IDX =$_SESSION['IDX'];
$chk_data = array("USER_IDX" => $data->USER_IDX,"CS_IDX" => $data->CS_IDX);
if($utilities -> chkTableInfoByObj('TBL_KAKAO_ALARM_WAIT_LIST',$chk_data)){
    echo json_encode(array("message" => "이미 알림 설정이 되었습니다.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


if ($sms->add_alert_list($data)){
    echo json_encode(array("message" => "등록 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}
?>
