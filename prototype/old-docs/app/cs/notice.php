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
?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        getNoticeInfo();
    })

    const getNoticeInfo = async () => {
        showLoading();
        let csObj =
            {

            };
        try {
            let param = JSON.stringify(csObj);
            let data = new FormData();
            data.append("csObj", param);
            let result = await axios.post('/api/cs/read_notice_info', data);

            console.log(result);
            if (result.data.isSuc) {
                const notice_info = result.data.list;
                const notice_cnt = notice_info.length;

                let inner = '';
                if (notice_cnt > 0 ) {
                    notice_info.forEach(item => {


                        inner+='<tr>';
                        inner+='    <td>';
                        inner+='       <a href="/app/cs/notice_view?idx='+item.IDX+'">';
                        inner+='            <strong>'+item.TITLE+'</strong>';
                        inner+='           <p>'+item.REGIST_DATE+'</p>';
                        inner+='        </a>';
                        inner+='   </td>';
                        inner+='</tr>';
                    });
                    document.querySelector("#notice_area").innerHTML = inner;
                }
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }

</script>

<section id="csCenterWrap" class="section">
    <div class="topBox">
        <strong>상담사 공지게시판</strong>
    </div>

    <div class="tabWrap">
        <div class="tabList">
            <ul>
                <li class="on">
                    <button type="button">공지사항</button>
                </li>
            </ul>
        </div>

        <div class="noticeTable">
            <table>
                <tbody id="notice_area">

                </tbody>
            </table>
        </div>

    </div>
</section>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>
