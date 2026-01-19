<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/recruit.php';

// get database connection
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$recruit = new Recruit($db);

$data = json_decode($_POST["csObj"]);


// query products
echo json_encode(array("csObj" => $recruit->readOne($data -> IDX),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

