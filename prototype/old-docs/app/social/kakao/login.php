<?php
include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/kakao/lib.php";
$kakaologin = new kakaoRestAPI();
if( $kakaologin->auth_apply !== true){ die("카카오로그인을 사용할 수 없습니다."); }

$arrUserInfo = array('id'=>'','nickname'=>'','email'=>'','gender'=>'');
if(!empty($_SESSION['auth_kakao_user_info'])){
    if( !empty($_SESSION['kakao_user_info']['id'])){ $arrUserInfo['id']= $_SESSION['kakao_user_info']['id'];  }
    if( !empty($_SESSION['kakao_user_info']['kakao_account']['profile']['nickname'])){ $arrUserInfo['nickname']= $_SESSION['kakao_user_info']['kakao_account']['profile']['nickname'];  }
    if( !empty($_SESSION['kakao_user_info']['kakao_account']['email'])){ $arrUserInfo['email']= $_SESSION['kakao_user_info']['kakao_account']['email']; }
    if( !empty($_SESSION['kakao_user_info']['kakao_account']['gender'])){ $arrUserInfo['gender']= $_SESSION['kakao_user_info']['kakao_account']['gender']; }
}

?>
<div class="wrap-kakao-login">
    <h1>카카오톡 API를 이용한 로그인 샘플(REST API)</h1>
    <ul>
        <li><a href="/kakao-login.php">처음화면으로</a></li>
        <li><a href="<?php echo $kakaologin->redirect_uri; ?>?logout=true">로그아웃</a></li>
        <li>
            <a href="<?php echo $kakaologin->request_url['code'] ?>"  class="kakao-login">
                <img src="//k.kakaocdn.net/14/dn/btroDszwNrM/I6efHub1SN5KCJqLm1Ovx1/o.jpg" width="180" alt="카카오 로그인 버튼"/>
            </a>
        </li>
    </ul>
    <h3>인증상태</h3>
    <ul>
        <li>토큰인증: <?php echo !empty($_SESSION['auth_kakao_token_info']) ? '<font color="blue">인증완료</font>':'<font color="red">인증대기</font>'; ?></li>
        <li>사용자인증: <?php echo !empty($_SESSION['auth_kakao_user_info']) ? '<font color="blue">인증완료</font>':'<font color="red">인증대기</font>'; ?></li>
    </ul>
    <h3>인증후 사용자 정보(아이디(고유번호),이메일,닉네임,성별)</h3>
    <ul>
        <li>아이디(고유번호): <input type="text" name="id" value="<?php echo $arrUserInfo['id'] ?>"></li>
        <li>닉네임: <input type="text" name="nickname" value="<?php echo $arrUserInfo['nickname'] ?>"></li>
        <li>이메일: <input type="text" name="email" value="<?php echo $arrUserInfo['email'] ?>"></li>
        <li>성별: <input type="text" name="gender" value="<?php echo $arrUserInfo['gender'] ?>"></li>
    </ul>
</div>
<style>
    .wrap-kakao-login{ padding:2%; }
    .wrap-kakao-login li{ margin:10px 0; }
</style>
