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

$data = json_decode($_POST["reviewObj"]);

$per_page = 5;
$page = $data -> PAGE;
$data->page = $page * $per_page;

$review_cnt = $cs->read_cs_review_cnt($data->IDX);
$faq_cnt    = $cs->read_cs_faq_cnt($data->IDX);

// query products
echo json_encode(array("list" => $cs->read_review($data),"review_cnt"=>$review_cnt,"faq_cnt"=>$faq_cnt,"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

