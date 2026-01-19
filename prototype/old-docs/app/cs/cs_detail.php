<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
$cs_idx = $_GET['idx'];
if (!isset($cs_idx) || $cs_idx==''){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/';
        </script>
        ";
}
?>
<script src="/app/assets/js/setMeta.js"></script>
<script>
    const metaInfo =
        {
            nick_name: '',
            cs_idx: '<?php echo $cs_idx?>'
        };

    document.addEventListener('DOMContentLoaded',async () => {
        await getCsInfo();

        setMeta({
            title: metaInfo.nick_name+' 사주로 타로, 운세온라인플랫폼',
            description:
                '상담사 : 국내 최고의 소문난 상담사들만 선별하였습니다. No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
            url: 'https://sajutarot.com/app/cs/cs_detail?idx='+metaInfo.cs_idx,
            keyword: ''
        });

        //getBookMarkInfo();
    })

    const getBookMarkInfo = async () => {
        let csObj =
            {
                IDX : <?php echo $cs_idx?>
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_book_info', data);

            console.log(result);
            if (result.data.isSuc) {
                document.querySelector('#book_mark').classList.add('on');
            } else {
                document.querySelector('#book_mark').classList.remove('on');
            }
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const doBookMark = async () => {
        showLoading();
        let csObj =
            {
                IDX : <?php echo $cs_idx?>
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/doBookMark', data);

            alert(result.data.message);
            console.log(result);
            getBookMarkInfo();
            if (result.data.isSuc) {


            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getCsInfo = async () => {
        showLoading();
        let csObj =
            {
                IDX : <?php echo $cs_idx?>
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_detail', data);

            if (result.data.isSuc) {
                let type = "";
                let cs_info = result.data.list;

                if (isNull(cs_info.IDX)){
                    alert('잘몬된 접근입니다.');
                    location.href='/';
                }

                let review_cnt = cs_info.review_cnt.CNT;
                let faq_cnt = cs_info.faq_cnt.CNT;

                // 메타 정보 세팅
                metaInfo.nick_name = cs_info.NICK_NAME;

                if (cs_info.TYPE == 1) {type="타로"}
                if (cs_info.TYPE == 3) {type="역학";}
                if (cs_info.TYPE == 2) {type="신점";
					document.querySelector("#iBox").classList.add("bg5");
					document.querySelector("#TYPE").classList.add("bg5");
				}
                if (cs_info.TYPE == 4) {
					type="사주";
					document.querySelector("#iBox").classList.add("bg2");
					document.querySelector("#TYPE").classList.add("bg2");
				}


                document.querySelector("#TYPE").innerHTML = type;
                document.querySelector("#review_cnt").innerHTML = review_cnt;
                document.querySelector("#faq_cnt").innerHTML = faq_cnt;

                document.querySelector('#IMG').src = '/app/assets/upload/cs/'+cs_info.IMG
                document.querySelector("#GRADE").src = '/app/assets/img/contents/ico-rank-'+cs_info.GRADE.toLowerCase()+'.png';
                document.querySelector("#NICK_NAME").innerHTML = cs_info.NICK_NAME;
                document.querySelector("#CODE").innerHTML = cs_info.CODE+'번';



                document.querySelector("#NOTICE").innerHTML = '<pre>'+cs_info.NOTICE.replace(/<br\s*[/]?>/gi, "\n")+'</pre>';
                document.querySelector("#GREETING").innerHTML = '<pre>'+cs_info.GREETING.replace(/<br\s*[/]?>/gi, "\n")+'</pre>';
                document.querySelector("#CAREER").innerHTML = '<pre>'+cs_info.CAREER.replace(/<br\s*[/]?>/gi, "\n")+'</pre>';
                document.querySelector("#WORK_TIME").innerHTML = '<pre>'+cs_info.WORK_TIME.replace(/<br\s*[/]?>/gi, "\n")+'</pre>';

                const cs_keyword = cs_info.CS_KEYWORD.split(',');
                let inner = '';
                for (const keyword of cs_keyword) {
                    inner +='<span>#'+keyword+'</span>';
                }
                document.querySelector('#CS_KEYWORD').insertAdjacentHTML("beforeend", inner);


                inner  ='';

                inner += ' <button type="button" id="book_mark" class="favBtn fN" onclick="doBookMark('+cs_info.IDX+'); favToggle(this)" >';
                inner += ' 즐겨찾기';
                inner += ' </button>';

                if (cs_info.STATUS == 1){
                    inner += '                <button type="button" class="csBtn play" onclick="showCallPop('+cs_info.IDX+')">';
                    inner += '                    상담하기';
                    inner += '                </button>';
                } else if(cs_info.STATUS == 2){
                    inner += '                <button type="button" class="csBtn ing" onclick="showAlarm(\''+cs_info.IDX+'\',\''+type+'\',\''+cs_info.NICK_NAME+'\',\''+cs_info.CODE+'\',\''+cs_info.STATUS+'\',\''+cs_info.IMG+'\')">';
                    //inner += '                <button type="button" class="csBtn ing" onclick="Javascript:alert(`현재 상담사는 상담중입니다.`);">';
                    inner += '                    상담중 <span>(접속 알림 설정)</span>';
                    inner += '                </button>';
                } else {
                    inner += '                <button type="button" class="csBtn miss" onclick="showAlarm(\''+cs_info.IDX+'\',\''+type+'\',\''+cs_info.NICK_NAME+'\',\''+cs_info.CODE+'\',\''+cs_info.STATUS+'\',\''+cs_info.IMG+'\')">';
                    inner += '                    부재중 <span>(접속 알림 설정)</span>';
                    inner += '                </button>';
                }
                document.querySelector('#btn_area').innerHTML=inner;

                getBookMarkInfo();
                hideLoading();
            } else {
                alert(result.data.message);
                location.href='/';
            }

        } catch (err) {
            console.log("Error >>", err);
        }



    }

</script>

<div id="detailTop">
	<div class="inner">
		<div class="leftArea">
			<!--<button type="button" class="btnBack" onclick="pageBack();">-->
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
			<a class="on" href="/app/cs/cs_detail?idx=<?php echo $cs_idx?>">상세정보</a>
			<a href="/app/cs/cs_review?idx=<?php echo $cs_idx?>">상담후기(<span id="review_cnt"></span>)</a>
			<a href="/app/cs/cs_faq?idx=<?php echo $cs_idx?>">상담문의(<span id="faq_cnt"></span>)</a>
		</div>
		<!--// fixedMenu -->

		<div class="csBox type1">
			<div id="iBox" class="ibox">
				<img id="IMG">
			</div>
			<div class="tagBox">
				<span ID="TYPE" class="cate"></span>
			</div>
			<div class="owner">
				<img ID="GRADE">
				<span ID="NICK_NAME">
				</span>
				<span ID="CODE"></span>
			</div>
		</div>

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>오늘의 공지</strong>
			</div>
			<div id="NOTICE" class="tbox tbox01 mt10"></div>
		</div>
		<!--// msgBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>인사말</strong>
			</div>
			<div id="GREETING" class="tbox tbox02 mt10"></div>
		</div>
		<!--// msgBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>주요 경력</strong>
			</div>
			<div id="CAREER" class="tbox tbox02 mt10"></div>
		</div>
		<!--// msgBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>활동 시간(24시)</strong>
			</div>
			<div id="WORK_TIME" class="tbox tbox02 mt10"></div>
		</div>
		<!--// msgBox -->

		<!-- msgBox -->
		<div class="msgBox mt25">
			<div class="title">
				<strong>상담 태그</strong>
			</div>
			<div id="CS_KEYWORD" class="tagBox"></div>
		</div>
		<!--// msgBox -->


		<!-- bottomBtn -->
		<div id="btn_area" class="bottomBtn mt25">



		</div>
		<!-- bottomBtn -->

  </section>

 <style>
	#dockBar {display:none !important;}
 </style>

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
