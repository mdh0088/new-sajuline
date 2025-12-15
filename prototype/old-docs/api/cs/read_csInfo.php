<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);

$data =  json_decode($_POST["csObj"]);

session_start();
$code = $_SESSION['CODE'];

$csObj = $ars->getChatTimeByCode($code);
$csInfo = $cs->getCsInfoByCode($code);
$csObj['STATUS'] = $csInfo['STATUS'];
$csObj['WORK_TIME'] = $csInfo['WORK_TIME'];
$csObj['NOTICE'] = $csInfo['NOTICE'];

// query products
echo json_encode(array("csObj" => $csObj,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

