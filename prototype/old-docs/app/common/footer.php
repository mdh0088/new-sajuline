
                <!-- 알림 팝업 -->
                <div class="layer" id="alarmPop">

                </div>

                <!-- 알림 팝업2 -->
                <div class="layer" id="alarmCheckPop">

                </div>

            <div class="layer csApplication" id="csApplicationPop">

            </div>


			</div>
			<!--// contents -->

			<footer id="footer">
				<button type="button" class="footerInfoBtn on" onclick="footerInfoToggle(this);"></button>

                <!-- 이용약관 팝업 창 -->
				<div class="inner">

					<ul class="foLink">
						<li><a href="/app/info/provision">이용약관</a></li>
						<li><a href="/app/info/privacy">개인정보처리방침</a></li>
						<li><a href="/app/cscenter/notice">고객센터</a></li>
						<li><a href="/app/recruit/apply">상담사 신청</a></li>
					</ul>

					<div class="foNotice footerInfo on">
						피플라인 통신판매중개시스템의 제공자로서 통신판매의<br>
						당사자가 아닙니다. 상품의 판매, 상담 내용을 포함하여 거래에 대한 <br>
						책임은 각 판매자(상담사)에게 있으며, 또한 피플라인 본 플랫폼 <br>
						외부에서 이루어진 상담 등으로 인하여 발생한 문제에 대해서도 <br>
						마찬가지로 책임을 지지 않습니다.<br>
						당 사이트의 모든 저작물의 저작권은 피플라인 있으며, <br>
						무단 복제나 도용은 금지되어 있습니다. <br>
					</div>

					<ul class="foInfo footerInfo on">
						<li><span>상호명</span>피플라인</li>
						<li><span>주소</span>서울시 광진구 광나루로 486</li>
						<li><span>사업자등록번호</span>647-34-01142</li>
						<li><span>대표</span>김진형</li>
						<li><span>통신판매번호</span>제2023-서울광진-0178호</li>
						<li><span>고객센터</span>02-6212-0465</li>
						<li><span>이메일</span>help@sajutarot.com</li>
					</ul>

<!-- 						<div class="copy">COPYRIGHT© UNSEKOREA ALL RIGHTS RESERVED.</div> -->

				</div>
			</footer>

			<!-- dockBar -->
			<div id="dockBar">
				<div class="inner">

					<!-- 상담사클릭>상세 히든 -->
					<ul>
						<li><a href="/"><img src="/app/assets/img/layout/ico-dock01.png">홈</a></li>
						<li><a href="/app/search/list"><img src="/app/assets/img/layout/ico-dock02.png">검색</a></li>
						<li><a href="/app/cs/quick"><img src="/app/assets/img/layout/ico-dock03.png">빠른 상담</a></li>
						<li><a href="/app/charge/point"><img src="/app/assets/img/layout/ico-dock04.png">충전</a></li>
						<li>
							<?php
								if (!isset($_SESSION['IDX'])) {
                                    echo '<a href="/app/user/login"><img src="/app/assets/img/layout/ico-dock05.png">로그인</a>';
								} else {
                                    if ($_SESSION['IS_CS'] == 'N'){
                                        echo '<a href="/app/user/mypage"><img src="/app/assets/img/layout/ico-dock05.png">마이페이지</a>';
                                    } else {
                                        echo '<a href="/app/cs/mypage"><img src="/app/assets/img/layout/ico-dock05.png">마이페이지</a>';
                                    }
								}
							?>
						</li>
                    </ul>
					<!--// 상담사클릭>상세 히든 -->

				</div>
			</div>
			<!--// dockBar -->

		</main>
		<!--// main -->
	</div>
	<!--// wrap -->
</body>
        <script type="text/javascript">
        (function(w, d, a){
            w.__beusablerumclient__ = {
                load : function(src){
                    var b = d.createElement("script");
                    b.src = src; b.async=true; b.type = "text/javascript";
                    d.getElementsByTagName("head")[0].appendChild(b);
                }
            };w.__beusablerumclient__.load(a + "?url=" + encodeURIComponent(d.URL));
        })(window, document, "//rum.beusable.net/load/b230322e165909u978");
        </script>

<!-- NAVER SCRIPT START -->
<script type="text/javascript" src="//wcs.naver.net/wcslog.js"></script>
<script type="text/javascript">
if(!wcs_add) var wcs_add = {};
wcs_add["wa"] = "s_16e3dd7704b3";
if (!_nasa) var _nasa={};
if (window.wcs ) {
    wcs.inflow("sajutarot.com");
    wcs_do(_nasa);
}
</script>
<!-- NAVER SCRIPT END -->

</html>
