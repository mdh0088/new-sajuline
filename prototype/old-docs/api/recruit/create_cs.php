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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/recruit.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$ars_database = new ARS_database();
$ars_db = $ars_database->getConnection();

//ars 객체 선언
$ars = new ARS($ars_db);

$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$recruit = new Recruit($db);

$data = json_decode($_POST["csObj"]);

$chk_data = array("IDX" => $data->IDX,"APPROVAL_YN" => 'Y');

if($utilities -> chkTableInfoByObj('TBL_CS',$chk_data)){
    echo json_encode(array("message" => "이미 등록된 상담사입니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}

if ($utilities -> chkTableInfoByValue('TBL_CS', 'CODE', $data->CODE)){
    echo json_encode(array("message" => "이미 등록된 코드입니다.","callback"=>"","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}


if ($recruit->update_approval($data)){
    $user_info= $utilities->readOne('TBL_CS',$chk_data);
    $name = mb_convert_encoding($user_info['NAME'], 'CP949', 'UTF-8');
    $nick_name = mb_convert_encoding($user_info['NICK_NAME'], 'CP949', 'UTF-8');

    $ars_data = array(  "idx"       => $user_info['IDX'],  "m_name" => $name              ,"m_nickname" => $nick_name,
                        "m_tel"     => $user_info['PHONE'],"m_tel1" => $user_info['PHONE'],"m_tel2"     => $user_info['PHONE'],
                        "m_mobile"  => $user_info['PHONE'],"m_id"   => $user_info['EMAIL'],"m_code"     => $user_info['CODE'] ,
                        "m_prate" => '1000');

    if($ars -> create_cs($ars_data)) {
        echo json_encode(array("message" => "상담사로 등록 되었습니다.", "callback" => "", "isSuc" => TRUE));
        http_response_code(200);
        exit;
    }

}
?>
