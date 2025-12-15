<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/app/main';
        </script>
        ";
}

if ($_SESSION['IS_CS']=='Y'){
    echo "
        <script>
            location.href='/app/cs/mypage';
        </script>
        ";
}


?>

<script>

    document.addEventListener('DOMContentLoaded', () => {
        getReviewInfoWithArs();
    })

    const getReviewInfoWithArs = async () => {
        showLoading();
        let reviewObj =

        try {
            let param = JSON.stringify(reviewObj);
            let data = new FormData();
            data.append("reviewObj", param);
            let result = await axios.post('/api/cs/read_review_cs', data);

            console.log(result);
            if (result.data.isSuc) {

            } else {
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

</script>

<section id="csWrap" class="section csHis">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>상담 내역</h3>
	</div>
	<!--// subTitBox -->

    <div class="tabWrap">
        <div class="tabList csHisTabList">
            <ul>
                <li class="on">
                    <button type="button" onclick="tabOpen(event, this, 'his01');">1개월</button>
                </li>
                <li>
                    <button type="button" onclick="tabOpen(event, this, 'his02');">2개월</button>
                </li>
                <li>
                    <button type="button" onclick="tabOpen(event, this, 'his03');">3개월</button>
                </li>
            </ul>
        </div>

        <div class="tabContWrap">
            <div id="his01" class="tabContItem">

                <div class="csHisBoxWrap">

                    <div class="csRevBox">
                        <div class="leftArea">
                            <div class="iBox">
                                <img src="/app/assets/img/dumy/dumy-people.png">
                            </div>
                        </div>
                        <div class="rightArea">
                            <div class="infoBox">
                                <div class="info">
                                    <span>
                                        <em class="cate bg1">타로</em>
                                    </span>
                                    <span>샤롯데</span>
                                    <span>114번</span>
                                </div>
                                <div class="date">
                                    <button type="button" onclick="fn_layer('csDetailPop', 320);">2022.3.29</button>
                                </div>
                            </div>
                            <div class="desc">
                                포인트 전화상담(10분 이하)
                            </div>
							<div class="state state-1">후기 완료</div>
							<div class="state state-2">후기 미완료</div>
                        </div>
                    </div>

                    <div class="csRevBox">
                        <div class="leftArea">
                            <div class="iBox">
                                <img src="/app/assets/img/dumy/dumy-people.png">
                            </div>
                        </div>
                        <div class="rightArea">
                            <div class="infoBox">
                                <div class="info">
                                    <span>
                                        <em class="cate bg1">타로</em>
                                    </span>
                                    <span>샤롯데</span>
                                    <span>114번</span>
                                </div>
                                <div class="date">
                                    <button type="button" onclick="fn_layer('csDetailPop', 320);">2022.3.29</button>
                                </div>
                            </div>
                            <div class="desc">
                                포인트 전화상담(10분 이하)
                            </div>
							<div class="state state-1">후기 완료</div>
							<div class="state state-2">후기 미완료</div>
                        </div>
                    </div>

                </div>

            </div>
            <div id="his02" class="tabContItem">
                3 개월
            </div>
            <div id="his03" class="tabContItem">
                6 개월
            </div>
        </div>

    </div>
</section>

<!-- 상담사 내역 > 상담 상세 내역 -->
<div class="layer csDetailPop" id="csDetailPop">
	<div class="inBox">
		<strong class="tit">상담 상세 내역</strong>
		<div class="csDetailTable">
			<dl>
				<dt>상담일시</dt>
				<dd>2023.02.08</dd>
			</dl>
			<dl>
				<dt>상담유형</dt>
				<dd>타로</dd>
			</dl>
			<dl>
				<dt>상담시간</dt>
				<dd>00:00:15</dd>
			</dl>
			<dl>
				<dt>상담사</dt>
				<dd>샤롯데 14번</dd>
			</dl>
			<dl>
				<dt>사용 포인트</dt>
				<dd>30,000P</dd>
			</dl>
			<dl>
				<dt>상담방법</dt>
				<dd>포인트 상담</dd>
			</dl>
		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('csDetailPop')">닫기</a>
	</div>
</div>
<!--// 상담사 내역 > 상담 상세 내역 -->

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
