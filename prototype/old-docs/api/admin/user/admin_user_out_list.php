<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/admin.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$admin = new Admin($db);
// instantiate product object

// instantiate product object
// query products
echo json_encode(array("list" => $admin->admin_user_out_list(),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

