<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if(!isset($_GET['type'])) {
    echo "<script>alert('잘못된 접근입니다.');</script>";
}


$type = $_GET['type'];

?>
<script>

    document.addEventListener('DOMContentLoaded', () => {
        getCsByType('','N');
    })

    const getCsByType = async (status,chk_new) => {
        showLoading();
        let csObj =
            {
                TYPE : <?php echo $type?>,
                STATUS : status,
                CHK_NEW : chk_new
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_cs_by_type', data);

            console.log(result);
            if (result.data.isSuc) {
                let inner = "";
                let type = "";
                let cs_list = result.data.list;

                cs_list.forEach((item, index) => {

                    if (item.TYPE == 1) {type="타로"}
                    if (item.TYPE == 2) {type="신점"}
                    // if (item.TYPE == 3) {type="역학"}
                    if (item.TYPE == 4) {type="사주"}
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
                        inner += '              <button type="button" class="csBtn ing" onclick="Javascript:alert(`현재 상담사는 상담중입니다.`);">';
                        inner += '                  상담중';
                        inner += '              </button>';
                    } else {
                        inner += '              <button type="button" class="csBtn miss" onclick="Javascript:alert(`현재 상담사는 부재중입니다.`);">';
                        inner += '                  부재중';
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
                    inner +='       <button type="button" class="revToggleBtn flBox alC" onclick="revToggle(this);">';
                    inner +='           <img src="/app/assets/img/contents/ico-rev-num.png">';
                    inner +='           <p>후기<span>'+item.review_list.length+'</span></p>';
                    inner +='       </button>';
                    inner +='   </div>';
                    inner +='   <div class="toggleRow">';
                    inner +='       <ul>';


                    for (let i = 0; i < item.review_list.length; i++) {
                        if (i === 3) {
                            break;
                        }
                        const review = item.review_list[i];

                        inner += '           <li>';
                        inner += '               <a onclick="Javascript:location.href=\'/app/cs/cs_review?idx='+item.IDX+'\' ">';
                        inner += '                   <p>';
                        inner += '                       <span>' + (i+1) + '</span>';
                        inner += '                       ' + review.USER_CONT + '';
                        inner += '                   </p>';
                        inner += '                   <span>' + review.NICK_NAME + '</span>';
                        inner += '               </a>';
                        inner += '           </li>';
                    }


                    inner +='       </ul>';
                    inner +='   </div>';
                    inner +='</div>';
                    inner +='</div>';

                });


                //document.querySelector('#cs_area').insertAdjacentHTML("beforeend", inner);
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
        if ($type == 1){echo '<h3 id="type_title">타로 상담</h3>';}
        else if ($type == 4){echo '<h3 id="type_title">사주/운세</h3>';}
        else if ($type == 2){echo '<h3 id="type_title">신점 상담</h3>';}
        ?>
    </div>
    <!--// subTitBox -->

    <!-- tabWrap -->
    <div class="tabWrap">
        <div class="tabList">
            <ul>
                <li class="on">
                    <!--<button type="button" onclick="getRecruitList(1); tabOpen(event, this, 'mainTab1');">상담가능</button>-->
                    <button type="button" onclick="getCsByType('','N'); tabOpen(event, this, 'taro01');">전체</button>
                </li>
                <li>
                    <button type="button" onclick="getCsByType(2,'N