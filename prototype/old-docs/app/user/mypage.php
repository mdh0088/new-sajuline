<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/header.php");

if (!isset($_SESSION['IDX'])){
    echo "
        <script>
            alert('로그인후 이용부탁드립니다.');
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

$user_idx = $_SESSION['IDX'];

?>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        getUserInfo();
    })

    const getUserInfo = async () => {
        showLoading();
        let userObj =
            {
                IDX : <?php echo $user_idx?>
            };
        try {
            let param = JSON.stringify(userObj);
            let data = new FormData();
            data.append("userObj", param);
            let result = await axios.post('/api/user/read_userInfo', data);

            console.log(result);
            if (result.data.isSuc) {
                let user_point = result.data.userObj.POINT;
                document.querySelector("#USER_POINT").innerHTML=user_point+"P";
            } else {

            }
            hideLoading();
        } catch (err) {
            console.log("Error >>", err);
        }
    }
</script>


<section id="mypageWrap" class="section">
	<!-- subTitBox -->
	<div class="subTitBox">
		<h3>마이페이지</h3>
		<button type="button" class="icoBtn icoSet" onclick="javascript:location.href='/app/user/edit'">설정</button>
	</div>
	<!--// subTitBox -->

	<div class="notiBox mt30">
		<div class="fl flW jcSb">
			<div class="leftArea">
				잔여 포인트 <strong id="USER_POINT"></strong>
			</div>
			<div class="rightArea">
				<a href="/app/charge/point">포인트 충전</a>
			</div>
		</div>
	</div>
	<div class="mypMenu">
		<ul>
			<li><a href="/app/user/history_cs">상담내역</a></li>
			<!-- <li><a href="">최근 상담</a></li> -->
			<!--<li><a href="">관심 상담사</a></li>-->
			<li><a href="/app/user/history_charge">나의 충전내역</a></li>
            <li><a href="/app/user/bookmark">관심 상담사</a></li>
			<li><a href="/app/user/history_review">나의 상담후기</a></li>
			<li><a href="/app/user/history_question">나의 문의내역</a></li>
		</ul>

	</div>

</section>

<script src="/app/assets/js/setMeta.js"></script>
<script>
    setMeta({
        title: '마이페이지',
        description:
            '마이페이지 : 사주로 내 나의 회원정보를 한눈에 ! No.1 전화 사주/타로상담 서비스 플랫폼 사주로',
        url: 'https://sajutarot.com/app/user/mypage',
        keyword: ''
    });
</script>

<?php
require_once($_SERVER['DOCUMENT_ROOT']."/app/common/footer.php");
?>

<style>
	footer {display:none !important;}
</style>
