<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$user = new User($db);

$data =  json_decode($_POST["userObj"]);



if (!$utilities->chkTableInfoByValue('TBL_USER', 'PHONE', $data->PHONE)) {
    echo json_encode(array("message" => "유저 정보가 존재하지 않습니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}



$userObj = $user->find_user_by_phone($data);
if ($userObj['JOIN_TYPE']=='kakao'){
    echo json_encode(array("message" => "카카오로 가입된 사용자입니다.\n 카카오로 로그인 부탁드립니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

if ($userObj['JOIN_TYPE']=='naver'){
    echo json_encode(array("message" => "네이버로 가입된 사용자입니다.\n 네이버로 로그인 부탁드립니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

// query products
echo json_encode(array("userObj" => $userObj,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

