<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

$amt = $_GET['amt'];
$charge_type = $_GET['charge_type'];
?>

<section id="mypageWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>포인트 충전</h3>
	</div>
	<!--// subTitBox -->


	<!-- completeBox -->
	<div class="completeBox">
        <?php
        if($charge_type == 'card'){
        ?>
		<strong><img src="/app/assets/img/icon/ico-complete.png">충전 완료</strong>
		<p>결제하신 <?php echo number_format($amt) ?>P 충전이 완료되었습니다.</p>

        <?php
        }else {
        ?>

		<!-- 무통장 -->

		<p>결제하신 <?php echo number_format($amt) ?>원 무통장 입금<br>접수가 완료 되었습니다.</p>
		<em class="infoT">
			※ 무통장입금(가상계좌)로 결제하신 경우, 결제일로 부터 7일이내에 <br>
			입금되어야 포인트 충전이 이뤄집니다.<br>
			기간 내에 입금되지 않을 경우 자동 취소 될 수 있습니다.
		</em>

		<!--// 무통장 -->
		<?php
        }
         ?>
	</div>
	<!--// completeBox -->

	<div class="bottomBtn col mt25">
		<a href="/app/charge/point" class="btn btnL mgMainColor">확인</a>
	</div>
</section>

<!-- 전환페이지 설정 -->
<!-- NAVER SCRIPT START -->
<script type="text/javascript" src="//wcs.naver.net/wcslog.js"></script>
<script type="text/javascript">
var _nasa={};
_nasa["cnv"] = wcs.cnv("1","<?php echo number_format($amt) ?>");
</script>
<!-- NAVER SCRIPT END -->

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
