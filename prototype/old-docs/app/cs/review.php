<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<script>
    let page = 0;
    let last_page = 0;
    document.addEventListener('DOMContentLoaded', () => {
        getTotalReview(0);
    })

    const page_move = (page) => {

        getTotalReview(page);

    }

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

    const getTotalReview = async (page) => {
        let searchObj =
            {
                PAGE : page
            };
        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            let result = await axios.post('/api/cs/read_total_review', data);
            console.log(result);
            let inner = '';
            let user_cont = '';
            if (result.data.isSuc) {
                last_page = result.data.last_page;

                let review_list = result.data.list;
                if (review_list.length > 0 ){
                    review_list.forEach((item, index) => {

                        const chat_time = item.CHAT_TIME;
                        const [hours, minutes, seconds] = chat_time.split(':').map(Number);
                        const totalMinutes = hours * 60 + minutes + seconds / 60;

                        let str = "";
                        if (totalMinutes < 10) {
                            str = '10분 이하';
                        } else if(totalMinutes >= 10 && totalMinutes<=30){
                            str = '10분 ~ 30분';
                        } else if(totalMinutes >= 30 && totalMinutes<=60){
                            str = '30분 ~ 60분';
                        } else if(totalMinutes >= 60){
                            str = '60분 이상';
                        }

						if (item.TYPE == 1) {type="타로"}
						if (item.TYPE == 2) {type="신점"}
						// if (item.TYPE == 3) {type="역학"}
						if (item.TYPE == 4) {type="사주"}

                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner +='   <div class="csRevBox">';
                        inner +='       <div class="leftArea">';

                        inner +='           <div class="iBox" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.CS_IDX+'\' ">';
                        inner +='               <img src="/app/assets/upload/cs/'+item.IMG+'">';
                        inner +='           </div>';

                        inner +='           <div class="info" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.CS_IDX+'\' ">';
                        inner +='               <span>'+item.CS_NICK_NAME+'</span>';
                        inner +='               <span>'+item.CODE+'번</span>';
                        inner +='           </div>';
                        inner +='       </div>';
                        inner +='       <div class="rightArea">';
                        inner +='           <div class="owner">';
                        inner +='               <p>'+item.USER_NICK_NAME+'</p>';
                        inner +='               <p>';
                        inner +='                   <span>'+item.USER_REGIST_DATE+'</span>';
                        inner +='                   <button type="button" onclick="showReport(' + item.IDX + ');">신고</button>';
                        inner +='               </p>';
                        inner +='           </div>';
						inner +='           <div class="timeText fl jcFE">';
						inner +=str;
                        inner +='           </div>';
                        inner +='           <div class="tbox">';
                        inner += '              <pre id="user_cont_'+item.IDX+'" class="cont">';
                        inner +=                    user_cont;
                        inner += '              </pre>';
                        inner +='           </div>';
                        inner +='       </div>';
                        inner +='   </div>';
                    });
                }
            } else {

            }
            //document.querySelector('#slide_area').insertAdjacentHTML("beforebegin", inner);
            document.querySelector('#cs_area').innerHTML=inner;


            let totalPages = Math.ceil(last_page / 5);
            let currentPageGroup = Math.ceil((page + 1) / 5);
            let startPage = (currentPageGroup - 1) * 5 + 1;
            let endPage = Math.min(startPage + 4, totalPages);


            inner = '';
            inner += '<a id="page_prev" onclick="page_move(' + ((currentPageGroup - 2) * 5) + ')"> < </a>';

            for (let i = startPage; i <= endPage; i++) {
                if (i === page + 1) {
                    inner += '<a id="page" onclick="page_move(' + (i - 1) + ')" class="current">' + i + '</a>';
                } else {
                    inner += '<a id="page" onclick="page_move(' + (i - 1) + ')">' + i + '</a>';
                }
            }

            inner += '<a id="page_next" onclick="page_move(' + (endPage) + ')"> > </a>';

            document.querySelector('#page_area').innerHTML = "";
            document.querySelector('#page_area').insertAdjacentHTML("afterbegin", inner);

            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>

<section id="csWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>상담 후기</h3>
	</div>
	<!--// subTitBox -->

	<!-- tabWrap -->
	<div class="tabWrap">
		<div class="tabList">
			<ul class="alFS">
				<li class="on" style="flex:none; padding:0 20px;">
					<button type="button">전체후기</button>
				</li>
			</ul>
		</div>
		<div id="cs_area" class="tabContWrap">
			<div id="cs_area" class="tabContItem">


			</div>
		</div>
        <div id="page_area"></div>
	</div>
	<!--// tabWrap -->
</section>
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

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '베스트 후기',
        description:
            '베스트후기 : 내담자의 생생한 후기를 직접 보고 결정하세요 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/cs/review',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
