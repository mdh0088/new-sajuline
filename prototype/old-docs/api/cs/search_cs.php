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

$data = json_decode($_POST["searchObj"]);

if (!empty($data->SEARCH_NAME)){
    session_start();

    $USER_CHK='COMMON';
    $USER_IDX='';
    $KEYWORD = $data -> SEARCH_NAME;
    if (isset($_SESSION['IDX']) && $_SESSION['IS_CS'] =='N' ){
        $USER_CHK='USER';
        $USER_IDX = $_SESSION['IDX'];
    } ELSE IF (isset($_SESSION['IDX']) && $_SESSION['IS_CS'] =='Y') {
        $USER_CHK='CS';
        $USER_IDX = $_SESSION['IDX'];
    }


    $cs->insert_search_log($USER_CHK,$USER_IDX,$KEYWORD);

}

// query products
echo json_encode(array("list" => $cs->read_search($data),"callback"=>"","isSuc"=>TRUE));
http_response_code(200);

