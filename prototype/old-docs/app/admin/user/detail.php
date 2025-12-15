<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/top.php");
$user_idx = $_GET['idx'];
?>

<style>
    #modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
    }

    #modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #fff;
        padding: 20px;
        border-radius: 5px;
        width: 80%;
        height: 80%;
        overflow: auto;
    }

    #popup {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        max-height: 80%; /* Add max height */
        overflow-y: auto; /* Add scroll for overflow */
        transform: translate(-50%, -50%);
        background-color: white;
        padding: 20px;
        border: 1px solid black;
        z-index: 1000;
    }
    #overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }

    /* Add this style for the pre tag inside the popup */
    #popup-content {
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    #edit-button {
        display: none;
        background-color: #b9b9e7;
        color: white;
        padding: 5px;
        cursor: pointer;
        margin-top: 10px;
    }

</style>

<script>

    document.addEventListener('DOMContentLoaded', () => {
        getUserInfo();
        getUserKakaoAlertLog();
    })

    const getUserInfo = () => {
        let userObj =
            {
                IDX		  : "<?php echo $user_idx ?>"
            };

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            axios.post('/api/user/admin_user_info', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {

                        userObj = result.data.userObj;
                        document.querySelector('#NICK_NAME').innerHTML=userObj.NICK_NAME;
                        document.querySelector('#USER_ID').innerHTML=userObj.USER_ID;
                        document.querySelector('#EMAIL').innerHTML=userObj.EMAIL;
                        document.querySelector('#PHONE').innerHTML=userObj.PHONE;
                        document.querySelector('#JOIN_TYPE').innerHTML=userObj.JOIN_TYPE;
                        document.querySelector('#REGIST_DATE').innerHTML=userObj.REGIST_DATE;
                        document.querySelector('#LAST_LOGIN').innerHTML=userObj.LAST_LOGIN;
                        document.querySelector('#USER_STATUS').innerHTML=userObj.USER_STATUS;
                        document.querySelector('#POINT').value=userObj.POINT;
                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }

    }


    const getUserKakaoAlertLog = () => {
        let userObj =
            {
                IDX		  : "<?php echo $user_idx ?>"
            };

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            axios.post('/api/admin/user/read_user_kakao_alert', data)
                .then((result) => {
                    console.log(result);
                    if (result.data.isSuc) {
                        let inner = '';
                        result.data.list.forEach(item => {
                            inner += '<div>';
                            inner += '<strong>전송일 : '+item.REGIST_DATE+'</strong><br>';
                            inner += '<strong>알림톡 종류 : '+item.NAME+'</strong><br>';
                            inner += item.SEND_CONT;
                            inner += '<hr></div>';
                        });
                        document.querySelector('#popup-content').innerHTML=inner;
                    } else {

                    }
                })
        } catch (err) {
            console.log("Error >>", err);
        }

    }


    const update_point = async () => {

        if (!confirm('정말로 이 작업을 수행하시겠습니까?')) {
            return;
        }

        let userObj =
            {
                IDX : '<?php echo $user_idx?>',
                POINT  : document.querySelector('#POINT').value
            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/admin_update_point', data);

            console.log(result);
            alert(result.data.message);
            if (result.data.isSuc) {

            } else {

            }
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    function showPopup() {
        document.getElementById('popup').style.display = 'block';
        document.getElementById('overlay').style.display = 'block';
    }

    function closePopup() {
        document.getElementById('popup').style.display = 'none';
        document.getElementById('overlay').style.display = 'none';
    }
</script>

<!-- Page Wrapper -->
<div id="wrapper">

    <!-- Sidebar -->
    <?php
    require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/navi.php");
    ?>
    <!-- End of Sidebar -->

    <!-- Content Wrapper -->
    <div id="content-wrapper" class="d-flex flex-column">

        <!-- Main Content -->
        <div id="content">
            <?php
            require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/header.php");
            ?>

            <!-- Begin Page Content -->
            <div class="container-fluid">

                <!-- Page Heading -->
                <h1 class="h3 mb-2 text-gray-800">유저</h1>
                <p class="mb-4">설명
                    <a target="_blank" href="https://www.chartjs.org/docs/latest/">
                        official Chart.js documentation
                    </a>.</p>

                <!-- Content Row -->
                <div class="row">
                    <div class="col-xl-8 col-lg-7">
                        <!-- Area Chart -->
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">유저 정보</h6>
                            </div>
                            <div class="card-body">
                                <p>닉네임 : <span id="NICK_NAME"></span> </p>
                                <p>아이디 : <span id="USER_ID"></span> </p>
                                <p>이메일 : <span id="EMAIL"></span></p>
                                <p>핸드폰 : <span id="PHONE"></span> </p>
                                <p>보유포인트 : <input type="text" id="POINT" value=""> <input type="button" value="수정" onclick="update_point()"></p>
                                <p>가입루트 : <span id="JOIN_TYPE"></span> </p>
                                <p>가입일 : <span id="REGIST_DATE"></span> </p>
                                <p>마지막로그인 : <span id="LAST_LOGIN"></span></p>
                                <p>유저상태 : <span id="USER_STATUS"></span> </p>
                                <p>알림톡 로그 : <button onclick="showPopup()">확인</button></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- /.container-fluid -->
            <div id="overlay" onclick="closePopup()"></div>
            <div id="popup">
                <pre id="popup-content">

                </pre>
            </div>
        </div>
        <!-- End of Main Content -->

        <!-- Footer -->
        <?php
        require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/footer.php");
        ?>
        <!-- End of Footer -->

    </div>
    <!-- End of Content Wrapper -->

</div>

<!-- End of Page Wrapper -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/admin/common/bottom.php");
?>

