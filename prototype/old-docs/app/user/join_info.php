<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

session_start();
if (isset($_SESSION['IDX'])){
    echo
    "
    <script>
        location.href='/';
    </script>
    ";
}
?>


<script src="/app/assets/js/social.js"></script>
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.js"></script>


<script>

    const sns_login = (type) => {
        let url = "";
        type === 'kakao'? url = kko_code : url = naver_code;

        if (isMobile()) {
            location.href=url;
        }else{
            window.open(url, "sns", "height=500,width=500");
        }
    }


</script>


<section id="memberWrap" class="section">
	<form id="joinForm" action="" method="">
		<!-- subTitBox -->
		<div class="subTitBox">
		  <h3>회원가입</h3>
		</div>
		<!--// subTitBox -->

		<!-- lineTitBox -->
		<div class="lineTitBox">
			<strong>회원정보 입력</strong>
			<p>
				회원가입하신 후 사주로 다양한 서비스와 혜택을
				이용해보세요.
			</p>
		</div>
		<!--// lineTitBox -->

		<!-- bottomBtn -->
		<div class="bottomBtn mt15">
		  <a href="/app/user/join" class="btn">사주로 회원가입</a>
		</div>
		<!--// bottomBtn-->

		<!-- lineTitBox -->
		<div class="lineTitBox mt50">
			<strong>간편 회원가입</strong>
			<p>
				SNS계정을 연동하여 빠르고 쉽고 안전하게 회원가입
				할 수 있습니다.
			</p>
		</div>
		<!--// lineTitBox -->

		<!-- snsLogin -->
		<div class="snsLogin">
		  <button type="button" class="loginKakao" id="kakao_login" onclick="sns_login('kakao')">
			<img src="/app/assets/img/contents/ico-kakao.png" class="카카오톡 로그인">
			카카오 간편가입
		  </button>
		  <button type="button" class="loginNaver" id="naver_login" onclick="sns_login('naver')">
			<img src="/app/assets/img/contents/ico-naver.png" alt="네이버 로그인">
			네이버 간편가입
		  </button>
		</div>
		<!--// snsLogin -->

		<!-- memberBanner -->
		<div class="memberBanner">
		  <div class="tBox">
			<a href="/app/user/login" class="joinBannerText">
				<strong>이미 회원이신가요?</strong>
			</a>
		  </div>
		</div>
		<!--// memberBanner -->
	</form>
</section>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '회원가입 정보',
        description:
            '회원가입 정보: 지금 회원가입하면?누구나 상담 가능한 무료 1만 상담포인트 지급!',
        url: 'https://sajutarot.com/app/user/join_info',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>


<style>
	footer {display:none !important;}
</style>
