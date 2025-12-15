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

<script>

    document.addEventListener('DOMContentLoaded', () => {
        // 체크한 값 세팅
        let saveIdCheckbox = document.getElementById("save-id");

        // 유저 아이디 세팅
        let userIdInput = document.getElementById("login_id");

        // 체크할 떄 localStorage에 저장한 userId 값 체크하여 있다면 값 세팅
        if(localStorage.getItem("userId")) {
            userIdInput.value = localStorage.getItem("userId");
            saveIdCheckbox.checked = true;
        }
    })


    const saveID= ()=>{
        if(document.querySelector('#save-id').checked) {
            localStorage.setItem("userId", document.querySelector("#login_id").value);
        } else {
            localStorage.removeItem("userId");
        }
    }

    const sns_login = (type) => {
        let url = "";
        type === 'kakao'? url = kko_code : url = naver_code;

        if (isMobile()) {
            location.href=url;
        }else{
            window.open(url, "sns", "height=500,width=500");
        }
    }

    const doLogin =  () => {


        if(isNull(document.querySelector("#login_id").value)){
            alert('아이디를 입력해주세요.');
            document.querySelector("#login_id").focus();
            return;
        }


        if(isNull(document.querySelector("#login_pw").value)){
            alert('비밀번호를 입력해주세요.');
            document.querySelector("#login_pw").focus();
            return;
        }

        let usrObj =
            {
                USER_ID		: document.querySelector("#login_id").value
                , PASSWORD  : document.querySelector("#login_pw").value
            };



        try {
            //let param = encodeURI(JSON.stringify(usrObj));
            let param = JSON.stringify(usrObj);
            let data = new FormData();
            data.append("usrObj",param);
            axios.post('/api/user/login',data,null)
                .then((result) => {
                    console.log(result);
                    alert(result.data.message);
                    if(result.data.isSuc){
                        location.href=result.data.callback;
                    }
                    // alert(result.data.IDX); 하나뽑기
                    // alert(result.data.list[1].IDX); 리스트뽑기
                }).catch((error) => {
                if(error.response.status === 400) {
                    //alert("400 error occurred");
                }
            });
        } catch(err) {
            alert(123);
            console.log("Error >>", err);
        }
    }

</script>



  <section id="memberWrap" class="section">
  	<form id="loginForm" name="loginForm" method="post" action="/dumy/member/login_proc.php">
		<!-- subTitBox -->
		<div class="subTitBox">
		  <h3>로그인<?php echo $_SESSION['name']?></h3>
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

		<!-- bottomBtn -->
		<div class="bottomBtn">
		  <button type="button" class="btn" onclick="doLogin()">로그인</button>
		</div>
		<!--// bottomBtn-->

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

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '로그인',
        description:
            '회원 로그인: 사주로 회원이면 저렴한 상담 혜택!',
        url: 'https://sajutarot.com/app/user/login',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>

<style>
	footer {display:none !important;}
</style>
