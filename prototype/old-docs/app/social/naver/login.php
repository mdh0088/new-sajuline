<?php
// 네이버 로그인 접근토큰 요청 예제
$client_id = "QDQsr7obOFGVg3iwhFUN";
$redirectURI = urlencode("https://sajuro1.cafe24.com/app/social/naver/callback.php");
$state = "RAMDOM_STATE";
$apiURL = "https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=".$client_id."&redirect_uri=".$redirectURI."&state=".$state;
?><a href="<?php echo $apiURL ?>">로그인</a>
