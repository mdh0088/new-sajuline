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
            alert('잘못된 접근입니다.');
            location.href='/';
        </script>
        ";
}

$user_idx = $_SESSION['IDX'];
?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        getUserFaqHistory();
    })

    const getUserFaqHistory = async () => {
        showLoading();
        let userObj =
            {
                IDX : <?php echo $user_idx?>
            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/read_faq_history', data);

            console.log(result);

            if (result.data.isSuc) {
                let review_info = result.data.list;

                if (review_info.length > 0) {
                    let inner = '';
                    let user_cont = '';
                    let cs_cont = '';
                    review_info.forEach(item => {

                        user_cont = item.USER_CONT.replace(/<br\s*[/]?>/gi, "\n");
                        inner += '<div class="mypQue">';
                        inner += '  <div class="queQ">';

                        inner += '      <p class="info">';
                        inner += '          <strong>'+item.USER_NICK_NAME+'<span>'+item.CS_NICK_NAME+'<span>'+item.USER_REGIST_DATE+'</span></strong>';
                        if (item.IS_CHK == 'N') {
                            inner += '          <span class="bgMainColor">답변완료</span>';
                        }
                        else {
                            inner += '          <span class="bgGray">답변대기</span>';
                        }
                        inner += '      </p>';

                        inner += '      <p class="cont">';
                        inner += '          '+user_cont;
                        inner += '      </p>';
                        inner += '  </div>';

                        if (item.IS_CHK == 'N') {
                            cs_cont = item.CS_CONT.replace(/<br\s*[/]?>/gi, "\n");
                            inner += '  <div div class="queA">';
                            inner += '      <p class="info">';
                            inner += '          <strong>' + item.CS_NICK_NAME + '</strong>';
                            inner += '          <span>'+item.CS_REGIST_DATE+'</span>';
                            inner += '      </p>';
                            inner += '      <p class="cont">';
                            inner += '          '+cs_cont;
                            inner += '      </p>';
                            inner += '  </div>';
                        }
                        inner += '</div>';
                    });
                    document.querySelector('#faq_area').insertAdjacentHTML("afterbegin", inner);

                }


            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>
<div id="detailTop">
	<div class="inner">
		<div class="leftArea">
			<button type="button" class="btnBack" onclick="pageBack();">
				<img src="/app/assets/img/contents/ico-back-btn.png">
				뒤로가기
			</button>
		</div>
	</div>
</div>

<section id="mypageWrap" class="section myCharge">

	<!-- subTitBox -->
	<div class="subTitBox">
	  <h3>나의 문의내역</h3>
	</div>
	<!--// subTitBox -->

	<div id="faq_area" class="mypQueWrap">
	</div>
</section>



<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '나의 문의내역',
        description:
            '나의 문의내역 : 내가 작성한 문의목록을 한눈에 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/user/history_question',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>

<style>
	footer {display:none !important;}
</style>
