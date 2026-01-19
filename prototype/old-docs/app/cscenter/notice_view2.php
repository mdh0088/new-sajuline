<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<section id="csCenterWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>공지사항</h3>
	</div>
	<!--// subTitBox -->

	<div class="noticeView">
		<div class="info">
			<strong>[안내] 오픈이벤트 2</strong>
			<p>2023. 3. 22</p>
		</div>
		<div class="tbox">
            <img src="/app/assets/img/contents/img-main-banner02.png" width="360">
		</div>
		<div class="btnArea">
			<button type="button" class="prevBtn" onclick="javascript:location.href='/app/cscenter/notice_view'">이전</button>
			<button type="button" class="backBtn" onclick="javascript:location.href='/app/cscenter/notice'">목록</button>
			<button type="button" class="nextBtn end" onclick="javascript:location.href='/app/cscenter/notice_view3'">다음</button> <!-- 마지막글에 class="end" 추가 -->
		</div>
	</div>

</section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
