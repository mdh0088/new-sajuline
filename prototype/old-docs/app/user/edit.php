<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('로그인후 이용부탁드립니다.');
            location.href='/';
        </script>
        ";
}


if ($_SESSION['IS_CS']=='Y'){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/';
        </script>
        ";
}

$user_idx = $_SESSION['IDX'];
?>

<script>

    let edit_type = "";

    const pw_toggleBtn = async (el) => {
        let $target = el.nextElementSibling;
        if (el.classList.contains("on")) {
            el.classList.remove("on");
            $target.classList.remove("on");
            edit_type = false;
        } else {
            edit_type = true;
            el.classList.add("on");
            $target.classList.add("on");
        }
    }

    const edit_user_info = async () => {


        // 비밀번호 수정 체크
        if (edit_type) {
            if(isNull(document.querySelector("#new_passwd").value)){
                alert('비밀번호를 입력해주세요.');
                document.querySelector("#new_passwd").focus();
                return;
            }

            if(isNull(document.querySelector("#new_passwd_chk").value)){
                alert('확인용 비밀번호를 입력해주세요.');
                document.querySelector("#new_passwd_chk").focus();
                return;
            }

            if(document.querySelector("#new_passwd").value != document.querySelector("#new_passwd_chk").value ){
                alert('비밀번호가 일치하지 않습니다.');
                document.querySelector("#new_passwd").focus();
                return;
            }

            if(!isValidPassword(document.querySelector("#new_passwd").value)){
                alert('비밀번호가 8자 이상, 영문 대/소문자, 숫자, 특수 문자 중 적어도 하나씩을 포함하고 있어야 합니다.');
                document.querySelector("#new_passwd").focus();
                return;
            }

        }

        let userObj =
            {
                IDX : <?php echo $user_idx?>
                , PASSWORD  : document.querySelector("#new_passwd").value
                //, NICK_NAME	: document.querySelector("#nick_name").value
            };


        showLoading();

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/update', data);

            console.log(result);
            alert(result.data.message);
            if (result.data.isSuc) {


            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }

    }
</script>


  <section id="memberWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>회원정보 수정</h3>
	</div>
	<!--// subTitBox -->

	<form id="changeUserInfo" action="" method="">
		<!-- infoBoxWrap -->
		<div class="infoBoxWrap">

			<!-- infoBox -->
			<div class="infoBox">
				<p>아이디*</p>
				<div class="inFlex">
					<?php echo $_SESSION['USER_ID']?>
				</div>
			</div>
			<!--// infoBox -->

			<!-- infoBox -->
			<div class="infoBox">
				<p><label for="pwCngBtn">비밀번호*</label></p>
				<button type="button" id="pwCngBtn" class="btn toggleBtn" onclick="pw_toggleBtn(this);">비밀번호 설정</button>
				<div class="toggleItem">

					<!-- infoBox -->
					<div class="infoBox mt20">
						<p><label for="new_passwd">새 비밀번호*</label></p>
						<div class="inFlex">
							<input type="password" id="new_passwd" title="새 비밀번호" placeholder="비밀번호를 입력하세요">
						</div>
					</div>
					<!--// infoBox -->

					<!-- infoBox -->
					<div class="infoBox">
						<p><label for="new_passwd_chk">새 비밀번호 확인*</label></p>
						<div class="inFlex">
							<input type="password" id="new_passwd_chk" title="새 비밀번호 확인" placeholder="비밀번호를 다시 입력하세요">
						</div>
					</div>
					<!--// infoBox -->

				</div>
			</div>
			<!--// infoBox -->

			<!-- infoBox -->
			<div class="infoBox">
				<p><label for="user_name">닉네임</label></p>
				<div class="inFlex">
					<input type="text" title="닉네임" id="nick_name" placeholder="닉네임" value="<?php echo $_SESSION['NICK_NAME']?>" readonly>
				</div>
			</div>
			<!--// infoBox -->

			<!-- infoBox -->
			<div class="infoBox">
				<p><label for="">휴대폰 번호*</label></p>
				<div class="inFlex">

					<?php
                    $phone_number = $_SESSION['PHONE'];
                    $converted_number = substr($phone_number, 0, 3) . "-" . substr($phone_number, 3, 4) . "-" . substr($phone_number, 7, 4);
                    echo $converted_number;
                    ?>
				</div>
			</div>
			<!--// infoBox -->

		</div>
		<!--// infoBoxWrap -->

		<!-- bottomBtn -->
		<div class="bottomBtn mt30">
		  <button type="button" class="btn" onclick="edit_user_info();">회원정보 수정</button>
		</div>
        <div class="btnSmall03 mt20">
		  <button type="button" class="btn delBtn" onclick="location.href='/app/user/delete'" >회원탈퇴</button>
		</div>
		<!--// bottomBtn-->
	</form>


  </section>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '회원정보 수정',
        description:
            '회원정보 수정 : 나의 회원보를 간편하게 수정하기 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/user/edit',
        keyword: ''
    });
</script>
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
