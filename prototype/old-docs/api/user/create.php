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
include_once $_SERVER['DOCUMENT_ROOT'].'/api/config/ars_database.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/ars.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/errorlog.php';
include_once $_SERVER['DOCUMENT_ROOT'].'/api/objects/sms.php';
include_once $_SERVER['DOCUMENT_ROOT']."/api/lib/sms/alert_kakao.php";


// get database connection
$ars_database   = new ARS_database(); $ars_db = $ars_database->getConnection();
$ars            = new ARS($ars_db);
$database       = new Database(); $db = $database->getConnection();
$utilities      = new Utilities($db);
$user           = new User($db);
$sms            = new SMS($db);
$kakaoAlert     = new kakaoAlert();

$data = json_decode($_POST["usrObj"]);
$phone_chk = $data->PHONE_CHK;
$key = "mysajuro##";
$decrypted = base64_decode($phone_chk) ^ $key;

$phone = $data->PHONE;
$phone_number_without_hyphen = str_replace("-", "", $phone);
$data->PHONE = $phone;

if ($data->JOIN_TYPE == 'common') {

    /* 아이디 중복 확인 */
    if ($utilities -> chkTableInfoByValue('TBL_USER', 'USER_ID', $data->USER_ID)||
        $utilities -> chkTableInfoByValue('TBL_CS','EMAIL',$data->USER_ID)) {
        echo json_encode(array("message" => "아이디가 존재합니다.","callback"=>"/","isSuc"=>FALSE));
        http_response_code(200);
        exit;
    }
}
else if($data->JOIN_TYPE == 'kakao'){
    $data->USER_ID = 'kko'.$data->USER_ID;
    $data->PASSWORD = 'kakao!@#%%';
}
else if($data->JOIN_TYPE == 'naver'){
    $data->PASSWORD = 'naver&*(%%';
}

if ($utilities -> chkTableInfoByValue('TBL_USER_EX','PHONE',$data->PHONE)){
    $ex_info = $user->get_ex_info($data->PHONE);
    if ($ex_info['ex_day'] < 150){
        echo json_encode(array("message" => "탈퇴후 150일 동안은 재가입이 불가능합니다.","callback"=>"/","isSuc"=>FALSE));
        http_response_code(200);
        exit;
    }
}


/* 닉네임 중복 확인 */
if ($utilities -> chkTableInfoByValue('TBL_USER','NICK_NAME',$data->NICK_NAME) ||
    $utilities -> chkTableInfoByValue('TBL_CS','NICK_NAME',$data->NICK_NAME)){
    echo json_encode(array("message" => "닉네임이 존재합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

/* 이메일 중복 확인 */
ELSE if ($utilities -> chkTableInfoByValue('TBL_USER','EMAIL',$data->EMAIL) ||
         $utilities -> chkTableInfoByValue('TBL_CS','EMAIL',$data->EMAIL)){
    echo json_encode(array("message" => "이메일이 존재합니다","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}
/* 핸드폰 중복 확인 */
ELSE if ($utilities -> chkTableInfoByValue('TBL_USER','PHONE',$data->PHONE)||
        $utilities -> chkTableInfoByValue('TBL_CS','PHONE',$data->EMAIL)){
    echo json_encode(array("message" => "핸드폰 번호가 존재합니다.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}

/* 핸드폰 본인 인증 확인 */
ELSE if ($decrypted != 'pchked'){
    echo json_encode(array("message" => $decrypted."핸드폰 본인 인증을 해주세요.","callback"=>"/","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


/* 가입 로직 시작 */
ELSE {

    if ($user->insertUser($data)){
        session_start();
        if(!isset($_SESSION['IDX'])) {
            $user_data = array("USER_ID" => $data->USER_ID, "EMAIL" => $data->EMAIL);
            $user_info= $utilities->readOne('TBL_USER',$user_data);
            foreach ($user_info as $key => $value) {
                $_SESSION[$key] = $value;
            }
            $_SESSION['IS_CS'] = 'N';
        }

        $nick_name = mb_convert_encoding($data->NICK_NAME, 'CP949', 'UTF-8');


        $ars_data = array(
            "u_id"        => $data->USER_ID
            ,"u_tel"      => $data->PHONE
            ,"u_kname"    => $nick_name
        );

        if($ars -> create_user($ars_data)) {

            if (!$utilities -> chkTableInfoByValue('TBL_USER_EX','PHONE',$data->PHONE)){
                $chk_data = array("IDX" => $_SESSION['IDX']);
                $user_info= $utilities->readOne('TBL_USER',$chk_data);

                $user->add_event_log('1',$user_info['IDX'],'신규회원 포인트 지급','10000');
                $ars ->new_user_point($data->PHONE,'10000');
            }

            $chk_data = array("USER_ID" => $data->USER_ID);
            $user_info= $utilities->readOne('TBL_USER',$chk_data);

            $result = $kakaoAlert->user_join_alert($user_info['PHONE'],$user_info['NICK_NAME']);
            if ($result['isSuc']){
                $obj = array(
                    "USER_TYPE" => "USER",
                    "USER_IDX"=>$user_info['IDX'],
                    "NO"=>$result['no'],
                    "CODE"=>$result['template'],
                    "CONT"=>$result['cont'],
                    "RESULT_CODE"=>$result['code']
                );
                $sms->add_history($obj);
            } else {
                $obj = array(
                    "USER_TYPE" => "USER",
                    "USER_IDX"=>$user_info['IDX'],
                    "NO"=>$result['no'],
                    "CODE"=>$result['template'],
                    "CONT"=>"",
                    "RESULT_CODE"=>$result['code']
                );
                $sms->add_history($obj);
            }



            $callback = "/app/user/join_complete";
            echo json_encode(array("message" => "환영합니다.","callback"=>"".$callback."","isSuc"=>TRUE));
            http_response_code(200);
            exit;
        }


    }
}
?>
