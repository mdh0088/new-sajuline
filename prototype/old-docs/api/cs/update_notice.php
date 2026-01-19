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
$data ->IDX = $_SESSION['IDX'];

if ($cs->update_notice($data)){
    echo json_encode(array("message" => "저장 되었습니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
}
?>
