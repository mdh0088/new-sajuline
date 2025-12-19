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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/cs.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';

// get database connection
$database   = new Database(); $db = $database->getConnection();
$utilities  = new Utilities($db);
$user       = new User($db);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405); // Method Not Allowed
    echo json_encode(array("message" => "허용된 통신 방식이 아닙니다."));
    return;
}

//파라미터
$data = json_decode($_POST["usrObj"]);

//데이터 세팅
$user->USER_ID = $data->USER_ID;
$user->PASSWORD = $data->PASSWORD;

if (empty($user->USER_ID) || empty($user->PASSWORD)) {
    http_response_code(400); // Bad Request
    echo json_encode(array("message" => "아이디와 비밀번호는 필수 입력 항목입니다."));
    return;
}


//유저 검증 데이터 세팅
$user_data = array("USER_ID" => $data->USER_ID);

//상담사 검증 데이터 세팅, APPROVAL_YN 값을 넣어주어 승인된 상담사만 로그인 허용
$cs_data = array("NICK_NAME" => $data->USER_ID,"APPROVAL_YN" => "Y","OUT_YN" => "N");

//유저 로그인 start
//유저는 email 형식으로 로그인이 불가능 하기 때문에 분기가 가능
if($utilities -> chkTableInfoByObj('TBL_USER',$user_data)){

    $user_info= $utilities->readOne('TBL_USER',$user_data);
    if (password_verify($user->PASSWORD, $user_info['PASSWORD'])) {
        session_start();
        if(!isset($_SESSION['IDX'])) {
            foreach ($user_info as $key => $value) {
                if ($key == "IDX" || $key == "USER_ID" || $key == "NAME" || $key == "NICK_NAME" || $key == "EMAIL" || $key == "PHONE" || $key == "USER_STATUS" || $key=="JOIN_TYPE") {
                    $_SESSION[$key] = $value;
                }
            }
            $_SESSION['IS_CS'] = 'N';
        }
        echo json_encode(array("message" => "환영합니다.","callback"=>"/","isSuc"=>TRUE));
        http_response_code(200);

        $utilities -> update_last_login($_SESSION['IDX'],'TBL_USER');
        $utilities -> addLoginLog($_SESSION['IDX'],'common');


    } else {
        // set response code
        http_response_code(200);
        echo json_encode(array("message" => "가입된 회원아이디가 아니거나 비밀번호가 틀립니다.\n비밀번호는 대소문자를 구분합니다.","isSuc"=>FALSE));
    }
//상담사 로그인 start
} else if ($utilities -> chkTableInfoByObj('TBL_CS',$cs_data)){

    $cs_info= $utilities->readOne('TBL_CS',$cs_data);
    if (password_verify($user->PASSWORD, $cs_info['PASSWORD'])) {
        session_start();
        if(!isset($_SESSION['IDX'])) {
            foreach ($cs_info as $key => $value) {
                if ($key == "IDX" || $key == "NAME" || $key == "NICK_NAME" || $key == "EMAIL" || $key == "PHONE" || $key == "USER_STATUS" || $key == "CODE" || $key == "GRADE") {
                    $_SESSION[$key] = $value;
                }
            }
            $_SESSION['IS_CS'] = 'Y';
        }
        echo json_encode(array("message" => "환영합니다.","callback"=>"/","isSuc"=>TRUE));
        http_response_code(200);

        $utilities -> update_last_login($_SESSION['IDX'],'TBL_CS');
        //$utilities -> addLoginLog($_SESSION['IDX'],'common');

    } else {
        // set response code
        http_response_code(200);
        echo json_encode(array("message" => "가입된 회원아이디가 아니거나 비밀번호가 틀립니다.\n비밀번호는 대소문자를 구분합니다.","isSuc"=>FALSE));
    }
} else{
    // set response code
    http_response_code(200);
    echo json_encode(array("message" => "가입된 회원아이디가 아니거나 비밀번호가 틀립니다.\n비밀번호는 대소문자를 구분합니다.","isSuc"=>FALSE));
}
?>
