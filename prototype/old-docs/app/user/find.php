<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
require_once($_SERVER['DOCUMENT_ROOT']."/config/kcp/cfg/cert_conf.php");
?>

<script>

    let phone_chk = 'N';
    document.domain = "sajutarot.com";

    window.addEventListener("message", receiveMessage, false);
    function receiveMessage(event) {
        document.querySelector('#veri_up_hash').value = event.data.veri_up_hash;
    }

    // 인증창 종료후 인증데이터 리턴 함수
    function auth_data( frm )
    {
        var auth_form     = document.form_auth;
        var nField        = frm.elements.length;
        var response_data = "";

        // up_hash 검증
        if( frm.up_hash.value != auth_form.veri_up_hash.value )
        {
            alert("up_hash 변조 위험있음");
        }

        alert(auth_form.veri_up_hash.value);


        //스마트폰 처리
        for ( i = 0; i < nField; i++ )
        {
            if( frm.elements[i].value != "" )
            {
                response_data += frm.elements[i].name + " : " + frm.elements[i].value + "\n";
            }
        }

        if( navigator.userAgent.indexOf("Android") > - 1 || navigator.userAgent.indexOf("iPhone") > - 1 )
        {
            document.getElementById( "cert_info" ).style.display = "";
            document.getElementById( "kcp_cert"  ).style.display = "none";
        }

        //alert(response_data);
    }

    // 인증창 호출 함수
    function auth_type_check()
    {
        var auth_form = document.form_auth;

        if( auth_form.ordr_idxx.value == "" )
        {
            alert( "요청번호는 필수 입니다." );

            return false;
        }
        else
        {
            if( navigator.userAgent.indexOf("Android") > - 1 || navigator.userAgent.indexOf("iPhone") > - 1 )
            {
                auth_form.target = "kcp_cert";

                document.getElementById( "memberWrap" ).style.display = "none";
                document.getElementById( "kcp_cert"  ).style.display = "";
            }
            else
            {
                var return_gubun;
                var width  = 410;
                var height = 500;

                var leftpos = screen.width  / 2 - ( width  / 2 );
                var toppos  = screen.height / 2 - ( height / 2 );

                var winopts  = "width=" + width   + ", height=" + height + ", toolbar=no,status=no,statusbar=no,menubar=no,scrollbars=no,resizable=no";
                var position = ",left=" + leftpos + ", top="    + toppos;
                var AUTH_POP = window.open('','auth_popup', winopts + position);

                auth_form.target = "auth_popup";
            }

            auth_form.action = "/config/kcp/SMART_ENC/smartcert_proc_req.php"; // 인증창 호출 및 결과값 리턴 페이지 주소
            auth_form.submit();
            //return true;
        }
    }

    window.onload=function()
    {
        init_orderid(); // 요청번호 샘플 생성
    }

    // 요청번호 생성 예제 ( up_hash 생성시 필요 )
    function init_orderid()
    {
        var today = new Date();
        var year  = today.getFullYear();
        var month = today.getMonth()+ 1;
        var date  = today.getDate();
        var time  = today.getTime();

        if(parseInt(month) < 10)
        {
            month = "0" + month;
        }

        var vOrderID = year + "" + month + "" + date + "" + time;

        document.form_auth.ordr_idxx.value = vOrderID;
    }

    function btn_disable(result,phone)
    {
        document.getElementById( "memberWrap" ).style.display = "";
        if (result=='Y'){
            phone_chk = 'Y';
            getUserID(phone);
        }
    }

    const getUserID = async (phone) => {
        showLoading();
        let userObj =
            {
                PHONE : phone,
                PHONE_CHK : document.querySelector("#phone_chk").value

            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/find_id', data);

            console.log(result);
            if (result.data.isSuc) {
                document.getElementById( "after_find" ).style.display = "";
                document.getElementById( "before_find"  ).style.display = "none";
                let str = "회원님의 아이디는<br>"+result.data.userObj.USER_ID+" 입니다.";
                document.querySelector("#user_id").innerHTML=str;
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const find_pw = async () => {

        if(isNull(document.querySelector("#id").value)){
            alert('아디디를 입력해주세요.');
            document.querySelector("#id").focus();
            return;
        }

        if(isNull(document.querySelector("#phone").value)){
            alert('핸드폰 번호를 입력해주세요.');
            return;
        }

        if(!validatePhoneNumber(document.querySelector("#phone").value)){
            alert('핸드폰 형식을 맞춰주세요.');
            return;
        }

        showLoading();
        let userObj =
            {
                USER_ID : document.querySelector("#id").value,
                PHONE : document.querySelector("#phone").value

            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/find_pw', data);
            console.log(result);
            if (result.data.isSuc) {
                alert('메일이 전송되었습니다.');
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }


</script>

  <section id="memberWrap" class="section">
  	<div class="memberFindBox">

		<!-- subTitBox -->
		<div class="subTitBox">
		  <h3>회원정보 찾기</h3>
		</div>
		<!--// subTitBox -->

		<div class="tabWrap">
			<div class="tabList">
				<ul>
					<li class="on">
						<button type="button" onclick="tabOpen(event, this, 'findTab1')">아이디 찾기</a>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'findTab2')">비밀번호 찾기</a>
					</li>
				</ul>
			</div>
			<!-- 회원 본인인증 -->

			<div class="tabContWrap">
				<!-- 아이디 찾기 -->
				<div class="tabContItem" id="findTab1">

					<div id="before_find" class="findBox">
						<strong>본인 인증을 해주세요.</strong>
                        <input type="button" value="인증버튼" class="btn" onclick="auth_type_check()">
						<p>
							가입한 휴대폰번호가 기억이 나지 않는 경우<br>
							고객센터로 문의해주세요.
						</p>
					</div>
					<!--// 회원 보인인증 -->

					<!-- 본인인증 후 아이디 노출 -->
					<div id="after_find" class="findBox">
						<strong id="user_id"></strong>
						<a href="./login" class="btn">로그인</a>
					</div>

					<!--// 본인인증 후 아이디 노출 -->
				</div>
				<!--// 아이디 찾기 -->
				<!-- 비밀번호 찾기 -->
				<div class="tabContItem"  id="findTab2">
					<form id="findPwForm" action="" method="">
						<div class="infoBoxWrap">
							<!-- infoBox -->
							<div class="infoBox">
								<p><label class="common_area" for="id">아이디 *</label></p>
								<div class="inFlex">
									<input id="id" name="id" type="text" title="아이디 입력" placeholder="아이디를 입력해주세요.">
								</div>
							</div>
							<!--// infoBox -->

							<!-- infoBox -->
							<div class="infoBox">
								<p><label for="phone" >휴대폰번호*</label></p>
								<div class="inFlex">
									<input type="text" class="form-control" id="phone" placeholder="-없이 입력하세요.">
								</div>
							</div>
							<!--// infoBox -->

							<!-- bottomBtn -->
							<div class="bottomBtn mt30">
							  <button type="button" class="btn" onclick="find_pw()">확인</button>
							</div>
							<!--// bottomBtn-->

							<!-- infoText -->
							<div class="infoText">
								<p>1. 가입하신 이메일로 임시 비밀번호를 보내 드립니다.</p>
								<p>2. 임시 비밀번호로 로그인 후 새 비밀번호로 변경하세요.</p>
								<p>3. 비밀번호 변경은 마이페이지 → 회원정보에서 가능합니다.</p>
							</div>
							<!--// infoText -->

						</div>
					</form>
				</div>
				<!--// 비밀번호 찾기 -->
			</div>

		</div>

	</div>


      <div id="cert_info">

          <input type="hidden" id="TX_SEQ_NO" name="TX_SEQ_NO" />
          <input type="hidden" id="RSLT_CD" name="RSLT_CD" />
          <input type="hidden" id="TEL_NO" name="TEL_NO" />
          <input type="hidden" id="tel" name="tel" />
          <form id="form_auth" name="form_auth" method="post">

              <input type="hidden" name="ordr_idxx" class="frminput" value="" size="40" readonly="readonly" maxlength="40"/>

              <input type="hidden" id="phone_chk" name="phone_chk"   value=""/>
              <!-- 요청종류 -->
              <input type="hidden" name="req_tx"       value="cert"/>
              <!-- 요청구분 -->
              <input type="hidden" name="cert_method"  value="01"/>
              <!-- 웹사이트아이디 : ../cfg/cert_conf.php 파일에서 설정해주세요 -->
              <input type="hidden" name="web_siteid"   value="<?= $g_conf_web_siteid ?>"/>
              <!-- 노출 통신사 default 처리시 아래의 주석을 해제하고 사용하십시요
                   SKT : SKT , KT : KTF , LGU+ : LGT
              <input type="hidden" name="fix_commid"      value="KTF"/>
              -->
              <!-- 사이트코드 : ../cfg/cert_conf.php 파일에서 설정해주세요 -->
              <input type="hidden" name="site_cd"      value="<?= $g_conf_site_cd ?>" />
              <!-- Ret_URL : ../cfg/cert_conf.php 파일에서 설정해주세요 -->
              <input type="hidden" name="Ret_URL"      value="<?= $g_conf_Ret_URL ?>" />
              <!-- cert_otp_use 필수 ( 메뉴얼 참고)
                   Y : 실명 확인 + OTP 점유 확인 , N : 실명 확인 only
              -->
              <input type="hidden" name="cert_otp_use" value="Y"/>
              <!-- 리턴 암호화 고도화 -->
              <input type="hidden" name="cert_enc_use_ext" value="Y"/>

              <!-- cert_able_yn input 비활성화 설정 -->
              <input type="hidden" name="cert_able_yn" value=""/>

              <input type="hidden" name="res_cd"       value=""/>
              <input type="hidden" name="res_msg"      value=""/>

              <!-- up_hash 검증 을 위한 필드 -->
              <input type="hidden" id="veri_up_hash" name="veri_up_hash" value=""/>

              <!-- web_siteid 을 위한 필드 -->
              <input type="hidden" name="web_siteid_hashYN" value="Y"/>

              <!-- 가맹점 사용 필드 (인증완료시 리턴)-->
              <input type="hidden" name="param_opt_1"  value="opt1"/>
              <input type="hidden" name="param_opt_2"  value="opt2"/>
              <input type="hidden" name="param_opt_3"  value="opt3"/>
          </form>
      </div>
  </section>
<iframe id="kcp_cert" name="kcp_cert" width="100%" height="700" frameborder="0" scrolling="no" style="display:none"></iframe>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '회원정보 찾기',
        description:
            '회원정보 찾기: 사주로 회원이면 저렴한 상담 혜택!',
        url: 'https://sajutarot.com/app/user/find',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
<style>
	footer {display:none !important;}
</style>
