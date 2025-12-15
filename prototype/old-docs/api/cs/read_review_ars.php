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

if (!isset($_SESSION['USER_ID'])){
    echo json_encode(array("isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
$user_id = $_SESSION['USER_ID'];

$cs_info = $cs->readOne($data->IDX);
$chatlist = $ars->getChatlogById($user_id,$cs_info['CODE']);

foreach ($chatlist as $key => $value) {
    $chatlist[$key]['NICK_NAME'] = $cs->getCsNickNameByCode($chatlist[$key]['m_code']);
}

//print_r($chatlist);

// query products
echo json_encode(array("list" => $chatlist,"callback"=>"","isSuc"=>TRUE), JSON_UNESCAPED_UNICODE);
http_response_code(200);

