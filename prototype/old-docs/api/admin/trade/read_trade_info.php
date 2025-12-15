<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/admin.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$database = new Database();
$db = $database->getConnection();

// instantiate product object
$admin = new Admin($db);


$data = json_decode($_POST["tradeObj"]);

// query products
$search_type = $data -> TYPE;
if ($search_type == 'day'){
    echo json_encode(array("list" => $admin->read_trade_info_day($data->MONTH_VALUE),"callback"=>"","isSuc"=>TRUE));
} else if ($search_type == 'month'){
    echo json_encode(array("list" => $admin->read_trade_info_month($data->YEAR_VALUE),"callback"=>"","isSuc"=>TRUE));
} else if ($search_type == 'year'){
    echo json_encode(array("list" => $admin->read_trade_info_year(),"callback"=>"","isSuc"=>TRUE));
}

http_response_code(200);

