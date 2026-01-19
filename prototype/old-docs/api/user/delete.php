<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

session_start();

// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$user           = new User($db);

$data = json_decode($_POST["userObj"]);

if (!isset($_SESSION['IDX'])) {
    echo json_encode(array("message" => "유저 세션이 끊어졌습니다.",  "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

$data -> IDX = $_SESSION['IDX'];
$chk_data = array("IDX" => $_SESSION['IDX']);
$user_info= $utilities->readOne('TBL_USER',$chk_data);

/*if ($user_info['JOIN_TYPE']!='common'){
    http_response_code(200);
    echo json_encode(array("message" => "SNS가입자 탈퇴는 관리자에게 문의를 부탁드립니다.","isSuc"=>FALSE));
    exit;
}*/

if (!password_verify($data->PASSWORD, $user_info['PASSWORD']) && $user_info['JOIN_TYPE']=='common') {
    echo json_encode(array("message" => "비밀번호가 틀립니다.\n비밀번호는 대소문자를 구분합니다.","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


if ($user->delete_user($data)){
    $user->add_delete_log($user_info);
    $ars->delete_user($user_info['PHONE']);
}


session_destroy();
echo json_encode(array("message" => "처리 되었습니다.","isSuc"=>TRUE));
http_response_code(200);
exit;
?>
