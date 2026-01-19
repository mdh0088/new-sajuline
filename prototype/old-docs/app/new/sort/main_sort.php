<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
include_once $_SERVER['DOCUMENT_ROOT'].'/api/shared/daily_log.php';
?>
<script src="/app/assets/js/swiper.min.js"></script>
<script src="/app/assets/js/swiper-bundle.min.js"></script>
<link rel="stylesheet" href="/app/assets/js/swiper.min.css"></script>

<style>
    #noti_area {
        position: relative;
        overflow: hidden;
        height: 30px; /* 원하는 높이로 설정하세요 */
    }
    #noti_area ul {
        position: absolute;
        margin: 0;
        padding: 0;
    }
    #noti_area li {
        list-style-type: none;
        margin-bottom: 10px; /* 원하는 간격으로 조절하세요 */
    }
</style>

<script>

    let cs_type = '';
    let cs_order_type ='';

    document.addEventListener('DOMContentLoaded', () => {

        getReview();
        setCsType('all');
        setOrderType('');

        const notiBox = document.getElementById('noti_area');
        const notiList = notiBox.querySelector('ul');

        function rollNotiBox() {
            const firstItem = notiBox.querySelector('li:first-child');

            firstItem.style.transition = 'margin-top 1s';
            firstItem.style.marginTop = `-${firstItem.offsetHeight}px`;

            setTimeout(() => {
                firstItem.style.transition = '';
                firstItem.style.marginTop = '';
                notiList.appendChild(firstItem);
            }, 1000);
        }

        setInterval(rollNotiBox, 3000); // 롤링 간격을 설정하세요 (여기서는 3초)
    })

    const setCsType = (type) => {
        cs_type = type;
        getRecruitList();
    }

    const setOrderType = (order_type) => {
        cs_order_type = order_type;
        getRecruitList();
        fn_layer_close('sortPop')
    }

    const getReview = async () => {
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_main_review', data);

            console.log(result);
            if (result.data.isSuc) {

                const noti_list = result.data.list;
                let inner = '';
                let user_cont = '';
                noti_list.forEach((item, index) => {
                    user_cont = item.USER_CONT;
                    if (user_cont.length > 40) {
                        user_cont = user_cont.slice(0, 40) + '...';
                    }

                    inner += '<li>';
                    inner += '    <a href="/app/cs/cs_review?idx='+item.CS_IDX+'">';
                    inner += '        <span>후기</span>';
                    inner += '        <p>'+user_cont+'</p>';
                    inner += '    </a>';
                    inner += '</li>';
                });
                document.querySelector('#noti_ul').innerHTML=inner;
            } else {
            }

        } catch (err) {
            console.log("Error >>", err);
        }
    }


    const getRecruitList = async () => {
        showLoading();
        document.querySelector('#cs_area').innerHTML = "";
        let csObj =
            {
                TYPE : cs_type,
                ORDER_TYPE : cs_order_type
            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_main', data);

            console.log(result);
            if (result.data.isSuc) {
                let inner = "";
                let type = "";
                let cs_list = result.data.list;
                cs_list.forEach((item, index) => {



                    if (item.TYPE == 1) {type="타로"}
                    if (item.TYPE == 2) {type="신점"}
                    if (item.TYPE == 3) {type="역학"}
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

                    //inner += '              <img src="/app/assets/upload/cs/'+item.IMG+'">';
                    inner += '              <img data-src="/app/assets/upload/cs/'+item.IMG+'" src="" class="lazy-load">';
                    inner += '          </div>';
                    inner += '          <div class="tbox flBox fdC jcSB">';
                    inner += '              <div class="topArea">';
                    inner += '					<p class="owner" onclick="Javascript:location.href=\'/app/cs/cs_detail?idx='+item.IDX+'\' ">';
                    inner += '						<span>';

                    inner += '							<img src="/app/assets/img/contents/ico-rank-'+item.GRADE.toLowerCase()+'.png">';

                    inner += '                          '+item.NICK_NAME+' ';
                    inner += '						</span>';
                    inner += '						<span>'+item.CODE+'번</span>';
                    inner += '						<span class="point flBox alC">';
                    inner += '							<span>p</span>';
                    inner += '							<em>'+item.AFTER_AMOUNT+'</em>';
                    inner += '						</span>';
                    inner += '					</p>';
                    inner += '					<p class="desc">'+item.SHORT_INFO+'</p>';
                    inner += '              </div>';

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

                    inner += '          </div>';
                    inner += '     </div>';
                    inner += '	</div>';

                    if(!isNull(item.NOTICE)) {
                        inner += '<div class="notiBox">';
                        inner += '  <ul>';
                        inner += '      <li>';
                        inner += '          <a href="#">';
                        inner += '              <span class="noti">공지