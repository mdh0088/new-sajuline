<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';


$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$cs = new Counselor($db);

$data = json_decode($_POST["csObj"]);

session_start();
if (isset($_SESSION['IDX'])){
    $user_data = array("USER_IDX" => $_SESSION['IDX'],"CS_IDX"=>$data -> IDX);
    if($utilities->chkTableInfoByObj('TBL_USER_BOOKMARK',$user_data)){
        echo json_encode(array("message" => "","callback"=>"","isSuc"=>TRUE));
        http_response_code(200);
        exit;
    } else {
        echo json_encode(array("message" => "","callback"=>"","isSuc"=>FALSE));
        http_response_code(200);
        exit;
    }
} else {
    echo json_encode(array("message" => "","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


?>
