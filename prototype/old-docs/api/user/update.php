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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

session_start();

// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$user             = new User($db);

$data = json_decode($_POST["userObj"]);
$data -> IDX = $_SESSION['IDX'];

$chk_data = array("IDX" => $_SESSION['IDX']);
$user_info= $utilities->readOne('TBL_USER',$chk_data);

/*if ($user_info['NICK_NAME'] != $data->NICK_NAME) {
    if ($utilities->chkTableInfoByValue('TBL_CS', 'NICK_NAME', $data->NICK_NAME)) {
        echo json_encode(array("message" => "닉네임이 존재합니다.", "callback" => "/", "isSuc" => FALSE));
        http_response_code(200);
        exit;
    }
}

if ($user_info['NICK_NAME'] != $data->NICK_NAME) {
    if ($utilities->chkTableInfoByValue('TBL_USER', 'NICK_NAME', $data->NICK_NAME)) {
        echo json_encode(array("message" => "닉네임이 존재합니다.", "callback" => "/", "isSuc" => FALSE));
        http_response_code(200);
        exit;
    }
}*/

if ($user->update($data)){
    $user_info= $utilities->readOne('TBL_USER',$chk_data);
    //$nick_name = mb_convert_encoding($user_info['NICK_NAME'], 'CP949', 'UTF-8');
    //$ars_data = array("u_kname"   => $nick_name, "u_id" => $user_info['USER_ID']);
    //if($ars -> update_user($ars_data)) {

        foreach ($user_info as $key => $value) {
            if ($key == "IDX" || $key == "USER_ID" || $key == "NAME" || $key == "NICK_NAME" || $key == "EMAIL" || $key == "PHONE") {
                $_SESSION[$key] = $value;
            }
        }
        $_SESSION['IS_CS'] = 'N';

        echo json_encode(array("message" => "유저 정보가 수정 되었습니다.", "callback" => "", "isSuc" => TRUE));
        http_response_code(200);
        exit;
    //}
}

?>
