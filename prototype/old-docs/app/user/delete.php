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

$join_type = $_SESSION['JOIN_TYPE'];
?>

<script>
    const join_type = '<?php echo $join_type ?>';
    const delete_user = async () => {

        let pw = "";
        if (!confirm('정말로 이 작업을 수행하시겠습니까? \n 탈퇴시 150일 이후 재가입이 가능합니다.')) {
            return;
        }

        if (join_type == 'common' ){
            pw = document.querySelector("#pw").value;
            if(isNull(document.querySelector("#pw").value) ){
                alert('비밀번호를 입력해주세요.');
                document.querySelector("#pw").focus();
                return;
            }

            if(isNull(document.querySelector("#chk_pw").value)){
                alert('확인용 비밀번호를 입력해주세요.');
                document.querySelector("#chk_pw").focus();
                return;
            }

            if(document.querySelector("#pw").value != document.querySelector("#chk_pw").value  ){
                alert('비밀번호가 일치하지 않습니다.');
                document.querySelector("#pw").focus();
                return;
            }
        }

        let userObj =
            {
                PASSWORD : pw
            };


        showLoading();

        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/delete', data);

            console.log(result);
            alert(result.data.message);
            if (result.data.isSuc) {
                location.href='/';
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
		<h3>화원 탈퇴</h3>
	</div>
	<!--// subTitBox -->

	<form id="deleteUserForm" action="" method="">
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
            <?php
            if ($join_type == 'common') {
            ?>
                <div class="infoBox mt20">
                    <p><label for="">비밀번호*</label></p>
                    <div class="inFlex">
                        <input type="password" id="pw" title="비밀번호" placeholder="비밀번호를 입력하세요">
                    </div>
                </div>
                <!--// infoBox -->

                <!-- infoBox -->
                <div class="infoBox">
                    <p><label for="">비밀번호 확인*</label></p>
                    <div class="inFlex">
                        <input type="password" id="chk_pw" title="비밀번호 확인" placeholder="비밀번호 확인">
                    </div>
                </div>
            <?
            }
            ?>

			<!--// infoBox -->

		</div>
		<!--// infoBoxWrap -->

		<div class="tbox mt25">
			<p>회원탈퇴 하시면 남아있는 포인트가 소멸됩니다.</p>
		</div>

		<!-- bottomBtn -->
		<div class="bottomBtn mt30">
		  <button type="button" class="btn" onclick="delete_user()">회원 탈퇴</button>
		</div>
		<!--// bottomBtn-->
	</form>


  </section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
