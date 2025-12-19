<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>
<script src="/app/assets/js/swiper.min.js"></script>
<script src="/app/assets/js/swiper-bundle.min.js"></script>
<link rel="stylesheet" href="/app/assets/js/swiper.min.css"></script>



<script>
    let jb = {};
    let search_arry = new Array();
    let report_idx = "";

    document.addEventListener('DOMContentLoaded', () => {
        getSearchList();
        getRecentReview();
        getSearchKeyword();
    })

    const getSearchList = () => {
        let search_set = new Set();
        let get_list = JSON.parse(localStorage.getItem("searchList"));

        if (get_list != null) {
            // 중복 값을 제거하면서 검색어 배열에 추가
            get_list.list.forEach(item => search_set.add(item));

            let inner = "";
            search_set.forEach((item, i) => {
                inner += '<span id="search_list_'+i+'" class="search_list">';
                inner += '	<button type="button" onclick="searhByList(\''+item+'\');">'+item+'</button>';
                inner += '	<button type="button" class="btnDel" onclick="search_list_del('+i+');">삭제</button>';
                inner += '</span>';
            });

            // 검색어 목록을 HTML에 삽입
            document.querySelector('#search_iist_target').innerHTML = inner;
        }
    };

    const searhByList = (keyword) => {
        document.querySelector('#search_name').value=keyword;
        getList(keyword);
    }

    const search_list_del = (idx) => {
        search_arry.splice(idx,1);
        jb.list = search_arry;
        localStorage.setItem("searchList", JSON.stringify(jb));
        document.querySelector('#search_list_'+idx).remove();
        getSearchList();
    }

    const delAll = () => {
        localStorage.clear();
        document.querySelectorAll('.search_list').forEach(function(node) {
            node.remove();
        });
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

    const getRecentReview = async () => {
        showLoading();
        let searchObj =
            {

            };
        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            let result = await axios.post('/api/cs/search_recent_reivew', data);
            console.log(result);
            let inner = '';
            let user_cont = '';
            if (result.data.isSuc) {
                let review_list = result.data.list;
                if (review_list.length > 0 ){
                    review_list.forEach((item) => {
                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner +='<div class="swiper-slide">';
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
                        inner +='           <div class="tbox">';
                        inner += '              <p id="user_cont_'+item.IDX+'" class="cont">';
                        inner +=                    user_cont;
                        inner += '              </p>';
                        inner +='           </div>';
                        inner +='       </div>';
                        inner +='   </div>';
                        inner +='</div>';
                    });
                }
            } else {

            }
            //document.querySelector('#slide_area').insertAdjacentHTML("beforebegin", inner);
            document.querySelector('#slide_area').innerHTML=inner;
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getSearchKeyword = async () => {
        showLoading();
        let searchObj =
            {

            };
        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            let result = await axios.post('/api/cs/read_keyword', data);
            console.log(result);
            let inner = '';
            if (result.data.isSuc) {
                let keyword_list = result.data.list;
                if (keyword_list.length > 0 ){
                    keyword_list.forEach((item,i) => {
                        inner +='<li>';
                        inner +='    <button type="button" onclick="searhByList(\''+item.KEYWORD+'\');">';
                        inner +='        <span>'+(i+1)+'</span>';
                        inner +='        <p>'+item.KEYWORD+'</p>';
                        inner +='    </button>';
                        inner +='</li>';
                    });
                }
            } else {

            }
            //document.querySelector('#slide_area').insertAdjacentHTML("beforebegin", inner);
            document.querySelector('#keyword_area').innerHTML=inner;
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getList = async (type) => {

        if (type!="search") {
            search_name = $('#search_name').val();
            if (search_name!="") {
                search_arry.push(search_name);
                jb.list = search_arry;
                localStorage.setItem("searchList", JSON.stringify(jb));
            }
            getSearchList();
        }
        showLoading();
        let searchObj =
        {
            SEARCH_NAME : document.querySelector("#search_name").value

        };

        try {
            let param = JSON.stringify(searchObj);
            let data = new FormData();
            data.append("searchObj", param);
            let result = await axios.post('/api/cs/search_cs', data);
            let inner = "";
            console.log(result);
            if (result.data.isSuc) {
                document.getElementById( "before_search" ).style.display = "none";
                document.getElementById( "after_search" ).style.display = "";
                let cs_list = result.data.list;
                let cs_type = "";
                if (cs_list.length > 0 ){
                    inner += '<div class="srchBox">';
                    inner += '    <div class="titBox">';
                    inner += '        <div class="leftArea">';
                    inner += '            <h3>검색결과</h3>';
                    inner += '        </div>';
                    inner += '    </div>';
                    cs_list.forEach((item, i) => {
                        if (item.TYPE == 1){ cs_type = '타로' }
                        else if (item.TYPE == 2){ cs_type = '신점' }
                        else if (item.TYPE == 3){ cs_type = '역학' }
                        else if (item.TYPE == 4){ cs_type = '사주' }
                        inner += '    <div class="csBox">';
                        inner += '        <div class="flBox">';

						if (item.TYPE == 1) {
							inner += '            <div class="ibox" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}else if (item.TYPE == 4)
						{
							inner += '            <div class="ibox bg2" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}else if (item.TYPE == 2)
						{
							inner += '            <div class="ibox bg5" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
						}



						if (item.TYPE == 1) {
	                        inner += '                <span class="cate">'+cs_type+'</span>';
						}else if (item.TYPE == 4)
						{
	                        inner += '                <span class="cate bg2">'+cs_type+'</span>';
						}else if (item.TYPE == 2)
						{
	                        inner += '                <span class="cate bg5">'+cs_type+'</span>';
						}


                        inner += '                <img src="/app/assets/upload/cs/'+item.IMG+'">';
                        inner += '            </div>';
                        inner += '            <div class="tbox">';
                        inner += '                <p class="owner" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
                        inner += '		            <span>';
                        inner += '			            <img src="/app/assets/img/contents/ico-rank-silver.png">';
                        inner += '			            '+item.NICK_NAME+' ';
                        inner += '		            </span>';
                        inner += '                   <span>'+item.CODE+'번</span>';
                        inner += '                <span class="point flBox alC">';
                        inner += '                  <span>p</span>';
                        inner += '                  <em>'+item.AFTER_AMOUNT+'</em>';
                        inner += '                </span>';
                        inner += '                </p>';
                        inner += '                <p class="desc">'+item.SHORT_INFO+'</p>';

                        if (item.STATUS == 1){
                            inner += '                <button type="button" class="csBtn play" onclick="showCallPop('+item.IDX+')">';
                            inner += '                    상담하기';
                            inner += '                </button>';
                        } else if(item.STATUS == 2){
                            inner += '                <button type="button" class="csBtn ing" onclick="Javascript:alert(`현재 상담사는 상담중입니다.`);">';
                            inner += '                    상담중';
                            inner += '                </button>';
                        } else {
                            inner += '                <button type="button" class="csBtn miss" onclick="Javascript:alert(`현재 상담사는 부재중입니다.`);">';
                            inner += '                    부재중';
                            inner += '                </button>';
                        }

                        inner += '            </div>';
                        inner += '        </div>';
                        inner += '    </div>';
                    });
                    inner += '</div>';
                } else {
                    inner += '<div class="nodata">';
                    inner += '    <p>"'+searchObj.SEARCH_NAME+'" 검색 결과가 없습니다.</p>';
                    inner += '</div>';
                }
            } else {

            }
            document.querySelector('#after_search').innerHTML=inner;
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>


<div id="detailTop" class="searchTop">
	<div class="inner">
		<div class="leftArea fN">
			<button type="button" class="btnBack" onclick="pageBack();">
				<img src="/app/assets/img/contents/ico-back-btn.png">
			</button>
			<div class="searchBox">
				<input type="text" id="search_name" title="검색어 입력" placeholder="검색어를 입력해주세요" onkeypress="if (event.keyCode == 13) getList()">
				<button type="button" class="btnSearch" onclick="getList()"></button>
			</div>
		</div>

	</div>
</div>


<section id="searchWrap" class="section">
	<div class="inner">
        <div class="srchBox">
            <div class="sbox searchHis">
                <div class="titBox fl alC jcSb">
                    <h3>최근검색어</h3>
                    <button type="button" onclick="delAll();">전체삭제</button>
                </div>
                <div class="hisBox" id="search_iist_target">

                </div>
            </div>
        </div>

        <div id="before_search">
            <!-- srchBox -->
            <div id="review_area" class="srchBox">

                <div class="titBox">
                    <div class="leftArea">
                        <h3>실시간 후기</h3>
                    </div>
                </div>

                <div class="slideWrap">
                    <div class="swiper-container dot row-01">
                        <div id="slide_area" class="swiper-wrapper">

                        </div>
                        <div class="swiper-pagination"></div>
                    </div>
                </div>

            </div>
            <!--// srchBox -->

            <!-- srchBox -->
            <div class="srchBox">
                <div class="titBox">
                    <div class="leftArea">
                        <h3>인기 검색어</h3>
                    </div>
                </div>
                <div class="srchList">
                    <ul id="keyword_area">

                    </uL>
                </div>
            </div>
            <!--// srchBox -->
        </div>

        <div id="after_search">

        </div>

	</div>
</section>


<!-- 신고하기 -->
<div class="layer layer03" id="layer03">
    <div class="inBox">
        <strong class="tit">신고하기</strong>
        <div class="popCont">

            <div class="comm">
                <strong class="mainColor">리뷰 내용</strong>
                <p id="target_report_cont" class="mt10">
                    신고내용신고내용신고내용신고내용신고내용신고내용신고내용신고내용신고내용신고내용
                </p>
                <strong class="mt25">작성자 : 김진오</strong>
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
                <button type="button" onclick="doReport(); fn_layer_close('layer03'); " class="btn btnBlack">등록</button>
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


<style>
	.swiper-wrapper {height:auto !important;}
</style>
<script>
	// swiper
	function slideSwiper(){

		var $slideItem01 = $(".swiper-container.col-01"),
			 $slideItem04 = $(".swiper-container.row-01");

		if(!$(".swiper-container").length > 0) return false;

		// col-01
		$slideItem01.each(function(i, el){
			var $this = $(this);
			$this.addClass('swiperCol01-' + i + 1);

			var swiper = new Swiper('.swiperCol01-' + i + 1, {
				observer: true,
				observeParents: true,
				slidesPerView : 2.3,
				spaceBetween: 15,
				autoHeight : true,
				breakpoints: {
					470: {
						slidesPerView : 1.4,
					},
				},
				watchOverflow: true
			});
		});
		// row-01
		$slideItem04.each(function(i, el){
			var $this = $(this);
			$this.addClass('swiperRow01-' + i + 1);

			var swiper = new Swiper('.swiperRow01-' + i + 1, {
				observer: true,
				observeParents: true,
				slidesPerView : 1,
				spaceBetween: 15,
				autoHeight : true,
				breakpoints: {
					470: {
						slidesPerView :1,
					},
				},
				watchOverflow: true,
				pagination : {
					el : '.swiper-pagination',
					clickable : true,
				},
			});
		});


	}
	$(window).on("load", function(){
		slideSwiper();
	})
</script>


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
<div class="layer csApplication" id="csApplicationPop">

</div>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '상담사 검색',
        description:
            '검색 : 사주로의 모든 정보를 한눈에! 내가 원하는 상담분야를 검색해보세요!',
        url: 'https://sajutarot.com/app/search/list',
        keyword: ''
    });
</script>