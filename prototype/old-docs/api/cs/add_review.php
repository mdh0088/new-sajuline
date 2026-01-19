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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$data =  json_decode($_POST["reviewObj"]);

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

$data -> USER_IDX = $_SESSION['IDX'];

if ($cs->addReview($data)){
    $ars -> update_chatlog_for_review($data->CHAT_IDX);
    echo json_encode(array("isSuc"=>TRUE), JSON_UNESCAPED_UNICODE);
    http_response_code(200);
} else{
    echo json_encode(array("isSuc"=>FALSE), JSON_UNESCAPED_UNICODE);
    http_response_code(200);

}
/*$chatlist = $cs->addReview($data);
foreach ($chatlist as $key => $value) {
    $chatlist[$key]['NICK_NAME'] = $cs->getCsNickNameByCode($chatlist[$key]['m_code']);
}*/

//print_r($chatlist);

// query products

