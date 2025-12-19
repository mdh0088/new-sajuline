<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>
<section id="csWrap" class="section csHis">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>이용 안내</h3>
	</div>
	<!--// subTitBox -->

	<div class="tabWrap ">
		<div class="tabList csHisTabList">
			<ul>
				<li class="on">
					<button type="button" onclick="tabOpen(event, this, 'mainTab1');">선불(포인트)상담</button>
				</li>
				<li>
					<button type="button" onclick="tabOpen(event, this, 'mainTab2')">후불(060)상담</button>
				</li>
			</ul>
		</div>
		<div class="tabContWrap">
			<div id="mainTab1" class="tabContItem">

				<div class="chargeGuideBox">
					<div class="gWrap">
						<p class="tit">사주로 포인트상담을 이용하면 좋다!?</p>
						<div class="tbox">
							<p><span>1.</span>내가 사용하고 싶은 만큼만 충전할수 있고 남으면 언제든 사용이 가능합니다. </p>
							<p><span>2.</span>이용요금이 선불로 납부되어 정보이용료(명세서)에 표시가 안됩니다.</p>
							<p><span>3.</span>후불전화(30초당 1,500원)에 비해 파격할인된 가격을 제공합니다.</p>
						</div>
					</div>
				</div>

				<div class="chargeGuideBox">
					<div class="gWrap">
						<p class="tit"><span>1</span>선불(포인트)상담 이용방법</p>
						<div class="tbox">
							<p><span>1.</span>사주로 홈페이지에서 회원가입 후 포인트 충전</p>
							<p><span>2.</span>원하시는 선생님 프로필에서 상담하기 클릭<br>
 ->상담하기 화면에서 (포인트)전화상담하기 버튼을 클릭</p>
							<p><span>3.</span>전화연결 시 선택한 선생님과 바로 연결 됩니다.</p>
						</div>
					</div>

					<div class="gWrap">
						<p class="tit"><span>2</span>선불(포인트)상담 이용방법</p>
						<div class="tbox">
							<p class="p0">포인트 상담번호<02-6209-0808>번호로 직접  건 후,<br>
원하시는 선생님의 고유번호  3자리를 입력하면 선생님 연결</p>
						</div>
					</div>

					<div class="gWrap">
						<p class="tit"><span>3</span>선불(포인트)상담 필수 확인사항</p>
						<div class="tbox">
							<p><span>1.</span>선생님과의 연결이 되기 전까지 포인트는 차감되지 않습니다.</p>
							<p><span>2.</span>30초당 상담사가 설정한 금액만큼 포인트 차감됩니다.</p>
							<p><span>3.</span>전화중에 종료 1분전 까지 충전이 가능하오니
 연장을 원하시는분은 종료 1분전까지 이용하실 수 있습니다.</p>
						</div>
					</div>
				</div>


			</div>
			<div id="mainTab2" class="tabContItem">
				<div class="chargeGuideBox">
					<div class="gWrap">
						<p class="tit"><span>1</span>후불(060)상담 이용방법</p>
						<div class="tbox">
							<p><span>1.</span>사주로 홈페이지에서 원하시는 선생님 프로필에서 상담하기 클릭<br>
 ->상담하기 화면에서 (060)전화상담하기 버튼을 클릭</p>
							<p><span>2.</span>연결 후 원하시는 선생님의 고유번호 3자리를 입력하면 선생님 연결</p>
						</div>
					</div>

					<div class="gWrap">
						<p class="tit"><span>2</span>후불(060)상담 이용방법</p>
						<div class="tbox">
							<p class="p0">060상담번호<060-800-1300>,<060-800-1500>번호로 직접  건 후,
원하시는 선생님의 고유번호  3자리를 입력하면 선생님 연결</p>
						</div>
					</div>

					<div class="gWrap">
						<p class="tit"><span>3</span>후불전화 필수 확인사항</p>
						<div class="tbox">
							<p><span>1.</span>전화 후 첫 연결중인 40초간은 요금이 부과되지 않습니다.</p>
							<p><span>2.</span>40초 이후 부터 상담사가 설정한 30초당 금액(VAT별도)의 이용료가 부과됩니다.</p>
							<p><span>3.</span>이용료는 다음달 이용요금명세서에 합산되어 청구됩니다.</p>
							<p class="bd"><span>※</span>포인트상담을 이용하실 경우 060상담보다 저렴한 요금으로 이용이 가능합니다.</p>
						</div>
					</div>

				</div>


			</div>
		</div>
	</div>



</section>


<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
