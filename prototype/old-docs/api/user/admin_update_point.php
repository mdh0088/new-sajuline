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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';

// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$user = new User($db);
// query products

$data = json_decode($_POST["userObj"]);
$user_info = $user->admin_user_info($data->IDX);

$chk_data = array("u_id" => $user_info['USER_ID'], "u_point" => $data->POINT);
if ($ars->admin_update_user_point($chk_data)){
    echo json_encode(array("message" => "저장 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
} else {
    echo json_encode(array("message" => "오류가 발생했습니다.\n 관리자에게 문의주세요.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
}
?>
