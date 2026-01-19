<?php

require_once($_SERVER['DOCUMENT_ROOT']."/config/db/init.php");
require_once($_SERVER['DOCUMENT_ROOT']."/src/util/common.php");

include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/naver/lib.php";

error_reporting( E_ALL );
ini_set( "display_errors", 1 );

$naverlogin = new naverRestAPI();
if( $naverlogin->auth_apply !== true){ die("네이버 로그인을 사용할 수 없습니다."); }


// 로그아웃일경우
if( !empty($_GET['logout'])){
    // 사용자 정보 호출
    $userLogout =  @json_decode($naverlogin->getLogout($_SESSION['kakao_token_info']['access_token']),true);

    /*
    // 에러
    if( !empty($userLogout['msg']) ){
        echo '<h1>사용자 로그아웃 요청실패</h1><pre>'; print_r($userLogout); echo '</pre>';
        exit;
    }
    */

    if(!empty($_SESSION['auth_naver_token_info'])) unset($_SESSION['auth_naver_token_info'],$_SESSION['naver_token_info']);
    if(!empty($_SESSION['auth_naver_user_info'])) unset($_SESSION['auth_naver_user_info'],$_SESSION['naver_user_info']);


    die(header("Location:".$naverlogin->result_uri));
}

if(!empty($_SESSION['auth_naver_token_info'])) unset($_SESSION['auth_naver_token_info'],$_SESSION['naver_token_info']);
if(!empty($_SESSION['auth_naver_user_info'])) unset($_SESSION['auth_naver_user_info'],$_SESSION['naver_user_info']);

$code = empty($_GET['code']) ? '': $_GET['code'];
$state = empty($_GET['state']) ? '': $_GET['state'];
$token = @json_decode($naverlogin->getToken($code,$state),true);

// 에러
/*
if( !empty($token['error']) ){
    echo '<h1>인증토큰 요청 실패</h1><pre>'; print_r($token); echo '</pre>';
    exit;
}
*/

// 세션에 토큰 정보를 저장
$_SESSION['auth_naver_token_info'] = true;
$_SESSION['naver_token_info'] = $token;

$userInfo =  @json_decode($naverlogin->getUserInfo($token['access_token']),true);

// 에러
/*
if( !empty($userInfo['msg']) ){
    echo '<h1>사용자 정보 요청실패</h1><pre>'; print_r($userInfo); echo '</pre>';
    exit;
}
*/

// 세션에 사용자 정보를 저장
$_SESSION['auth_naver_user_info'] = true;
$_SESSION['naver_user_info'] = $userInfo;

$chk_obj = new stdClass();
$chk_obj -> EMAIL = $_SESSION['naver_user_info']['response']['email'];
if(chkTableInfoByObj('TBL_USER',$chk_obj)){
    setUserSession($chk_obj);
    die(header("Location:".'/'));
}
else
{
    die(header("Location:".$naverlogin->result_uri));
}


// 사용자 정보 요청
//die(header("Location:".$naverlogin->result_uri));

