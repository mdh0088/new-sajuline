<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/admin.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


// get database connection
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$admin          = new Admin($db);

$data = json_decode($_POST["reviewObj"]);
$admin-> update_review_hide($data);

echo json_encode(array("message" => "처리 되었습니다.","isSuc"=>TRUE));
http_response_code(200);
exit;
?>
