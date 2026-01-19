<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);
$user = new User($db);
$data =  json_decode($_POST["faqObj"]);

session_start();
if (!isset($_SESSION['IDX'])){
    echo json_encode(array("isSuc"=>FALSE));
    http_response_code(200);
}

if ($_SESSION['IS_CS']=='Y'){
    echo json_encode(array("isSuc"=>FALSE));
    http_response_code(200);
}

// query products
echo json_encode(array("list" => $user->read_admin_faq_info($_SESSION['IDX']),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

