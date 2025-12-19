<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
$cs_idx = $_GET['idx'];
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
    let page = 0;
    let last_page = 0;
    document.addEventListener('DOMContentLoaded', () => {
        getFaqInfo();
    })

    const page_move = (type) => {

        if (type=='prev' && page <= 0 ){
            alert('첫 페이지입니다.');
            return;
        }

        if (type=='next' && (page+1) == last_page) {
            alert('마지막 페이지입니다.');
            return;
        }

        if (type == 'prev') {
            page--;
        }

        if (type == 'next') {
            page++;
        }

        getFaqInfo();

    }

    const showFaq = () => {
        // document.querySelector('#modal').style.display = 'block';
		fn_layer('layer09', 320);
    }


    const getFaqInfo = async () => {
        showLoading();
        let faqObj =
            {
                IDX : <?php echo $cs_idx?>,
                PAGE : page
            };
        try {
            let param = JSON.stringify(faqObj);
            let data = new FormData();
            data.append("faqObj", param);
            let result = await axios.post('/api/cs/read_faq', data);

            console.log(result);
            if (result.data.isSuc) {

                let inner = '';
                let cs_info = result.data.list;
                let review_cnt = result.data.review_cnt.CNT;
                let faq_cnt = result.data.faq_cnt.CNT;
                last_page = result.data.last_page;

                document.querySelector("#review_cnt").innerHTML = review_cnt;
                document.querySelector("#faq_cnt").innerHTML = faq_cnt;


                document.querySelector('#faq_area').innerHTML = "";
                if (cs_info.length > 0) {
                    cs_info.forEach(item => {
                        inner += '<div class="mypQue">';
                        inner += '  <div class="queQ">';
                        inner += '      <p class="info">';
						inner += '			<strong>'+item.USER_NICK_NAME+'<span>'+item.USER_REGIST_DATE+'</span>'+'</strong>';
                        if (item.IS_CHK == 'N') {
                            inner += '      <span class="bgMainColor" value="답변 완료">답변 완료</span>';
                        }
						inner += '      </p>';
                        inner += '      <p class="cont secret">비밀글입니다.</p>';
                        inner += '  </div>';

                        if (item.IS_CHK == 'N') {
                            inner += '  <div class="queA">';
                            inner += '      <p class="info">';
                            inner += '			<strong>'+item.CODE+' '+item.CS_NICK_NAME+'</strong>';
                            inner += '			<span>'+item.CS_REGIST_DATE+'</span>';
                            inner += '		</p>';
                            inner += '      <p class="cont secret">비밀글입니다.</p>';
                            inner += '  </div>';
                        }
                        inner += '</div>';
                    });

                    document.querySelector('#faq_area').insertAdjacentHTML("afterbegin", inner);

                    inner = '';
                    inner += '<a id="page_prev" onclick="page_move(\'prev\')"> < </a>';
                    inner += '<a id="page" onclick="page_move(\'no\')"> '+'<b>'+ (page+1)+'</b>'+'<em>'+'/'+'</em>'+'<span>'+last_page+'</span>'+' </a>';
                    inner += '<a id="page_next" onclick="page_move(\'next\')"> > </a>';

                    document.querySelector('#page_area').innerHTML = "";
                    document.querySelector('#page_area').insertAdjacentHTML("afterbegin", inner);
                }

                hideLoading();


            } else {
            }

        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const doFaq = async () => {
        showLoading();

        let faq_cont =  document.querySelector('#faq_cont').value;
        if (isNull(faq_cont)){
            alert('문의 내용을 작성해주세요.');
            return;
        }

        let faqObj =
            {
                IDX  : <?php echo $cs_idx?>,
                CONT : faq_cont
            };

        try {
            let param = JSON.stringify(faqObj);
            let data = new FormData();
            data.append("faqObj", param);
            let result = await axios.post('/api/cs/doFaq', data);

            console.log(result);
            //alert(result.data.message);
            if (result.data.isSuc) {
                fn_layer('layer10', 320);
                getFaqInfo();
                //location.reload();
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

window.addEventListener('load', function() {
	document.title = `상담사 상담문의 | 사주로`;
	document.getElementsByTagName('meta')["description"].content = "상담사 상담문의 : 국내 최고의 소문난 상담사 문의 페이지입니다. No.1 전화 사주/타로상담 서비스 플랫폼 사주로";
});
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
		<a href="/app/cs/cs_review?idx=<?php echo $cs_idx?>">상담후기(<span id="review_cnt"></span>)</a>
		<a class="on" href="/app/cs/cs_faq?idx=<?php echo $cs_idx?>">상담문의(<span id="faq_cnt"></span>)</a>
	</div>
	<!--// fixedMenu -->

	<div class="csFaqTop">
		<p>
			상담문의는 상담 가능시간, 인사등의<br>
			간단한 문의만 가능합니다.
		</p>
		<input type="button" class="btn bgMainColor writeBtn w100p" value="문의하기" onclick="showFaq();">
	</div>

	<div id="faq_area" class="mypQueWrap">
		<!-- mypQue -->

		<!--// mypQue -->
	</div>

	<div id="page_area"></div>


</section>

<style>
	#faq_area {display:block !important;}
</style>

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
				<button type="button" onclick="doFaq();  fn_layer_close('layer09');" class="btn btnBlack">등록</button>
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



<!--
<div>
   <div id="faq_area">
        <div>
            <div>
                <span>진오</span>
                <span>22.4.15</span>
                <input type="button" value="답변 완료"><br>
                <span>비밀글입니다.</span>
            </div>

            <div>
                <span>88</span>
                <span>샤롭데</span>
                <span>2022.3.29</span><br>
                <span>비밀글입니다.</span>
            </div>
        </div>
    </div>

    <div id="page_area">

    </div>


    <div id="modal" style="display: none;">
        <div id="modal-content">
            <input type="button" value="닫기" onclick="Javascript:document.getElementById('modal').style.display = 'none';">
            <h1>문의하기</h1><br>
            <textarea id="faq_cont" style="width: 500px; height: 200px" placeholder="문의 내용을 작성해주세요."></textarea>

            <input type="button" value="등록" onclick="doFaq()">
        </div>
    </div>
</div>
 -->
<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
