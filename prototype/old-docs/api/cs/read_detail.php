<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';

// get database connection
$database = new Database();
$db = $database->getConnection();
$utilities      = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);


$data = json_decode($_POST["csObj"]);


if (!$utilities->chkTableInfoByValue('TBL_CS', 'IDX', $data->IDX)) {
    echo json_encode(array("message" => "상담사가 존재하지 않습니다.", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

// query products
echo json_encode(array("list" => $cs->read_detail($data),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

