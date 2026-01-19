<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
$cs_idx = $_GET['idx'];

$user_id = "";
if (isset($_SESSION['USER_ID'])){
    $user_id = $_SESSION['USER_ID'];
}

if (!isset($cs_idx) || $cs_idx==''){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/app/main';
        </script>
        ";
}
?>
<script>
// 메타태그
document.addEventListener("DOMContentLoaded", () => {
	document.title = "상담사 상담후기 | 사주로";
	document.getElementsByTagName('meta')["description"].content = "상담사 상담 후기 : 생생한 후기를 직접 보고 결정하세요 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로 ";
});
</script>

<style>
    #modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
    }

    #modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #fff;
        padding: 20px;
        border-radius: 5px;
        width: 80%;
        height: 80%;
        overflow: auto;
    }

</style>

<script>
    let page = 0;
    let report_idx = "";
    document.addEventListener('DOMContentLoaded', () => {
        getReviewInfo();
    })

    const showReport = (idx) => {
        // document.querySelector('#modal').style.display = 'block';
		fn_layer(`layer03`, 320);
        let target_cont = document.querySelector('#user_cont_'+idx).innerText;
        document.querySelector('#target_report_cont').innerText = target_cont;

        report_idx = idx;
    }

    const doReport = async() => {
        showLoading();

        let reportObj =
            {
                IDX : report_idx,
                TYPE : document.querySelector('input[name="report_type"]:checked').value,
                CONT : document.querySelector('#report_cont').value
            };

        try {
            let param = JSON.stringify(reportObj);
            let data = new FormData();
            data.append("reportObj", param);
            let result = await axios.post('/api/cs/doReport', data);

            if (result.data.isSuc) {
                fn_layer(`layer04`, 320);
                //location.reload();
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }

    }


    const add_page = () => {
        page++;
        getReviewInfo();
    }

    const getReviewInfo = async () => {
        showLoading();
        let reviewObj =
            {
                IDX : '<?php echo $cs_idx?>',
                PAGE : page
            };
        try {
            let param = JSON.stringify(reviewObj);
            let data = new FormData();
            data.append("reviewObj", param);
            let result = await axios.post('/api/cs/read_review', data);

            if (result.data.isSuc) {

                let cs_info = result.data.list;
                let review_cnt = result.data.review_cnt.CNT;
                let faq_cnt = result.data.faq_cnt.CNT;


                document.querySelector("#review_cnt").innerHTML = review_cnt;
                document.querySelector("#faq_cnt").innerHTML = faq_cnt;
				//document.querySelector('#review_area').innerHTML = "";
                if (cs_info.length > 0) {
                    document.querySelector("#total_cnt").innerHTML = '전체후기(' + review_cnt + '+)';

                    let inner = '';
                    let user_cont = '';
                    let cs_cont = '';
                    //document.querySelector('#CAREER').value = csObj.CAREER.replace(/<br\s*[/]?>/gi, "\n");
                    cs_info.forEach(item => {

                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");
                        inner += '<div class="mypRev">';
                        inner += '   <div class="revQ">';
                        inner += '       <p class="info">';
						inner += '			<strong>' + item.USER_NICK_NAME + '</strong>';
                        inner += '			<span class="right">'
						inner += '				<span>' + item.USER_REGIST_DATE + '</span>';
						inner += '				<button type="button" onclick="showReport(' + item.IDX + ');">신고</button>';
                        inner += '			</span>';
						inner += '		 </p>';
                        inner += '       <p id="user_cont_'+item.IDX+'" class="cont">';
                        inner += user_cont;
                        inner += '       </p>';
                        inner += '   </div>';

                        if (!isNull(item.CS_CONT)) {
                            cs_cont = item.CS_CONT.replace(/<br\s*[/]?>/gi, "\n");
                            inner += '   <div class="revA">';
	                        inner += '       <p class="info">';
							inner += '			<strong>'+ item.CODE +' '+ item.CS_NICK_NAME + '</strong>';
                            inner += '			<span>' + item.CS_REGIST_DATE + '</span>';
							inner += '		 </p>';
                            inner += '       <p id="cs_'+item.IDX+'" class="cont">';
                            inner += cs_cont;
                            inner += '       </p>';
                            inner += '   </div>';
                        }

                        inner += '</div>';
                    });
					document.querySelector('#review_area').insertAdjacentHTML("beforeend", inner);
                } else {
                    document.querySelector("#total_cnt").innerHTML = '전체후기(0)';
                    document.querySelector('#review_area').style.display = "none";
                    document.querySelector('#none_info').style.display = "block";

                }

            } else {
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const showReview = async () => {
        // document.querySelector('#modal').style.display = 'block';
        fn_layer(`revPop`, 320);


        showLoading();

        let reviewObj =
            {
                IDX : '<?php echo $cs_idx?>'
            };

        try {
            let param = JSON.stringify(reviewObj);
            let data = new FormData();
            data.append("reviewObj", param);
            let result = await axios.post('/api/cs/read_review_ars', data);
			let review_info = result.data.list;

            if (result.data.isSuc) {
               // location.reload();


				if(review_info.length > 0) {

					let inner = '';
					review_info.forEach(item => {
						inner += '<tr>';
						inner += '    <td>'+item.yyyy+'.'+item.mm+'.'+item.dd+'</td>';
						inner += '    <td>'+item.NICK_NAME+'</td>';
						inner += '    <td>';
						inner += '        <button type="button" onclick="fn_layer_close(`revPop`); showReviewAdd(\''+item.idx+'\'); ">';
						inner += '            후기 작성';
						inner += '        </button>';
						inner += '    </td>';
						inner += '</tr>';
					});
					document.querySelector('#review_target').innerHTML = inner;

				}else {
					let inner = '';
					inner += '<tr>';
					inner += '    <td colspan="3">작성 가능한 후기가 없습니다.</td>';
					inner += '</tr>';
					document.querySelector('#review_target').innerHTML = inner;
				}




            } else {


            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }

    }


    const showReviewAdd = (idx) => {
        fn_layer(`layer01`, 320);
        let inner = '';
        inner +='<strong class="tit">후기 작성하기</strong>';
        inner +='<div class="popCont">';
        inner +='    <textarea id="mem_cont" title="후기 작성하기" placeholder="후기를 작성해주세요."></textarea>';
        inner +='    <div class="btnArea">';
        inner +='        <button type="button" onclick="addReview('+idx+')" class="btn btnBlack">등록</button>';
        inner +='    </div>';
        inner +='</div>';
        inner +='<a href="javascript:void(0)" onclick="fn_layer_close(`layer01`);">닫기</a>';
        document.querySelector('#review_add_area').innerHTML = inner;
    }


    const addReview = async (idx) => {
        // document.querySelector('#modal').style.display = 'block';
        showLoading();
        let reviewObj =
            {
                CHAT_IDX : idx,
                USER_CONT : document.querySelector('#mem_cont').value,
                IDX : <?php echo $cs_idx?>
            };

        try {
            let param = JSON.stringify(reviewObj);
            let data = new FormData();
            data.append("reviewObj", param);
            let result = await axios.post('/api/cs/add_review', data);

            if (result.data.isSuc) {
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }

        fn_layer_close(`layer01`);
        fn_layer(`layer02`, 320);
    }

</script>


<div id="detailTop">
	<div class="inner">
		<div class="leftArea">
            <button type="button" class="btnBack" onclick="location.href='/'">
				<img src="/app/assets/img/contents/ico-back-btn.png">
				뒤로가기
			</button>
		</div>
		<div class="rightArea">
			<a href="/">홈</a>
		</div>
	</div>
</div>

 <section id="mypageWrap" class="section csDetail inFixedMenu">

	<!-- fixedMenu -->
	<div class="fixedMenu">
		<a href="/app/cs/cs_detail?idx=<?php echo $cs_idx?>">상세정보</a>
		<a class="on" href="/app/cs/cs_review?idx=<?php echo $cs_idx?>">상담후기(<span id="review_cnt"></span>)</a>
		<a href="/app/cs/cs_faq?idx=<?php echo $cs_idx?>">상담문의(<span id="faq_cnt"></span>)</a>
	</div>
	<!--// fixedMenu -->

	<div class="csRevTop">
		<p>실제 상담한 회원만 작성 가능한 상담후기!<img src="/app/assets/img/contents/ico-cs-rev-i.png"></p>
		<span id="none_info" style="display: none;">등록된 후기가 없습니다. <br> 후기를 작성해주세요.</span> <br>
		<input type="button" class="btn bgMainColor writeBtn w100p" value="후기 작성하기" onclick="showReview()">
	</div>

	<div class="tabWrap">
		<div class="tabList">
			<ul class="alFS jcFS">
				<li class="on" style="flex:none; padding:0 20px;">
					<button type="button" id="total_cnt">전체후기(0)</button>
				</li>
			</ul>
		</div>
	</div>

	<div id="reviewList" class="boardList mt30">
		<!-- listBoxWrap -->
		<div class="listBoxWrap ">



			<div id="review_area" class="mypRevWrap">


			</div>

			<!-- bottomBtn -->
			<div class="mt25">
				<button type="button" class="btn btnSmall fN m0a w100p" onclick="add_page()">더보기</button>
			</div>
			<!--// bottomBtn -->

		</div>
		<!-- listBoxWrap -->
	</div>



</section>
<style>
	#review_area {display:block !important;}
</style>


<!-- 후기 작성하기 -->
<div class="layer layer01" id="layer01">
	<div id="review_add_area" class="inBox">

	</div>
</div>
<!--// 후기 작성하기 -->

<!-- 후기 작성하기 -->
<div class="layer revPop" id="revPop">
	<div class="inBox">
		<strong class="tit">후기 작성하기</strong>
		<div class="popCont">
			<div class="colTable">
				<table class="table">
					<thead>
						<tr>
							<th>상담일시</th>
							<th>상담사명</th>
							<th>후기 작성</th>
						</tr>
					</thead>
					<tbody id="review_target">

					</tbody>
				</table>
			</div>
		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('revPop');">닫기</a>
	</div>
</div>
<!--// 후기 작성하기 -->


<!-- 신고하기 -->
<div class="layer layer03" id="layer03">
	<div class="inBox">
		<strong class="tit">신고하기</strong>
		<div class="popCont">

			<div class="comm">
				<strong class="mainColor">리뷰 내용</strong>
				<p id="target_report_cont" class="mt10">

				</p>
				<strong class="mt25">작성자 : </strong>
				<strong class="mt15 mainColor">신고 사유</strong>
				<ul class="mt10">
					<li>
						<div class="radioBox">
							<input id="tarot" class="form-check-input" type="radio" name="report_type" value="1" checked>
							<label class="form-check-label" for="tarot">영리목적/홍보성</label>
						</div>
					</li>
					<li>
						<div class="radioBox">
							<input id="psychic" class="form-check-input" type="radio" name="report_type" value="2">
							<label class="form-check-label" for="psychic">개인정보노출</label>
						</div>
					</li>
					<li>
						<div class="radioBox">
							<input id="palmistry" class="form-check-input" type="radio" name="report_type" value="3">
							<label class="form-check-label" for="palmistry">불법정보</label>
						</div>
					</li>
					<li>
						<div class="radioBox">
							<input id="divination1" class="form-check-input" type="radio" name="report_type" value="4">
							<label class="form-check-label" for="divination1">음란성/선정성</label>
						</div>
					</li>
					<li>
						<div class="radioBox">
							<input id="divination2" class="form-check-input" type="radio" name="report_type" value="5">
							<label class="form-check-label" for="divination2">욕설/인신공격</label>
						</div>
					</li>
					<li>
						<div class="radioBox">
							<input id="divination3" class="form-check-input" type="radio" name="report_type" value="6">
							<label class="form-check-label" for="divination3">기타</label>
						</div>
					</li>
				</ul>
				<strong class="mt30 mainColor">상세내용(선택)</strong>
				<textarea id="report_cont" class="mt10" title="상세내용(선택)" placeholder="상세 내용을 입력해주세요"></textarea>
			</div>

			<!-- btnArea -->
			<div class="btnArea">
				<button type="button" onclick="doReport(); fn_layer_close('layer03');" class="btn btnBlack">등록</button>
			</div>
			<!--// btnArea -->

		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('layer03');">닫기</a>
	</div>
</div>
<!--// 신고하기 -->

<!-- 신고하기 > 등록 -->
<div class="layer layer04" id="layer04">
	<div class="inBox">
		<strong class="tit">신고하기</strong>
		<div class="popCont">
			<div class="icoText">
				<p>신고처리 완료되었습니다.</p>
			</div>
		</div>
		<a href="javascript:void(0)" onclick="fn_layer_close('layer04')">닫기</a>
	</div>
</div>
<!--// 신고하기 > 등록 -->



<!--     <div id="modal" style="display: none;">
        <div id="modal-content">
            <input type="button" value="닫기" onclick="Javascript:document.getElementById('modal').style.display = 'none';">

            <h1>리뷰내용</h1><br>
            <p id="review_cont">

            </p>
            작성자 : <span id="reporter_id"><?php echo $user_id ?></span><br>
            신고사유<br>

            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="1" checked>
                <label class="form-check-label" for="tarot">영리목적/홍보성</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="2">
                <label class="form-check-label" for="psychic">개인정보노출</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="3">
                <label class="form-check-label" for="palmistry">불법정보</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="4">
                <label class="form-check-label" for="divination">음란성/선정성</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="5">
                <label class="form-check-label" for="divination">욕설/인신공격</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="report_type" value="6">
                <label class="form-check-label" for="divination">기타</label>
            </div><br>

            상세내용(선택)
            <textarea id="report_cont" style="width: 500px; height: 200px"></textarea>

            <input type="button" value="등록" onclick="doReport()">
        </div>
    </div>
 -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
