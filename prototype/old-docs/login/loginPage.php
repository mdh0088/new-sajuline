<script src="./social_key.js"></script>

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
  	<form id="loginForm" name="loginForm" method="post">
		<!-- subTitBox -->
		<div class="subTitBox">
		  <h3>로그인</h3>
		</div>
		<!--// subTitBox -->

		<!-- inputbox -->
		<div class="inputBox">
		  <input type="text" title="아이디 입력" placeholder="아이디" id="login_id" name="login_id">
		  <input type="password" title="비밀번호 입력" placeholder="비밀번호" id="login_pw" name="login_pw">
		</div>
		<!--// inputBox -->

		<!-- linkBox -->
		<div class="linkBox">
		  <div class="checkBox">
			<input type="checkbox" title="아이디 저장" id="save-id" name="save-id" onclick="saveID();">
			<label class="form-check-label" for="save-id">아이디저장</label>
		  </div>
		  <div class="link">
			<a href="./find" id="find-id-btn">아이디 찾기</a>
			<a href="./find" id="find-pw-btn">비밀번호 찾기</a>
		  </div>
		</div>
		<!-- linkBox -->

		<!-- snsLogin -->
		<div class="snsLogin">
		  <button type="button" class="loginKakao" id="kakao_login" onclick="sns_login('kakao')">
			<img src="/app/assets/img/contents/ico-kakao.png" class="카카오톡 로그인">
			카카오톡
		  </button>
		  <button type="button" class="loginNaver" id="naver_login" onclick="sns_login('naver')">
			<img src="/app/assets/img/contents/ico-naver.png" alt="네이버 로그인">
			네이버
		  </button>
		</div>
		<!--// snsLogin -->

		<!-- memberBanner -->
		<div class="memberBanner">
		  <div class="tBox">
		  	<a href="/app/user/join_info">
				<strong>아직 회원이 아니신가요?</strong>
				<p>회원가입 후 다양한 혜택을 누려보세요.</p>
			</a>
		  </div>
		</div>
		<!--// memberBanner -->
	</form>
  </section>