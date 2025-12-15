<?php
include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/kakao/lib.php";
include_once $_SERVER['DOCUMENT_ROOT']."/config/lib/social/naver/lib.php";
$kakaologin = new kakaoRestAPI();
$naverlogin = new naverRestAPI();

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

    const doLogin =  () => {

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
                })
        } catch(err) {
            console.log("Error >>", err);
        }
    }

</script>

<div>
    로그인 |
    <a href="/app/user/register">회원가입</a><br>
    <input type="text" id="login_id" placeholder="아이디"><br>
    <input type="text" id="login_pw" placeholder="비밀번호"><br>
    <input type="button" value="로그인" onclick="doLogin();"><br>
    <input type="checkbox" id="auto_yn"> 자동로그인
    <input type="button" value="정보찾기"><br>
    <!--<a href="<?php /*echo $naverlogin->request_url['code'] */?>">네이버 로그인</a><br>
    <a href="<?php /*echo $kakaologin->request_url['code'] */?>">카카오 로그인</a><br>-->

    <a id="naver_login" href="">네이버 로그인</a><br>
    <a id="kakao_login" href="">카카오 로그인</a><br>
</div>

