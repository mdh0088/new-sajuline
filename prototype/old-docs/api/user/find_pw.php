<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// files needed to connect to database
include_once $_SERVER['DOCUMENT_ROOT'] . '/api/config/database.php';
include_once $_SERVER['DOCUMENT_ROOT'] . '/api/objects/user.php';
include_once $_SERVER['DOCUMENT_ROOT'] . '/api/shared/utilities.php';
include_once $_SERVER['DOCUMENT_ROOT'] . '/api/shared/errorlog.php';


$database = new Database();
$db = $database->getConnection();
$utilities = new Utilities($db);

// instantiate product object
$user = new User($db);

$data = json_decode($_POST["userObj"]);

if (!$utilities->chkTableInfoByValue('TBL_USER', 'USER_ID', $data->USER_ID)) {
    echo json_encode(array("message" => "유저 정보가 존재하지 않습니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

if (!$utilities->chkTableInfoByValue('TBL_USER', 'PHONE', $data->PHONE)) {
    echo json_encode(array("message" => "유저 정보가 존재하지 않습니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

$chk_data = array("USER_ID" => $data->USER_ID,"PHONE" => $data->PHONE);
if(!$utilities -> chkTableInfoByObj('TBL_USER',$chk_data)){
    echo json_encode(array("message" => "유저 정보가 존재하지 않습니다.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}


$userObj = $user->find_user_by_phone_and_id($data);

if ($userObj['JOIN_TYPE']=='kakao'){
    echo json_encode(array("message" => "카카오로 가입된 사용자입니다.\n 카카오로 로그인 부탁드립니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

if ($userObj['JOIN_TYPE']=='naver'){
    echo json_encode(array("message" => "네이버로 가입된 사용자입니다.\n 네이버로 로그인 부탁드립니다.", "callback" => "/", "isSuc" => FALSE));
    http_response_code(200);
    exit;
}

$idx     = $userObj['IDX'];
$email   = $userObj['EMAIL'];
$user_id = $userObj['USER_ID'];
$current_time = date('Y-m-d H:i:s');
$new_pw  = $utilities->generatePassword();
$body =
    '
     <div class="mail_view_contents">
        <div class="mail_view_contents_inner" data-translate-body-17536="">
            <div>
                <div style="margin:30px auto;width:600px;border:10px solid #f7f7f7">
                    <div style="border:1px solid #dedede">
                        <h1 style="padding:30px 30px 0;background:#f7f7f7;color:#555;font-size:1.4em">회원정보 찾기 안내</h1>
                        <span style="display:block;padding:10px 30px 30px;background:#f7f7f7;text-align:right">
                            <a href="https://sajutarot.com" target="_blank" rel="noreferrer noopener">사주로</a>
                        </span>
                        <p style="margin:20px 0 0;padding:30px 30px 30px;border-bottom:1px solid #eee;line-height:1.7em">
                            회원님은 '.$current_time.' 에 회원정보 찾기 요청을 하셨습니다.<br>
                            저희 사이트는 관리자라도 회원님의 비밀번호를 알 수 없기 때문에, 비밀번호를 알려드리는 대신 새로운 비밀번호를 생성하여 안내 해드리고 있습니다.<br>
                            아래에서 변경될 비밀번호를 확인하신 후, <span style="color:#ff3061"><strong>변경된 비밀번호</strong>로 로그인 부탁드립니다.</span><br>
                            로그인 후에는 정보수정 메뉴에서 새로운 비밀번호로 변경해 주십시오.
                        </p>
                        <p style="margin:0;padding:30px 30px 30px;border-bottom:1px solid #eee;line-height:1.7em">
                            <span style="display:inline-block;width:100px">회원아이디</span> '.$user_id.'<br>
                            <span style="display:inline-block;width:100px">변경된 비밀번호</span> <strong style="color:#ff3061">'.$new_pw.'</strong>
                        </p>
                    </div>
                </div>
            </div>
        </div>
     </div>   
    ';

$title = '[사주로] 요청하신 회원정보 찾기 안내 메일입니다';

if($utilities->sendMail($email, $body, $title)){
    // query products

    $obj = new stdClass();
    $obj->IDX = $idx;
    $obj->PASSWORD = $new_pw;
    $user->update_pw($obj);

    echo json_encode(array("userObj" => $userObj, "callback" => "", "isSuc" => TRUE));
    http_response_code(200);
    exit;
} else {
    // query products
    echo json_encode(array("message" => "메일 전송에 실패했습니다. \n관리자에게 문의주세요.","callback"=>"","isSuc"=>FALSE));
    http_response_code(200);
    exit;
}



?>
