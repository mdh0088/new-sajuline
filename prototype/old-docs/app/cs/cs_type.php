<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if(!isset($_GET['type'])) {
    echo
        "
        <script>
            alert('잘못된 접근입니다.');
            location.href = '/';
        </script>
        ";
}


$type = $_GET['type'];

?>
<?php
	if ($type == 1){
		echo '<title>타로 상담 | 사주로</title>';
	}
	else if ($type == 4){
		echo '<title>사주/운세 | 사주로</title>';
	}
	else if ($type == 2){
		echo '<title>신점 상담 | 사주로</title>';
	}
?>

<script>

    let cs_type = '';
    let cs_chk_new = '';
    let cs_order_type ='';

    document.addEventListener('DOMContentLoaded', () => {
        setCsType('','N');
    })

    const setCsType = (type,chk_new) => {
        cs_type = type;
        cs_chk_new = chk_new;
        getCsByType();


    }

    const setOrderType = (order_type) => {
        cs_order_type = order_type;
        getCsByType();
        let order_nm = "사주로순";
        if (order_type=="review"){
            order_nm = "후기 많은 순";
        } else if(order_type=="bookmark") {
            order_nm = "즐겨찾기 많은 순";
        } else if(order_type=="point") {
            order_nm = "상담포인트 높은 순";
        }
        document.querySelector('#order_nm').innerText = order_nm;
        fn_layer_close('sortPop')
    }

    const getMainReview = async (CS_IDX) => {
        let csObj =
            {
                CS_IDX : CS_IDX
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_main_review', data);

            if (result.data.isSuc) {

                let inner = "";
                let review_list = result.data.list;
                if (review_list.length > 0) {
                    for (let i = 0; i < review_list.length; i++) {
                        inner += '           <li>';
                        inner += '               <a onclick="Javascript:location.href=\'/app/cs/cs_review?idx=' + review_list[i].CS_IDX + '\' ">';
                        inner += '                   <p>';
                        inner += '                       <span>' + (i + 1) + '</span>';
                        inner += '                       ' + review_list[i].USER_CONT + '';
                        inner += '                   </p>';
                        inner += '                   <span>' + review_list[i].NICK_NAME + '</span>';
                        inner += '               </a>';
                        inner += '           </li>';
                    }
                    document.querySelector('#review_area_'+CS_IDX).innerHTML = inner;
                }
            } else {
            }

        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const getCsByType = async () => {
        showLoading();
        let csObj =
            {
                TYPE : <?php echo $type?>,
                STATUS : cs_type,
                CHK_NEW : cs_chk_new,
                ORDER_TYPE : cs_order_type,
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_cs_by_type', data);

            if (result.data.isSuc) {
                let inner = "";
                let type = "";
                let cs_list = result.data.list;

                cs_list.forEach((item, index) => {

                    if (item.TYPE == 1) {
						type="타로";
						// 메타태그

					}
                    if (item.TYPE == 2) {
						type="신점"
						// 메타태그

					}
                    // if (item.TYPE == 3) {type="역학"}
                    if (item.TYPE == 4) {
						type="사주"
						// 메타태그

					}
                    /*
                    review_obj = getMainReviewList(item.IDX);
                    console.log(review_obj);*/

                    inner += '<div class="mainContItem">';
                    inner += '  <div class="csBox">';
                    inner += '      <div class="flBox">';

					if (item.TYPE == 1)
					{
						inner += '          <div class="ibox" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
					}else if (item.TYPE == 2)
					{
						inner += '          <div class="ibox bg5" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
					}else if (item.TYPE == 4)
					{
						inner += '          <div class="ibox bg2" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
					}


					if (item.TYPE == 1)
					{
						inner += '              <span class="cate">'+type+'</span>';
					}else if (item.TYPE == 2)
					{
						inner += '              <span class="cate bg5">'+type+'</span>';
					}else if (item.TYPE == 4)
					{
						inner += '              <span class="cate bg2">'+type+'</span>';
					}

                    inner += '              <img src="/app/assets/upload/cs/'+item.IMG+'">';
                    inner += '          </div>';
                    inner += '          <div class="tbox">';
                    inner += '              <p class="owner" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
                    inner += '                  <span>';
                    inner += '                      <img src="/app/assets/img/contents/ico-rank-'+item.GRADE.toLowerCase()+'.png">';
                    inner += '                          '+item.NICK_NAME+' ';
                    inner += '                  </span>';
                    inner += '                  <span>'+item.CODE+'번</span>';
                    inner += '              </p>';
                    inner += '              <p class="desc">'+item.SHORT_INFO+'</p>';
                    inner += '              <p class="point flBox alC">';
                    inner += '                  <span>p</span>';
                    inner += '                  <em>'+item.AFTER_AMOUNT+'</em>';
                    inner += '              </p>';

                    if (item.STATUS == 1){
                        inner += '              <button type="button" class="csBtn play" onclick="showCallPop('+item.IDX+')">';
                        inner += '                  상담하기';
                        inner += '              </button>';
                    } else if (item.STATUS == 2) {
                        inner += '              <button type="button" class="csBtn ing" onclick="showAlarm(\''+item.IDX+'\',\''+type+'\',\''+item.NICK_NAME+'\',\''+item.CODE+'\',\''+item.STATUS+'\',\''+item.IMG+'\')">';
                        inner += '                  상담중 <span>(접속 알림 설정)</span>';
                        inner += '              </button>';
                    } else {
                        inner += '              <button type="button" class="csBtn miss" onclick="showAlarm(\''+item.IDX+'\',\''+type+'\',\''+item.NICK_NAME+'\',\''+item.CODE+'\',\''+item.STATUS+'\',\''+item.IMG+'\')">';
                        inner += '                  부재중 <span>(접속 알림 설정)</span>';
                        inner += '              </button>';
                    }



                    inner += '          </div>';
                    inner += '     </div>';
                    inner += '	</div>';

                    if (!isNull(item.NOTICE)) {
                        inner += '<div class="notiBox">';
                        inner += '  <ul>';
                        inner += '      <li>';
                        inner += '          <a href="/app/cs/cs_detail?idx='+item.IDX+'">';
                        inner += '              <span class="noti">공지</span>';
                        inner += '              <p>' + item.NOTICE + '</p>';
                        inner += '          </a>';
                        inner += '      </li>';
                        inner += '  </ul>';
                        inner += '</div>';
                    }

                    inner +='<div class="revToggle">';
                    inner +='   <div class="toggleTop flBox alC jcFe">';
                    inner +='       <button type="button" class="revToggleBtn flBox alC" onclick="getMainReview('+item.IDX+'); revToggle(this);">';
                    inner +='           <img src="/app/assets/img/contents/ico-rev-num.png">';
                    inner +='           <p>후기<span>'+item.TOTAL_REVIEW_CNT+'</span></p>';
                    inner +='       </button>';
                    inner +='   </div>';
                    inner +='   <div class="toggleRow">';
                    inner +='       <ul id="review_area_'+item.IDX+'">';

                    inner +='       </ul>';
                    inner +='   </div>';
                    inner +='</div>';
                    inner +='</div>';

                });

                document.querySelector('#cs_area').innerHTML=inner;
                hideLoading();
            } else {
            }

        } catch (err) {
            console.log("Error >>", err);
        }
    }


</script>

<section id="csWrap" class="section">
    <!-- subTitBox -->
    <div class="subTitBox">
        <?php
        if ($type == 1){
			echo '<h3 id="type_title">타로 상담</h3>';
			echo '<span class="desc">SAJUTAROT - 타로 상담 페이지입니다.</span>';
		}
        else if ($type == 4){
			echo '<h3 id="type_title">사주/운세</h3>';
			echo '<span class="desc">SAJUTAROT - 사주/운 페이지입니다.</span>';
		}
        else if ($type == 2){
			echo '<h3 id="type_title">신점 상담</h3>';
			echo '<span class="desc">SAJUTAROT - 신점 상담 페이지입니다.</span>';
		}
        ?>
    </div>
    <!--// subTitBox -->

    <!-- tabWrap -->
    <div class="tabWrap">
        <div class="tabList">
            <ul>
                <li class="on">
                    <!--<button type="button" onclick="getRecruitList(1); tabOpen(event, this, 'mainTab1');">상담가능</button>-->
                    <button type="button" onclick="setCsType('','N'); tabOpen(event, this, 'taro01');">전체</button>
                </li>
                <li>
                    <button type="button" onclick="setCsType(2,'N'); tabOpen(event, this, 'taro02')">상담중</button>
                </li>
                <li>
                    <button type="button" onclick="setCsType('','Y'); tabOpen(event, this, 'taro03')">신규</button>
                </li>
            </ul>
        </div>

        <!-- 정렬 버튼 -->
        <div class="sortBtnWrap">
            <div class="flBox jcFE">
                <button type="button" id="order_nm" onclick="fn_layer('sortPop', 320);">사주로순</button>
            </div>
        </div>
        <!--// 정렬 버튼 -->

        <div id="cs_area" class="tabContWrap">



        </div>
    </div>
    <!--// tabWrap -->

    <!-- 정렬 팝업 -->
    <div class="layer sortPop" id="sortPop">
        <div class="inBox">
            <strong class="tit">정렬</strong>
            <ul class="sortList">
                <li onclick="setOrderType('');">사주로순</li>
                <li onclick="setOrderType('review');">후기 많은 순</li>
                <li onclick="setOrderType('bookmark');">즐겨찾기 많은 순</li>
                <li onclick="setOrderType('point');">상담포인트 높은 순</li>
            </ul>
            <a href="javascript:void(0)" onclick="fn_layer_close('sortPop')">닫기</a>
        </div>
    </div>
    <!--// 정렬 팝업 -->
</section>

<script src="/app/assets/js/setMeta.js"></script>
<script>

    const type = "<?php echo $type?>";
    const metaInfo = {};
    if (type == 1){
        metaInfo.title = '타로상담';
        metaInfo.content = '타로상담 : 내 속마음 꿰뚫는 타로마스터와 1:1 전화상담';
    } else if (type == 2){
        metaInfo.title = '사주/운세';
        metaInfo.content = '사주/운세 : 적중률 좋기로 소문난 상담사와 1:1 전화상담';
    } else if (type == 4) {
        metaInfo.title = '신점상담';
        metaInfo.content = '신점상담 : 용하기로 소문난 상담사와 1:1 전화상담';
    }

    setMeta({
        title: metaInfo.title,
        description: metaInfo.content,
        url: 'https://sajutarot.com/app/cs/cs_type?type='+type,
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
