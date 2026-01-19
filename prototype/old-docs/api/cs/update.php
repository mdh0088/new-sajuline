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

$chk_data = array("IDX" => $data->IDX,"APPROVAL_YN" => 'Y');
$user_info= $utilities->readOne('TBL_CS',$chk_data);

$keywords = implode(',', $data->KEYWORD);
$data -> keywords = $keywords;

$valid_extensions = ['png', 'jpg', 'jpeg','PNG','JPG','JPEG'];
$uploaded_files = [];

$data -> IMG = $data->IMG_VALUE;
if ($user_info['IMG'] != $data->IMG_VALUE){
    if (isset($_FILES['file'])) {
        $files = $utilities->reArrayFiles($_FILES['file']);
        foreach ($files as $file) {
            if ($file['error'] == 0 && $file['size'] > 0) {
                $extension = pathinfo($file['name'], PATHINFO_EXTENSION);
                if (!in_array($extension, $valid_extensions)) {
                    http_response_code(200);
                    echo json_encode(array("message" => "업로드가 불가능한 형식의 파일이 있습니다. (png, jpg, jpeg 만 가능)","isSuc"=>FALSE));
                    exit;
                }

                $new_file_name = date("Ymd") . '_' . uniqid() . '.' . $extension;
                $uploaded_files[] = $new_file_name;
            }
        }

        $img_keys = ['IMG'];
        $img_count = 0;
        foreach ($img_keys as $key) {
            $data->{$key} = '';
        }
        foreach ($uploaded_files as $file) {
            move_uploaded_file($files[$img_count]['tmp_name'], $_SERVER['DOCUMENT_ROOT'] . '/app/assets/upload/cs/' . $file);
            $data->{$img_keys[$img_count]} = $file;
            if (++$img_count >= 5) break;
        }

    } else {
        http_response_code(200);
        echo json_encode(array("message" => "파일을 업로드 해주세요.","isSuc"=>FALSE));
        exit;
    }
}


$required_fields = ['NICK_NAME', 'NAME'];
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

if ($user_info['NICK_NAME'] != $data->NICK_NAME) {
    if ($utilities->chkTableInfoByValue('TBL_CS', 'NICK_NAME', $data->NICK_NAME)) {
        echo json_encode(array("message" => "닉네임이 존재합니다.", "callback" => "/", "isSuc" => FALSE));
        http_response_code(200);
        exit;
    }
}
/*
if ($user_info['EMAIL'] != $data->EMAIL) {
    if ($utilities->chkTableInfoByValue('TBL_USER', 'EMAIL', $data->EMAIL) || $utilities->chkTableInfoByValue('TBL_CS', 'EMAIL', $data->EMAIL)) {
        echo json_encode(array("message" => "이메일이 존재합니다.", "callback" => "/", "isSuc" => FALSE));
        http_response_code(200);
        exit;
    }
}
*/
/*if ($user_info['PHONE'] != $data->PHONE) {
    if ($utilities->chkTableInfoByValue('TBL_CS', 'PHONE', $data->PHONE)) {
        echo json_encode(array("message" => "핸드폰 번호가 존재합니다.", "callback" => "/", "isSuc" => FALSE));
        http_response_code(200);
        exit;
    }
}*/

if ($user_info['CODE'] != $data->CODE) {
    if ($utilities->chkTableInfoByValue('TBL_CS', 'CODE', $data->CODE)) {
        echo json_encode(array("message" => "이미 등록된 코드입니다.", "callback" => "", "isSuc" => TRUE));
        http_response_code(200);
        exit;
    }
}

if (empty($user_info['PASSWORD'])){
    echo json_encode(array("message" => "비밀번호를 먼저 등록해주세요.", "callback" => "", "isSuc" => TRUE));
    http_response_code(200);
    exit;
}

if ($cs->update($data)){


    $user_info= $utilities->readOne('TBL_CS',$chk_data);
    $name = mb_convert_encoding($user_info['NAME'], 'CP949', 'UTF-8');
    $nick_name = mb_convert_encoding($user_info['NICK_NAME'], 'CP949', 'UTF-8');

    $m_bunho = '1';
    if ($user_info['GRADE']=='GOLD'){
        $m_bunho ='2';
    }

    $ars_data = array(
        "m_name"        => $name
        ,"m_nickname"   => $nick_name
        ,"m_tel"        => $user_info['PHONE']
        ,"m_id"         => $user_info['EMAIL']
        ,"m_code"       => $user_info['CODE']
        ,"m_prate"      => $user_info['AFTER_AMOUNT']
        ,"m_state"      => $user_info['STATUS']
        ,"m_bunho"      => $m_bunho
    );

    if($ars -> update_cs($ars_data)) {
        $ars -> create_cs_log($ars_data);
        echo json_encode(array("message" => "상담사 정보가 수정 되었습니다.", "callback" => "", "isSuc" => TRUE));
        http_response_code(200);
        exit;
    }


}

/*
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
*/
?>
