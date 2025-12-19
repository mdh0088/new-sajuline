<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

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

$ars_info = $ars->getUserInfoById($user_info['USER_ID']);
$user_info['POINT'] = $ars_info['u_point'];


echo json_encode(array("userObj" => $user_info,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

