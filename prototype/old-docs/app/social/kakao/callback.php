<?php
require_once($_SERVER['DOCUMENT_ROOT']."/config/db/init.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/util/common.php");

include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/kakao/lib.php";


error_reporting( E_ALL );
ini_set( "display_errors", 1 );

$kakaologin = new kakaoRestAPI();
if( $kakaologin->auth_apply !== true){ die("카카오로그인을 사용할 수 없습니다."); }

// 로그아웃일경우
if( !empty($_GET['logout'])){

    // 사용자 정보 호출
    $userLogout =  @json_decode($kakaologin->getLogout($_SESSION['kakao_token_info']['access_token']),true);


    // 에러
    if( !empty($userLogout['msg']) ){
        echo '<h1>사용자 로그아웃 요청실패</h1><pre>'; print_r($userLogout); echo '</pre>';
        exit;
    }

    if(!empty($_SESSION['auth_kakao_token_info'])) unset($_SESSION['auth_kakao_token_info'],$_SESSION['kakao_token_info']);
    if(!empty($_SESSION['auth_kakao_user_info'])) unset($_SESSION['auth_kakao_user_info'],$_SESSION['kakao_user_info']);


    die(header("Location:".$kakaologin->result_uri));
}


if(!empty($_SESSION['auth_kakao_token_info'])) unset($_SESSION['auth_kakao_token_info'],$_SESSION['kakao_token_info']);
if(!empty($_SESSION['auth_kakao_user_info'])) unset($_SESSION['auth_kakao_user_info'],$_SESSION['kakao_user_info']);


// 받은 코드로 처리
$code = empty($_GET['code']) ? '': $_GET['code'];
$token = @json_decode($kakaologin->getToken($code),true);

// 에러
if( !empty($token['error']) ){
    echo '<h1>인증토큰 요청 실패</h1><pre>'; print_r($token); echo '</pre>';
    exit;
}

// 세션에 토큰 정보를 저장
$_SESSION['auth_kakao_token_info'] = true;
$_SESSION['kakao_token_info'] = $token;



// 사용자 정보 호출
$userInfo =  @json_decode($kakaologin->getUserInfo($token['access_token']),true);



// 에러
if( !empty($userInfo['msg']) ){
    echo '<h1>사용자 정보 요청실패</h1><pre>'; print_r($userInfo); echo '</pre>';
    exit;
}

$_SESSION['auth_kakao_user_info'] = true;
$_SESSION['kakao_user_info'] = $userInfo;


$chk_obj = new stdClass();
$chk_obj -> USER_ID = 'kko'.$_SESSION['kakao_user_info']['id'];
//$chk_obj -> EMAIL = $_SESSION['kakao_user_info']['kakao_account']['email'];
if(chkTableInfoByObj('TBL_USER',$chk_obj)){
    setUserSession($chk_obj);
    die(header("Location:".'/'));
}
else
{
    die(header("Location:".$kakaologin->result_uri));
}

