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
$data =  json_decode($_POST["callObj"]);

$type = 1;
$userAgent = strtolower($_SERVER['HTTP_USER_AGENT']);
if (strpos($userAgent, 'android') !== false) {
    $type = 2; // Android
} elseif (strpos($userAgent, 'iphone') !== false || strpos($userAgent, 'ipad') !== false || strpos($userAgent, 'ipod') !== false) {
    $type = 3; // Apple (iPhone, iPad or iPod)
} elseif (preg_match('/(up.browser|up.link|mmp|symbian|smartphone|midp|wap|vodafone|o2|pocket|kindle|mobile|pda|psp|treo)/i', $userAgent)) {
    $type = 1; // Mobile web
}

$data -> TYPE = $type;
if($ars->update_mobile($data)){
    echo json_encode(array("isSuc"=>TRUE));
    http_response_code(200);
} else {
    echo json_encode(array("isSuc"=>FALSE));
    http_response_code(200);
}





