<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>



  <section id="memberWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>화원정보 수정</h3>
		<p>
			회원님의 정보를 안전하게 보호하기 위해<br>
			계정 비밀번호를 입력해주세요.
		</p>
	</div>
	<!--// subTitBox -->

	<form id="findPwForm" action="" method="">
		<div class="infoBoxWrap">


			<!-- infoBox -->
			<div class="infoBox">
				<p><label class="common_area" for="pw">비밀번호*</label></p>
				<div class="inFlex">
					<input type="password" id="pw" name="pw" title="비밀번호 입력" placeholder="비밀번호를 입력해주세요.">
				</div>
			</div>
			<!--// infoBox -->

			<!-- bottomBtn -->
			<div class="bottomBtn mt30">
			  <button type="button" class="btn">확인</button>
			</div>
			<!--// bottomBtn-->

		</div>
	</form>

  </section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>


<style>
	footer {display:none !important;}
</style>
