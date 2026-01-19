<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$cs             = new Counselor($db);

$data = json_decode($_POST["csObj"]);

$required_fields = ['PASSWORD'];
$errors = [];

foreach ($required_fields as $field) {
    if (empty($data->$field)) {
        $errors[] = "$field 를 입력해주세요.";
    }
}

if (!empty($errors)) {
    echo json_encode(['message' => implode("\n", $errors), 'callback' => '/', 'isSuc' => false]);
    http_response_code(200);
    exit;
}

if ($cs->update_pw($data)){
    echo json_encode(array("message" => "비밀번호가 수정 되었습니다.", "callback" => "", "isSuc" => TRUE));
    http_response_code(200);
    exit;
}

?>
