<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>SB Admin 2 - Login</title>

    <!-- Custom fonts for this template-->
    <link href="vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link
        href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i"
        rel="stylesheet">

    <!-- Custom styles for this template-->
    <link href="css/sb-admin-2.min.css" rel="stylesheet">

    <script src="/app/assets/js/config.js"></script>
    <script src="/app/assets/js/social.js"></script>
    <script src="/app/assets/js/function.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.4.10/dist/sweetalert2.min.js"></script>

</head>

<?php
session_start();
if (isset($_SESSION['IDX'])){
    echo
    "
    <script>
        location.href='/app/admin/main';
    </script>
    ";
}
?>


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

        let usrObj =
            {
                USER_ID		: document.querySelector("#login_id").value
                , PASSWORD  : document.querySelector("#login_pw").value
            };

        if (usrObj.USER_ID.length < 1 || usrObj.PASSWORD.length < 1){
            alert('로그인 정보를 입력해주세요.');
            return;
        }

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
                        location.href='/app/admin/main';
                    }
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

<body class="bg-gradient-primary">

    <div class="container">

        <!-- Outer Row -->
        <div class="row justify-content-center">

            <div class="col-xl-10 col-lg-12 col-md-9">

                <div class="card o-hidden border-0 shadow-lg my-5">
                    <div class="card-body p-0">
                        <!-- Nested Row within Card Body -->
                        <div class="row">
                            <div class="col-lg-6 d-none d-lg-block bg-login-image"></div>
                            <div class="col-lg-6">
                                <div class="p-5">
                                    <div class="text-center">
                                        <h1 class="h4 text-gray-900 mb-4">Sajuro</h1>
                                    </div>
                                    <form class="user">
                                        <div class="form-group">
                                            <input type="email" class="form-control form-control-user"
                                                id="login_id" aria-describedby="emailHelp"
                                                placeholder="Enter User ID...">
                                        </div>
                                        <div class="form-group">
                                            <input type="password" class="form-control form-control-user"
                                                id="login_pw" placeholder="Password">
                                        </div>
                                        <div class="form-group">
                                            <div class="custom-control custom-checkbox small">
                                                <input type="checkbox" class="custom-control-input" id="save-id" onclick="saveID();">
                                                <label class="custom-control-label" for="save-id">Save User ID</label>
                                            </div>
                                        </div>
                                        <a class="btn btn-primary btn-user btn-block" onclick="doLogin();">
                                            Login
                                        </a>
                                        <!--
                                        <hr>
                                        <a class="btn btn-google btn-user btn-block" onclick="sns_login('kakao')">
                                            Login with Kakao
                                        </a>
                                        <a class="btn btn-facebook btn-user btn-block" onclick="sns_login('naver')">
                                           Login with Naver
                                        </a>
                                        -->
                                    </form>
                                    <hr>

                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>

    </div>

    <!-- Bootstrap core JavaScript-->
    <script src="vendor/jquery/jquery.min.js"></script>
    <script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

    <!-- Core plugin JavaScript-->
    <script src="vendor/jquery-easing/jquery.easing.min.js"></script>

    <!-- Custom scripts for all pages-->
    <script src="js/sb-admin-2.min.js"></script>

</body>

</html>
