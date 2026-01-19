<?php
session_start();

if (!isset($_SERVER['HTTPS']) || $_SERVER['HTTPS'] !== 'on') {
    $redirect_url = "https://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
    header("Location: $redirect_url");
    exit;
}
/*
if (isset($_SESSION['IDX']) && $_SESSION['IS_CS'] =='N' ){
    include_once $_SERVER['DOCUMENT_ROOT'].'/api/point/virtual_update.php';
}*/

/*
if(!isset($_SESSION['id']))
{
    echo '<script>alert("로그인 후 이용해주세요.");</script>';
    echo "<script>location.replace('/user/login.php');</script>";
    exit;
}
$query = "select * from user where id='{$_SESSION['id']}'";
$result=sql_query($query);
$row=sql_fetch($result);
$url=$_SERVER["PHP_SELF"];

if ($row['use_yn']=='Y') {
    echo '<script>alert("제한된 이용자입니다.");</script>';
    echo "<script>location.replace('/user/login.php');</script>";
    exit;
}
*/





?>
<html>
    <head>
        <title>사주로</title>
        <meta charset="UTF-8" />
		<meta name="theme-color" content="#D5D4ED">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width, initial-scale=1">
		<!-- naver WebMasterTools -->
		<meta name="naver-site-verification" content="4d232487a3b4628c086e4c7961dcbcdcb98a0692" />
		<!--// naver WebMasterTools -->

        <!--<meta id="meta_sajurot_title" name="title" content="사주로 | 사주타로 | 사주로 타로, 운세온라인플랫폼">-->


<!--        <meta id="meta_sajurot_description" name="description" content="타로, 운세, 사주, 꿈해몽 전화상담 전문 사주로와 함께 행복한 인생 만들기">
        <meta id="meta_sajurot_url" name="url" content="https://sajutarot.com">
		<meta name="keywords" content="타로, 운세, 사주, 꿈해몽 전화상담 전문 사주로와 함께 행복한 인생 만들기">
		<meta property="og:type" content="website">
        <meta property="og:title" content="사주로 | 사주타로 | 사주로 타로, 운세온라인플랫폼">
        <meta property="og:description" content="타로, 운세, 사주, 꿈해몽 전화상담 전문 사주로와 함께 행복한 인생 만들기">
        <meta property="og:url" content="https://sajutarot.com">
        <meta property="og:image" content="https://sajutarot.com/app/assets/img/layout/logo.png">

-->


        <meta property="description" name="description" content="타로, 운세, 사주, 꿈해몽 전화상담 전문 사주로와 함께 행복한 인생 만들기" />
        <meta property="keywords" name="keywords" content="" />
        <meta property="og:type" content="website" />
        <meta property="og:title" name="og:title" itemprop="title name" content="사주로 | 사주타로 | 사주로 타로, 운세온라인플랫폼" />
        <meta property="og:title" name="twitter:title" itemprop="title name" content="사주로 | 사주타로 | 사주로 타로, 운세온라인플랫폼" />
        <meta
                property="og:description"
                name="og:description"
                itemprop="description"
                content="사주로 - 운세온라인플랫폼"
        />
        <meta
                property="og:description"
                name="twitter:description"
                itemprop="description"
                content="사주로 - 운세온라인플랫폼"
        />
        <meta property="og:url" name="og:url" content="사주로 - 운세온라인플랫폼" />
        <meta property="og:url" name="twitter:url" content="사주로 - 운세온라인플랫폼" />
        <meta
                property="og:image"
                itemprop="image primaryImageOfPage"
                name="og:image"
                content="https://sajutarot.com/app/assets/img/layout/logo.png"
        />
        <meta
                property="og:image"
                itemprop="image primaryImageOfPage"
                name="twitter:image"
                content="https://sajutarot.com/app/assets/img/layout/logo.png"
        />


        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Expires" content="-1" />
        <meta http-equiv="Cache-Control" content="no-cache" />

        <link rel="stylesheet" href="/app/assets/css/function.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.css">
		<link rel="stylesheet" href="/app/assets/css/style.css" />


        <script src="/app/assets/js/jquery-3.4.1.min.js"></script>
    	<script src="/app/assets/js/jquery-ui.js"></script>
    	<script src="/app/assets/js/swiper.min.js"></script>
    	<script src="/app/assets/js/common.js"></script>
        <script src="/app/assets/js/function.js"></script>
        <script src="/app/assets/js/alarm.js"></script>
        <script src="/app/assets/js/config.js"></script>

        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.js"></script>
    	<script src="https://malsup.github.io/min/jquery.form.min.js"></script>


        <!-- 개발용 부트스트랩 -->
