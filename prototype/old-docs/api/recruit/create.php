<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");


// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/recruit.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$database = new Database();
$db = $database->getConnection();

// utilities
$utilities = new Utilities($db);

// instantiate product object
$user = new User($db);
$recruit = new Recruit($db);

$data = json_decode($_POST["usrObj"]);
$keywords = implode(',', $data->KEYWORD);
$data -> keywords = $keywords;

$valid_extensions = ['png', 'jpg', 'jpeg','PNG','JPG','JPEG'];
$uploaded_files = [];


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

    $img_keys = ['IMG1', 'IMG2', 'IMG3', 'IMG4', 'IMG5'];
    $img_count = 0;
    foreach ($img_keys as $key) {
        $data->{$key} = '';
    }
    foreach ($uploaded_files as $file) {
        move_uploaded_file($files[$img_count]['tmp_name'], $_SERVER['DOCUMENT_ROOT'].'/app/assets/upload/recruit/' . $file);
        $data->{$img_keys[$img_count]} = $file;
        if (++$img_count >= 5) break;
    }


} else {
    http_response_code(200);
    echo json_encode(array("message" => "파일을 업로드 해주세요.","isSuc"=>FALSE));
    exit;
}


$required_fields = ['NICK_NAME', 'NAME', 'PHONE', 'EMAIL','KEYWORD',];
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

if ($utilities -> chkTableInfoByValue('TBL_CS','NICK_NAME',$data->NICK_NAME)){
    echo json_encode(array("message" => "닉네임이 존재합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
ELSE if ($utilities -> chkTableInfoByValue('TBL_USER','EMAIL',$data->EMAIL) || $utilities -> chkTableInfoByValue('TBL_CS','EMAIL',$data->EMAIL)){
    echo json_encode(array("message" => "이메일이 존재합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
ELSE if ($utilities -> chkTableInfoByValue('TBL_CS','PHONE',$data->PHONE)){
    echo json_encode(array("message" => "핸드폰 번호가 존재합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}



if ($recruit->create($data)){

    $callback = "/app/recruit/apply";
    echo json_encode(array("message" => "등록 되었습니다.","callback"=>"".$callback."","isSuc"=>TRUE));
    http_response_code(200);
    exit;
}
?>
