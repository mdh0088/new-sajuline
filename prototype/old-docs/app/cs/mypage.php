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

if ($_SESSION['IS_CS']!='Y'){
    echo "
        <script>
            location.href='/';
        </script>
        ";
}


?>

<script>

    document.addEventListener('DOMContentLoaded', () => {
       getCsInfo();
       getNoticeInfo();
       getCsReviewInfo();
       getCsFaqInfo();
       getAdminFaqInfo();
    })

    const getCsInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_csInfo', data);

            console.log(result);
            if (result.data.isSuc) {

                let csObj = result.data.csObj;
                let currentDate = new Date();
                let currentYear = currentDate.getFullYear();
                let currentMonth = currentDate.getMonth() + 1; // JavaScript에서 월은 0부터 시작하므로 1을 더합니다.

                if (csObj.STATUS == 1 || csObj.STATUS== 3) {
                    document.querySelector('input[name="stateSelect"][value="' + csObj.STATUS + '"]').checked = true;
                }
                document.querySelector('#cs_worktime').value = csObj.WORK_TIME.replace(/<br\s*[/]?>/gi, "\n");;
                document.querySelector('#cs_notice').value = csObj.NOTICE.replace(/<br\s*[/]?>/gi, "\n");

                let inner = '';
                inner += '<div class="tbox">';
                inner += `    <strong>${currentYear}-${currentMonth}월 현재 상담시간</strong>`;
                inner += '    <p>'+csObj.total_time_this_month+'</p>';
                inner += '</div>';

                document.querySelector("#point_area").innerHTML=inner;
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const change_status = async () => {
        showLoading();
        let csObj =
            {
                STATUS  : document.querySelector('input[name="stateSelect"]:checked').value
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/update_status', data);

            if (result.data.isSuc) {

            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const update_worktime = async () => {
        showLoading();
        let csObj =
            {
                WORKTIME  : document.querySelector('#cs_worktime').value
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/update_worktime', data);

            console.log(result);
            if (result.data.isSuc) {

            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const update_notice = async () => {
        showLoading();
        let csObj =
            {
                NOTICE  : document.querySelector('#cs_notice').value
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/update_notice', data);

            console.log(result);
            if (result.data.isSuc) {

            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const reply_review = async (idx,review_type) => {


        showLoading();
        let csObj =
            {
                IDX : idx,
                REPLY  : document.querySelector('#reply_'+idx).value,
                REVIEW_TYPE : review_type
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/update_review_reply', data);

            console.log(result);
            if (result.data.isSuc) {
                alert(result.data.message);
                getCsReviewInfo();
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getCsReviewInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_cs_review_info', data);

            console.log(result);
            if (result.data.isSuc) {
                const review_info = result.data.list;
                const review_cnt = review_info.length;

                document.querySelector('#review_cnt').innerHTML = '('+review_cnt+')';


                let inner = '';
                let user_cont = '';
                let cs_cont = '';

                if ( review_cnt > 0 ) {
                    review_info.forEach(item => {
                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner += '<div class="mypRev">';
                        inner += '    <div class="revQ">';
                        inner += '        <p class="info">';
                        inner += '            <strong>' + item.USER_NICK_NAME + '</strong>';
                        inner += '            <span class="right">';
                        inner += '						<span>' + item.USER_REGIST_DATE + '</span>';
                        inner += '						<button type="button" onclick="fn_layer(`layer03`, 320)">신고</button>';
                        inner += '					</span>';
                        inner += '        </p>';
                        inner += '        <p class="cont">';
                        inner += '            ' + user_cont;
                        inner += '        </p>';
                        inner += '    </div>';
                        if (isNull(item.CS_CONT)) {
                            inner += '    <div class="answerArea">';
                            inner += '        <textarea id="reply_' + item.IDX + '"></textarea>';
                            inner += '        <div class="btnArea alC jcC g10">';
                            inner += '            <button type="button" class="btn btnGray">취소</button>';
                            inner += '            <button type="button" class="btn btnMainColor" onclick="reply_review(' + item.IDX + ',\''+item.REVIEW_TYPE+'\');">등록</button>';
                            inner += '        </div>';
                            inner += '    </div>';
                        } else {
                            cs_cont = item.CS_CONT.replace(/<br\s*[/]?>/gi, "\n");
                            inner += '   <div class="revA">';
                            inner += '      <p class="info">';
                            inner += '          <strong>' + item.CS_NICK_NAME + '</strong>';
                            inner += '          <span>' + item.CS_REGIST_DATE + '</span>';
                            inner += '      </p>';
                            inner += '       <p id="cs_' + item.IDX + '">';
                            inner += cs_cont;
                            inner += '       </p>';
                            inner += '   </div>';
                        }
                        inner += '</div>';
                    });
                    document.querySelector("#review_area").innerHTML = inner;
                }
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }



    const reply_faq = async (idx) => {
        showLoading();
        let csObj =
            {
                IDX : idx,
                REPLY  : document.querySelector('#reply_faq_'+idx).value
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/update_faq_reply', data);

            console.log(result);
            if (result.data.isSuc) {
                alert(result.data.message);
                getCsFaqInfo();
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getCsFaqInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_cs_faq_info', data);

            console.log(result);
            if (result.data.isSuc) {
                const faq_info = result.data.list;
                const faq_cnt = faq_info.length;
                document.querySelector('#faq_cnt').innerHTML = '('+faq_cnt+')';


                let inner = '';
                let user_cont = '';
                let cs_cont = '';
                if(faq_cnt > 0) {

                    faq_info.forEach(item => {
                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner += '<div class="mypQue">';
                        inner += '    <div class="queQ">';
                        inner += '        <p class="info">';
                        inner += '            <strong>' + item.USER_NICK_NAME + '<span>' + item.USER_REGIST_DATE + '</span></strong>';
                        if (isNull(item.CS_CONT)) {
                            inner += '            <span class="bgGray" value="답변 완료">답변대기</span>';
                        } else {
                            inner += '            <span class="bgMainColor" value="답변 완료">답변 완료</span>';
                        }
                        inner += '        </p>';
                        inner += '       <p class="cont">' + user_cont + '</p>';
                        inner += '   </div>';

                        if (isNull(item.CS_CONT)) {
                            inner += '<div class="answerArea">';
                            inner += '    <textarea id="reply_faq_' + item.IDX + '"></textarea>';
                            inner += '   <div class="btnArea alC jcC g10">';
                            /*inner += '       <button type="button" class="btn btnGray">취소</button>';*/
                            inner += '       <button type="button" class="btn btnMainColor" onclick="reply_faq(' + item.IDX + ');">등록</button>';
                            inner += '    </div>';
                            inner += ' </div>';
                        } else {
                            cs_cont = item.CS_CONT.replace(/<br\s*[/]?>/gi, "\n");
                            inner += '   <div class="queA">';
                            inner += '       <p class="info">';
                            inner += '            <strong>' + item.CS_NICK_NAME + '</strong>';
                            inner += '           <span>' + item.CS_REGIST_DATE + '</span>';
                            inner += '       </p>';
                            inner += '       <p id="cs_faq_' + item.IDX + '" class="cont">';
                            inner += cs_cont;
                            inner += '      </p>';
                            inner += '   </div>';
                        }
                        inner += '</div>';

                    });
                    document.querySelector("#faq_area").innerHTML = inner;
                }
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const write_admin_faq = async () => {
        showLoading();
        let csObj =
            {
                CONT  : document.querySelector('#faq_cont').value
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/create_admin_faq', data);

            console.log(result);
            if (result.data.isSuc) {
                alert(result.data.message);
                getCsFaqInfo();
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getAdminFaqInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_admin_faq_info', data);

            console.log(result);
            if (result.data.isSuc) {
                const faq_info = result.data.list;
                const faq_cnt = faq_info.length;
                document.querySelector('#admin_cnt').innerHTML = '('+faq_cnt+')';

                let inner = '';
                let admin_cont = '';
                let cs_cont = '';
                if (faq_cnt > 0 ) {


                    faq_info.forEach(item => {
                        cs_cont = item.CS_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner += '<div class="mypQue">';
                        inner += '    <div class="queQ">';
                        inner += '        <p class="info">';
                        inner += '            <strong>' + item.CS_NICK_NAME + '<span>' + item.CS_REGIST_DATE + '</span></strong>';
                        if (isNull(item.ADMIN_CONT)) {
                            inner += '            <span class="bgGray" value="답변 완료">답변대기</span>';
                        } else {
                            inner += '            <span class="bgMainColor" value="답변 완료">답변 완료</span>';
                        }
                        inner += '        </p>';
                        inner += '       <p class="cont">' + cs_cont + '</p>';
                        inner += '   </div>';

                        if (!isNull(item.ADMIN_CONT)) {
                            admin_cont = item.ADMIN_CONT.replace(/<br\s*[/]?>/gi, "\n");
                            inner += '   <div class="queA">';
                            inner += '       <p class="info">';
                            inner += '            <strong>' + item.ADMIN_NICK_NMAE + '</strong>';
                            inner += '           <span>' + item.ADMIN_REGIST_DATE + '</span>';
                            inner += '       </p>';
                            inner += '       <p id="cs_admin_faq_' + item.IDX + '" class="cont">';
                            inner += admin_cont;
                            inner += '      </p>';
                            inner += '   </div>';
                        }
                        inner += '</div>';

                    });

                    document.querySelector("#admin_faq_area").innerHTML = inner;
                }
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const getNoticeInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_notice_info', data);

            console.log(result);
            if (result.data.isSuc) {
                const notice_info = result.data.list;
                const notice_cnt = notice_info.length;

                let inner = '';
                if (notice_cnt > 0 ) {
                    notice_info.forEach(item => {
                        inner+='<li>';
                        inner+='    <a href="/app/cs/notice_view?idx='+item.IDX+'">';
                        inner+='        <strong>'+item.TITLE+'</strong>';
                        inner+='        <p>'+item.REGIST_DATE+'</p>';
                        inner+='    </a>';
                        inner+='</li>';
                    });
                    document.querySelector("#notice_area").innerHTML = inner;
                }
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>



<section id="mypageWrap" class="section">

	<!-- subTitBox -->
	<div class="subTitBox">
	  <h3>상담사 페이지</h3>
	  <a class="absBtn" href="/app/cs/cs_pay">상담료 안내</a>
	</div>
	<!--// subTitBox -->

	<form id="mypCounselor" action="" method="">

		<!-- stateBox -->
		<div class="stateBox">
			<p class="userName">
				<img src="/app/assets/img/contents/ico-rank-<?echo strtolower($_SESSION['GRADE'])?>.png"><?echo $_SESSION['NICK_NAME']?>
			</p>
			<div class="radioWrap">
				<div class="radioBox">
					<input type="radio" id="stateSelect01" name="stateSelect" value="1">
					<label for="stateSelect01">대기</label>
				</div>
				<div class="radioBox">
					<input type="radio" id="stateSelect02" name="stateSelect" value="3">
					<label for="stateSelect02">부재중</label>
				</div>
				<button type="button" class="btn btnBlack btnSmall02 fN" onclick="change_status();">변경저장</button>
			</div>
		</div>
		<!--// stateBox -->


		<!--  notiBox  -->
		<div class="notiBox mt25" id="point_area">

		</div>
		<!--// notiBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>활동시간</strong>
				<button type="button" class="btn btnBlack btnSmall02" onclick="update_worktime();">변경하기</button>
			</div>
			<textarea id="cs_worktime"></textarea>
		</div>
		<!--// msgBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>오늘의 공지</strong>
				<button type="button" class="btn btnBlack btnSmall02" onclick="update_notice();">변경하기</button>
			</div>
			<textarea id="cs_notice"></textarea>
		</div>
		<!--// msgBox -->

		<!-- tabWrap -->
		<div class="tabWrap mt40">

			<!-- tab -->
			<div class="tabList">
				<ul>
					<li class="on">
						<button type="button" onclick="tabOpen(event, this, 'mypTab1');">공지사항</button>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'mypTab2');">
							고객 후기<span id="review_cnt">(999+)</span>
						</button>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'mypTab3');">
							상담 문의<span id="faq_cnt">(999+)</span>
						</button>
					</li>
					<li>
						<button type="button" onclick="tabOpen(event, this, 'mypTab4');">
							관리자문의<span id="admin_cnt">(99)</span>
						</button>
					</li>
				</ul>
			</div>
			<!--// tab -->

			<div class="tabContWrap">

				<!-- 공지사항 -->
				<div class="tabContItem" id="mypTab1">
					<div class="mypCsNotice">
						<ul id="notice_area">
							<!--<li>
								<a href="#">
									<strong>[안내] 공지사항 올립니다. 긴급안내 공지</strong>
									<p>2022. 4. 15</p>
								</a>
							</li>
							<li>
								<a href="#">
									<strong>[안내] 공지사항 올립니다. 긴급안내 공지</strong>
									<p>2022. 4. 15</p>
								</a>
							</li>-->
						</ul>
					</div>
				</div>
				<!--// 공지사항 -->

				<!-- 고객 후기 -->
				<div class="tabContItem" id="mypTab2">
					<div id="review_area" class="mypCsRev mypRevWrap">



					</div>
				</div>
				<!--// 고객 후기 -->

				<!-- 상담 문의 -->
				<div class="tabContItem" id="mypTab3">

					<div id="faq_area" class="mypQueWrap">
						<!-- mypQue -->

						<!--// mypQue -->
					</div>

				</div>
				<!--// 상담 문의 -->

				<!-- 관리자문의 -->
				<div class="tabContItem" id="mypTab4">

					<div class="mypCsInqText">
						<p>
                        선생님의 정보 변경 및 관리자에게 문의사항을 남겨주시면 <br>
                        답변 혹은 연락드리도록 하겠습니다.
						</p>
						<button type="button" class="btn" onclick="fn_layer('layer09', 320);">문의하기</button>
					</div>

					<div id="admin_faq_area" class="mypQueWrap">
						<!-- mypQue
						<div class="mypQue">
							<div class="queQ">
								<p class="info">
									<strong>진오<span>22.3.29</span></strong>
									<span class="bgGray" value="답변 완료">답변대기</span>
									<span class="bgMainColor" value="답변 완료">답변 완료</span>

								</p>
								<p class="cont">상담시간이 어떻게 되나요??</p>
							</div>
							<div class="queA">
								<p class="info">
									<strong>관리자</strong>
									<span>2022.3.29</span>
								</p>
								<p class="cont">
									답이 늦었네요<br>
									죄송합니다~~ 지금 통화 가능해요~~
								</p>
							</div>
						</div>
						// mypQue

						 mypQue
						<div class="mypQue">
							<div class="queQ">
								<p class="info">
									<strong>진오<span>22.3.29</span></strong>
									<span class="bgGray" value="답변 완료">답변대기</span>
									<<span class="bgMainColor" value="답변 완료">답변 완료</span>
								</p>
								<p class="cont">상담시간이 어떻게 되나요??</p>
							</div>

						</div>
						// mypQue -->
					</div>

				</div>
				<!-- 관리자문의 -->
			</div>
			<!--//  tabContWrap -->
		</div>
		<!--// tabWrap -->

	</form>

</section>


<!-- 상담사 문의하기 -->
<div class="layer layer09" id="layer09">
	<div class="inBox">
		<strong class="tit">문의하기</strong>
		<div class="popCont">
			<div class="comm">
				<strong>문의내용</strong>
				<textarea id="faq_cont" class="mt10" title="문의 내용 작성" placeholder="문의 내용을 작성해주세요."></textarea>
			</div>
			<!-- btnArea -->
			<div class="btnArea">
				<button type="button" onclick="fn_layer('layer10', 320); fn_layer_close('layer09'); write_admin_faq();" class="btn btnBlack">등록</button>
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

<style>
	footer {display:none !important;}
</style>
