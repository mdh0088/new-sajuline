<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");
?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        //getAdminFaqInfo();
    })


    const getAdminFaqInfo = async () => {
        showLoading();
        let faqObj ={};

        try {
            let param = JSON.stringify(faqObj);
            let data = new FormData();
            data.append("faqObj", param);
            let result = await axios.post('/api/user/read_admin_faq_info', data);

            console.log(result);
            if (result.data.isSuc) {

                let inner = '';
                let review_info = result.data.list;
                let user_cont = '';
                let admin_cont = '';

                if (review_info.length > 0) {

                    review_info.forEach(item => {
                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");

                        inner += '<div class="mypQue">';
                        inner += '  <div class="queQ">';
                        inner += '      <p class="info">';
                        inner += '			<strong>'+item.USER_NICK_NAME+'<span>'+item.USER_REGIST_DATE+'</span>'+'</strong>';
                        if (!isNull(item.ADMIN_CONT)) {
                            inner += '      <span class="bgMainColor" value="답변 완료">답변 완료</span>';
                        } else {
                            inner += '      <span class="bgGray" value="답변 완료">답변대기</span>';
                        }
                        inner += '      </p>';
                        inner += '		<span>'+item.USER_TITLE+'</span>'; //제목

                        inner += '      <p class="cont"><pre>'+user_cont+'</pre></p>';
                        inner += '  </div>';

                        if (!isNull(item.ADMIN_CONT)) {
                            admin_cont =item.ADMIN_CONT.replace(/<br\s*[/]?>/gi, "\n");

                            inner += '  <div class="queA">';
                            inner += '      <p class="info">';
                            inner += '			<strong>관리자</strong>';
                            inner += '			<span>'+item.ADMIN_REGIST_DATE+'</span>';
                            inner += '		</p>';
                            inner += '      <p class="cont"><pre>'+admin_cont+'</pre></p>';
                            inner += '  </div>';
                        }
                        inner += '</div>';

                    });

                    document.querySelector('#faq_area').innerHTML=inner;
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

        let faq_title =  document.querySelector('#faq_cont_1').value;
        let faq_cont =  document.querySelector('#faq_cont_2').value;

        if (isNull(faq_title)){
            alert('제목을 작성해주세요.');
            return;
        }

        if (isNull(faq_cont)){
            alert('문의 내용을 작성해주세요.');
            return;
        }

        let faqObj =
            {
                TITLE  : faq_title,
                CONT : faq_cont
            };

        try {
            let param = JSON.stringify(faqObj);
            let data = new FormData();
            data.append("faqObj", param);
            let result = await axios.post('/api/user/doFaq', data);

            console.log(result);
            //alert(result.data.message);
            if (result.data.isSuc) {
                getAdminFaqInfo();
                //location.reload();
            } else {
                alert(result.data.message);
            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>
<section id="csCenterWrap" class="section">
    <div class="topBox">
        <strong>사주로 고객센터</strong>
        <p class="call">02.6212.0465</p>
        <p class="info1">
            카카오톡 : tarob  I 이메일 : tarotb@naver.com
        </p>
        <p class="info2">
            업무시간 : 09:00~17:00<br>
            점심시간 : 12:00~13:00<br>
            주말 및 공휴일 휴무
        </p>
    </div>

    <div class="tabWrap">
        <div class="tabList">
            <ul>
                <li>
                    <button type="button" onclick="window.location.href='/app/cscenter/notice'">공지사항</button>
                </li>
                <li>
                    <button type="button" onclick="window.location.href='/app/cscenter/faq'">FAQ</button>
                </li>
                <li class="on">
                    <button type="button">1:1문의</button>
                </li>
            </ul>
        </div>

        <!-- subTitBox -->
        <div class="subTitBox">
            <h3>1:1 문의</h3>
        </div>
        <!--// subTitBox -->

        <div class="csFaqTop">
            <p>
                상담문의는 상담 가능시간, 인사등의<br>
                간단한 문의만 가능합니다.
            </p>
            <input type="button" class="btn bgMainColor writeBtn w100p" value="문의하기" onclick="fn_layer('layer09', 320);">
        </div>


        <div id="faq_area" class="mypQueWrap">

        </div>


    </div>
</section>

<!-- 상담사 문의하기 -->
<div class="layer layer09" id="layer09">
    <div class="inBox">
        <strong class="tit">문의하기</strong>
        <div class="popCont">
            <div class="comm">
                <strong>문의내용</strong>
                <textarea id="faq_cont_1" class="mt10" title="문의 제목 작성" placeholder="제목을 작성해주세요."></textarea>
                <textarea id="faq_cont_2" class="mt10" title="문의 내용 작성" placeholder="문의 내용을 작성해주세요."></textarea>
            </div>
            <!-- btnArea -->
            <div class="btnArea">
                <button type="button" onclick="doFaq(); fn_layer('layer10', 320); fn_layer_close('layer09');" class="btn btnBlack">등록하기</button>
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

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '1:1 문의',
        description:
            '1:1 문의 : 사주로 로그인 후 더욱 다양한 혜택을 만나보세요!사주로는 회원에겐 언제나 할인상담 제공!',
        url: 'https://sajutarot.com/app/cscenter/inquiry',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
