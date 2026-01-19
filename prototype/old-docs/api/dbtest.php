<?php
error_reporting(E_ALL);
ini_set("display_errors", 1);
ini_set('log_errors', 1);


include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';


$ars_database = new ARS_database();
$ars_Db = $ars_database->getConnection();

$ars = new ARS($ars_Db);


/*$ars_data = array(

"u_id"         => 'mdh55'
,"u_point"       => 50000
);

if($ars -> charge_point($ars_data)) {
    echo json_encode(array("message" => "상담사 정보가 수정 되었습니다.", "callback" => "", "isSuc" => TRUE));
    http_response_code(200);
    exit;
}*/



