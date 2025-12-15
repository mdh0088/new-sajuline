<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$user = new User($db);

$data =  json_decode($_POST["userObj"]);

$userObj = $user->find_user_by_idx($data);
$chk_data = array("USER_ID" => $userObj['USER_ID'],"PHONE" => $userObj['PHONE']);
$ars_userObj = $ars->getUserInfo($chk_data);
$userObj['POINT'] = $ars_userObj['u_point'];

// query products
echo json_encode(array("userObj" => $userObj,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

