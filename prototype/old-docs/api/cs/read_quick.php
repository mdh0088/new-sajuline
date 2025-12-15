<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$cs = new Counselor($db);


// query products
echo json_encode(array("list" => $cs->read_quick(),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