<!--        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV" crossorigin="anonymous"></script>
    -->    <!-- 개발용 부트스트랩 -->

	<!— Google tag (gtag.js) —>
	<script async src="https://www.googletagmanager.com/gtag/js?id=G-CH4RCKR1PP"></script>
	<script>
	  window.dataLayer = window.dataLayer || [];
	  function gtag(){dataLayer.push(arguments);}
	  gtag('js', new Date());

	  gtag('config', 'G-CH4RCKR1PP');
	</script>

	<title>SAJUTAROT - NO.1 전화 사주/타로상담  서비스 플랫폼</title>


    </head>

    <script>
        const doLogout =  () => {
            try {
                //let param = encodeURI(JSON.stringify(usrObj));
                axios.post('/api/user/logout',null)
                    .then((result) => {
                        if(result.data){
                            alert(result.data.message);
                            location.href='/';
                        }

                        // alert(result.data.IDX); 하나뽑기
                        // alert(result.data.list[1].IDX); 리스트뽑기
                    })
            } catch(err) {
                console.log("Error >>", err);
            }
        }



        document.addEventListener('DOMContentLoaded', () => {
            cs_status();
        })

        const cs_status =  () => {
            try {
                //let param = encodeURI(JSON.stringify(usrObj));
                axios.post('/api/cs/cs_status',null)
                    .then((result) => {
                    })
            } catch(err) {
                console.log("Error >>", err);
            }
        }
    </script>
<body>



	<!-- wrap -->
	<div id="wrap">

		<!-- 후기 작성하기 > 등록 -->
		<div class="layer layer02" id="layer02">
			<div class="inBox">
				<strong class="tit">후기 작성하기</strong>
				<div class="popCont">
					<div class="icoText">
						<p>후기 등록이 완료되었습니다.</p>
					</div>
				</div>
				<a href="javascript:void(0)" onclick="fn_layer_close('layer02'); Javascript:location.reload()">닫기</a>
			</div>
		</div>
		<!--// 후기 작성하기 > 등록 -->

		<!-- main -->
		<main id="main">

			<!-- header -->
			<header id="header">
				<div class="inner">
					<h1 class="logo">
						<a href="/">
							메인으로 이동
						</a>
					</h1>

					<div class="util">
						<?php
                            if (!isset($_SESSION['IDX'])) {
                        ?>
                                <a href="/app/user/login" class="btnLogin">
									<img src="/app/assets/img/layout/btn-login.png">
									로그인
								</a>
                                <?php
                            } else {
                        ?>
                                <a href="Javascript:doLogout();" class="btnLogout">
									<img src="/app/assets/img/layout/btn-logout.png">
									로그아웃
								</a>
                        <?php
                            }
                        ?>
					</div>
				</div>
			</header>
			<!--// header -->
            <div id="loading-overlay" class="hidden" style="display: none">
                <div class="loading-spinner"></div>
            </div>

			<!-- contents -->
			<div id="contents">

            <!--카카오 채널하기 스크립트 -->

            <script>
            window.kakaoAsyncInit = function() {
                Kakao.Channel.createAddChannelButton({
                container: '#kakao-talk-channel-add-button',
                });
            };

            (function(d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) return;
                js = d.createElement(s); js.id = id;
                js.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.1.0/kakao.channel.min.js';
                js.integrity = 'sha384-MEvxc+j9wOPB2TZ85/N6G3bt3K1/CgHSGNSM+88GoytFuzP4C9szmANjTCNfgKep';
                js.crossOrigin = 'anonymous';
                fjs.parentNode.insertBefore(js, fjs);
            })(document, 'script', 'kakao-js-sdk');
            </script>

            <!--카카오 문의하기 스크립트 -->
            <!--
            <script>
            window.kakaoAsyncInit = function() {
                Kakao.Channel.createChatButton({
                container: '#kakao-talk-channel-chat-button',
                });
            };

            (function(d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) return;
                js = d.createElement(s); js.id = id;
                js.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.1.0/kakao.channel.min.js';
                js.integrity = 'sha384-MEvxc+j9wOPB2TZ85/N6G3bt3K1/CgHSGNSM+88GoytFuzP4C9szmANjTCNfgKep';
                js.crossOrigin = 'anonymous';
                fjs.parentNode.insertBefore(js, fjs);
            })(document, 'script', 'kakao-js-sdk');
            </script>-->
            <!--카카오 채널하기 -->
           <div class="kakao_c"
            id="kakao-talk-channel-add-button"
            data-channel-public-id="_NrvUxj"
            data-size="small"
            data-support-multiple-densities="true"
            ></div>

            <!--카카오 문의하기 스크립트 -->
            <!--
            <div class="kakao_m"
            id="kakao-talk-channel-chat-button"
            data-channel-public-id="_NrvUxj"
            data-title="question"
            data-size="small"
            data-color="mono"
            data-shape="mobile"
            data-support-multiple-densities="true"
            ></div>-->
