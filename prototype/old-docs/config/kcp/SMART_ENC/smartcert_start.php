<?
/* ============================================================================== */
/* =   PAGE : 인증 요청 PAGE                                                    = */
/* = -------------------------------------------------------------------------- = */
/* =   Copyright (c)  2012.01   KCP Inc.   All Rights Reserved.                 = */
/* ============================================================================== */

/* ============================================================================== */
/* =   환경 설정 파일 Include                                                   = */
/* = -------------------------------------------------------------------------- = */
include "../cfg/cert_conf.php";       // 환경설정 파일 include

/* = -------------------------------------------------------------------------- = */
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="user-scalable=yes, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, width=device-width, target-densitydpi=medium-dpi" >
    <title>*** KCP Online Certification System [PHP Version] ***</title>
    <link href="../css/sample.css" rel="stylesheet" type="text/css">
    <script type="text/javascript">

        document.domain = "www.sajuline.com";

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

            alert(response_data);
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

                    document.getElementById( "cert_info" ).style.display = "none";
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

        /* 예제 */
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

        function btn_disable(result)
        {

/*            $('#check-phone').removeClass("w3-blue");
            $('#check-phone').addClass("w3-gray");
            $('#check-phone').val("본인 인증 완료");
            $('#check-phone').attr("disabled", "true");
            $('#check-phone-msg').show();
            $('#next_area').show();*/
           // window.document.kcbResultForm.submit();
            document.getElementById( "cert_info" ).style.display = "";
        }

        function chk_all(){
            if($('#uk-agree-all').prop('checked')==true){
                $('#uk-agree1').prop('checked',true);
                $('#uk-agree2').prop('checked',true);

            }else{
                $('#uk-agree1').prop('checked',false);
                $('#uk-agree2').prop('checked',false);
            }

        }

    </script>
</head>
<body oncontextmenu="return false;" ondragstart="return false;" onselectstart="return false;">

<div align="center" id="cert_info">
    <section id="memberWrap" class="section">
        <form id="joinAgreement" action="" method="">
            <!-- subTitBox -->
            <div class="subTitBox">
                <h3>회원가입</h3>
            </div>
            <!--// subTitBox -->
        </form>
    </section>

    <div class="join m_wrap member">

        <form id="data_form" name="kcbResultForm" action="https://www.sajuline.com" method="GET">

            <div class="join_section">

                <div class="mem_row round_box agreementBox agreementBox01">
                    <div class="checkbox">
                        <input id="uk-agree-all" type="checkbox" onclick="chk_all();">
                        <label  for="uk-agree-all">아래 내용에 모두 동의합니다.</label>
                    </div>
                </div>

                <div class="mem_row agreementBox agreementBox02">
                    <div class="checkbox">
                        <input id="uk-agree1" type="checkbox">
                        <label for="uk-agree1">개인정보취급방침 </label>
                    </div>
                    <span style="color:blue;text-decoration: underline;" onclick="$('.agree-text.1').toggle();">보기</span>
                </div>
                <div class="agree-text 1" style=""><?=$privacy?></div>

                <div class="agreementBox agreementBox02">
                    <div class="checkbox">
                        <input id="uk-agree2" type="checkbox">
                        <label for="uk-agree2">서비스 이용약관 동의 </label>
                    </div>
                    <span style="color:blue;text-decoration: underline;" onclick="$('.agree-text.2').toggle();">보기</span>
                </div>
                <div class="agree-text 2" style=""><?=$agreement?></div>
            </div>


            <div class="join_section">
                <p class="mem_row align_center agreementBtn">
                    <input class="w3-btn w3-blue btn_join_join" type="button" onclick="auth_type_check()"  value="핸드폰 본인 인증">

                </p>
                <p class="mem_row align_center" id="check-phone-msg" style="display:none;"><strong class="color_red">*</strong> 핸드폰 본인 인증이 완료되었습니다.</p>
                <input type="hidden" id="TX_SEQ_NO" name="TX_SEQ_NO" />
                <input type="hidden" id="RSLT_CD" name="RSLT_CD" />
                <input type="hidden" id="TEL_NO" name="TEL_NO" />
                <input type="hidden" id="PHONE_CHK" name="PHONE_CHK" />
                <input type="hidden" id="tel" name="tel" />
            </div>

            <div class="join_section" id="next_area" style="display:none;">
                <p class="mem_row align_center">
                    <input class="w3-btn w3-blue btn_join_join" type="button" id="uk-join-btn" value="다음">
                </p>
            </div>
        </form>

    </div>

    <form id="form_auth" name="form_auth" method="post">

        <input type="hidden" name="ordr_idxx" class="frminput" value="" size="40" readonly="readonly" maxlength="40"/>

        <input type="text" id="phone_chk" name="phone_chk"   value=""/>
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
        <input type="text" id="veri_up_hash" name="veri_up_hash" value=""/>

        <!-- web_siteid 을 위한 필드 -->
        <input type="hidden" name="web_siteid_hashYN" value="Y"/>

        <!-- 가맹점 사용 필드 (인증완료시 리턴)-->
        <input type="hidden" name="param_opt_1"  value="opt1"/>
        <input type="hidden" name="param_opt_2"  value="opt2"/>
        <input type="hidden" name="param_opt_3"  value="opt3"/>
    </form>
</div>
<iframe id="kcp_cert" name="kcp_cert" width="100%" height="700" frameborder="0" scrolling="no" style="display:none"></iframe>
</body>
</html>
