<?php
require_once($_SERVER['DOCUMENT_ROOT']."/config/db/init.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/dao/user.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/util/common.php");


error_reporting( E_ALL );
ini_set( "display_errors", 1 );

/*
$User = new User;
$obj = json_decode($_POST['usrObj']);
$result = $User -> getUserInfoById($obj->ID);
echo json_encode($result);
*/

/*
$User = new User;
$obj = json_decode($_POST['usrObj']);
$result = $User -> getListtest($obj->ID);
echo $result;
*/

$User = new User;
$usrObj = json_decode($_POST['usrObj']);

$return_obj = new stdClass();
$return_obj -> isSuc        =   "";
$return_obj -> msg          =   "";

if ($usrObj->JOIN_TYPE == 'common') {
    /* 아이디 중복 확인 */
    if (chkTableInfoByValue('TBL_USER', 'USER_ID', $usrObj->USER_ID)) {
        $return_obj->isSuc = FALSE;
        $return_obj->msg = "아이디가 존재합니다.";
        echo json_encode($return_obj);
        return;
    }
}
else if($usrObj->JOIN_TYPE == 'kakao'){
    $usrObj->USER_ID = 'kko'.$usrObj->USER_ID;
    $usrObj->PASSWORD = 'kakao!@#%%';
}
else if($usrObj->JOIN_TYPE == 'naver'){
    $usrObj->PASSWORD = 'naver&*(%%';
}

/* 닉네임 중복 확인 */
if (chkTableInfoByValue('TBL_USER','NICK_NAME',$usrObj->NICK_NAME)){
    $return_obj -> isSuc        =   FALSE;
    $return_obj -> msg          =   "닉네임이 존재합니다.";
    echo json_encode($return_obj);
    return;
}


/* 이메일 중복 확인 */
ELSE if (chkTableInfoByValue('TBL_USER','EMAIL',$usrObj->EMAIL)){
    $return_obj -> isSuc        =   FALSE;
    $return_obj -> msg          =   "이메일이 존재합니다.";
    echo json_encode($return_obj);
    return;
}
/* 핸드폰 중복 확인 */
ELSE if (chkTableInfoByValue('TBL_USER','PHONE',$usrObj->PHONE)){
    $return_obj -> isSuc        =   FALSE;
    $return_obj -> msg          =   "핸드폰 번호가 존재합니다.";
    echo json_encode($return_obj);
    return;
}
/* 가입 로직 시작 */
ELSE {
    if ($User->insertUser($usrObj)){
        $return_obj -> isSuc        =   TRUE;
        $return_obj -> msg          =   "환엽합니다.";
        $return_obj -> callback     =   "/app/user/join_complete";
        echo json_encode($return_obj);
        return;
    }
}



?>
