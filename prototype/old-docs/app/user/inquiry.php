<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<section id="csCenterWrap" class="section">

	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>1:1 문의</h3>
	</div>
	<!--// subTitBox -->

	<div class="csFaqTop">
		<p>
			상담문의는 상담 가능시간, 인사등의<br>
			간단한 문의만 가능합니다.
		</p>
		<input type="button" class="btn bgMainColor writeBtn w100p" value="문의하기" onclick="fn_layer('layer09', 320);">
	</div>


	<div id="faq_area" class="mypQueWrap">
		<!-- mypQue -->
		<div class="mypQue">
			<div class="queQ">
				<p class="info">
					<strong>진오<span>22.3.29</span></strong>
					<!--<span class="bgGray" value="답변 완료">답변대기</span>-->
					<span class="bgMainColor" value="답변 완료">답변 완료</span>

				</p>
				<p class="cont">회원탈퇴를 하고 싶습니다.</p>
			</div>
			<div class="queA">
				<p class="info">
					<strong>샤롯데</strong>
					<span>2022.3.29</span>
				</p>
				<p class="cont">처리 완료했습니다.</p>
			</div>
		</div>
		<!--// mypQue -->

		<!-- mypQue -->
		<div class="mypQue">
			<div class="queQ">
				<p class="info">
					<strong>진오<span>22.3.29</span></strong>
					<span class="bgGray" value="답변 완료">답변대기</span>
					<!-- <span class="bgMainColor" value="답변 완료">답변 완료</span> -->
				</p>
				<p class="cont">회원탈퇴를 하고 싶습니다.</p>
			</div>
			<!--<div class="queA">
				<p class="info">
					<strong>샤롯데</strong>
					<span>2022.3.29</span>
				</p>
				<p class="cont">처리 완료했습니다.</p>
			</div>-->
		</div>
		<!--// mypQue -->
	</div>

	<div id="page_area"></div>


</section>

<!-- 상담사 문의하기 -->
<div class="layer layer09" id="layer09">
	<div class="inBox">
		<strong class="tit">문의하기</strong>
		<div class="popCont">
			<div class="comm">
				<strong>문의내용</strong>
				<textarea id="faq_cont_1" class="mt10" title="문의 제목 작성" placeholder="제목을 작성해주세요."></textarea>
				<textarea id="faq_cont_2" class="mt10" title="문의 내용 작성" placeholder="문의 내용을 작성해주세요."></textarea>
			</div>
			<!-- btnArea -->
			<div class="btnArea">
				<button type="button" onclick="doFaq(); fn_layer('layer10', 320); fn_layer_close('layer09');" class="btn btnBlack">등록하기</button>
			</div>
			<!--// btnArea -->
		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('layer09')">닫기</a>
	</div>
</div>
<!--// 상담사 문의하기 -->

<!-- 상담사 문의하기 > 등록 -->
<div class="layer layer10" id="layer10">
	<div class="inBox">
		<strong class="tit">문의하기</strong>
		<div class="popCont">
			<div class="icoText">
				<p>문의등록이 완료되었습니다.</p>
			</div>
		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('layer10')">닫기</a>
	</div>
</div>
<!--// 상담사 문의하기 > 등록 -->


<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
