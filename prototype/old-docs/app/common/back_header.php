<?php
session_start();
/*
if(!isset($_SESSION['id']))
{
    echo '<script>alert("�α��� �� �̿����ּ���.");</script>';
    echo "<script>location.replace('/user/login.php');</script>";
    exit;
}
$query = "select * from user where id='{$_SESSION['id']}'";
$result=sql_query($query);
$row=sql_fetch($result);
$url=$_SERVER["PHP_SELF"];

if ($row['use_yn']=='Y') {
    echo '<script>alert("���ѵ� �̿����Դϴ�.");</script>';
    echo "<script>location.replace('/user/login.php');</script>";
    exit;
}
*/

?>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="/app/assets/css/function.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.css">

        <script src="/app/assets/js/jquery-3.4.1.min.js"></script>
    	<script src="/app/assets/js/jquery-ui.js"></script>
    	<script src="/app/assets/js/swiper.min.js"></script>
    	<script src="/app/assets/js/common.js"></script>
        <script src="/app/assets/js/function.js"></script>
        <script src="/app/assets/js/config.js"></script>

        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.js"></script>
    	<script src="https://malsup.github.io/min/jquery.form.min.js"></script>


        ���߿� ��Ʈ��Ʈ��
        <!-- <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous"> -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV" crossorigin="anonymous"></script>
        <!-- ���߿� ��Ʈ��Ʈ�� -->

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

                        // alert(result.data.IDX); �ϳ��̱�
                        // alert(result.data.list[1].IDX); ����Ʈ�̱�
                    })
            } catch(err) {
                console.log("Error >>", err);
            }
        }

    </script>
<body>
	<!-- wrap -->
	<div id="wrap">
		<!-- main -->
		<main id="main">

			<!-- header -->
			<header id="header">
				<div class="inner">
					<div class="leftArea">

					</div>

					<div class="rightArea">
                        <?php
                            if (!isset($_SESSION['IDX'])) {
                        ?>
                                <a href="/app/user/login" class="btn btn-primary">�α���</a>
                                <a href="/app/user/join_info"  class="btn btn-secondary">ȸ������</a>
                        <?php
                            } else {
                        ?>
                                <a href="Javascript:doLogout();" class="btn btn-primary">�α׾ƿ�</a>
                                <a href="/app/user/mypage" class="btn btn-secondary">����������</a>
                                <a href="/app/charge/point" class="btn btn-secondary">����Ʈ ����</a>
                        <?php
                            }
                        ?>
                        <a href="/app/recruit/info" class="btn btn-secondary">�����Ͻ�û</a>
					</div>

				</div>
			</header>
			<!--// header -->
            <div id="loading-overlay" class="hidden" style="display: none">
                <div class="loading-spinner"></div>
            </div>
			<!-- contents -->
			<div id="contents">
