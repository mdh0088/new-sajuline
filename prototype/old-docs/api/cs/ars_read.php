<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");



// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/recruit.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$ars_database = new ARS_database();
$ars_db = $ars_database->getConnection();

//ars 객체 선언
$ars = new ARS($ars_db);


//$ars -> create_cs();
print_r($ars->read());
echo json_encode(array("list" => $ars->read(),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);
exit;
?>
