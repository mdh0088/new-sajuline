<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>
<script>
// 메타태그
document.addEventListener("DOMContentLoaded", () => {
	document.title = `회원가입 완료 | 사주로`;
	document.getElementsByTagName('meta')["description"].content = "회원가입 완료: 사주로 회원이 되신 것을 환영합니다.";
});
</script>

<section id="memberWrap" class="section">
	<div id="joinComplete">
		<!-- subTitBox -->
		<div class="subTitBox">
		  <h3>회원가입</h3>
		</div>
		<!--// subTitBox -->

		<!-- completeBox -->
		<div class="completeBox">
			<strong><img src="/app/assets/img/icon/ico-complete.png">가입완료</strong>
			<p>사주로 회원이 되신 것을 환영합니다.</p>
		</div>
		<!--// completeBox -->

		<div class="bottomBtn col mt25">
			<a href="/app/main" class="btn btnL">메인으로 가기</a>
		</div>

	</div>
</section>


<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>

<style>
	footer {display:none !important;}
</style>
