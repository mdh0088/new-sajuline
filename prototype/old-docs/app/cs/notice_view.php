<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('잘못된 접근입니다.');
            location.href='/app/main';
        </script>
        ";
}

if ($_SESSION['IS_CS']!='Y'){
    echo "
        <script>
            location.href='/app/main';
        </script>
        ";
}

$idx = $_GET['idx'];
?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        getNoticeDetailInfo(<?php echo $idx?>);
    })

    const getNoticeDetailInfo = async (idx) => {

        if (idx=='' || idx==null) {
            alert('마지막 글입니다.');
            return;
        }

        showLoading();
        let noticeObj =
            {
                IDX : idx
            };
        try {
            let param = JSON.stringify(noticeObj);
            let data = new FormData();
            data.append("noticeObj", param);
            let result = await axios.post('/api/cs/read_notice_detail_info', data);

            console.log(result);
            if (result.data.isSuc) {

                let inner ='';
                const obj =  result.data.noticeObj;
                const title =obj.TITLE;
                const cont =obj.CONT.replace(/<br\s*[/]?>/gi, "\n");;
                const regi_date =obj.REGIST_DATE;
                const prev_idx =obj.PREV_IDX;
                const next_idx =obj.NEXT_IDX;

                inner+='<div class="info">';
                inner+='    <strong id="notice_title">'+title+'</strong>';
                inner+='    <p id="notice_date">'+regi_date+'</p>';
                inner+='</div>';
                inner+=' <div class="tbox">';
                inner+='    <pre id="notice_cont">';
                inner+=cont;
                inner+='    </pre>';
                inner+='</div>';
                inner+='<div class="btnArea">';
                inner+='    <button type="button" class="prevBtn" onclick="getNoticeDetailInfo('+prev_idx+')">이전</button>';
                inner+='    <button type="button" class="backBtn" onclick="javascript:location.href=`/app/cs/mypage`">목록</button>';
                inner+='    <button type="button" class="nextBtn end" onclick="getNoticeDetailInfo('+next_idx+')">다음</button>';
                inner+='</div>';

                document.querySelector("#notice_area").innerHTML=inner;
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

</script>

<section id="csCenterWrap" class="section">
    <!-- subTitBox -->
    <div class="subTitBox">
        <h3>공지사항</h3>
    </div>
    <!--// subTitBox -->

    <div class="noticeView" id="notice_area">
        <div class="info">
            <strong id="notice_title"></strong>
            <p id="notice_date"></p>
        </div>
        <div class="tbox">
            <p id="notice_cont">
            </p>
        </div>
        <div class="btnArea">
            <button type="button" class="prevBtn">이전</button>
            <button type="button" class="backBtn" onclick="javascript:location.href='/app/cs/notice'">목록</button>
            <button type="button" class="nextBtn end">다음</button>  <!--마지막글에 class="end" 추가 -->
        </div>
    </div>

</section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
