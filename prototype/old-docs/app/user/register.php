<?php
require_once($_SERVER['DOCUMENT_ROOT']."/common/header.php");

include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/kakao/lib.php";
include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/naver/lib.php";
$kakaologin = new kakaoRestAPI();
$naverlogin = new naverRestAPI();




?>

<a href="/app/user/join">일반회원가입</a><br>
<a href="<?php echo $kakaologin->request_url['code'] ?>">카카오</a><br>
<a href="<?php echo $naverlogin->request_url['code'] ?>">네이버</a><br><br><br><br>



<?php
require_once($_SERVER['DOCUMENT_ROOT']."/common/footer.php");
?>

