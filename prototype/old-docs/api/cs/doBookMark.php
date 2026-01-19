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


$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);

$data = json_decode($_POST["csObj"]);

session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인후 이용 부탁드립니다.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
} else {
    $data -> USER_IDX = $_SESSION['IDX'];
}

if ($_SESSION['IS_CS'] == 'Y'){
    echo json_encode(array("message" => "상담사 계정으로는 불가능합니다. ","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
$user_data = array("USER_IDX" => $_SESSION['IDX'],"CS_IDX"=>$data -> IDX);
if($utilities->chkTableInfoByObj('TBL_USER_BOOKMARK',$user_data)){
    $cs -> deleteBookMark($_SESSION['IDX'],$data -> IDX);
    echo json_encode(array("message" => "즐겨찾기가 취소 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
} else {
    $cs -> doBookMark($_SESSION['IDX'],$data -> IDX);
    echo json_encode(array("message" => "즐겨찾기가 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}



?>
