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


if(!isset($_SESSION['IDX'])){
    echo json_encode(array("message" => "로그인 세션이 만료되었습니다. \n 다시 로그인을 해주세요.","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

$data->CODE = $_SESSION['CODE'];

//if($cs->update_status($data)){
    $arsObj = $ars->update_status_by_code($data);
//}

// query products
echo json_encode(array("csObj" => $arsObj,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

