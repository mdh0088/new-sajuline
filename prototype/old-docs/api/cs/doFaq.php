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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$sms = new SMS($db);
$kakaoAlert = new kakaoAlert();

$data = json_decode($_POST["faqObj"]);
session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인후 이용 부탁드립니다.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
} else {
    $data -> USER_IDX = $_SESSION['IDX'];
}
if ($_SESSION['IS_CS'] == 'Y'){
    echo json_encode(array("message" => "상담사 계정으로는 문의가 불가능합니다. \n 관리자에게 문의 부탁드립니다. ","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
if ($cs->doFaq($data)){

    $chk_data = array("IDX" => $data->IDX,"APPROVAL_YN" => 'Y');
    $cs_info= $utilities->readOne('TBL_CS',$chk_data);
    $result = $kakaoAlert->cs_faq_alert($cs_info['PHONE']);
    if ($result['isSuc']){
        $obj = array(
            "USER_TYPE" => "CS",
            "USER_IDX"=>$data->IDX,
            "NO"=>$result['no'],
            "CODE"=>$result['template'],
            "CONT"=>$result['cont'],
            "RESULT_CODE"=>$result['code']
        );
        $sms->add_history($obj);
    } else {
        $obj = array(
            "USER_TYPE" => "CS",
            "USER_IDX"=>$data->IDX,
            "NO"=>$result['no'],
            "CODE"=>$result['template'],
            "CONT"=>"",
            "RESULT_CODE"=>$result['code']
        );
        $sms->add_history($obj);
    }

    echo json_encode(array("message" => "등록 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}
?>
