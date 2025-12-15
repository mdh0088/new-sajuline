<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/';
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
        getReviewInfoWithArs(1);
    })

    const getReviewInfoWithArs = async (month) => {
        showLoading();
        let reviewObj=
            {
                MONTH : month
            };

        try {
            let param = JSON.stringify(reviewObj);
            let data = new FormData();
            data.append("reviewObj", param);
            let result = await axios.post('/api/user/read_review_cs', data);

            console.log(result);
            if (result.data.isSuc) {
                let review_info = result.data.list;

                let inner = '';

                review_info.forEach(item => {

                    const chat_time = item.chat_time;
                    const [hours, minutes, seconds] = chat_time.split(':').map(Number);
                    const totalMinutes = hours * 60 + minutes + seconds / 60;

                    let str = "";
                    if (totalMinutes < 10) {
                        str = '포인트 전화상담(10분 이하)';
                    } else if(totalMinutes >= 10 && totalMinutes<=30){
                        str = '포인트 전화상담(10분 ~ 30분)';
                    } else if(totalMinutes >= 30 && totalMinutes<=60){
                        str = '포인트 전화상담(30분 ~ 60분)';
                    } else if(totalMinutes >= 60){
                        str = '포인트 전화상담(60분 이상)';
                    }

                    let type = "";
                    if (item.csInfo.TYPE == 1) {type="타로"}
                    if (item.csInfo.TYPE == 2) {type="신점"}
                    if (item.csInfo.TYPE == 3) {type="역학"}
                    if (item.csInfo.TYPE == 4) {type="사주"}

					inner +='<div class="csRevBox">';
                    inner +='<div class="leftArea">';
                    inner +='    <div class="iBox">';
                    inner +='       <img src="/app/assets/upload/cs/'+item.csInfo.IMG+'">';
                    inner +='    </div>';
                    inner +='</div>';
                    inner +='<div class="rightArea">';
                    inner +='    <div class="infoBox">';
                    inner +='        <div class="info">';
                    inner +='                    <span>';
                    inner +='                        <em class="cate bg1">'+type+'</em>';
                    inner +='                    </span>';
                    inner +='            <span>'+item.csInfo.NICK_NAME+'</span>';
                    inner +='            <span>'+item.csInfo.CODE+'번</span>';
                    inner +='       </div>';
                    inner +='       <div class="date">';
                    inner +='           <button type="button" onclick="showDetail(\''+item.chat_day+'\',\''+item.csInfo.TYPE+'\',\''+item.chat_time+'\',\''+item.csInfo.NICK_NAME+' '+item.csInfo.CODE+'\',\''+item.usepoint+'\',\''+item.chat_type+'\')">'+item.chat_day+'</button>';
                    inner +='       </div>';
                    inner +='    </div>';
                    inner +='    <div class="desc">';
                    inner +='        '+str;
                    inner +='    </div>';

                    if (item.review_info && !isNull(item.review_info.USER_CONT)){
                        inner +='    <div class="state state-1" onclick="Javascript:location.href=\'/app/cs/cs_review?idx='+item.csInfo.IDX+'\' ">후기 완료</div>';
                    } else {
                        inner +='    <div class="state state-2" onclick="Javascript:location.href=\'/app/cs/cs_review?idx='+item.csInfo.IDX+'\' ">후기 작성하기</div>';
                    }
/*
                    if (item.IS_CHK == 'Y'){
                        inner +='    <div class="state state-1">후기 완료</div>';
                    } else {
                        inner +='    <div class="state state-2">후기 미완료</div>';
                    }
                    */
                    inner +='    </div>';
                    inner +='</div>';

                });
                document.querySelector("#review_area").innerHTML=inner;


            } else {
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

    const showDetail=  (chat_day,type,chat_time,nick_name,usepoint,chat_type) => {
        fn_layer(`csDetailPop`, 320);
        let inner = '';
        inner +='<dl>';
        inner +='    <dt>상담일시</dt>';
        inner +='    <dd>'+chat_day+'</dd>';
        inner +='</dl>';
        inner +='<dl>';
        inner +='    <dt>상담유형</dt>';
        inner +='    <dd>'+type+'</dd>';
        inner +='</dl>';
        inner +='<dl>';
        inner +='    <dt>상담시간</dt>';
        inner +='    <dd>'+chat_time+'</dd>';
        inner +='</dl>';
        inner +='<dl>';
        inner +='    <dt>상담사</dt>';
        inner +='   <dd>'+nick_name+'번</dd>';
        inner +='</dl>';
        inner +='<dl>';
        inner +='    <dt>사용 포인트</dt>';
        inner +='   <dd>'+usepoint+'P</dd>';
        inner +='</dl>';
        inner +='<dl>';
        inner +='    <dt>상담방법</dt>';
        let str = '';
        if (chat_type==1){
            str = '포인트 상담';
        } else {
            str = '후불 상담';
        }
        inner +='    <dd>'+str+'</dd>';

        inner +='</dl>';

        document.querySelector("#detail_area").innerHTML=inner;
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
                    <button type="button" onclick="getReviewInfoWithArs(1);tabOpen(event, this, 'his01');">1개월</button>
                </li>
                <li>
                    <button type="button" onclick="getReviewInfoWithArs(2);tabOpen(event, this, 'his01');">2개월</button>
                </li>
                <li>
                    <button type="button" onclick="getReviewInfoWithArs(3);tabOpen(event, this, 'his01');">3개월</button>
                </li>
            </ul>
        </div>

        <div class="tabContWrap">
            <div id="his01" class="tabContItem">
                <div id="review_area" class="csHisBoxWrap">

                </div>
            </div>
        </div>

    </div>
</section>

<!-- 상담사 내역 > 상담 상세 내역 -->
<div class="layer csDetailPop" id="csDetailPop">
    <div class="inBox">
        <strong class="tit">상담 상세 내역</strong>
        <div class="csDetailTable" id="detail_area">

        </div>
        <a href="javascript:void(0)" onclick="fn_layer_close('csDetailPop')">닫기</a>
    </div>
</div>
<!--// 상담사 내역 > 상담 상세 내역 -->

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '상담내역',
        description:
            '상담내역 : 누구와 상담했을까? 나의 상담내역을 한눈에 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/user/history_cs',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>


<style>
	footer {display:none !important;}
</style>
